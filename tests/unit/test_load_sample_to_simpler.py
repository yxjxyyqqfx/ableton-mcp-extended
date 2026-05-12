"""Tests for the load_sample_to_simpler tool wrapper + handler (B7 bundle)."""

import importlib
import os
import sys
import types

import pytest


def _reload_server():
    import MCP_Server.server as server  # noqa: WPS433
    return importlib.reload(server)


def _make_remote_script():
    framework = types.ModuleType("_Framework")
    control_surface = types.ModuleType("_Framework.ControlSurface")

    class _ControlSurfaceStub:
        def __init__(self, *args, **kwargs):
            pass

        def song(self):
            return None

        def show_message(self, msg):
            pass

        def log_message(self, msg):
            pass

        def schedule_message(self, delay, fn):
            fn()

    control_surface.ControlSurface = _ControlSurfaceStub
    sys.modules["_Framework"] = framework
    sys.modules["_Framework.ControlSurface"] = control_surface
    framework.ControlSurface = control_surface
    sys.modules.pop("AbletonMCP_Remote_Script", None)
    import AbletonMCP_Remote_Script as pkg  # noqa: WPS433
    return pkg


def test_remote_script_registers_load_sample_to_simpler_command():
    """The new command name must be present in the VALID_COMMANDS allowlist."""
    pkg = _make_remote_script()
    assert "load_sample_to_simpler" in pkg.VALID_COMMANDS


def test_remote_script_handler_method_exists():
    """The _load_sample_to_simpler handler is bound on the class."""
    pkg = _make_remote_script()
    assert hasattr(pkg.AbletonMCP, "_load_sample_to_simpler")


def test_server_tool_is_registered():
    """The server module exposes load_sample_to_simpler as an MCP tool."""
    server = _reload_server()
    assert hasattr(server, "load_sample_to_simpler")
    tool_obj = server.load_sample_to_simpler
    fn = getattr(tool_obj, "fn", None) or getattr(tool_obj, "_fn", None) or tool_obj
    assert callable(fn)
    assert fn.__doc__ and "Load a browser sample item" in fn.__doc__


def test_server_tool_returns_loaded_message_on_success():
    """The wrapper returns a human-readable success string and includes the device list."""
    server = _reload_server()
    from unittest import mock

    fake_conn = mock.MagicMock()
    fake_conn.send_command.return_value = {
        "loaded": True,
        "item_name": "Kick.wav",
        "devices_after": ["Simpler"],
    }
    with mock.patch.object(server, "get_ableton_connection", return_value=fake_conn):
        tool_obj = server.load_sample_to_simpler
        fn = getattr(tool_obj, "fn", None) or getattr(tool_obj, "_fn", None) or tool_obj
        message = fn(ctx=None, track_index=1, uri="query:Samples#FileId_42", device_index=0)
        assert "Kick.wav" in message
        assert "Simpler" in message
        # send_command should receive 0-based indices
        fake_conn.send_command.assert_called_once_with(
            "load_sample_to_simpler",
            {"track_index": 0, "item_uri": "query:Samples#FileId_42", "device_index": None},
        )
