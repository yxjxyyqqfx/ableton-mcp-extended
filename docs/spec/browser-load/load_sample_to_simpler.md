## load_sample_to_simpler

**Status**: PR-able
**Source**: `/legacy/MCP_Server/server.py:656-681`; `/legacy/AbletonMCP_Remote_Script/__init__.py:1496-1538`
**LOC delta**: ~69
**Live compat**: Live 11 + 12 (нет version-gate в самом load-path; версия Live пробрасывается через `application().get_major_version()` в `/legacy/AbletonMCP_Remote_Script/__init__.py:1996-2001`)

### Rationale (Russian)
Эта пара wrapper+handler покрывает базовый и безопасный сценарий загрузки сэмпла по URI в Simpler или напрямую на MIDI-трек. Реализация опирается на выбор целевого трека/девайса и `browser.load_item`, что соответствует ограничениям Live API (read-only для прямой записи в `Simpler.sample`). Фича изолирована и не привязана к fork-специфичным путям.

### API Contract
```python
def load_sample_to_simpler(ctx: Context, track_index: int, uri: str, device_index: int = 0) -> str:

def _load_sample_to_simpler(self, track_index, item_uri, device_index=None):
```

### Examples
1. `load_sample_to_simpler(track_index=1, uri="query:Samples#FileId_123", device_index=1)` загружает sample в выбранный Simpler на треке 1.
2. `load_sample_to_simpler(track_index=2, uri="query:Samples#FileId_456", device_index=0)` загружает sample на MIDI-трек 2 без явного выбора девайса.

### Tests
- `tests/unit/test_browser.py::test_load_sample_to_simpler_contract` (planned)
- `tests/integration/test_browser_live.py::test_load_sample_to_simpler_live` (planned)

### English Description
Loads a browser sample by URI into either a selected Simpler device or the target MIDI track. The server wrapper normalizes 1-based indices and forwards to a handler that resolves the BrowserItem and performs the actual `browser.load_item` operation.
