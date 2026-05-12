## _smoke_resample

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1671-1833`, `/workspace/docs/triage-raw/init.py.patch:179-183`

### Rationale
- Add an end-to-end resampling smoke test surface to validate export/recording path viability on the current host before broader automation.

### API Contract
- `_process_command` for `smoke_resample` reads:
  - `source_track_index = params.get("source_track_index", 0)`
  - `duration_seconds = params.get("duration_seconds", 4.0)`
  - calls `_smoke_resample(source_track_index, duration_seconds)`
- `_smoke_resample` returns metadata including:
  - track creation indices/names
  - routing mode (`master_resampling` or `specific_track`)
  - session clip slots and arrangement clips with `file_path`/`file_exists`/`file_size`
  - `has_clip`, `cleanup_ok`, and any `error/traceback`
- Always attempts cleanup (`song.delete_track(temp_index)`) in `finally`.

### Examples
- Payload: `{\"type\": \"smoke_resample\", \"params\": {\"source_track_index\": -1, \"duration_seconds\": 2.0}}`
- Success response includes `mode = master_resampling` and `has_clip = true`.

### Tests
- Add/update: `tests/unit/test_probes.py::test_smoke_resample_master_mode_signature`
- Add/update: `tests/unit/test_probes.py::test_smoke_resample_cleanup_on_success`

### English Description
- Fork-only controlled recording smoke command that creates a temporary audio track, attempts a timed resample capture, verifies clip output artifacts, and deletes temp state.
