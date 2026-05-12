## _probe_track_api_dir

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1835-1895`, `/workspace/docs/triage-raw/init.py.patch:166-168`

### Rationale
- Enumerate track API surface area to detect renamed/missing routing and freeze-related attrs across Live versions.

### API Contract
- `_process_command` path: `command.type == \"probe_track_api_dir\"` with optional `track_index` -> `_probe_track_api_dir(track_index=0)`.
- `_probe_track_api_dir` returns counts and attribute name arrays for:
  - selected track (`track_attrs`, `track_attrs_count`, `routing_related`, `freeze_related`)
  - master (`master_attrs_count`)
  - first return track (`return_track_attrs`, `return_track_freeze_related`)
  - first audio track (`audio_track_attrs`, `audio_track_routing_related`)
  - optional `clip_slot_attrs` / `clip_attrs`
  - routing enums introspection (`airt_type`, `airt_count`)
- Includes best-effort route/channel metadata and `error` fields if traversal fails.

### Examples
- Payload: `{\"type\": \"probe_track_api_dir\", \"params\": {\"track_index\": 1}}`
- Expected response includes `track_attrs_count` and a non-empty `routing_related` list for Live versions exposing routing methods.

### Tests
- Add/update: `tests/unit/test_probes.py::test_probe_track_api_dir_structure`
- Add/update: `tests/unit/test_probes.py::test_probe_track_api_dir_includes_filters`

### English Description
- Fork-only introspection spec for Live track/master/return/audio object attribute discovery used to harden compatibility logic against API drift.
