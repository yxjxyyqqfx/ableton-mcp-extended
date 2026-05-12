## verify_drum_pad_loaded

**Status**: PR-able
**Source**: `/legacy/MCP_Server/server.py:782-806`; `/legacy/AbletonMCP_Remote_Script/__init__.py:1731-1829`
**LOC delta**: ~120 (wrapper + verifier)
**Live compat**: Live 11 + 12

### Rationale (Russian)
Проверка загрузки pad нужна для надёжного пост-условия после browser.load_item, особенно когда возможны расхождения по pad note. Функция даёт структурированную диагностику (`no_chain`, `wrong_filename`, `off_by_one`) вместо «тихих» сбоев. Это полезно не только для форка, но и для любого автоматизированного Drum Rack pipeline.

### API Contract
```python
def verify_drum_pad_loaded(
    ctx: Context,
    track_index: int,
    rack_device_index: int,
    pad_note: int,
    expected_filename: str = "",
) -> str:

def _verify_drum_pad_loaded(self, track_index, rack_device_index, pad_note, expected_filename=""):
```

### Examples
1. `verify_drum_pad_loaded(ctx, track_index=1, rack_device_index=1, pad_note=36)`
2. `verify_drum_pad_loaded(ctx, track_index=1, rack_device_index=1, pad_note=36, expected_filename="Kick_01.wav")`

### Tests
- `tests/unit/test_drum_rack_verify.py::test_verify_reports_no_chain_when_pad_empty`
- `tests/unit/test_drum_rack_verify.py::test_verify_reports_off_by_one_when_expected_filename_found_on_other_pad`
- `tests/integration/test_drum_rack_flow.py::test_verify_after_load_returns_loaded_true`

### English Description
Adds a dedicated verification API for Drum Rack pad loads with explicit mismatch reasons and filename matching support. This makes load outcomes machine-checkable and gives orchestration layers a reliable signal for retries, diagnostics, and user-facing error messages.
