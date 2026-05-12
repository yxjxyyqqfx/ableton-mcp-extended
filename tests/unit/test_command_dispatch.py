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
