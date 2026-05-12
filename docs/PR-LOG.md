# PR submission log

Tracks the lifecycle of the five upstream PRs derived from the `our-extensions` work.

- **Target repository**: [uisato/ableton-mcp-extended](https://github.com/uisato/ableton-mcp-extended)
- **Source fork**: [bunau-dj/ableton-mcp-extended](https://github.com/bunau-dj/ableton-mcp-extended)
- **Body drafts**: `.sisyphus/pr-bodies/<feature>.md` (English, GitHub-ready)
- **Master description**: [`docs/PR-DESCRIPTIONS.md`](./PR-DESCRIPTIONS.md)

## Submission pacing (from `.sisyphus/plans/ableton-mcp-clean-fork-restructure.md` § Phase 5)

| Transition  | Minimum wait                                                | Rationale                              |
| ----------- | ----------------------------------------------------------- | -------------------------------------- |
| T5.1 → T5.2 | ≥48 h after T5.1 submit, **or** any author signal           | Tone calibration with maintainer       |
| T5.2 → T5.3 | ≥24 h between submissions                                   | Avoid burst pattern                    |
| T5.3 → T5.4 | ≥24 h between submissions                                   | Same                                   |
| T5.4 → T5.5 | ≥24 h between submissions                                   | Same                                   |
| Any → next  | **STOP** if maintainer requested changes on a previous PR   | Resolve feedback first, then resume    |
| Any → next  | **STOP** if maintainer closed/rejected a previous PR        | Re-evaluate strategy with user         |

**T5.1 (PR-A) is always submitted via the web UI by the user** for tone calibration. Subsequent PRs may be agent-submitted via `gh pr create` after the maintainer's first signal validates the body style.

## Status table

| PR  | Feature                              | Origin branch                        | Compare URL                                                                                                                                                          | Submitted (UTC) | URL                | Last signal | State                                                |
| --- | ------------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------ | ----------- | ---------------------------------------------------- |
| A   | `feat(config)`: env-driven host/port | `pr/config-env-vars`                 | [compare](https://github.com/uisato/ableton-mcp-extended/compare/main...bunau-dj:ableton-mcp-extended:pr/config-env-vars)                                             | (pending)       | (pending)          | —           | branch pushed, body drafted, awaiting user submit    |
| B   | dispatch + concurrency + diagnostics | `pr/dispatch-and-load-foundation`    | [compare](https://github.com/uisato/ableton-mcp-extended/compare/main...bunau-dj:ableton-mcp-extended:pr/dispatch-and-load-foundation)                               | (pending)       | (pending)          | —           | branch pushed, body drafted, blocked by T5.1 pacing  |
| C   | `load_sample_to_simpler`             | `pr/load-sample-to-simpler`          | [compare](https://github.com/uisato/ableton-mcp-extended/compare/main...bunau-dj:ableton-mcp-extended:pr/load-sample-to-simpler)                                     | (pending)       | (pending)          | —           | branch pushed, body drafted, stacked on PR-B         |
| D   | Drum Rack pad family                 | `pr/drum-rack-family`                | [compare](https://github.com/uisato/ableton-mcp-extended/compare/main...bunau-dj:ableton-mcp-extended:pr/drum-rack-family)                                           | (pending)       | (pending)          | —           | branch pushed, body drafted, stacked on PR-C         |
| E   | expanded URI search roots            | `pr/find-browser-item-uri-expansion` | [compare](https://github.com/uisato/ableton-mcp-extended/compare/main...bunau-dj:ableton-mcp-extended:pr/find-browser-item-uri-expansion)                            | (pending)       | (pending)          | —           | branch pushed, body drafted, stacked on PR-B         |

## How to submit (per PR)

1. Open the PR's compare URL above.
2. GitHub will show "Choose a base repository... and a head repository...". Confirm: base = `uisato/ableton-mcp-extended:main`, head = `bunau-dj/ableton-mcp-extended:<branch>`.
3. Copy the body from `.sisyphus/pr-bodies/<feature>.md` into the description field.
4. Set the title to the corresponding commit subject from `docs/PR-DESCRIPTIONS.md`:
   - PR-A: `feat(config): support ABLETON_HOST and ABLETON_PORT env vars`
   - PR-B: `feat(remote): centralize dispatch + add browser-load concurrency primitives + drum-rack diagnostics`
   - PR-C: `feat: load_sample_to_simpler tool + handler`
   - PR-D: `feat: Drum Rack pad family (ensure / load / verify / wait)`
   - PR-E: `feat(remote): expand _find_browser_item_by_uri roots + accept list/tuple input`
5. Click "Create pull request".
6. Paste the resulting PR URL back into the agent chat. The agent will fill in the corresponding row above and start the pacing timer for the next PR.

## Notes

- Each PR branch is independent of `our-extensions` and was cherry-picked onto `upstream/main @ 1116449` directly, so any maintainer can rebase or squash without touching the fork.
- The fork-only commit (`57833ed`, F6 diagnostic probes) is **excluded** from every PR — it lives only on `bunau-dj:our-extensions`.
- If the maintainer prefers all five changes in a single PR, all five branches can be merged together into `our-extensions` (or a new combined branch) and submitted as one. The split is a courtesy, not a requirement.
