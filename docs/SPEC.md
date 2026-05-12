# SPEC — Fork Feature Catalog

**Plan**: `clean-fork-restructure` Phase 2 / T2.7
**Date**: 2026-05-10
**Sources**: per-feature spec files under `docs/spec/<family>/*.md`
**Triage**: [docs/TRIAGE.md](TRIAGE.md)
**Branch target**: `our-extensions` (cut from `upstream/main @ 1116449`)

## Coverage matrix

| Family | Spec dir | Files | Status mix |
|---|---|---|---|
| F1 Drum Rack pad | `docs/spec/drum-rack/` | 8 | 8 PR-able |
| F2 Browser / sample loading | `docs/spec/browser-load/` | 9 | 5 PR-able + 4 rework |
| F3 + F4 + F5 + F7 Infrastructure | `docs/spec/infrastructure/` | 10 | 9 PR-able + 1 rework |
| F6 Probes (fork-only) | `docs/spec/probes/` | 9 | 9 fork-only |
| **Deferred families** (T2.2/T2.3/T2.4 — not in diff scope) | `docs/spec/deferred-families.md` | 1 | — |
| **Total** | | **36** spec files + 1 deferred doc | **22 PR-able + 9 fork-only + 5 rework** |

## Table of contents

### F1 — Drum Rack pad family (PR-able, 8 features)

- [ ] [`ensure_drum_rack_on_track`](spec/drum-rack/ensure_drum_rack_on_track.md) — idempotent Drum Rack create/load
- [ ] [`load_sample_to_drum_pad`](spec/drum-rack/load_sample_to_drum_pad.md) — URI → Drum Rack pad
- [ ] [`verify_drum_pad_loaded`](spec/drum-rack/verify_drum_pad_loaded.md) — post-load verification with mismatch enum
- [ ] [`wait_for_load_complete`](spec/drum-rack/wait_for_load_complete.md) — async pad-load polling
- [ ] [`_find_drum_pad_by_note`](spec/drum-rack/_find_drum_pad_by_note.md) — lookup helper
- [ ] [`_find_actual_pad_note`](spec/drum-rack/_find_actual_pad_note.md) — off-by-one diagnostics
- [ ] [`_devices_signature`](spec/drum-rack/_devices_signature.md) — device fingerprint helper
- [ ] [`_load_complete_predicate`](spec/drum-rack/_load_complete_predicate.md) — load-done predicate

### F2 — Browser / sample loading (mixed PR-able + rework, 9 features)

- [ ] [`load_sample_to_simpler`](spec/browser-load/load_sample_to_simpler.md) — URI → Simpler / track (PR-able)
- [ ] [`load_browser_sample_by_name`](spec/browser-load/load_browser_sample_by_name.md) — filename + root → pad (**rework**: lift hardcoded valid_roots)
- [ ] [`resolve_filepath_to_browser_path`](spec/browser-load/resolve_filepath_to_browser_path.md) — host fs → browser URI (**rework**: parameterize mount prefixes)
- [ ] [`_browser_children`](spec/browser-load/_browser_children.md) — safe tree accessor (PR-able)
- [ ] [`_search_browser_by_name`](spec/browser-load/_search_browser_by_name.md) — name search (PR-able)
- [ ] [`_find_browser_item_by_uri`](spec/browser-load/_find_browser_item_by_uri.md) — URI search expansion (PR-able)
- [ ] [`_find_browser_item_by_name_under_path`](spec/browser-load/_find_browser_item_by_name_under_path.md) — name-under-path (**rework**: generalize)
- [ ] [`_FILEPATH_BROWSER_MAPPING`](spec/browser-load/_FILEPATH_BROWSER_MAPPING.md) — mount→browser table (**rework**: configurable)
- [ ] [`user_folders_path_traversal`](spec/browser-load/user_folders_path_traversal.md) — user_folders special-case (**rework**: clean up)

### F3 + F4 + F5 + F7 — Infrastructure (PR-able, 10 features)

- [ ] [`ableton_host_port_env_vars`](spec/infrastructure/ableton_host_port_env_vars.md) — `ABLETON_HOST/PORT` config (F3, trivial)
- [ ] [`valid_commands_registry`](spec/infrastructure/valid_commands_registry.md) — `VALID_COMMANDS` + dispatch wiring (F5)
- [ ] [`eof_newline_server_py`](spec/infrastructure/eof_newline_server_py.md) — POSIX trailing newline (F7, cosmetic)
- [ ] [`_load_locks_state`](spec/infrastructure/_load_locks_state.md) — concurrency state init (F4)
- [ ] [`_next_worker_seq`](spec/infrastructure/_next_worker_seq.md) — worker sequence allocator (F4)
- [ ] [`_record_lock_event`](spec/infrastructure/_record_lock_event.md) — event trace recorder (F4)
- [ ] [`_drain_lock_events`](spec/infrastructure/_drain_lock_events.md) — event drainer (F4)
- [ ] [`_get_load_lock`](spec/infrastructure/_get_load_lock.md) — per-load lock factory (F4)
- [ ] [`_load_browser_item_with_retry`](spec/infrastructure/_load_browser_item_with_retry.md) — state machine for scheduled browser loading (F4, **rework**: dependency injection)
- [ ] [`long_load_timeout_whitelist`](spec/infrastructure/long_load_timeout_whitelist.md) — extended timeout per command (F4)

### F6 — Probes (fork-only, never upstream, 9 features)

- [ ] [`_probe_environment`](spec/probes/_probe_environment.md) — Live/app capabilities probe
- [ ] [`_probe_export_capabilities`](spec/probes/_probe_export_capabilities.md) — macOS export pipeline probe
- [ ] [`_probe_export_dialog_controls`](spec/probes/_probe_export_dialog_controls.md) — Export Audio dialog UI scrape
- [ ] [`_probe_routing_full`](spec/probes/_probe_routing_full.md) — full routing dump
- [ ] [`_probe_routing_current_value`](spec/probes/_probe_routing_current_value.md) — current routing reader
- [ ] [`_probe_routing_setter`](spec/probes/_probe_routing_setter.md) — routing setter test
- [ ] [`_restore_routing_by_display_name`](spec/probes/_restore_routing_by_display_name.md) — display-name restore
- [ ] [`_smoke_resample`](spec/probes/_smoke_resample.md) — resample smoke test
- [ ] [`_probe_track_api_dir`](spec/probes/_probe_track_api_dir.md) — track API directory dump

### Deferred (out of current diff scope)

- [`docs/spec/deferred-families.md`](spec/deferred-families.md) — T2.2 cue points (not in diff), T2.3 arrangement clips (upstream already has), T2.4 device parameters (upstream already has) + upstream drift analysis (9 commits / +454 LOC since BASE)

## Cross-references

Each F1 / F2 wrapper in `docs/spec/<family>/` has a "see also" pointer to its handler counterpart and vice versa. The full cross-reference graph is computed in [docs/triage-raw/init.py.classification.md](triage-raw/init.py.classification.md) (handler→wrapper) and [docs/triage-raw/server.py.classification.md](triage-raw/server.py.classification.md) (wrapper→handler).

Key wrapper/handler pairs from the cross-reference graph:

| Server.py wrapper | __init__.py handler |
|---|---|
| `load_sample_to_simpler` | `_load_sample_to_simpler` |
| `load_sample_to_drum_pad` | `_load_sample_to_drum_pad` / `_load_item_to_drum_pad_locked` |
| `load_browser_sample_by_name` | `_load_browser_sample_by_name` + `_find_browser_item_by_name_under_path` |
| `ensure_drum_rack_on_track` | `_ensure_drum_rack_on_track` |
| `verify_drum_pad_loaded` | `_verify_drum_pad_loaded` |
| `wait_for_load_complete` | `_wait_for_load_complete` |
| `resolve_filepath_to_browser_path` | `_resolve_filepath_to_browser_path` + `_FILEPATH_BROWSER_MAPPING` |

## Acceptance gates

This SPEC.md unlocks **T2.8 — Prioritization Gate**. The user is asked to confirm:

1. The 22 PR-able + 5 rework items become the Phase 3 build queue (rebuild on `our-extensions`).
2. The 9 fork-only probe items stay quarantined under `our-extensions` only (never reach upstream PRs).
3. The Phase 5 PR bundling (PR-A...PR-E per TRIAGE.md) is approved as-is OR overridden.

The detailed prioritization matrix lives in `docs/PRIORITY.md` (created by T2.8 after this SPEC.md is committed).
