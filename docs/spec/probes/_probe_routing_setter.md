## _probe_routing_setter

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1890-1932`, `/workspace/docs/triage-raw/init.py.patch:169-171`

### Rationale
- Validate whether Live 12-style routing setter behavior is available by attempting a temporary set/restore cycle.

### API Contract
- `_process_command` path: `command.type == "probe_routing_setter"` -> `_probe_routing_setter(track_index=0)`.
- `_probe_routing_setter(track_index=0)`:
  - returns `skipped` when track has no audio input
  - scans `available_input_routing_types` for `display_name == 'resampling'`
  - if found, captures `live12_set_ok`, `live12_old_type_display`, `live12_after_set_display`, `live12_restored_display`
- Uses setter semantics under try/finally with per-path error keys.

### Examples
- Payload: `{\"type\": \"probe_routing_setter\", \"params\": {\"track_index\": 1}}`
- Expected success result may include: `{"resampling_rt_found": true, "live12_set_ok": true}`.

### Tests
- Add/update: `tests/unit/test_probes.py::test_probe_routing_setter_no_audio_track`
- Add/update: `tests/unit/test_probes.py::test_probe_routing_setter_resampling_probe`

### English Description
- Fork-only setter probe that checks routing API mutability without requiring an actual production routing configuration change.
