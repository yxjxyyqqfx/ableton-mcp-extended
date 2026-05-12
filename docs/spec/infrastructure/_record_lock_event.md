## _record_lock_event

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1182-1190`
**LOC delta**: ~9
**Live compat**: Live 11 + 12

### Rationale (Russian)
Функция пишет временные метки жизненного цикла lock-операций, чтобы после выполнения можно было понять порядок конкурентных действий. Это особенно важно при редких race-condition, которые сложно воспроизводить локально. Helper нейтрален к домену и может использоваться любыми долгими операциями.

### API Contract
```python
def _record_lock_event(self, key, event, worker_id, **extra):
```

### Examples
1. `self._record_lock_event((0, 0), "acquire_request", worker_id, pad_note=36)`
2. `self._record_lock_event((0, 0), "release", worker_id)`

### Tests
- `tests/unit/test_load_lock_events.py::test_record_lock_event_appends_timestamped_event`
- `tests/unit/test_load_lock_events.py::test_record_lock_event_merges_extra_fields`
- `tests/integration/test_concurrent_loads.py::test_lock_event_trace_contains_acquire_and_release`

### English Description
Adds a structured lock-event recorder with timestamps and optional metadata for each worker. This provides lightweight observability into lock acquisition/release behavior during concurrent load operations.
