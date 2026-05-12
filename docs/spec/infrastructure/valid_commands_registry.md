## valid_commands_registry

**Status**: PR-able
**Source**: `/legacy/AbletonMCP_Remote_Script/__init__.py:9-60`, `/legacy/AbletonMCP_Remote_Script/__init__.py:113-186`
**PR Group**: F5

### Rationale
- Replace broad command-type conditionals with a bounded `VALID_COMMANDS` allowlist to reject unknown commands and make dispatch intent explicit.
- Keep `_process_command` routing centrally updated as new MCP handlers are added.

### API Contract
- Add/maintain `VALID_COMMANDS = frozenset({...})` including new command names from `load_*`, drum-rack, and probe handlers.
- In `_process_command`, route mutating commands through `elif command_type in VALID_COMMANDS:` instead of ad-hoc tuple membership.
- New command handlers are invoked from the same dispatch branch (e.g., `load_sample_to_simpler`, `load_sample_to_drum_pad`, `load_browser_sample_by_name`, `ensure_drum_rack_on_track`, `verify_drum_pad_loaded`, `wait_for_load_complete`, `resolve_filepath_to_browser_path`, and probe commands).

### Examples
- Add `"load_sample_to_drum_pad"` and related tool names to `VALID_COMMANDS`; unknown `type` payloads now reject deterministically before handler execution.
- Supported PR-able command example: `probe_environment` is currently excluded from PR scope (fork-only path) and should not be considered for upstream-ready allowlist.

### Tests
- `tests/unit/test_command_dispatch.py::test_valid_command_runs_when_in_allowlist`
- `tests/unit/test_command_dispatch.py::test_unknown_command_rejected_when_not_allowed`

### English Description
Introduce a centralized allowlist for server-side MCP command dispatch in `__init__.py`, replacing a brittle hardcoded branch and reducing accidental exposure of arbitrary command names. This spec is PR-able and aligned with F5 because it enables safe routing for newly introduced upstream commands.
