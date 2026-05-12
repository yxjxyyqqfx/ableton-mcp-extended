# server.py — Per-Hunk Classification (T1.2)

Source patch: `docs/triage-raw/server.py.patch` (232 LOC, 4 hunks).
Diff base: upstream `8abb8fd` (Merge PR #14, "Standardize 1-based indexing").
Target: `/legacy/MCP_Server/server.py` (committed + uncommitted).

## Classification table

| Hunk lines (patch) | Hunk header | Function/Section | Classification | Notes |
|---|---|---|---|---|
| L5-L12 | `@@ -3,6 +3,7 @@` | Add `import os` to top-level imports | PR-able | Trivial; required by hunk 2 env-var lookup. Zero risk. |
| L13-L24 | `@@ -323,7 +324,10 @@` | `AbletonConnection(host=..., port=...)` now reads `ABLETON_HOST` / `ABLETON_PORT` env vars with localhost/9877 defaults | PR-able | Universal value: backward-compatible defaults, makes containerized / remote-Live setups possible. No breaking change. |
| L25-L222 | `@@ -647,6 +651,200 @@` | 7 new `@mcp.tool()` functions: `load_sample_to_simpler`, `load_sample_to_drum_pad`, `load_browser_sample_by_name`, `ensure_drum_rack_on_track`, `verify_drum_pad_loaded`, `wait_for_load_complete`, `resolve_filepath_to_browser_path` | mixed (see rows below) | Sub-classified per tool below; each tool is a thin wrapper that forwards args to `__init__.py` handler via `ableton.send_command(...)`. |
| L226-L232 | `@@ -1850,4 +2048,4 @@` | Add trailing newline at EOF (`-    main()` → `+    main()\n`) | PR-able | Cosmetic — fixes "no newline at end of file" warning. POSIX-compliant. |

## Hunk 3 sub-classification (7 new tools)

| Sub-hunk lines | Tool name | Classification | Notes |
|---|---|---|---|
| L29-L56 | `load_sample_to_simpler(track_index, uri, device_index=0)` | PR-able | Generic sample-into-Simpler loader using browser URI. Project-agnostic; mirrors existing `load_instrument_or_effect` pattern. **see also**: `load_sample_to_simpler` handler in `__init__.py`. |
| L58-L94 | `load_sample_to_drum_pad(track_index, uri, pad_note=36, rack_device_index=1, replace=False)` | PR-able | Generic Drum Rack pad loader using browser URI. Idempotent via `replace` flag. **see also**: `load_sample_to_drum_pad` handler in `__init__.py`. |
| L96-L128 | `load_browser_sample_by_name(track_index, filename, search_root, pad_note=36, rack_device_index=1, replace=False)` | rework | Generic concept but `valid_roots = {"User_folders/_lib_", "User_folders/Splice"}` hardcodes project-specific browser root names. **Rework**: lift `valid_roots` to module-level constant or accept callable validator; or accept any browser path with a path-traversal guard. **see also**: `load_browser_sample_by_name` handler in `__init__.py`. |
| L131-L157 | `ensure_drum_rack_on_track(track_index=0, name="", create_if_missing=True)` | PR-able | Idempotent ensure-or-create primitive. Universal Drum Rack lifecycle utility. **see also**: `ensure_drum_rack_on_track` handler in `__init__.py`. |
| L159-L181 | `verify_drum_pad_loaded(track_index, rack_device_index, pad_note, expected_filename="")` | PR-able | Generic post-load verification helper. Returns `mismatch_reason` enum `{None, no_chain, wrong_filename, off_by_one}`. **see also**: `verify_drum_pad_loaded` handler in `__init__.py`. |
| L184-L206 | `wait_for_load_complete(track_index, rack_device_index, pad_note, max_ticks=20)` | PR-able | Polling wait primitive — useful for any async Live operation. **see also**: `wait_for_load_complete` handler in `__init__.py`. |
| L209-L220 | `resolve_filepath_to_browser_path(filepath)` | rework | Concept is universal (host filesystem → browser URI mapping) but the underlying handler in `__init__.py` likely hardcodes Mac vs container path remapping for `/ocp/mnt/_lib_`. **Rework**: split into pure path-mapping function + injectable path-remap config; the wrapper itself is fine, the handler needs the rework. **see also**: `resolve_filepath_to_browser_path` handler in `__init__.py`. |

## Summary

- **PR-able**: 8 hunks/sub-hunks (`import os`, env-var config, EOF newline, `load_sample_to_simpler`, `load_sample_to_drum_pad`, `ensure_drum_rack_on_track`, `verify_drum_pad_loaded`, `wait_for_load_complete`)
- **rework**: 2 sub-hunks (`load_browser_sample_by_name` valid_roots, `resolve_filepath_to_browser_path` host-mapping)
- **fork-only**: 0
- **drop**: 0
- **Total classified**: 10 (4 top-level hunks; hunk 3 sub-divided into 7 tools = 4 - 1 + 7 = 10 rows)

## Notes for Phase 2

1. The 2 `rework` items become PR-able after refactor: lift hardcoded constants to module-level + injectable config.
2. All 7 new tools are 1:1 wrappers — depend on matching handlers in `__init__.py` (covered by T1.3 cross-references).
3. Env-var config (hunk 2) should ship together with documentation update (README / config section).
4. No `fork-only` or `drop` content found in `server.py` — entire file is upstream-ready or rework-ready.
