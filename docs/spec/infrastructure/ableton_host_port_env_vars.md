## ableton_host_port_env_vars

**Status**: PR-able
**Source**: `/legacy/MCP_Server/server.py:340-345`; `/workspace/docs/triage-raw/server.py.patch` hunk @@-323,17
**PR Group**: F3

### Rationale
Make Live host/port configuration explicit and overridable at runtime without code edits by reading `ABLETON_HOST` and `ABLETON_PORT` env vars before creating `AbletonConnection`.

### API Contract
When building the connection, resolve:
- `host = os.getenv("ABLETON_HOST", "localhost")`
- `port = int(os.getenv("ABLETON_PORT", "9877"))`

In `get_ableton_connection()`, replace hard-coded `AbletonConnection(host="localhost", port=9877)` with env-backed values.

### Examples
- `ABLETON_HOST=10.0.0.5 ABLETON_PORT=9877` to target remote host/port.
- Default remains unchanged when env vars are missing.

### Tests
- `tests/unit/test_server_connection.py::test_host_port_defaults_to_localhost_9877`
- `tests/unit/test_server_connection.py::test_host_port_override_from_env`

### English Description
This change makes the MCP server connection configurable through environment variables so CI, remote hosts, or alternate Ableton instances can be selected without changing source code. F3 is PR-ready and does not add fork-specific behavior.
