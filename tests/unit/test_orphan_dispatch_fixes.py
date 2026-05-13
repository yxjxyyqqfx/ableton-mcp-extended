"""Regression guard for the three orphan-dispatch fixes.

Before this fix, AbletonMCP_Remote_Script._process_command had three elif
branches that called instance methods which were never defined on the
class:

  - command_type == "load_instrument_or_effect" -> self._load_instrument_or_effect(...)
  - command_type == "get_browser_categories"    -> self._get_browser_categories(...)
  - command_type == "get_browser_items"         -> self._get_browser_items(...)

Live's main-thread task wrapper silently swallowed the AttributeError on
all three so clients received `{"status": "success", "result": null}`
instead of an error.

Fix:
  - Route load_instrument_or_effect through the existing _load_browser_item
    method (same signature, identical semantics — load a browser item by
    URI onto a track).
  - Drop the get_browser_categories and get_browser_items dispatch cases
    so clients receive a clean `Unknown command` error instead of a
    silent null.
"""

import os
import pathlib
import re
import sys
import types


class _StubControlSurface:
    def __init__(self, c_instance):
        pass

    def log_message(self, msg):
        pass


_framework = types.ModuleType("_Framework")
_cs_module = types.ModuleType("_Framework.ControlSurface")
_cs_module.ControlSurface = _StubControlSurface
sys.modules.setdefault("_Framework", _framework)
sys.modules.setdefault("_Framework.ControlSurface", _cs_module)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from AbletonMCP_Remote_Script import AbletonMCP  # noqa: E402


_SOURCE = pathlib.Path(AbletonMCP.__module__.replace(".", "/")).with_suffix(".py")
_SOURCE_TEXT = (pathlib.Path(__file__).resolve().parents[2] / "AbletonMCP_Remote_Script" / "__init__.py").read_text(encoding="utf-8")


def test_load_instrument_or_effect_routes_to_load_browser_item():
    """The dispatch must call the existing _load_browser_item method, not
    the (non-existent) _load_instrument_or_effect.
    """
    pattern = re.compile(
        r'command_type == "load_instrument_or_effect".*?result = self\.(_[a-z_]+)\(',
        re.DOTALL,
    )
    match = pattern.search(_SOURCE_TEXT)
    assert match, "load_instrument_or_effect dispatch case not found"
    callee = match.group(1)
    assert callee == "_load_browser_item", (
        "load_instrument_or_effect should dispatch to _load_browser_item, "
        "got {0!r}".format(callee)
    )
    assert hasattr(AbletonMCP, "_load_browser_item"), (
        "_load_browser_item method must exist on AbletonMCP"
    )


def test_orphan_get_browser_dispatches_removed():
    """The get_browser_categories and get_browser_items dispatch cases
    must NOT be present — their handler methods were never defined.
    """
    assert 'command_type == "get_browser_categories"' not in _SOURCE_TEXT, (
        "get_browser_categories dispatch case must be removed"
    )
    assert 'command_type == "get_browser_items"' not in _SOURCE_TEXT, (
        "get_browser_items dispatch case must be removed"
    )


def test_load_browser_item_method_signature_matches_dispatch():
    """_load_browser_item takes (track_index, item_uri) — same shape as
    load_instrument_or_effect's params (track_index + uri), so the route
    is signature-compatible.
    """
    import inspect

    sig = inspect.signature(AbletonMCP._load_browser_item)
    params = [p for p in sig.parameters if p != "self"]
    assert len(params) == 2, (
        "_load_browser_item should take exactly (track_index, item_uri); "
        "got {0!r}".format(params)
    )
