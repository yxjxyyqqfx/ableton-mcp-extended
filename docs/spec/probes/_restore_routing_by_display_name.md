## _restore_routing_by_display_name

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1649-1669`, `/workspace/docs/triage-raw/init.py.patch:175-178`

### Rationale
- Provide deterministic restoration path by display name for route types that differ between Live versions and environments.

### API Contract
- `_process_command` for `restore_routing_by_display_name` reads:
  - `track_index = params.get("track_index", 0)`
  - `target_display_name = params.get("target_display_name", "")`
  - calls `_restore_routing_by_display_name(track_index, target_display_name)`
- `_restore_routing_by_display_name(track_index, target_display_name)`:
  - finds matching `rt.display_name` in `t.available_input_routing_types`
  - sets `t.input_routing_type = match`, returns `{set_ok, after_display}`
  - returns `error` + `available_names` when not found.

### Examples
- Payload: `{\"type\": \"restore_routing_by_display_name\", \"params\": {\"track_index\": 1, \"target_display_name\": \"Resampling\"}}`
- Expected success: `{"set_ok": true, "after_display": "Resampling"}`.

### Tests
- Add/update: `tests/unit/test_probes.py::test_restore_routing_by_display_name_not_found`
- Add/update: `tests/unit/test_probes.py::test_restore_routing_by_display_name_happy_path`

### English Description
- Fork-only command to restore a track input routing route by UI display name, enabling robust fallback when exact enum objects differ across versions.
