"""Tests for the VALID_COMMANDS allowlist used by AbletonMCP._process_command dispatch.

These tests verify that the registry is well-formed and covers the read-only
plus mutating handlers expected by the server. Handler bodies are not exercised
here because they depend on the Ableton Live runtime; this is purely the
allowlist contract.
"""

import sys
import types
from unittest import mock


def _import_remote_script_module():
    """Load AbletonMCP_Remote_Script with stubs for the Live-only _Framework dep."""
    if "_Framework" not in sys.modules:
        framework = types.ModuleType("_Framework")
        sys.modules["_Framework"] = framework

        control_surface = types.ModuleType("_Framework.ControlSurface")

        class _ControlSurfaceStub:
            def __init__(self, *args, **kwargs):
                pass

        control_surface.ControlSurface = _ControlSurfaceStub
        sys.modules["_Framework.ControlSurface"] = control_surface
        framework.ControlSurface = control_surface

    import AbletonMCP_Remote_Script as pkg  # noqa: WPS433
    return pkg


def test_valid_commands_is_frozenset():
    """VALID_COMMANDS must be an immutable frozenset to prevent runtime mutation."""
    pkg = _import_remote_script_module()
    assert isinstance(pkg.VALID_COMMANDS, frozenset)


def test_valid_commands_contains_baseline_read_handlers():
    """Read-only handlers expected to be supported in upstream baseline."""
    pkg = _import_remote_script_module()
    for cmd in ("get_session_info", "get_track_info"):
        assert cmd in pkg.VALID_COMMANDS, "expected {0} in VALID_COMMANDS".format(cmd)


def test_valid_commands_contains_baseline_mutating_handlers():
    """Mutating handlers that existed before the refactor must remain allowlisted."""
    pkg = _import_remote_script_module()
    expected = {
        "create_midi_track",
        "set_track_name",
        "create_clip",
        "add_notes_to_clip",
        "set_tempo",
        "fire_clip",
        "stop_clip",
        "start_playback",
        "stop_playback",
        "load_browser_item",
        "set_song_time",
        "set_arrangement_loop",
        "create_arrangement_clip",
        "set_device_parameter",
        "delete_track",
        "set_track_volume",
        "set_track_panning",
    }
    missing = expected - pkg.VALID_COMMANDS
    assert not missing, "expected commands missing from VALID_COMMANDS: {0!r}".format(sorted(missing))


def test_valid_commands_rejects_unknown_command_names():
    """Sanity: random unknown command names are NOT in the allowlist."""
    pkg = _import_remote_script_module()
    for bogus in ("delete_universe", "fly_to_moon", ""):
        assert bogus not in pkg.VALID_COMMANDS


def test_main_thread_task_commands_are_in_allowlist():
    """Regression guard: every `command_type == "X"` branch inside
    `main_thread_task()` must have a matching VALID_COMMANDS entry.

    _process_command dispatches mutating commands through the
    `elif command_type in VALID_COMMANDS:` branch which schedules
    main_thread_task. If a command is in main_thread_task body but missing
    from the allowlist, it falls through to the next elif (or to
    'Unknown command') instead of running on the main thread.

    Read-only commands dispatched OUTSIDE main_thread_task (e.g.
    `get_browser_tree`, `get_arrangement_info`) are intentionally NOT in
    the allowlist — they are dispatched via specific elif cases AFTER
    the `in VALID_COMMANDS` branch and rely on falling through. The
    only exceptions are `get_session_info` and `get_track_info`, which
    are dispatched BEFORE the allowlist branch and remain in the set
    for completeness.
    """
    import pathlib
    import re

    pkg = _import_remote_script_module()
    source = pathlib.Path(pkg.__file__).read_text(encoding="utf-8")

    # Extract command_type matches inside the def main_thread_task() body.
    body_match = re.search(
        r"def main_thread_task\(\):(?P<body>.*?)response_queue\.put\(\s*\{\s*\"status\":\s*\"success\"",
        source,
        re.DOTALL,
    )
    assert body_match, "Failed to locate main_thread_task body"
    pattern = re.compile(r'command_type\s*==\s*"([a-z_][a-z0-9_]*)"')
    main_thread = set(pattern.findall(body_match.group("body")))
    assert main_thread, "Failed to extract dispatch branches from main_thread_task body"

    missing = sorted(main_thread - set(pkg.VALID_COMMANDS))
    assert not missing, (
        "main_thread_task handlers missing from VALID_COMMANDS allowlist: {0!r}. "
        "Add them to VALID_COMMANDS so the dispatcher routes them through the "
        "main-thread scheduler.".format(missing)
    )
