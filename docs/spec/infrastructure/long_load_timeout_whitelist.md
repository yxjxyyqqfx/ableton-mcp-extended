## long_load_timeout_whitelist

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:529-537`
**LOC delta**: ~9
**Live compat**: Live 11 + 12

### Rationale (Russian)
Whitelist длинных команд нужен, чтобы загрузочные операции не падали по общему короткому таймауту IPC-ответа. Для browser-driven load сценариев 10 секунд часто недостаточно даже при корректной работе Live. Явное разделение short/long timeout повышает надёжность и предсказуемость API.

### API Contract
```python
_LONG_LOAD_COMMANDS = (
    "load_sample_to_drum_pad",
    "load_sample_to_simpler",
    "load_browser_sample_by_name",
    "ensure_drum_rack_on_track",
    "wait_for_load_complete",
    "probe_export_dialog_controls",
)
_wait_timeout = 90.0 if command_type in _LONG_LOAD_COMMANDS else 10.0
```

### Examples
1. `command_type = "load_sample_to_drum_pad"  # uses 90.0s wait timeout`
2. `command_type = "set_track_volume"  # uses 10.0s wait timeout`

### Tests
- `tests/unit/test_command_timeout_policy.py::test_long_load_commands_use_extended_timeout`
- `tests/unit/test_command_timeout_policy.py::test_non_whitelisted_commands_use_default_timeout`
- `tests/integration/test_server_command_timeouts.py::test_drum_load_command_does_not_timeout_at_default_window`

### English Description
Adds an explicit long-load timeout whitelist so commands that legitimately require more time are not treated as failures by the default IPC timeout. This preserves responsiveness for normal commands while improving robustness for browser-driven load workflows.
