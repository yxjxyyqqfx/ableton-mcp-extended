## _load_browser_item_with_retry

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1268-1440`
**LOC delta**: ~170
**Live compat**: Live 11 + 12

### Rationale (Russian)
Это центральная state-machine для асинхронной загрузки browser item: она правильно разделяет worker-thread и main-thread фазы, а также обрабатывает timeout/topology errors. Функция превращает нестабильный sequence `load_item + polling` в воспроизводимый протокол с явной структурой результата. Такой orchestration-паттерн общий и достоин апстрим-переноса.

### API Contract
```python
def _load_browser_item_with_retry(self, spec, item, response_queue, max_ticks=20):
```

### Examples
1. `self._load_browser_item_with_retry(spec={"kind": "drum_pad", "track_index": 0, "rack_device_index": 0, "pad_note": 36, "replace": False}, item=item, response_queue=q, max_ticks=20)`
2. `self._load_browser_item_with_retry(spec={"kind": "drum_pad", "track_index": 1, "rack_device_index": 0, "pad_note": 38, "replace": True}, item=item, response_queue=q, max_ticks=60)`

### Tests
- `tests/unit/test_load_retry_state_machine.py::test_retry_loader_returns_timeout_error_after_max_ticks`
- `tests/unit/test_load_retry_state_machine.py::test_retry_loader_returns_topology_changed_when_signature_breaks`
- `tests/integration/test_concurrent_loads.py::test_retry_loader_completes_and_releases_lock_on_success`

### English Description
Introduces a lock-aware retry state machine for browser item loading that bridges worker-thread coordination with main-thread Ableton API calls. It standardizes success, timeout, and topology-change outcomes into a structured response contract, improving reliability under asynchronous load behavior.
