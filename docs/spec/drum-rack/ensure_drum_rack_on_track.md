## ensure_drum_rack_on_track

**Status**: PR-able
**Source**: `/legacy/MCP_Server/server.py:757-778`; `/legacy/AbletonMCP_Remote_Script/__init__.py:1651-1729`
**LOC delta**: ~100 (wrapper + handler)
**Live compat**: Live 11 + 12

### Rationale (Russian)
Фича нужна как идемпотентная точка входа для сценариев загрузки сэмплов в Drum Rack: она либо находит существующий rack, либо корректно создаёт его. Это снижает количество ошибок в пользовательских командах и упрощает оркестрацию следующих шагов загрузки. Поведение универсальное и не зависит от локальных форк-хаκов.

### API Contract
```python
def ensure_drum_rack_on_track(
    ctx: Context,
    track_index: int = 0,
    name: str = "",
    create_if_missing: bool = True,
) -> str:

def _ensure_drum_rack_on_track(self, track_index=-1, name="", create_if_missing=True):
```

### Examples
1. `ensure_drum_rack_on_track(ctx, track_index=1, name="Drums", create_if_missing=True)`
2. `ensure_drum_rack_on_track(ctx, track_index=0, name="New Drum Bus", create_if_missing=True)`

### Tests
- `tests/unit/test_drum_rack_ensure.py::test_ensure_returns_existing_rack_without_creation`
- `tests/unit/test_drum_rack_ensure.py::test_ensure_creates_track_and_rack_when_track_index_zero`
- `tests/integration/test_drum_rack_flow.py::test_ensure_then_load_pad_end_to_end`

### English Description
Adds an idempotent Drum Rack ensure primitive that either reuses an existing rack on a target MIDI track or creates one when needed. This gives callers a stable precondition before any pad-level load operation and avoids fragile caller-side rack discovery logic.
