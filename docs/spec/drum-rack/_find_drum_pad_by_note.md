## _find_drum_pad_by_note

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1641-1649`
**LOC delta**: ~9
**Live compat**: Live 11 + 12

### Rationale (Russian)
Это маленький, но важный helper для единообразного поиска pad по MIDI note во всех путях верификации/загрузки. Он убирает дублирование циклов по `rack.drum_pads` и делает поведение более предсказуемым. Несмотря на internal-статус, функция поддерживает PR-able публичные сценарии.

### API Contract
```python
def _find_drum_pad_by_note(self, rack, pad_note):
```

### Examples
1. `pad = self._find_drum_pad_by_note(rack, 36)`
2. `pad = self._find_drum_pad_by_note(rack, 127)  # returns None if missing`

### Tests
- `tests/unit/test_drum_rack_helpers.py::test_find_drum_pad_by_note_returns_matching_pad`
- `tests/unit/test_drum_rack_helpers.py::test_find_drum_pad_by_note_returns_none_for_missing_note`
- `tests/integration/test_drum_rack_flow.py::test_verify_uses_pad_lookup_for_target_note`

### English Description
Adds a focused helper that resolves Drum Rack pads by MIDI note and safely returns `None` when unavailable. This keeps pad resolution logic centralized and reduces duplicated iteration code in higher-level load and verification paths.
