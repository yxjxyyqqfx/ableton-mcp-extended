## _next_worker_seq

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1176-1180`
**LOC delta**: ~5
**Live compat**: Live 11 + 12

### Rationale (Russian)
Метод выдаёт монотонный worker_id для связывания lock-событий с конкретной операцией загрузки. Это нужно для читаемой диагностики конкурентных сценариев и корректной корреляции событий. Логика общая и безопасная для апстрима.

### API Contract
```python
def _next_worker_seq(self):
```

### Examples
1. `worker_id = self._next_worker_seq()`
2. `self._record_lock_event(key, "acquire_request", self._next_worker_seq())`

### Tests
- `tests/unit/test_load_lock_events.py::test_next_worker_seq_increments_monotonically`
- `tests/unit/test_load_lock_events.py::test_next_worker_seq_is_thread_safe_under_parallel_calls`
- `tests/integration/test_concurrent_loads.py::test_each_load_emits_unique_worker_id`

### English Description
Adds a thread-safe monotonic sequence allocator for load workers. The generated IDs are used to correlate lock events and make concurrent execution traces unambiguous.
