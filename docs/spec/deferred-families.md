# Deferred families — not in current diff scope

Plan `clean-fork-restructure.md` (T2.1-T2.6) predicted 6 spec families. After Phase 1 TRIAGE, only 3 of them turned out to apply to the actual diff. The other 3 are documented here as **deferred** so the SPEC.md aggregate accounts for them honestly.

## T2.2 — Cue point management

**Planned features**: `get_cue_points`, `jump_to_cue_point`, `create_cue_point`, `delete_cue_point`.

**Status**: **Not in current diff scope.**

`git diff 8abb8fd..HEAD -- 'MCP_Server/server.py' 'AbletonMCP_Remote_Script/__init__.py'` (in /legacy) does not show any of these symbols. No new code was added for cue point management between the upstream BASE and our /legacy worktree, so there is nothing to spec.

**Future**: If cue point work is added later, follow the same SPEC template under `docs/spec/cue-points/`.

## T2.3 — Arrangement clip family

**Planned features**: `create_arrangement_midi_clip`, `create_arrangement_audio_clip`, `duplicate_clip_to_arrangement`, `delete_arrangement_clip`, `set_arrangement_clip_property`, `manage_clip_automation`, `get_arrangement_info`, `set_arrangement_loop`, `set_song_time`.

**Status**: **Not in current diff scope (upstream already has these).**

These features already exist on `upstream/main`. They were introduced by PR #11 (commit `9b52a14 feat: add Arrange View control via MCP tools`), merged BEFORE our BASE commit `8abb8fd`. We inherit them as-is; no fork divergence to spec.

**Future**: If our fork introduces new arrangement clip behavior, add specs under `docs/spec/arrangement/`.

## T2.4 — Device parameter family

**Planned features**: `get_device_parameters`, `navigate_device_preset`, plugin aliases from `plugin_aliases.py`.

**Status**: **Not in current diff scope (upstream already has these).**

Device/parameter control was introduced by PR #12 (commit `3ff1061 feat: add device/parameter control and VST instrument support`), merged BEFORE BASE `8abb8fd`. `plugin_aliases.py` exists in upstream (not in our diff).

External plugin discovery (`2d1bda9 Add external plugin discovery/load tools with caching and tests`) landed in upstream **after** our BASE `8abb8fd` but **before** our rebuild target `upstream/main = 1116449`. The `our-extensions` branch (cut from `upstream/main`) already inherits it; no spec needed here.

## Upstream drift between BASE and rebuild target

When generating diffs in T1.1 we used BASE `8abb8fd` (the merge-base with /legacy). Upstream `main` has since advanced **+9 commits** to `1116449`. The new commits between BASE and HEAD include:

- `2d1bda9` external plugin discovery/load tools + tests
- `a8b3132` Remove NEW_CHANGES.md from PR
- `0c2141c` track deletion safety status tool and last-track guard
- `af25923` Ableton songwriter skill scaffolding
- `f012873` PR #16 mcp-server-changes (RobertTylman)
- `a8463bf` Guard group tracks in get_track_info and get_arrangement_info
- `484deab` Fix README Mac install path for Remote Scripts
- `67bd55e` PR #19 docs/remote-script-mac-path
- `1116449` PR #17 fix/group-track-guard (current HEAD)

**Implication for Phase 3**: Rebuilds on `our-extensions` (which sits on `1116449`) may collide with these upstream changes. When porting `_load_browser_item_with_retry` or `_get_track_info` callsites, check for upstream-side modifications first (`git diff 8abb8fd..upstream/main -- <file>`). Document any collision in the per-commit message.

**Future**: If our fork extends device control, add specs under `docs/spec/devices/`.

## Coverage rationale

| Planned T2.x | Family | Status | Spec dir |
|---|---|---|---|
| T2.1 | F1 Drum Rack pad | covered | `docs/spec/drum-rack/` |
| T2.2 | Cue points | deferred (not in diff) | — |
| T2.3 | Arrangement clips | deferred (upstream has it) | — |
| T2.4 | Device parameters | deferred (upstream has it) | — |
| T2.5 | F2 Browser/sample loading | covered | `docs/spec/browser-load/` |
| T2.6 | F6 Probes (fork-only) | covered | `docs/spec/probes/` |
| — | F3 Connection config | covered | `docs/spec/infrastructure/` |
| — | F4 Load orchestration | covered | `docs/spec/infrastructure/` |
| — | F5 Command registry | covered | `docs/spec/infrastructure/` |
| — | F7 Cosmetic | covered | `docs/spec/infrastructure/` |

Effective Phase 2 SPEC coverage = ALL families that actually appear in the diff. The three deferred families are honest "no work needed" findings, not gaps.
