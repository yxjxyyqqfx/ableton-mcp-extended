## _probe_routing_full

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1562-1630`, `/workspace/docs/triage-raw/init.py.patch:185-183`

### Rationale
- Capture a full snapshot of routing enums and related categories to adapt to Live version/API differences.

### API Contract
- `_process_command` path: `command.type == "probe_routing_full"` -> `_probe_routing_full(track_index=0)` with `track_index = params.get("track_index", 0)`.
- `_probe_routing_full(track_index=0)` returns:
  - `track_name`, `airt_count`, `airt_full` entries (`display_name`, `category`, `attached_object_type`)
  - `categories`
  - `input_routings_count`, `input_routings_sample`
  - `input_sub_routings_count`, `input_sub_routings_sample`
  - `current_input_routing`, `current_input_sub_routing`
- Any exception is surfaced as `error` with stack in `traceback`.

### Examples
- Payload: `{\"type\": \"probe_routing_full\", \"params\": {\"track_index\": 0}}`
- On success, consumers can compare `airt_full` against previously captured Live versions.

### Tests
- Add/update: `tests/unit/test_probes.py::test_probe_routing_full_includes_categories`
- Add/update: `tests/integration/test_probes.py::test_probe_routing_full_dispatch`

### English Description
- Fork-only deep routing inspector used to map available input routing objects and categories across Live versions and host setups.
