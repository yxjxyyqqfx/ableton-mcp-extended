"""Tests for fork-only B10/B11/B12 features (name-based sample loading + filepath
resolution + user_folders cleanup).

These bundles are intentionally fork-only — they carry hardcoded host/container
paths (`/ocp/mnt/_lib_`, `/ocp/mnt/Splice`) and a fixed valid_roots whitelist
(`User_folders/_lib_`, `User_folders/Splice`) that would need design discussion
before going upstream. See docs/PRIORITY.md B10/B11/B12 for the rework plan.

The tests cover allowlist membership, handler-method presence, and server
@mcp.tool() registration. Live runtime behavior (real browser walk, real path
resolution) is exercised by the QA scripts in the fork.
"""

import sys
import types

import pytest


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

    if "Queue" not in sys.modules:
        sys.modules["Queue"] = sys.modules["queue"]

    import AbletonMCP_Remote_Script  # noqa: WPS433

    return AbletonMCP_Remote_Script


@pytest.fixture
def remote_mod():
    return _import_remote_script_module()


@pytest.fixture
def script(remote_mod):
    """Construct a bare AbletonMCP instance bypassing __init__'s socket setup."""
    instance = remote_mod.AbletonMCP.__new__(remote_mod.AbletonMCP)
    instance.log_message = lambda *args, **kwargs: None
    return instance


def test_valid_commands_contains_b10_b11_entries(remote_mod):
    """B10/B11 dispatch is wired via VALID_COMMANDS allowlist."""
    assert "load_browser_sample_by_name" in remote_mod.VALID_COMMANDS
    assert "resolve_filepath_to_browser_path" in remote_mod.VALID_COMMANDS


def test_handler_methods_exist_on_ableton_mcp(remote_mod):
    """B10/B11 handler methods are defined on the AbletonMCP class."""
    assert hasattr(remote_mod.AbletonMCP, "_load_browser_sample_by_name")
    assert hasattr(remote_mod.AbletonMCP, "_find_browser_item_by_name_under_path")
    assert hasattr(remote_mod.AbletonMCP, "_resolve_filepath_to_browser_path")


def test_filepath_browser_mapping_is_class_level_constant(remote_mod):
    """B11 _FILEPATH_BROWSER_MAPPING is a class attribute with hardcoded paths."""
    mapping = remote_mod.AbletonMCP._FILEPATH_BROWSER_MAPPING
    assert isinstance(mapping, list)
    # Sanity-check that the two main mount prefixes are present.
    prefixes = {entry[0] for entry in mapping}
    assert "/ocp/mnt/_lib_" in prefixes
    assert "/ocp/mnt/Splice" in prefixes
    # Both should map to User_folders/* browser roots.
    browser_roots = {entry[1] for entry in mapping}
    assert "User_folders/_lib_" in browser_roots
    assert "User_folders/Splice" in browser_roots


def test_resolve_filepath_returns_browser_root_for_exact_prefix(script):
    """B11: exact prefix match returns the browser root verbatim."""
    assert script._resolve_filepath_to_browser_path("/ocp/mnt/_lib_") == "User_folders/_lib_"
    assert script._resolve_filepath_to_browser_path("/ocp/mnt/Splice") == "User_folders/Splice"


def test_resolve_filepath_appends_relative_suffix(script):
    """B11: subpath under a known mount maps to <browser_root>/<rel>."""
    assert script._resolve_filepath_to_browser_path("/ocp/mnt/_lib_/Drums/Kick.wav") == \
        "User_folders/_lib_/Drums/Kick.wav"
    assert script._resolve_filepath_to_browser_path("/ocp/mnt/Splice/Pack/snare.flac") == \
        "User_folders/Splice/Pack/snare.flac"


def test_resolve_filepath_rejects_unknown_prefix(script):
    """B11: paths outside the hardcoded mapping raise typed ValueError."""
    with pytest.raises(ValueError, match="unsupported_prefix"):
        script._resolve_filepath_to_browser_path("/tmp/random.wav")


def test_resolve_filepath_rejects_empty(script):
    """B11: empty filepath raises typed ValueError."""
    with pytest.raises(ValueError, match="empty_path"):
        script._resolve_filepath_to_browser_path("")


def test_server_tool_load_browser_sample_by_name_is_registered():
    """B10 @mcp.tool() wrapper is registered with a docstring marked fork-only."""
    _import_remote_script_module()
    from MCP_Server import server

    assert hasattr(server, "load_browser_sample_by_name")
    doc = server.load_browser_sample_by_name.__doc__ or ""
    assert "Fork-only" in doc or "fork-only" in doc.lower()
    # Valid roots should be mentioned somewhere in the docstring or signature.
    assert "User_folders" in doc or "search_root" in doc


def test_server_tool_resolve_filepath_is_registered():
    """B11 @mcp.tool() wrapper is registered with a docstring marked fork-only."""
    _import_remote_script_module()
    from MCP_Server import server

    assert hasattr(server, "resolve_filepath_to_browser_path")
    doc = server.resolve_filepath_to_browser_path.__doc__ or ""
    assert "Fork-only" in doc or "fork-only" in doc.lower()


def test_server_tool_load_browser_sample_rejects_invalid_search_root():
    """B10 server wrapper short-circuits invalid search_root before contacting Live."""
    _import_remote_script_module()
    from MCP_Server import server

    # Without a live connection this would fail at send_command; but the
    # invalid-search-root check should short-circuit BEFORE that.
    result = server.load_browser_sample_by_name(
        ctx=None,
        track_index=1,
        filename="kick.wav",
        search_root="Library/Kicks",  # not in valid_roots
        pad_note=36,
        rack_device_index=1,
        replace=False,
    )
    assert "invalid_search_root" in result
