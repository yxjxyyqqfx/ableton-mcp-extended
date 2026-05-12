"""Tests for safer browser-tree accessors (B5 bundle).

`_browser_children` normalizes the irregular shapes Live's browser exposes
(strings, lists, BrowserItem with `.children`, or numeric-indexable iterables).
`_search_browser_by_name` walks the standard browser roots.
"""

import sys
import types

import pytest


@pytest.fixture
def remote_script_module():
    """Stub _Framework and reload the remote script module.

    Same fixture pattern as test_load_orchestration: re-register the stub on
    every fixture call so module-level state from other tests can't poison us.
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


class _ItemWithChildrenList:
    def __init__(self, name, children=()):
        self.name = name
        self.children = list(children)
        self.is_loadable = False


class _LoadableItem:
    def __init__(self, name):
        self.name = name
        self.is_loadable = True
        self.children = []


def test_browser_children_returns_empty_for_none(script):
    """None input never raises and returns an empty list."""
    assert script._browser_children(None) == []


def test_browser_children_returns_empty_for_string_leaf(script):
    """String-like leaves cannot be enumerated and return []."""
    assert script._browser_children("some_path") == []
    assert script._browser_children(b"some_bytes") == []


def test_browser_children_returns_list_input_unchanged(script):
    """list/tuple inputs are passed through (they are already enumerated)."""
    payload = ["a", "b", "c"]
    assert script._browser_children(payload) is payload
    assert script._browser_children(("x", "y")) == ("x", "y")


def test_browser_children_reads_children_attribute_when_present(script):
    """Items exposing `.children` use that path directly."""
    child_a = _ItemWithChildrenList("a")
    child_b = _ItemWithChildrenList("b")
    parent = _ItemWithChildrenList("root", children=[child_a, child_b])
    result = script._browser_children(parent)
    assert result == [child_a, child_b]


def test_search_browser_by_name_finds_loadable_in_first_matching_root(script):
    """Returns the first loadable BrowserItem whose name matches case-insensitively."""
    needle = _LoadableItem("Kick_01.wav")
    samples_root = _ItemWithChildrenList("samples-root", children=[
        _ItemWithChildrenList("subdir", children=[needle]),
    ])

    class _Browser:
        pass

    browser = _Browser()
    browser.samples = samples_root  # type: ignore[attr-defined]

    found = script._search_browser_by_name(browser, "kick_01.wav", max_depth=4)
    assert found is needle


def test_search_browser_by_name_returns_none_when_absent(script):
    """Returns None when no roots / no matches."""
    empty_browser = type("B", (), {"samples": _ItemWithChildrenList("empty")})()
    assert script._search_browser_by_name(empty_browser, "missing.wav") is None
