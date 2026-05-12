## _drain_lock_events

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1192-1199`
**LOC delta**: ~8
**Live compat**: Live 11 + 12

### Rationale (Russian)
Helper выбирает события только для текущего worker_id, чтобы не смешивать параллельные последовательности. Это делает отчёты о загрузке пригодными для автоматического анализа. Такая селекция событий полезна в любых сериализованных очередях.

### API Contract
```python
def _drain_lock_events(self, key, worker_id):
```

### Examples
1. `events = self._drain_lock_events((track_index, rack_device_index), worker_id)`
2. `result["lock_sequence"] = self._drain_lock_events(key, worker_id)`

### Tests
- `tests/unit/test_load_lock_events.py::test_drain_lock_events_returns_only_requested_worker_events`
- `tests/unit/test_load_lock_events.py::test_drain_lock_events_returns_empty_list_for_unknown_key`
- `tests/integration/test_concurrent_loads.py::test_result_includes_worker_scoped_lock_sequence`

### English Description
Adds worker-scoped lock event extraction so each load result can include only its own synchronization timeline. This prevents cross-talk between concurrent workers and keeps diagnostics actionable.
