## _probe_routing_current_value

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1631-1648`, `/workspace/docs/triage-raw/init.py.patch:172-173`

### Rationale
- Provide a tiny state readout of current routing selections for quick assertions during diagnostics.

### API Contract
- `_process_command` dispatch: `probe_routing_current_value` with optional `track_index` -> `_probe_routing_current_value(track_index=0)`.
- `_probe_routing_current_value(track_index=0)` returns display names for:
  - `input_routing_type_display`
  - `input_routing_channel_display`
  - `output_routing_type_display`
  - `output_routing_channel_display`
  - plus `track_name`
- Errors are reported via `error` string.

### Examples
- Payload: `{\"type\": \"probe_routing_current_value\", \"params\": {\"track_index\": 2}}`
- Expected response: `{\"track_index\": 2, \"input_routing_type_display\": \"Ext. In\"}`

### Tests
- Add/update: `tests/unit/test_probes.py::test_probe_routing_current_value_reads_fields`
- Add/update: `tests/integration/test_probes.py::test_probe_routing_current_value_dispatch`

### English Description
- Fork-only lightweight status probe for routing type/channel fields, useful for comparing pre/post routing setter outcomes.
