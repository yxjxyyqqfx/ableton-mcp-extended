## _probe_export_capabilities

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1074-1274`, `/workspace/docs/triage-raw/init.py.patch:161-162`

### Rationale
- Record whether host environment and Ableton API support the export pipeline dependencies used only by fork diagnostics.
- Keep probe logic explicit and non-upstream-safe.

### API Contract
- In `_process_command`, when `command.type == "probe_export_capabilities"`, call `_probe_export_capabilities()` with no args.
- `_probe_export_capabilities()` returns a dict including:
  - `subprocess_importable`, `osascript_callable`, `osascript_callable`/`returncode/stdout/stderr`
  - `accessibility_granted`, `accessibility_probe_returncode/stdout/stderr`
  - `song_has_create_audio_track`, `track_has_audio_input`, `track0_available_input_routing_names`, `python_version`
  - per-module flags for `wave`, `hashlib`, `shutil`, `json`, `uuid`, `secrets`, `unicodedata`
- Read-only; all failures are encoded as `<key>_error` fields where possible.

### Examples
- Payload: `{\"type\": \"probe_export_capabilities\"}`
- Example success: `{"subprocess_importable": true, "accessibility_granted": false, "song_has_create_audio_track": true}`

### Tests
- Add/update: `tests/unit/test_probes.py::test_probe_export_capabilities_records_flags`
- Add/update: `tests/integration/test_probes.py::test_probe_export_capabilities_dispatch`

### English Description
- Fork-only diagnostic command that returns environment and API capability probes needed before trying export/recording experiments.
