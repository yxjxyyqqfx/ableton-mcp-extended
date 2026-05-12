## _get_load_lock

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1201-1206`
**LOC delta**: ~6
**Live compat**: Live 11 + 12

### Rationale (Russian)
Метод предоставляет lazy-инициализацию lock по ключу `(track_index, rack_device_index)`, чтобы синхронизация была адресной, а не глобальной. Это позволяет сохранять параллелизм между независимыми rack-ами и при этом защищать критическую секцию в одном rack. Примитив универсален и подходит для апстрим-конкурентных задач.

### API Contract
```python
def _get_load_lock(self, track_index, rack_device_index):
```

### Examples
1. `lock = self._get_load_lock(track_index=0, rack_device_index=1)`
2. `with_lock = self._get_load_lock(*key)`

### Tests
- `tests/unit/test_load_lock_state.py::test_get_load_lock_returns_same_instance_for_same_key`
- `tests/unit/test_load_lock_state.py::test_get_load_lock_creates_distinct_locks_for_distinct_keys`
- `tests/integration/test_concurrent_loads.py::test_same_rack_loads_are_serialized_by_shared_lock`

### English Description
Adds keyed lock retrieval with on-demand creation for per-rack synchronization. This enables fine-grained serialization without blocking unrelated load operations across different track/rack pairs.
