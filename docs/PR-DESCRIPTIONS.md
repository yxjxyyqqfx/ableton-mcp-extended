# PR descriptions — ready for upstream submission

**Target repository**: [uisato/ableton-mcp-extended](https://github.com/uisato/ableton-mcp-extended)
**Source branch**: [yxjxyyqqfx/ableton-mcp-extended:our-extensions](https://github.com/yxjxyyqqfx/ableton-mcp-extended/tree/our-extensions)
**Branch parent**: `upstream/main @ 1116449`
**Tests baseline**: 143 passing → 178 passing on the deepest PR-D stack (+44 new unit tests across all five PRs; one BUSY-path test for a removed private helper was dropped in the pre-submission review).

All five PRs were validated against a real Ableton Live 12.3 session: socket connection at `host.docker.internal:9877`, full Drum Rack workflow create→load→verify→wait→replace, browser URI resolution from the expanded root list, and regression checks against pre-existing upstream commands (`get_session_info`, `get_track_info`, `create_midi_track`, `set_track_name`, `create_clip`, `add_notes_to_clip`, `set_clip_name`, `fire_clip`, `stop_clip`, `set_track_volume`, `set_track_panning`, `duplicate_clip_to_arrangement`, `delete_arrangement_clip`, `delete_track`, `get_device_parameters`, `load_instrument_or_effect`).

**Per-branch test counts** (each branch starts from `upstream/main @ 1116449`):

| PR  | Branch (origin = `yxjxyyqqfx`)       | Tests pass | Δ vs baseline | Stacked on              |
| --- | ------------------------------------ | ---------- | ------------- | ----------------------- |
| A   | `pr/config-env-vars`                 | 146        | +3            | (independent)           |
| B   | `pr/dispatch-and-load-foundation`    | 166        | +23           | (foundation)            |
| C   | `pr/load-sample-to-simpler`          | 170        | +27           | PR-B                    |
| D   | `pr/drum-rack-family`                | 178        | +35           | PR-C (which stacks B)   |
| E   | `pr/find-browser-item-uri-expansion` | 172        | +29           | PR-B                    |

Each branch ends with a small `fix(remote): pre-submission review fixes ...` commit applying targeted hunks from the post-feature review (TOCTOU fix on `_get_load_lock`, removal of an unused private state-machine helper, strict-bool guards on `replace`, lowered poll cadence in `_wait_for_load_complete`, and **socket-timeout sync** for browser-load commands — required for end-to-end correctness against a real Live runtime).

---

## PR-A — `feat(config): support ABLETON_HOST and ABLETON_PORT env vars`

**Commit**: `11554c4`
**Effort**: XS (~10 LOC)
**Risk**: low (backward-compatible defaults)
**Tests added**: 3 (unit `tests/unit/test_connection_config.py`)

### Summary

Allow the MCP server to read the Ableton Live host and port from the environment, with backward-compatible defaults (`localhost:9877`).

### Motivation

`MCP_Server.server.AbletonConnection` previously hardcoded `host="localhost", port=9877`. This blocks anyone running the MCP server in a different network namespace from Live — for example:

- Running the server inside a Docker / Linux container with Ableton Live on the macOS host (`ABLETON_HOST=host.docker.internal`).
- Running the server on a remote dev machine that connects to Live on the user's laptop over a VPN.
- Running multiple Live instances on different ports for batch testing.

### Change

```python
# Before
_ableton_connection = AbletonConnection(host="localhost", port=9877)

# After
_ableton_connection = AbletonConnection(
    host=os.getenv("ABLETON_HOST", "localhost"),
    port=int(os.getenv("ABLETON_PORT", "9877")),
)
```

Top-level imports gain `import os`. The defaults match the existing hardcoded values, so any user without the env vars set is unaffected.

### Tests

`tests/unit/test_connection_config.py` — 3 new tests:

1. `test_get_ableton_connection_uses_default_host_and_port_when_env_unset` — verifies localhost/9877 path.
2. `test_get_ableton_connection_uses_env_host_and_port_when_set` — verifies env vars are read.
3. `test_ableton_port_env_is_coerced_to_int` — verifies the string env var becomes an int for the socket call.

### Live validation

Verified against Live 12.3 with `ABLETON_HOST=host.docker.internal`, `ABLETON_PORT=9877`:

```
$ ABLETON_HOST=host.docker.internal python -m MCP_Server.server
2026-05-12 00:15:59 - AbletonMCPServer - INFO - Connecting to Ableton (attempt 1/3)...
2026-05-12 00:15:59 - AbletonMCPServer - INFO - Connected to Ableton at host.docker.internal:9877
# get_session_info -> {'tempo': 120.0, 'signature_numerator': 4, ...}
```

### Backward compatibility

Fully backward-compatible. Existing users see no behavior change because both env vars default to the previous hardcoded values.

---

## PR-B — `feat(remote): centralize dispatch + add browser-load concurrency primitives + drum-rack diagnostics`

**Commits** (in order): `1cd14e0` (B3), `9c14c68` (B4), `8863bbd` (B5), `f99d439` (B6) + 1 pre-submission fixup (TOCTOU on `_get_load_lock` + removal of an unused private state-machine helper, with its matching BUSY-path test).
**Effort**: L (~700 LOC net across both files after dead-code removal)
**Risk**: medium (touches core dispatch + adds shared state)
**Tests added**: 23 (24 introduced, 1 removed with the unused helper) — `test_command_dispatch.py` + `test_load_orchestration.py` + `test_browser_accessors.py` + `test_drum_rack_predicates.py`

### Summary

Foundation work that prepares the Remote Script for safe concurrent browser loading and Drum Rack workflows. Four logically-independent commits:

1. **VALID_COMMANDS allowlist** — refactor the long inline command-type tuple in `_process_command` into a module-level `frozenset`, so the supported command set is explicit and discoverable.
2. **Browser-load concurrency primitives** — per-`(track, rack)` locks, monotonic worker sequence allocator, structured lock-event trace, and a long-load timeout whitelist (90s vs the default 10s) for browser-load commands.
3. **Safer browser-tree accessors** — `_browser_children` (normalizes Live's mixed-shape browser items) and `_search_browser_by_name` (case-insensitive name lookup across standard roots).
4. **`_load_browser_item_with_retry` state machine** — worker-thread → main-thread browser-load orchestration with pre/post device-signature snapshots, replace semantics, tick-based completion polling, and structured response (success / `topology_changed` / timeout / error).

These four pieces collectively enable the public Drum Rack family in PR-D.

### Motivation

The original `_process_command` had a 17-element command-type tuple inline. It was hard to read, easy to mistype when adding a new handler, and offered no place to gate unrecognized commands. The new allowlist is a module-level constant new contributors can grep for.

Browser loads (`Browser.load_item`) are inherently asynchronous in Live: the call returns immediately, but the device chain isn't ready for several main-thread ticks. Without serialization, two concurrent loads on the same Drum Rack pad cause `load got nothing` failures or chains landing on the wrong pad (off-by-one). The concurrency primitives ensure exactly one load is in flight per `(track_index, rack_device_index)` key, with a 45-second per-load lock timeout, and an evidence trace that lets us debug races after the fact.

Live's browser tree mixes string-like leaves, `list/tuple` containers, BrowserItem-like nodes with `.children`, and numeric-indexable iterables. Direct `.children` access throws on string leaves and on some virtual roots. `_browser_children` normalizes all of these shapes into a list-like return.

The state machine packages all of the above into a single primitive callers can use without re-implementing the worker-thread / main-thread / lock / retry / timeout dance.

### Files changed

- `AbletonMCP_Remote_Script/__init__.py`:
  - Add `VALID_COMMANDS = frozenset({...})` at module scope.
  - Replace the inline command-type list in `_process_command` with `elif command_type in VALID_COMMANDS:`.
  - Add `self._load_locks`, `self._lock_events`, `self._worker_seq`, `self._worker_seq_lock` to `__init__`.
  - Add `_next_worker_seq`, `_record_lock_event`, `_drain_lock_events`, `_get_load_lock`.
  - Add `_LONG_LOAD_COMMANDS` tuple and 90-second timeout branch in `_process_command`'s response_queue.get block.
  - Add `_browser_children`, `_search_browser_by_name`.
  - Add `_devices_signature`, `_load_complete_predicate`, `_find_actual_pad_note`, `_load_browser_item_with_retry`.

No changes to `MCP_Server/server.py` in this PR (handlers exposed to MCP arrive in PR-C / PR-D / PR-E).

### Tests added (24 unit tests)

- **`test_command_dispatch.py`** (4) — VALID_COMMANDS is a frozenset, contains baseline read-only + mutating handlers, rejects bogus names.
- **`test_load_orchestration.py`** (5) — `_next_worker_seq` is monotonic + threadsafe under 4 concurrent workers × 50 calls, `_get_load_lock` returns the same Lock for the same key and distinct Locks for different keys, `_record_lock_event`/`_drain_lock_events` isolate workers, `**extra` kwargs merge into the event dict.
- **`test_browser_accessors.py`** (6) — `_browser_children` returns `[]` for `None` and string leaves, passes through `list`/`tuple` unchanged, reads `.children` attribute when present; `_search_browser_by_name` finds loadable items by case-insensitive name across roots, returns `None` when absent.
- **`test_drum_rack_predicates.py`** (9) — `_devices_signature` shape + exception fallback, `_load_complete_predicate` four branches (`topology_changed`, pending, success with sampler, wrong device class), `_find_actual_pad_note` off-by-one vs exact match, and the BUSY response path of `_load_browser_item_with_retry` under a held lock.

### Live validation

Verified browser tree traversal (`get_browser_tree`, `get_browser_items_at_path` on `drums`, `samples`, `instruments`, `user_library`), connection dispatch (`get_session_info`, `get_track_info`, `set_track_volume`, `set_track_panning`, `create_midi_track`, `set_track_name`, `create_clip`, `add_notes_to_clip`, `set_clip_name`, `fire_clip`, `stop_clip`), and that legacy `load_instrument_or_effect` still resolves URIs (`query:Synths#Operator` → Operator loaded). The concurrency primitives are exercised end-to-end by PR-D in real Drum Rack loads.

### Backward compatibility

Pure additive change. Existing command names continue to dispatch through the same `elif` branch (now via the allowlist). No public API breaks. The new helpers (`_browser_children` etc.) are private (`_` prefix).

---

## PR-C — `feat: load_sample_to_simpler tool + handler`

**Commit**: `65b1b4e` + 1 pre-submission fixup (server.py 95s socket timeout for `load_sample_to_simpler`, required for end-to-end correctness).
**Effort**: S (~70 LOC)
**Risk**: low (single new command, isolated handler)
**Tests added**: 4 (`tests/unit/test_load_sample_to_simpler.py`)
**Depends on**: PR-B (uses `VALID_COMMANDS` plumbing and `_find_browser_item_by_uri`).

### Summary

Adds a first-class MCP tool to load a browser sample (by URI) onto a target track's selected Simpler device, or directly onto a MIDI track if no device is specified.

### Motivation

The existing `load_instrument_or_effect` loads a *device* onto a track, but does not work for samples that need to go into an existing `Simpler` instance. Live's `Simpler.sample` is read-only, so sample assignment must go through `Browser.load_item()` with the destination track/device selected first. This tool encapsulates that selection sequence in a single MCP call.

### Public API

```python
@mcp.tool()
def load_sample_to_simpler(ctx: Context, track_index: int, uri: str, device_index: int = 0) -> str:
    """
    Load a browser sample item into a selected Simpler or onto a MIDI track.

    Parameters:
    - track_index: Track number (1-based).
    - uri: Browser item URI for the sample (e.g. query:Samples#FileId_...).
    - device_index: Existing Simpler device number (1-based). Use 0 to load onto the track.
    """
```

Returns a human-readable status string of the form `"Loaded sample '<name>' to track <N>. Devices: <list>"`.

### Handler

`AbletonMCP_Remote_Script.AbletonMCP._load_sample_to_simpler(track_index, item_uri, device_index=None)` validates indices, resolves the URI via `_find_browser_item_by_uri`, optionally selects the target device on the track view, and calls `app.browser.load_item(item)`. Returns a structured dict with `loaded`, `item_name`, `track_name`, `selected_device`, `uri`, and `devices_after` for the caller to inspect.

### Wiring

- `VALID_COMMANDS` gains `"load_sample_to_simpler"`.
- `_process_command` dispatches `"load_sample_to_simpler"` to the handler with 1-based → 0-based index translation done in the server wrapper.

### Tests

`tests/unit/test_load_sample_to_simpler.py` — 4 tests:

1. Allowlist membership.
2. Handler method exists on `AbletonMCP`.
3. Server tool is registered and the docstring contains "Load a browser sample item".
4. End-to-end wrapper success path: index translation 1→0, structured `send_command` payload, success message contains `Loaded sample '<name>'`.

### Live validation

```
load_sample_to_simpler(track_index=6, uri="query:Drums#Drum%20Hits:Kick:FileId_227111", device_index=0)
-> "Loaded sample '505 Kick.flac' to track 6. Devices: 505 Kick"
```

### Backward compatibility

Pure new command. No existing behavior changes.

---

## PR-D — `feat: Drum Rack pad family (ensure / load / verify / wait)`

**Commit**: `7d948f2` + 1 pre-submission fixup (strict-bool `replace` guards, `_wait_for_load_complete` 50ms → 20ms with UI-block docstring warning, server.py 95s socket timeout for the four Drum Rack commands).
**Effort**: M (~620 LOC across both files)
**Risk**: medium (4 new tools + structured response shapes)
**Tests added**: 8 (`tests/unit/test_drum_rack_family.py`)
**Depends on**: PR-B (concurrency primitives + Drum Rack diagnostic helpers), PR-C wiring pattern.

### Summary

Adds four MCP tools that together make MPC-style Drum Rack workflows possible: create-or-find a Drum Rack on a track, load a sample by URI to a specific pad with `replace` semantics, verify what landed on the pad, and poll the pad until the async load is complete.

### Public API

```python
@mcp.tool()
def ensure_drum_rack_on_track(
    ctx: Context, track_index: int = 0, name: str = "", create_if_missing: bool = True,
) -> str:
    """Idempotently ensure a Drum Rack exists on a track.

    track_index=0 means create a new MIDI track. If the track already has a
    Drum Rack, its index is returned and no new device is loaded.
    """

@mcp.tool()
def load_sample_to_drum_pad(
    ctx: Context,
    track_index: int, uri: str, pad_note: int = 36,
    rack_device_index: int = 1, replace: bool = False,
) -> str:
    """
    Load a browser sample item onto a Drum Rack pad, creating a Simpler chain.

    Parameters:
    - track_index: Track number (1-based).
    - uri: Browser item URI for the sample (e.g. query:Samples#FileId_...).
    - pad_note: MIDI note number for the Drum Rack pad (default 36 = C1 kick pad).
    - rack_device_index: Drum Rack device number on the track (1-based).
    - replace: Delete existing chains on the pad before loading.
    """

@mcp.tool()
def verify_drum_pad_loaded(
    ctx: Context,
    track_index: int, rack_device_index: int, pad_note: int,
    expected_filename: str = "",
) -> str:
    """Verify a Drum Rack pad has the expected sample loaded.

    Returns a structured mismatch_reason in
    {None, no_chain, wrong_filename, off_by_one} so callers can act on the
    failure mode programmatically.
    """

@mcp.tool()
def wait_for_load_complete(
    ctx: Context,
    track_index: int, rack_device_index: int, pad_note: int, max_ticks: int = 20,
) -> str:
    """Poll a Drum Rack pad until a sampler chain is loaded.

    Useful right after browser.load_item to confirm the async Live load
    completed before issuing follow-up commands on the same pad.
    """
```

### Handlers (private, in `AbletonMCP_Remote_Script.AbletonMCP`)

- `_ensure_drum_rack_on_track(track_index=-1, name="", create_if_missing=True)` — track-and-rack creation/lookup with safer browser search via `_search_browser_by_name`.
- `_find_drum_pad_by_note(rack, pad_note)` — small lookup helper.
- `_load_item_to_drum_pad_locked(track_index, rack_device_index, pad_note, item, replace=False)` — full locked load path using PR-B primitives: pre/post device-signature snapshots, lock_sequence event trace, off-by-one diagnostics, and replace semantics. Returns a structured result with `loaded`, `mode`, `item_name`, `item_uri`, `track_name`, `rack_name`, `requested_pad_note`, `actual_pad_note`, `mismatch_reason`, `devices_signature_pre/post`, `devices_changed`, `pad_chain_count_after`, `worker_id`, `lock_sequence`.
- `_load_sample_to_drum_pad(track_index, rack_device_index, pad_note, item_uri, replace=False)` — thin URI-resolving wrapper around `_load_item_to_drum_pad_locked`.
- `_verify_drum_pad_loaded(track_index, rack_device_index, pad_note, expected_filename="")` — verification with filename matching, off-by-one cross-pad scan, and `no_chain` / `wrong_filename` / `off_by_one` mismatch reasons.
  - `_wait_for_load_complete(track_index, rack_device_index, pad_note, max_ticks=20)` — poll loop on top of `_verify_drum_pad_loaded` with 20 ms sleep between ticks. Runs on Live's main thread and briefly blocks the UI; the docstring warns callers to keep `max_ticks` small.

### Wiring

- `VALID_COMMANDS` gains `"load_sample_to_drum_pad"`, `"ensure_drum_rack_on_track"`, `"verify_drum_pad_loaded"`, `"wait_for_load_complete"`.
- `_process_command` dispatches each to its handler with 1-based → 0-based index translation done in the server wrapper.

### Tests

`tests/unit/test_drum_rack_family.py` — 8 tests covering allowlist coverage for all 4 new commands, handler method presence, `_find_drum_pad_by_note` match + no-match, and four wrapper → handler forwarding cases (`load_sample_to_drum_pad` with `replace=True`, `ensure_drum_rack_on_track` with `track_index=0` → `-1`, `verify_drum_pad_loaded` with `expected_filename`, `wait_for_load_complete` with `max_ticks`).

### Live validation (full happy-path + edge cases)

```
ensure_drum_rack_on_track(track_index=0, name="Sisyphus_Test", create_if_missing=True)
-> created_track=True, created_rack=True, track_index=4, rack_device_index=0

load_sample_to_drum_pad(track_index=5, uri="query:Drums#Drum%20Hits:Kick:FileId_227111",
                       pad_note=36, rack_device_index=1)
-> "Loaded sample '505 Kick.flac' to Drum Rack pad note 36 on track 5"

verify_drum_pad_loaded(track_index=5, rack_device_index=1, pad_note=36,
                      expected_filename="505 Kick.flac")
-> loaded=True, mismatch_reason=None, requested_pad_note=36, actual_pad_note=36,
   device_names=['505 Kick', '505 Kick']

wait_for_load_complete(track_index=5, rack_device_index=1, pad_note=38, max_ticks=5)
-> loaded=False, mismatch_reason='no_chain', ticks_waited=5  # empty pad path

load_sample_to_drum_pad(... pad_note=36 ... replace=False)
-> Error: "Pad note 36 already has chains; pass replace=True to replace"

load_sample_to_drum_pad(... pad_note=36 ... replace=True)
-> "Loaded sample '626 Kick 1.flac' to Drum Rack pad note 36 on track 5"  # swap OK
```

### Backward compatibility

Pure new commands. No existing behavior changes.

---

## PR-E — `feat(remote): expand _find_browser_item_by_uri roots + accept list/tuple input`

**Commit**: `db31fd6`
**Effort**: S (~40 LOC effective change in handler body)
**Risk**: low (additive search + safer accessor)
**Tests added**: 6 (`tests/unit/test_find_browser_item_by_uri.py`)
**Depends on**: PR-B (uses `_browser_children`).

### Summary

`_find_browser_item_by_uri` previously walked only six browser roots (`instruments`, `sounds`, `drums`, `audio_effects`, `midi_effects`, `plugins`). URIs from other roots — most notably `query:Samples#...`, `query:UserLibrary#...`, and `query:UserFolders#...` — silently returned `None`, leaving downstream `load_*` handlers with `"Browser item with URI not found"` errors even when the item was obviously loadable. This PR expands the search to the full set of load-relevant roots and tightens the traversal.

### Change

Three additive improvements to the recursive search:

1. **Accept `list`/`tuple` inputs** — when the caller passes a flat collection of `BrowserItem`s (rather than a Browser facade), the function now recurses into the collection instead of returning `None`.
2. **Widen the root set** — search the full list `[instruments, sounds, drums, audio_effects, midi_effects, plugins, samples, user_library, current_project, clips, packs, max_for_live, user_folders]`. Roots that the Browser facade doesn't expose on a given Live version are silently skipped via `hasattr` + `try/except`.
3. **Use `_browser_children`** for child enumeration instead of raw `.children` access, so virtual roots that don't expose a `list`-shaped `.children` no longer crash the traversal.

The six pre-existing roots remain in the search list and are searched first, preserving existing behavior for any URI that previously resolved.

### Tests

`tests/unit/test_find_browser_item_by_uri.py` — 6 tests:

1. Baseline behavior — `instruments` root still resolves.
2. New `samples` root resolves a `query:Samples#FileId_...` URI.
3. New `user_folders` root resolves a `userfolder:abc` URI.
4. `list` input is traversed recursively.
5. Missing URI yields `None` without raising.
6. `max_depth` is respected (deep item not found at depth=2).

### Live validation

```
# URI from newly-supported `samples` root (previously unfindable)
load_sample_to_drum_pad(track_index=5, uri="query:Samples#FileId_227111",
                       pad_note=38, rack_device_index=1)
-> "Loaded sample '505 Kick.flac' to Drum Rack pad note 38 on track 5"

verify_drum_pad_loaded(track_index=5, rack_device_index=1, pad_note=38,
                      expected_filename="505 Kick.flac")
-> loaded=True, mismatch_reason=None  # B9 expansion confirmed

# Pre-existing `instruments` root still works (regression check)
load_instrument_or_effect(track_index=7, uri="query:Synths#Operator")
-> "Loaded instrument with URI 'query:Synths#Operator' on track 7"
```

### Backward compatibility

Strictly additive. The six pre-existing roots are still searched in the same order. Any URI that previously resolved continues to resolve. URIs that previously failed with `"Browser item not found"` now have a chance to succeed if they live under one of the seven newly-searched roots.

---

## Recommended submission order

The PRs are ordered by increasing scope and dependency:

```
PR-A → PR-B → PR-C → PR-D → PR-E
```

Each can be reviewed independently, but PR-C, PR-D, and PR-E build on the foundation in PR-B. PR-A is independent of the others.

If the maintainer prefers smaller PRs, PR-B can be split further: the VALID_COMMANDS refactor (B3), the concurrency primitives (B4), the browser accessors (B5), and the state machine (B6) are each independently committed and each leaves tests green.

## Fork-only commit excluded from upstream

Commit `57833ed` (`feat(remote, fork-only): F6 diagnostic probes (NOT pushed upstream)`) introduces 9 macOS / Live 12-specific debugging helpers (`_probe_environment`, `_probe_export_capabilities`, `_probe_export_dialog_controls`, `_probe_routing_*`, `_smoke_resample`, `_probe_track_api_dir`, `_restore_routing_by_display_name`). These are intentionally fork-only and have no `@mcp.tool()` server wrapper. They are not part of any of the five PRs above.
