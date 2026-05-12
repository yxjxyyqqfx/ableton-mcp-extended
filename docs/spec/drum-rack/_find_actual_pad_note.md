## _find_actual_pad_note

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1246-1267`
**LOC delta**: ~22
**Live compat**: Live 11 + 12

### Rationale (Russian)
Helper нужен для диагностики ситуации, когда сэмпл оказался не на запрошенном pad (типичный off-by-one в практических сценариях). Он отделяет диагностику от бизнес-логики загрузки и не пытается «магически» исправлять состояние. Такой подход прозрачен для апстрим-поддержки и безопасен для автоматизации.

### API Contract
```python
def _find_actual_pad_note(self, rack, pre_pad_count, requested_pad_note):
```

### Examples
1. `actual_note, reason = self._find_actual_pad_note(rack, pre_pad_count=0, requested_pad_note=36)`
2. `actual_note, reason = self._find_actual_pad_note(rack, pre_pad_count=1, requested_pad_note=38)  # reason may be "off_by_one"`

### Tests
- `tests/unit/test_drum_rack_helpers.py::test_find_actual_pad_note_returns_requested_when_matching`
- `tests/unit/test_drum_rack_helpers.py::test_find_actual_pad_note_flags_off_by_one_on_mismatch`
- `tests/integration/test_drum_rack_flow.py::test_load_reports_actual_pad_note_when_shifted`

### English Description
Adds a diagnostic helper that identifies which pad actually changed after a load operation and reports off-by-one mismatches. This keeps discrepancy detection explicit and makes troubleshooting pad-targeting issues straightforward for calling tools.
