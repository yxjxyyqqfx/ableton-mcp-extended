## _load_complete_predicate

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1215-1245`
**LOC delta**: ~31
**Live compat**: Live 11 + 12

### Rationale (Russian)
Predicate нужен для формализации критерия «загрузка действительно завершена» в main-thread retry loop. Он объединяет три проверки: неизменность topology, появление chain и корректный sampler-класс устройства. Это уменьшает ложные успехи и делает результат загрузки воспроизводимым.

### API Contract
```python
def _load_complete_predicate(self, track, target_pad, pre_pad_count,
                                pre_devices_signature,
                                expected_classes=None):
```

### Examples
1. `reason, done = self._load_complete_predicate(track, target_pad, pre_pad_count, pre_sig)`
2. `reason, done = self._load_complete_predicate(track, target_pad, 0, pre_sig, expected_classes={"OriginalSimpler"})`

### Tests
- `tests/unit/test_drum_rack_predicate.py::test_predicate_waits_until_chain_contains_sampler_device`
- `tests/unit/test_drum_rack_predicate.py::test_predicate_returns_topology_changed_when_signature_differs`
- `tests/integration/test_drum_rack_flow.py::test_retry_loader_uses_completion_predicate_for_exit`

### English Description
Adds a completion predicate for Drum Rack loads that validates topology stability, chain materialization, and sampler device class. This encapsulates readiness logic in one place and improves correctness of retry-driven load orchestration.
