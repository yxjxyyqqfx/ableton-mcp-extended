## _devices_signature

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:1208-1213`
**LOC delta**: ~6
**Live compat**: Live 11 + 12

### Rationale (Russian)
Функция строит компактную сигнатуру topology трека до/после загрузки и используется как инвариант целостности. Это позволяет поймать нежелательную подмену устройства (например, Drum Rack → Simpler) в асинхронных сценариях. Helper общий и полезен для апстрима как guardrail.

### API Contract
```python
def _devices_signature(self, track):
```

### Examples
1. `pre_sig = self._devices_signature(track)`
2. `topology_changed = pre_sig != self._devices_signature(track)`

### Tests
- `tests/unit/test_drum_rack_helpers.py::test_devices_signature_is_stable_without_topology_changes`
- `tests/unit/test_drum_rack_helpers.py::test_devices_signature_changes_when_device_chain_changes`
- `tests/integration/test_drum_rack_flow.py::test_load_flow_records_pre_and_post_device_signatures`

### English Description
Introduces a lightweight track topology signature used to detect structural device changes during asynchronous loads. The helper provides a deterministic comparison primitive for completion checks and failure diagnostics.
