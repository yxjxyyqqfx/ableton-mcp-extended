## wait_for_load_complete

**Status**: PR-able
**Source**: `/legacy/MCP_Server/server.py:810-831`; `/legacy/AbletonMCP_Remote_Script/__init__.py:1831-1851`
**LOC delta**: ~35 (wrapper + polling helper)
**Live compat**: Live 11 + 12

### Rationale (Russian)
В Live загрузка через browser может завершаться не мгновенно, поэтому нужен отдельный polling helper с контролем числа тиков. Он снимает необходимость дублировать цикл ожидания на стороне клиентов. Функция универсальна и полезна для апстрим-интеграций, где важна детерминированная синхронизация.

### API Contract
```python
def wait_for_load_complete(
    ctx: Context,
    track_index: int,
    rack_device_index: int,
    pad_note: int,
    max_ticks: int = 20,
) -> str:

def _wait_for_load_complete(self, track_index, rack_device_index, pad_note, max_ticks=20):
```

### Examples
1. `wait_for_load_complete(ctx, track_index=1, rack_device_index=1, pad_note=36)`
2. `wait_for_load_complete(ctx, track_index=1, rack_device_index=1, pad_note=38, max_ticks=60)`

### Tests
- `tests/unit/test_drum_rack_wait.py::test_wait_returns_early_on_loaded_pad`
- `tests/unit/test_drum_rack_wait.py::test_wait_stops_after_max_ticks_and_returns_last_probe`
- `tests/integration/test_drum_rack_flow.py::test_wait_after_load_eventually_reports_loaded`

### English Description
Introduces a polling helper that waits for asynchronous Drum Rack pad loads to become observable. The function repeatedly probes pad state with bounded retries, returning structured verification output for both success and timeout paths.
