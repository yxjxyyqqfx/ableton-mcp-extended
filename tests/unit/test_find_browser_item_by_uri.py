"""Tests for the expanded _find_browser_item_by_uri (B9 bundle).

Covers the new behavior added on top of the upstream baseline:
- list/tuple inputs are traversed recursively.
- The category set is widened beyond the original 6 (instruments, sounds,
  drums, audio_effects, midi_effects, plugins) to include samples,
  user_library, current_project, clips, packs, max_for_live, user_folders.
- Non-list children iterables use the safer _browser_children accessor.
"""

import sys
import types

import pytest


@pytest.fixture
def remote_script_module():
    """Stub _Framework and reload AbletonMCP_Remote_Script.

    Same isolating pattern as the other test files in this directory.
    """
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


@pytest.fixture
def script(remote_script_module, monkeypatch):
    monkeypatch.setattr(remote_script_module.AbletonMCP, "start_server", lambda self: None)
    return remote_script_module.AbletonMCP(c_instance=None)


class _Item:
    def __init__(self, uri, children=()):
        self.uri = uri
        self.children = list(children)


class _Browser:
    """Minimal stub of Live's Browser exposing one or more category roots."""

    def __init__(self, **categories):
        for name, value in categories.items():
            setattr(self, name, value)


def test_finds_item_in_instruments_category(script):
    """Baseline behavior: the original instruments category still resolves."""
    target = _Item("query:Live#FileId_kick")
    browser = _Browser(instruments=_Item("root", children=[target]))
    found = script._find_browser_item_by_uri(browser, "query:Live#FileId_kick")
    assert found is target


def test_finds_item_in_newly_added_samples_category(script):
    """B9 adds 'samples' to the recognized roots; verify it's now searched."""
    target = _Item("query:Samples#FileId_42")
    browser = _Browser(
        instruments=_Item("instr", children=[]),
        samples=_Item("samples-root", children=[target]),
    )
    found = script._find_browser_item_by_uri(browser, "query:Samples#FileId_42")
    assert found is target


def test_finds_item_in_user_folders_root(script):
    """user_folders is one of the newly added roots."""
    target = _Item("userfolder:abc")
    browser = _Browser(
        instruments=_Item("instr", children=[]),
        user_folders=_Item("uf-root", children=[target]),
    )
    found = script._find_browser_item_by_uri(browser, "userfolder:abc")
    assert found is target


def test_list_input_is_traversed(script):
    """Pass a list of browser items directly (not via a Browser facade)."""
    target = _Item("query:Live#42")
    found = script._find_browser_item_by_uri(
        [_Item("a"), _Item("b"), target],
        "query:Live#42",
    )
    assert found is target


def test_returns_none_when_uri_absent(script):
    """Unknown URI yields None without raising."""
    browser = _Browser(instruments=_Item("root", children=[_Item("u1"), _Item("u2")]))
    assert script._find_browser_item_by_uri(browser, "query:Missing") is None


def test_respects_max_depth(script):
    """At depth == max_depth recursion stops; deeper item is not found."""
    leaf = _Item("deep_uri")
    nested = _Item("l3", children=[leaf])
    root = _Item("root", children=[_Item("l1", children=[_Item("l2", children=[nested])])])
    browser = _Browser(instruments=root)
    assert script._find_browser_item_by_uri(browser, "deep_uri", max_depth=2) is None
