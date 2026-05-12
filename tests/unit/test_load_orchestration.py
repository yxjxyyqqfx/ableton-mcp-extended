"""Tests for browser-load concurrency primitives (B4 bundle).

Covers the worker-seq allocator, lock-event recorder/drainer, and per-(track,
rack) lock factory. Live runtime is stubbed so AbletonMCP can be instantiated
in-process.
"""

import sys
import threading
import types

import pytest


@pytest.fixture
def remote_script_module():
    """Provide AbletonMCP_Remote_Script with Live deps stubbed out.

    The stub installs `_Framework.ControlSurface.ControlSurface` with a constructor
    that accepts arbitrary args (Live's real signature) and minimal helper
    methods so AbletonMCP.__init__ can run without a real Live process. The
    module is force-reloaded so it picks up our stub even if a prior test
    imported a different stub.
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

    # Force reload so the module picks up our refreshed stub.
    sys.modules.pop("AbletonMCP_Remote_Script", None)
    import AbletonMCP_Remote_Script as pkg  # noqa: WPS433
    return pkg


@pytest.fixture
def script_instance(remote_script_module, monkeypatch):
    """Create an AbletonMCP instance with the socket server disabled."""
    monkeypatch.setattr(remote_script_module.AbletonMCP, "start_server", lambda self: None)
    return remote_script_module.AbletonMCP(c_instance=None)


def test_next_worker_seq_is_monotonic_and_threadsafe(script_instance):
    """Sequential calls return strictly increasing ids; concurrent calls do not collide."""
    first = script_instance._next_worker_seq()
    second = script_instance._next_worker_seq()
    assert second == first + 1

    results = []
    lock = threading.Lock()

    def worker():
        for _ in range(50):
            value = script_instance._next_worker_seq()
            with lock:
                results.append(value)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(results) == len(set(results)), "worker_seq must not collide under concurrency"


def test_get_load_lock_returns_same_lock_for_same_key(script_instance):
    """Repeated calls with same (track_index, rack_device_index) return the SAME Lock object."""
    lock_a = script_instance._get_load_lock(1, 0)
    lock_b = script_instance._get_load_lock(1, 0)
    assert lock_a is lock_b


def test_get_load_lock_distinct_per_key(script_instance):
    """Different (track, rack) pairs get distinct Lock objects."""
    lock_t1 = script_instance._get_load_lock(1, 0)
    lock_t2 = script_instance._get_load_lock(2, 0)
    lock_rack = script_instance._get_load_lock(1, 1)
    assert lock_t1 is not lock_t2
    assert lock_t1 is not lock_rack
    assert lock_t2 is not lock_rack


def test_record_and_drain_lock_events_isolates_workers(script_instance):
    """Events recorded for one worker_id are not returned to another."""
    key = (1, 0)
    worker_a = 1
    worker_b = 2

    script_instance._record_lock_event(key, "acquire_request", worker_a, pad_note=36)
    script_instance._record_lock_event(key, "acquire_granted", worker_a, pad_note=36)
    script_instance._record_lock_event(key, "acquire_request", worker_b, pad_note=38)

    events_a = script_instance._drain_lock_events(key, worker_a)
    events_b = script_instance._drain_lock_events(key, worker_b)

    assert [e["event"] for e in events_a] == ["acquire_request", "acquire_granted"]
    assert [e["event"] for e in events_b] == ["acquire_request"]
    assert all(e["worker_id"] == worker_a for e in events_a)
    assert all(e["worker_id"] == worker_b for e in events_b)


def test_record_lock_event_attaches_extra_fields(script_instance):
    """**extra kwargs are merged into the event dict."""
    key = (3, 0)
    script_instance._record_lock_event(key, "acquire_granted", worker_id=42, pad_note=40)
    events = script_instance._drain_lock_events(key, worker_id=42)
    assert events[0]["pad_note"] == 40
    assert events[0]["event"] == "acquire_granted"
    assert events[0]["worker_id"] == 42
    assert "ts" in events[0]
