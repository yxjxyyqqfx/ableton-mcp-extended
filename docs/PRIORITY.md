# PRIORITY — Build & PR Submission Order

**Plan**: `clean-fork-restructure` Phase 2 / T2.8
**Date**: 2026-05-10
**Sources**: [TRIAGE.md](TRIAGE.md), [SPEC.md](SPEC.md), [v1 plan](../.sisyphus/plans/ableton-mcp-midi-read-and-upstream-sync.md)
**Status**: **CONFIRMED** (see User Confirmation at end of file)

## Scoring axes

| Axis | Meter | Scale |
|---|---|---|
| **Effort** | LOC + test surface + complexity | S(<50) / M(50-300) / L(300-800) / XL(>800) |
| **Value (user)** | Critical for our immediate music workflow | 1-5 |
| **Value (community)** | Universally applicable upstream | 1-5 |
| **Risk** | Edge cases, Live API churn, breaking change | low / med / high |
| **Dependencies** | Features that must land first | list IDs |
| **PR Size (LOC)** | Rough PR diff size | numeric |
| **Upstream Fit** | Acceptance probability (rubric 1-5) | 1-5 |

### Upstream Fit rubric

- **5 Strong fit**: bug fix + open issue with maintainer interest
- **4 Good fit**: universal, matches existing tool patterns, <300 LOC
- **3 Plausible**: useful but needs author discussion (API/naming)
- **2 Speculative**: niche or contentious, expect pushback
- **1 Poor fit**: project-specific, unlikely to land

## Matrix (12 logical feature bundles, sorted by recommended Build Order)

| # | ID | Feature bundle | Spec dir | Effort | Val(user) | Val(comm) | Risk | Deps | PR LOC | Upstream Fit |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B1 | `eof_newline_server_py` (POSIX trailing newline) | infrastructure | S | 1 | 3 | low | — | <5 | 5 (cosmetic, trivial) |
| 2 | B2 | `ableton_host_port_env_vars` (`ABLETON_HOST/PORT`) | infrastructure | S | 4 | 4 | low | — | ~10 | 4 (universal, container-friendly) |
| 3 | B3 | `valid_commands_registry` (allowlist + dispatch) | infrastructure | S | 5 | 5 | low | — | ~50 | 5 (required for any future tool) |
| 4 | B4 | F4 concurrency primitives (`_load_locks_state`, `_next_worker_seq`, `_record_lock_event`, `_drain_lock_events`, `_get_load_lock`, `long_load_timeout_whitelist`) | infrastructure | M | 4 | 4 | med | B3 | ~250 | 4 (race-free browser loads, broadly useful) |
| 5 | B5 | `_browser_children` + `_search_browser_by_name` (safer accessors) | browser-load | S | 4 | 4 | low | B3 | ~100 | 4 (defensive code, matches Live API best practice) |
| 6 | B6 | `_load_browser_item_with_retry` (state machine) | infrastructure | L | 5 | 4 | med | B3, B4, B5 | ~300 | 4 (centralizes async load orchestration) |
| 7 | B7 | `load_sample_to_simpler` (wrapper + handler) | browser-load | M | 5 | 4 | low | B6 | ~70 | 4 (universal sample-into-Simpler API) |
| 8 | B8 | F1 Drum Rack pad family (ensure / load / verify / wait + internals) | drum-rack | L | 5 | 5 | med | B6 | ~600 | 4 (large but MPC-style Drum Rack workflow is in-demand) |
| 9 | B9 | `_find_browser_item_by_uri` expansion (broader roots) | browser-load | S | 3 | 3 | low | B5 | ~50 | 4 (safer browser-search hardening) |
| 10 | B10 | **Rework**: `load_browser_sample_by_name` + `_find_browser_item_by_name_under_path` — lift `valid_roots` to module-level config | browser-load | M | 3 | 4 | med | B9 | ~150 | 3 (name-based sample lookup; needs API discussion with author) |
| 11 | B11 | **Rework**: `resolve_filepath_to_browser_path` + `_FILEPATH_BROWSER_MAPPING` + `_resolve_filepath_to_browser_path` — parameterize mount prefixes | browser-load | M | 4 | 3 | med | B9 | ~120 | 3 (host-fs↔browser-URI mapping; configurability needs design) |
| 12 | B12 | **Rework**: `user_folders_path_traversal` cleanup | browser-load | M | 2 | 3 | med | B9 | ~80 | 3 (workaround removal — needs alternative impl agreed by author) |
| — | F6 | F6 probes (fork-only, NEVER PR'd) | probes | M | 4 | 1 | n/a | — | n/a | 1 (project-specific diagnostics) |

## Build Order (Phase 3 commit sequence) — POST-CONFIRMATION SCOPE

User-confirmed scope: **B1-B9 + F6** (defer B10-B12 to a later cycle).

1. [x] B1 — `eof_newline_server_py` — **NO-OP** (already in upstream/main, verified `tail -c 1` is `\n`)
2. [x] B2 — `ableton_host_port_env_vars` — commit `11554c4` (3 tests added, 146 total passing)
3. [x] B3 — `valid_commands_registry` — commit `1cd14e0` (refactor + 4 tests, 150 total passing)
4. [ ] B4 — F4 concurrency primitives
5. [ ] B5 — `_browser_children` + `_search_browser_by_name`
6. [ ] B6 — `_load_browser_item_with_retry`
7. [ ] B7 — `load_sample_to_simpler`
8. [ ] B8 — F1 Drum Rack pad family
9. [ ] B9 — `_find_browser_item_by_uri` expansion
10. [ ] F6 — Fork-only probes (separate commit, not pushed to upstream)

### Deferred (post-confirmation)

These bundles are **ported into our-extensions from /legacy as-is** (so the fork keeps working as expected) but are NOT cleaned up for upstream and NOT included in the Phase 5 PR queue. They will be revisited in a follow-up cycle after PR-A...PR-D land.

- ~~B10 — Rework: name-based sample lookup~~ DEFERRED
- ~~B11 — Rework: filepath → browser path mapping~~ DEFERRED
- ~~B12 — Rework: user_folders cleanup~~ DEFERRED

Rationale for deferral (user-approved):
- 3/5 Upstream Fit means meaningful pushback risk during review.
- Each requires API design discussion with maintainer that could block the rest of the PR queue.
- The fork itself doesn't need the rework — only the upstream-PR-ready version does.
- Phase 4 (v1 MIDI plan) delivers more user-visible value per day of effort.

## PR Submission Order (Phase 5) — POST-CONFIRMATION

| PR | Bundle | Contents | Effort | Recommended Live testing |
|---|---|---|---|---|
| **PR-A** | B1 + B2 | Cosmetic + config | XS | Smoke import in Live 12 |
| **PR-B** | B3 + B4 + B5 + B6 | Dispatch + concurrency + safe accessors + retry state machine | L | Live 11 + 12 manual smoke (browser load happy path) |
| **PR-C** | B7 | `load_sample_to_simpler` | S | Live 12 (Simpler load test, 5 samples) |
| **PR-D** | B8 | Drum Rack family | M | Live 11 + 12 (Drum Rack create + load + verify + replace path) |
| **PR-E** | B9 | `_find_browser_item_by_uri` expansion (rework parts B10-B12 deferred) | XS | Live 12 (URI search edge cases) |

PRs are submitted in order A→E. Each PR depends on the previous landing (B numbers reflect dependencies).

**Total PRs to upstream**: 5
**Total fork-only commits**: 1 (F6 probes, stays on `our-extensions` local + push to fork remote `origin` but not to `upstream`)
**Deferred from Phase 5**: B10-B12 reworks (will become PR-F/G/H in a future cycle)

## Risk register

- **Live API version drift** (Live 11 vs 12): B4-B8 use browser APIs that differ between versions. Per SPEC files, version gating uses `application().get_major_version()`. Need manual smoke test in both before each PR.
- **Upstream drift since BASE** (9 commits, +454 LOC in target files): B8 (Drum Rack family) lands on top of `1116449` which already has `2d1bda9` external plugin tools — verify no symbol collisions before B8 commit.
- **Rework PR fit** (PR-E items B10-B12): all rated 3/5 Upstream Fit because they re-shape configurability surface; expect maintainer discussion on `valid_roots` and `_FILEPATH_BROWSER_MAPPING` API.

## User confirmation gate

To unblock Phase 3, please confirm ONE of the following:

### Option 1 — Accept as-is (recommended)
Reply with: `OK PRIORITY` (or equivalent acknowledgement).
Agent will record below as `### User Confirmation` + timestamp and proceed to Phase 3.

### Option 2 — Override with edits
Reply specifying any of the following:
- Reorder build queue: `B7 before B4` (or similar)
- Reorder PRs: `swap PR-C and PR-D`
- Re-rate axes: `B8 risk = high` (with rationale)
- Skip features: `defer B10-B12 to a later cycle`

Agent will update the matrix with your overrides + timestamp + rationale, then proceed.

### Option 3 — Ask for analysis
Reply with: `analyze B8 risk` (or similar). Agent will provide deeper analysis on specific items before you decide.

---

### User Confirmation

**Confirmed at**: 2026-05-10T23:50:00Z
**Decision**: accept with deferral
**Overrides**:
- Phase 3 scope = B1..B9 + F6 (10 commits) instead of B1..B12 + F6 (13 commits)
- B10, B11, B12 (rework bundles) deferred to a follow-up cycle after PR-A..PR-D land
- PR-E now contains only B9 (no rework items)

**Rationale**:
- Rework bundles rate 3/5 Upstream Fit; risk of API discussion blocking the rest of the queue.
- Fork itself works fine with the /legacy versions of those features (no upstream cleanup needed for fork users).
- Phase 4 (v1 MIDI plan) delivers more user-visible value per unit of effort.
- Deferred bundles will be revisited after upstream momentum is established through PR-A..PR-D landings.
