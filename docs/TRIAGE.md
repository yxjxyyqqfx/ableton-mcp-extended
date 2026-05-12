# Fork Divergence Triage

**Plan**: `clean-fork-restructure` Phase 1 / T1.4
**Date**: 2026-05-10
**Sources**: `docs/triage-raw/server.py.classification.md`, `docs/triage-raw/init.py.classification.md`
**Diff base**: upstream `8abb8fd` → `/legacy` (committed + uncommitted)
**Files analyzed**: `MCP_Server/server.py` (232 LOC, 4 hunks → 10 rows) + `AbletonMCP_Remote_Script/__init__.py` (2189 LOC, 13 hunks → 25 rows)

## Executive summary

| Classification | server.py | init.py | Total |
|---|---|---|---|
| **PR-able** | 8 | 17 | **25** |
| **rework** | 2 | 4 | **6** |
| **fork-only** | 0 | 4 | **4** |
| **drop** | 0 | 0 | **0** |
| **Total** | 10 | 25 | **35** |

**Headline**: ~94% of fork divergence is upstream-worthy (PR-able + rework = 31/35). Only 4 probe/exploration helpers are session-specific and stay in the fork.

## Feature groupings

### F1 — Drum Rack pad family (PR-able)

End-to-end Drum Rack workflow: ensure rack exists, load sample to pad, verify load, wait for completion.

**Items** (server wrapper + handler pairs):
- `ensure_drum_rack_on_track` ↔ `_ensure_drum_rack_on_track` (PR-able)
- `load_sample_to_drum_pad` ↔ `_load_sample_to_drum_pad` / `_load_item_to_drum_pad_locked` (PR-able)
- `verify_drum_pad_loaded` ↔ `_verify_drum_pad_loaded` (PR-able)
- `wait_for_load_complete` ↔ `_wait_for_load_complete` (PR-able)
- `_find_drum_pad_by_note`, `_find_actual_pad_note`, `_devices_signature`, `_load_complete_predicate` (PR-able internals)

**LOC delta**: ~600. **Live compat**: Live 11 + 12. **Effort**: M (1.5-2 days for SPEC + clean re-implementation + tests).

### F2 — Browser / sample loading (mixed: PR-able + rework)

URI-based and name-based sample/instrument loading via Live's browser API.

**Items**:
- `load_sample_to_simpler` ↔ `_load_sample_to_simpler` (PR-able)
- `_load_browser_item_with_retry` state machine (PR-able)
- `_browser_children` safe accessor (PR-able)
- `_search_browser_by_name`, `_find_browser_item_by_uri` expansion (PR-able)
- `load_browser_sample_by_name` + `_find_browser_item_by_name_under_path` (**rework**: hardcoded `User_folders/_lib_` / `User_folders/Splice` valid_roots → lift to config)
- `resolve_filepath_to_browser_path` + `_resolve_filepath_to_browser_path` + `_FILEPATH_BROWSER_MAPPING` (**rework**: hardcoded `/ocp/mnt/...` mount prefixes → inject via env or config)
- Browser path traversal / user_folders special-case (**rework**: special-case cleanup)

**LOC delta**: ~700. **Live compat**: Live 11 + 12. **Effort**: L (3-4 days — rework items need design before PR).

### F3 — Connection configuration (PR-able, trivial)

Make Live connection host/port overridable via env vars.

**Items**:
- `import os` (PR-able)
- `AbletonConnection(host=ABLETON_HOST, port=ABLETON_PORT)` env-var lookup with `localhost` / `9877` defaults (PR-able)

**LOC delta**: +5. **Live compat**: any. **Effort**: XS (<1 hour incl. README update + test).

### F4 — Load orchestration & concurrency (PR-able)

Lock sequencing, event tracing, retry/timeout primitives that make browser loads race-free.

**Items**:
- `_load_locks`, `_lock_events`, `_worker_seq` shared state
- `_next_worker_seq`, `_record_lock_event`, `_drain_lock_events`, `_get_load_lock`
- Long-load timeout whitelist

**LOC delta**: ~250. **Live compat**: any. **Effort**: M (1 day — needs concurrency test fixture).

### F5 — Command registry plumbing (PR-able)

Wire the new handlers into the `VALID_COMMANDS` allowlist and dispatch.

**Items**:
- `VALID_COMMANDS` allowlist additions (PR-able)
- New-wrapper dispatch in `_do_command` (PR-able)

**LOC delta**: ~70. **Effort**: XS — bundled with the features it enables.

### F6 — Fork-only probes (NOT submitted upstream)

Diagnostic / environment exploration helpers used during local debugging. Kept in `our-extensions` branch but never PR'd.

**Items** (all `fork-only`):
- `_probe_environment` — Live/app capabilities probe
- `_probe_export_capabilities` — macOS/AppleScript export pipeline probe
- `_probe_export_dialog_controls` — Accessibility/UI scrape of Export Audio dialog
- `_probe_routing_full`, `_probe_routing_current_value`, `_probe_routing_setter`, `_restore_routing_by_display_name`, `_smoke_resample`, `_probe_track_api_dir` — routing/API exploration

**LOC delta**: ~880. **Live compat**: Live 12 + macOS only. **Effort**: 0 (already exists in /legacy, copy verbatim into fork branch).

### F7 — Cosmetic (PR-able)

- EOF newline in `MCP_Server/server.py` (PR-able)

**Effort**: trivial (auto-applied at commit time).

## Recommended Phase 3 commit order

Designed so each commit is atomic, leaves repo green (`pytest tests/unit/`), and respects dependencies:

| # | Commit | Group | Deps |
|---|---|---|---|
| 1 | `chore: trailing newline at EOF in server.py` | F7 | — |
| 2 | `feat(config): support ABLETON_HOST / ABLETON_PORT env vars` | F3 | — |
| 3 | `feat(remote): expand VALID_COMMANDS allowlist for new tools` | F5 | — |
| 4 | `feat(remote): browser-load concurrency primitives (locks, seq, events)` | F4 | 3 |
| 5 | `feat(remote): safer browser-tree accessors (_browser_children, _search_browser_by_name)` | F2 partial | 4 |
| 6 | `feat(remote): _load_browser_item_with_retry state machine` | F2 partial | 4, 5 |
| 7 | `feat: load_sample_to_simpler tool + handler` | F2 partial | 6 |
| 8 | `feat: Drum Rack pad load family (ensure / load / verify / wait)` | F1 | 6 |
| 9 | `feat: _find_browser_item_by_uri expansion (broader roots)` | F2 partial | 5 |
| 10 | `refactor: lift load_browser_sample_by_name valid_roots to config` | F2 rework | 9 |
| 11 | `refactor: parameterize FILEPATH_BROWSER_MAPPING + resolve_filepath_to_browser_path` | F2 rework | 9 |
| 12 | `refactor: clean up user_folders browser path traversal` | F2 rework | 9 |
| 13 | `(fork-only) bring in probe_* helpers and routing diagnostics` | F6 | — (separate, never pushed to origin/upstream) |

**PR submission order** (Phase 5): one PR per logical bundle:
- PR-A: commits 1 + 2 (cosmetic + config) — XS
- PR-B: commits 3 + 4 + 5 + 6 (foundation: dispatch + concurrency + browser accessors) — M
- PR-C: commit 7 (Simpler loader) — S
- PR-D: commit 8 (Drum Rack family) — M
- PR-E: commit 9 + 10 + 11 + 12 (browser search + rework cleanup) — M
- (no PR for F6 — fork-only)

## Effort summary

- **PR-able prep (Phase 3 commits 1-9)**: ~5-7 days
- **Rework (Phase 3 commits 10-12)**: ~3 days (design + refactor)
- **Fork-only port (commit 13)**: ~0.5 day (mechanical copy)
- **Phase 4 (v1 MIDI plan execution)**: tracked separately
- **Phase 5 PR submission**: ~1 day (5 PRs × 1-2h prep each)

**Total**: ~10-12 days of focused work for the full restructure.

## Phase 2 input

Feature families that need SPEC documents (Phase 2 / T2.1-T2.6):

- T2.1 — F1 Drum Rack pad family (`load_sample_to_drum_pad`, `ensure_drum_rack_on_track`, `verify_drum_pad_loaded`, `wait_for_load_complete`)
- T2.2 — Cue point management (NOT in current diff scope — predicted from plan, may be deferred)
- T2.3 — Arrangement clip family (NOT in current diff scope — predicted, deferred)
- T2.4 — Device parameter family (NOT in current diff scope — predicted, deferred)
- T2.5 — F2 Browser / sample loading (`load_sample_to_simpler`, `load_browser_sample_by_name`, `resolve_filepath_to_browser_path`)
- T2.6 — F6 Bounce/probe utilities (fork-only — minimal SPEC just to document quarantine boundary)

Plus implicit specs covered by commit bundles in PR-A/PR-B/PR-C/PR-D/PR-E above.

**T2.8 user-prioritization gate**: after T2.1-T2.7 SPECs land, present to user to confirm Phase 3 commit order (default = the table above) and freeze the build queue.

## References

- Plan: [.sisyphus/plans/ableton-mcp-clean-fork-restructure.md](../.sisyphus/plans/ableton-mcp-clean-fork-restructure.md)
- Per-file classifications: [server.py.classification.md](triage-raw/server.py.classification.md), [init.py.classification.md](triage-raw/init.py.classification.md)
- Raw patches: [server.py.patch](triage-raw/server.py.patch), [init.py.patch](triage-raw/init.py.patch)
- Upstream CI inventory: [UPSTREAM-CI.md](UPSTREAM-CI.md)
- Evidence dir: [.sisyphus/evidence/clean-fork-restructure/phase-1/](../.sisyphus/evidence/clean-fork-restructure/phase-1/)
