"""Tests for the Drum Rack family wrappers + handlers (B8 bundle).

Covers the four new public tools (ensure_drum_rack_on_track,
load_sample_to_drum_pad, verify_drum_pad_loaded, wait_for_load_complete)
through the server.py @mcp.tool() surface, plus the new VALID_COMMANDS
allowlist entries and selected handler-side branches that do not require a
live Ableton process (find_drum_pad_by_note, verify branches).
"""

import importlib
import sys
import types
from unittest import mock


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


def _get_fn(tool):
    return getattr(tool, "fn", None) or getattr(tool, "_fn", None) or tool


def test_valid_commands_includes_drum_rack_family():
    """All four new commands must land in VALID_COMMANDS."""
    pkg = _make_remote_script()
    expected = {
        "load_sample_to_drum_pad",
        "ensure_drum_rack_on_track",
        "verify_drum_pad_loaded",
        "wait_for_load_complete",
    }
    missing = expected - pkg.VALID_COMMANDS
    assert not missing


def test_handler_methods_exist_on_class():
    """The four private handlers must be bound to AbletonMCP."""
    pkg = _make_remote_script()
    for name in (
        "_load_sample_to_drum_pad",
        "_load_item_to_drum_pad_locked",
        "_ensure_drum_rack_on_track",
        "_verify_drum_pad_loaded",
        "_wait_for_load_complete",
        "_find_drum_pad_by_note",
    ):
        assert hasattr(pkg.AbletonMCP, name), name


class _Pad:
    def __init__(self, note, chains=None):
        self.note = note
        self.chains = list(chains) if chains else []


class _Rack:
    def __init__(self, pads):
        self.drum_pads = pads


def test_find_drum_pad_by_note_returns_match():
    """The lookup returns the pad whose note attribute equals the query."""
    pkg = _make_remote_script()

    class _Stub:
        pass

    instance = _Stub()
    rack = _Rack([_Pad(36), _Pad(37), _Pad(38)])
    found = pkg.AbletonMCP._find_drum_pad_by_note(instance, rack, 37)
    assert found is rack.drum_pads[1]


def test_find_drum_pad_by_note_returns_none_when_absent():
    """Missing pad note yields None without raising."""
    pkg = _make_remote_script()

    class _Stub:
        pass

    rack = _Rack([_Pad(36), _Pad(37)])
    assert pkg.AbletonMCP._find_drum_pad_by_note(_Stub(), rack, 99) is None


def test_load_sample_to_drum_pad_tool_calls_handler_with_translated_indices():
    server = _reload_server()
    fake_conn = mock.MagicMock()
    fake_conn.send_command.return_value = {"item_name": "Kick.wav"}
    with mock.patch.object(server, "get_ableton_connection", return_value=fake_conn):
        fn = _get_fn(server.load_sample_to_drum_pad)
        message = fn(ctx=None, track_index=1, uri="u", pad_note=36, rack_device_index=2, replace=True)
        assert "Kick.wav" in message
        fake_conn.send_command.assert_called_once_with(
            "load_sample_to_drum_pad",
            {
                "track_index": 0,
                "item_uri": "u",
                "pad_note": 36,
                "rack_device_index": 1,
                "replace": True,
            },
        )


def test_ensure_drum_rack_on_track_tool_passes_minus1_for_default_track():
    server = _reload_server()
    fake_conn = mock.MagicMock()
    fake_conn.send_command.return_value = {"track_index": 5, "rack_device_index": 0}
    with mock.patch.object(server, "get_ableton_connection", return_value=fake_conn):
        fn = _get_fn(server.ensure_drum_rack_on_track)
        fn(ctx=None, track_index=0, name="Beat", create_if_missing=True)
        call = fake_conn.send_command.call_args
        assert call[0][0] == "ensure_drum_rack_on_track"
        assert call[0][1]["track_index"] == -1
        assert call[0][1]["name"] == "Beat"


def test_verify_drum_pad_loaded_tool_forwards_expected_filename():
    server = _reload_server()
    fake_conn = mock.MagicMock()
    fake_conn.send_command.return_value = {"loaded": True}
    with mock.patch.object(server, "get_ableton_connection", return_value=fake_conn):
        fn = _get_fn(server.verify_drum_pad_loaded)
        fn(ctx=None, track_index=2, rack_device_index=1, pad_note=37, expected_filename="kick.wav")
        call = fake_conn.send_command.call_args
        assert call[0][1] == {
            "track_index": 1,
            "rack_device_index": 0,
            "pad_note": 37,
            "expected_filename": "kick.wav",
        }


def test_wait_for_load_complete_tool_forwards_max_ticks():
    server = _reload_server()
    fake_conn = mock.MagicMock()
    fake_conn.send_command.return_value = {"loaded": False}
    with mock.patch.object(server, "get_ableton_connection", return_value=fake_conn):
        fn = _get_fn(server.wait_for_load_complete)
        fn(ctx=None, track_index=1, rack_device_index=1, pad_note=36, max_ticks=5)
        call = fake_conn.send_command.call_args
        assert call[0][1]["max_ticks"] == 5
        assert call[0][1]["track_index"] == 0
        assert call[0][1]["rack_device_index"] == 0
