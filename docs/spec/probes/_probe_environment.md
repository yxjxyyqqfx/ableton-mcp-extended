## _probe_environment

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1029-1074`, `/workspace/docs/triage-raw/init.py.patch:159-160`

### Rationale
- Capture environment/readiness state without mutating Live state.
- Keep fork-only compatibility checks (`_probe_environment`) out of upstream spec while documenting exact payload contract.

### API Contract
- In `_process_command`, when `command.type == "probe_environment"`, dispatch to `_probe_environment()` with no args.
- `_probe_environment()` returns a dict containing:
  - `live_version`
  - `control_surface_has_schedule_message`
  - `application_has_schedule_message`
  - `application_dir_filtered`
  - `browser_attrs_sample`
- Read-only; may still include partial/empty values on attribute-access failures.

### Examples
- Payload: `{\"type\": \"probe_environment\"}`
- Expected result fragment: `{\"live_version\": \"11.2.4\", \"control_surface_has_schedule_message\": true, \"browser_attrs_sample\": [\"...\"]}`

### Tests
- Add/update: `tests/unit/test_probes.py::test_probe_environment_key_fields`
- Add/update: `tests/integration/test_probes.py::test_probe_environment_dispatch`

### English Description
- Probe command that reports API/version introspection signals before attempting any fork-only routing or audio-path mutations.
