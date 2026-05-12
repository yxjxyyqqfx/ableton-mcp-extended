"""Tests for F6 fork-only probe handlers.

The probe handlers are diagnostic helpers that read Live state. Full execution
needs a Live runtime, so these tests verify:
- VALID_COMMANDS gating (each probe command name is registered).
- Each handler method exists on the class.

The probes are NOT exposed through MCP tool wrappers in server.py — they are
intentionally fork-only and only reachable through direct send_command from
debugging clients.
"""

import sys
import types


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


PROBE_COMMANDS = (
    "probe_environment",
    "probe_export_capabilities",
    "probe_export_dialog_controls",
    "probe_track_api_dir",
    "probe_routing_setter",
    "probe_routing_current_value",
    "restore_routing_by_display_name",
    "smoke_resample",
    "probe_routing_full",
)

PROBE_HANDLERS = (
    "_probe_environment",
    "_probe_export_capabilities",
    "_probe_export_dialog_controls",
    "_probe_track_api_dir",
    "_probe_routing_setter",
    "_probe_routing_current_value",
    "_restore_routing_by_display_name",
    "_smoke_resample",
    "_probe_routing_full",
)


def test_all_probe_commands_are_in_valid_commands():
    """Every fork-only probe must be in the allowlist so dispatch can reach it."""
    pkg = _make_remote_script()
    for cmd in PROBE_COMMANDS:
        assert cmd in pkg.VALID_COMMANDS, "missing in VALID_COMMANDS: {0}".format(cmd)


def test_all_probe_handlers_exist_on_class():
    """Every probe handler method is bound on AbletonMCP."""
    pkg = _make_remote_script()
    for handler in PROBE_HANDLERS:
        assert hasattr(pkg.AbletonMCP, handler), "missing handler: {0}".format(handler)
