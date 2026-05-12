## load_sample_to_drum_pad

**Status**: PR-able
**Source**: `/legacy/MCP_Server/server.py:685-719`; `/legacy/AbletonMCP_Remote_Script/__init__.py:1540-1640`
**LOC delta**: ~135 (wrapper + URI wrapper + locked loader)
**Live compat**: Live 11 + 12

### Rationale (Russian)
Эта фича реализует основной путь загрузки сэмпла на конкретный pad Drum Rack с предсказуемой валидацией и режимом replace. Она инкапсулирует сложность выбора падa, загрузки browser item и проверки результата в одном контракте. Такой путь нужен апстриму, потому что это базовая операция для MPC-like workflow в Live.

### API Contract
```python
def load_sample_to_drum_pad(
    ctx: Context,
    track_index: int,
    uri: str,
    pad_note: int = 36,
    rack_device_index: int = 1,
    replace: bool = False,
) -> str:

def _load_item_to_drum_pad_locked(self, track_index, rack_device_index, pad_note, item, replace=False):

def _load_sample_to_drum_pad(self, track_index, rack_device_index, pad_note, item_uri, replace=False):
```

### Examples
1. `load_sample_to_drum_pad(ctx, track_index=1, uri="query:Samples#FileId_123", pad_note=36)`
2. `load_sample_to_drum_pad(ctx, track_index=2, uri="query:Samples#FileId_456", pad_note=38, rack_device_index=1, replace=True)`

### Tests
- `tests/unit/test_drum_rack_load.py::test_load_sample_to_drum_pad_requires_replace_when_pad_non_empty`
- `tests/unit/test_drum_rack_load.py::test_load_sample_to_drum_pad_returns_actual_pad_and_lock_sequence`
- `tests/integration/test_drum_rack_flow.py::test_load_sample_to_drum_pad_happy_path`

### English Description
Introduces a first-class Drum Rack pad loading flow that resolves a browser URI and loads it into a selected pad with replace semantics. The implementation centralizes pad validation, selection, and structured load metadata so callers receive deterministic behavior and debuggable outcomes.
