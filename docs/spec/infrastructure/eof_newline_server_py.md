## eof_newline_server_py

**Status**: PR-able
**Source**: `/workspace/docs/triage-raw/server.py.patch`
**PR Group**: F7

### Rationale
- Fix cosmetic diff noise from missing end-of-file newline in `server.py`.
- Ensure POSIX-style newline-at-EOF compliance for stable formatting checks and patch hygiene.
- Keep behavior identical while normalizing file termination only.

### API Contract
- Target file: `/workspace/MCP_Server/server.py`.
- Ensure final line `main()` is followed by an EOF newline character.
- Preserve all function bodies, command handlers, and socket logic unchanged.
- Remove the patch-level state of `\ No newline at end of file`.

### Examples
- Before: `git diff --check /workspace/MCP_Server/server.py` reports missing EOF newline.
- After: `git diff --check /workspace/MCP_Server/server.py` shows no newline warning for `main()`.
- Manual binary check: file bytes end with `\n` at the final byte.

### Tests
- `python -m py_compile /workspace/MCP_Server/server.py`
- `python - <<'PY'\nfrom pathlib import Path\nassert Path('/workspace/MCP_Server/server.py').read_bytes().endswith(b'\\n')\nprint('ok')\nPY`
- `git diff --check /workspace/docs/spec/infrastructure/eof_newline_server_py.md` (no whitespace errors for the new spec content).

### English Description
- This PR-able infra spec records the end-of-file newline normalization in `MCP_Server/server.py` introduced with host/port/env changes.
- It is purely a formatting-safe cleanup that prevents noisy diffs and keeps tooling happy without affecting runtime functionality.
