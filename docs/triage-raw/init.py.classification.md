| Hunk lines | Function/Section | Classification | Notes |
|---|---|---|---|
| L5-L60 | VALID_COMMANDS registry | PR-able | Adds new command names to the control-surface allowlist so the server can route them safely. |
| L69-L74 | _FILEPATH_BROWSER_MAPPING | rework | Useful mapping, but the mount/host prefixes are hardcoded to this fork’s environment and should be configurable. |
| L82-L85 | _load_locks / _lock_events / _worker_seq init | PR-able | Shared concurrency state for serialized loads and event tracing; broadly useful for race-free browser loads. |
| L93-L95 | resolve_filepath_to_browser_path dispatch | PR-able | Wires the new filepath resolver into command handling. see also: resolve_filepath_to_browser_path in server.py |
| L113-L158 | VALID_COMMANDS main dispatch for new wrappers | PR-able | Adds server-facing handlers for the new sample/rack load and verification commands. see also: load_sample_to_simpler, load_sample_to_drum_pad, load_browser_sample_by_name, ensure_drum_rack_on_track, verify_drum_pad_loaded, wait_for_load_complete in server.py |
| L194-L203 | Long-load timeout whitelist | PR-able | Extends response timeouts for browser-load and probe commands that legitimately take longer than normal commands. |
| L214-L245 | _next_worker_seq / _record_lock_event / _drain_lock_events / _get_load_lock | PR-able | Generic lock sequencing and evidence capture for concurrent loads; improves reliability without fork-specific behavior. |
| L247-L305 | _devices_signature / _load_complete_predicate / _find_actual_pad_note | PR-able | Core load-completion detection and off-by-one diagnostics for Drum Rack loads; reusable helper logic. |
| L307-L479 | _load_browser_item_with_retry | PR-able | Main state machine for scheduled browser loading with lock coordination and timeout handling. |
| L481-L533 | _browser_children | PR-able | Safe browser-tree child accessor that avoids brittle direct `.children` assumptions. |
| L535-L577 | _load_sample_to_simpler | PR-able | Generic sample-to-Simpler/track loader. see also: load_sample_to_simpler in server.py |
| L579-L678 | _load_item_to_drum_pad_locked / _load_sample_to_drum_pad | PR-able | Core Drum Rack pad load path with locking and verification plumbing. see also: load_sample_to_drum_pad in server.py |
| L680-L688 | _find_drum_pad_by_note | PR-able | Small reusable lookup helper for Drum Rack pad resolution. |
| L690-L768 | _ensure_drum_rack_on_track | PR-able | Idempotent Drum Rack creation/loading helper. see also: ensure_drum_rack_on_track in server.py |
| L770-L890 | _verify_drum_pad_loaded / _wait_for_load_complete | PR-able | Verification/polling helpers for post-load success. see also: verify_drum_pad_loaded, wait_for_load_complete in server.py |
| L892-L958 | _find_browser_item_by_name_under_path | rework | Good concept, but the supported roots are hardcoded to specific library paths and should be generalized/configured. see also: load_browser_sample_by_name in server.py |
| L960-L979 | _load_browser_sample_by_name | PR-able | Thin wrapper that composes name lookup with Drum Rack loading. see also: load_browser_sample_by_name in server.py |
| L981-L1027 | _search_browser_by_name | PR-able | Generic browser search helper expanded to more browser roots; useful upstream search utility. |
| L1029-L1072 | _probe_environment | fork-only | Read-only session probe for Live/app capabilities; diagnostic only, not an upstream feature. |
| L1074-L1273 | _probe_export_capabilities | fork-only | macOS/AppleScript export pipeline probing for this environment; clearly a local experiment. |
| L1275-L1560 | _probe_export_dialog_controls | fork-only | Accessibility/UI scraping probe for Export Audio dialog; session-specific debugging code. |
| L1562-L1943 | _probe_routing_full / _probe_routing_current_value / _restore_routing_by_display_name / _smoke_resample / _probe_track_api_dir / _probe_routing_setter | fork-only | Routing/API exploration and smoke-test code; useful for investigation, but not commit-ready upstream behavior. |
| L1945-L1966 | _resolve_filepath_to_browser_path | rework | Good utility, but the mount-to-browser mapping is hardcoded to this fork’s filesystem layout and should be configurable. see also: resolve_filepath_to_browser_path in server.py |
| L1981-L2020 | _find_browser_item_by_uri expansion | PR-able | Broadens browser-root traversal and switches to the safer child accessor; generally useful browser-search hardening. |
| L2021-L2189 | Browser path traversal / user_folders special-case | rework | Helpful path traversal refactor, but the special-cased user_folders handling is a workaround that needs cleanup before upstreaming. |

## Summary
- PR-able: 17 hunks
- fork-only: 4 hunks
- drop: 0 hunks
- rework: 4 hunks
- Total: 25 (must match hunk count after sub-division)
