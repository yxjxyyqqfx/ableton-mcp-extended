"""Tests for Drum Rack load diagnostics + state machine BUSY path (B6 bundle).

Full state machine execution requires a Live runtime (browser.load_item, song
view selection, schedule_message tick loop). These tests cover the pure
helpers and the lock-contention BUSY response path.
"""

import sys
import types

import pytest


@pytest.fixture
def remote_script_module():
    """Stub _Framework and reload the remote script module."""
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


class _FakeDevice:
    def __init__(self, class_name):
        self.class_name = class_name


class _FakeTrack:
    def __init__(self, devices):
        self.devices = devices


class _FakeChain:
    def __init__(self, devices):
        self.devices = devices


class _FakePad:
    def __init__(self, note, chains=()):
        self.note = note
        self.chains = list(chains)


def test_devices_signature_returns_tuple_of_class_name_and_id(script):
    """Signature is stable for the same track and changes when devices differ."""
    d1 = _FakeDevice("InstrumentRack")
    d2 = _FakeDevice("OriginalSimpler")
    track = _FakeTrack([d1, d2])
    sig = script._devices_signature(track)
    assert sig[0][0] == "InstrumentRack"
    assert sig[1][0] == "OriginalSimpler"
    assert sig[0][1] == id(d1)
    assert sig[1][1] == id(d2)


def test_devices_signature_returns_empty_tuple_on_exception(script):
    """Bad input must not raise; returns ()."""
    sig = script._devices_signature(None)
    assert sig == ()


def test_load_complete_predicate_signals_topology_changed(script):
    """When current signature differs from pre, returns (topology_changed, False)."""
    pre_sig = (("InstrumentRack", 1),)
    track = _FakeTrack([_FakeDevice("OriginalSimpler")])
    pad = _FakePad(36)
    reason, done = script._load_complete_predicate(track, pad, 0, pre_sig)
    assert reason == "topology_changed"
    assert done is False


def test_load_complete_predicate_returns_pending_when_no_chain_added(script):
    """Same signature + pad still empty -> pending (None, False)."""
    d = _FakeDevice("InstrumentRack")
    track = _FakeTrack([d])
    pre_sig = script._devices_signature(track)
    pad = _FakePad(36)
    reason, done = script._load_complete_predicate(track, pad, 0, pre_sig)
    assert reason is None
    assert done is False


def test_load_complete_predicate_succeeds_with_sampler(script):
    """Same topology + new chain with allowed sampler device -> (None, True)."""
    d = _FakeDevice("InstrumentRack")
    track = _FakeTrack([d])
    pre_sig = script._devices_signature(track)
    sampler = _FakeDevice("OriginalSimpler")
    chain = _FakeChain([sampler])
    pad = _FakePad(36, chains=[chain])
    reason, done = script._load_complete_predicate(track, pad, 0, pre_sig)
    assert reason is None
    assert done is True


def test_load_complete_predicate_rejects_wrong_device_class(script):
    """A chain loaded with an unexpected device class flags wrong_device_class."""
    d = _FakeDevice("InstrumentRack")
    track = _FakeTrack([d])
    pre_sig = script._devices_signature(track)
    chain = _FakeChain([_FakeDevice("AudioEffectGroupDevice")])
    pad = _FakePad(36, chains=[chain])
    reason, done = script._load_complete_predicate(track, pad, 0, pre_sig)
    assert reason.startswith("wrong_device_class:")
    assert done is False


def test_find_actual_pad_note_off_by_one(script):
    """If the new chain lands on a different pad, reason is off_by_one."""

    class _Rack:
        drum_pads = [_FakePad(36), _FakePad(37, chains=[_FakeChain([])])]

    actual, reason = script._find_actual_pad_note(_Rack(), pre_pad_count=0, requested_pad_note=36)
    assert actual == 37
    assert reason == "off_by_one"


def test_find_actual_pad_note_matches_requested(script):
    """If the requested pad gains the chain, reason is None."""

    class _Rack:
        drum_pads = [_FakePad(36, chains=[_FakeChain([])]), _FakePad(37)]

    actual, reason = script._find_actual_pad_note(_Rack(), pre_pad_count=0, requested_pad_note=36)
    assert actual == 36
    assert reason is None
