## _load_locks_state

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:101-104`
**LOC delta**: ~4
**Live compat**: Live 11 + 12

### Rationale (Russian)
Инициализация shared state для блокировок и трассировки — фундамент для безопасной конкурентной загрузки. Без этого состояния параллельные загрузки в один rack могут давать race-condition и недетерминированные ошибки. Примитивы универсальны и применимы за пределами Drum Rack сценариев.

### API Contract
```python
self._load_locks = {}  # key: (track_index, rack_device_index) -> threading.Lock
self._lock_events = {}  # key: (track_index, rack_device_index) -> list of event dicts
self._worker_seq = 0
```

### Examples
1. `key = (track_index, rack_device_index); lock = self._load_locks.get(key)`
2. `self._lock_events.setdefault(key, []).append({"event": "acquire_request"})`

### Tests
- `tests/unit/test_load_lock_state.py::test_load_lock_state_is_initialized_in_constructor`
- `tests/unit/test_load_lock_state.py::test_worker_sequence_starts_at_zero`
- `tests/integration/test_concurrent_loads.py::test_shared_lock_state_serializes_same_rack_loads`

### English Description
Introduces shared in-memory state for per-rack locks, lock-event traces, and worker sequencing. These primitives provide the foundation for deterministic serialization and post-mortem visibility in concurrent load operations.
