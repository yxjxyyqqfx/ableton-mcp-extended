## _probe_export_dialog_controls

**Status**: fork-only
**Source**: `/workspace/docs/triage-raw/init.py.patch:1275-1560`, `/workspace/docs/triage-raw/init.py.patch:163-165`

### Rationale
- Snapshot export-dialog UI affordances in a constrained, read-only way for troubleshooting without triggering exports.

### API Contract
- In `_process_command`, `command.type == "probe_export_dialog_controls"` dispatches to `_probe_export_dialog_controls(max_depth)` where `max_depth = params.get("max_depth", 5)`.
- `_probe_export_dialog_controls(max_depth=5)` sets `read_only=true`, records `max_depth`, and captures AppleScript results in fields such as:
  - `pre_escape`, `open_dialog`, `windows_after_shortcut`, `file_menu_items`, `window_tree`, `windows_after_close`
- Must only open Export Audio/Video (`Cmd+Shift+R`) and close dialog via Escape; must never invoke rendering.

### Examples
- Payload: `{\"type\": \"probe_export_dialog_controls\", \"params\": {\"max_depth\": 3}}`
- Returned payload includes `windows_after_shortcut.stdout` and `window_tree.lines_count` (or relevant error fields).

### Tests
- Add/update: `tests/unit/test_probes.py::test_probe_export_dialog_controls_default_depth`
- Add/update: `tests/unit/test_probes.py::test_probe_export_dialog_controls_respects_depth`

### English Description
- Fork-only UI probe for Live export control accessibility, intended to verify dialog controls and prevent regressions in export-automation diagnostics.
