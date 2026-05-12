# Upstream CI/CD Inventory

**Repository**: `uisato/ableton-mcp-extended` @ `upstream/main` (HEAD `1116449`)
**Survey date**: 2026-05-10
**Surveyor**: T1.3a (clean-fork-restructure plan, Phase 1)

## Workflows

- **GitHub Actions**: none
  - `.github/workflows/` directory does **not exist**
  - No automated checks run on PRs

## Other CI services

- **Travis CI**: not configured (no `.travis.yml`)
- **CircleCI**: not configured (no `.circleci/config.yml`)
- **GitLab CI**: not configured (no `.gitlab-ci.yml`)
- **Azure Pipelines**: not configured (no `azure-pipelines.yml`)

## Pre-commit / git hooks

- **pre-commit framework**: not configured (no `.pre-commit-config.yaml`)
- **husky / lint-staged**: not applicable (Python project)

## Test runner

- **pytest**: configured in `pyproject.toml`
  - `[tool.pytest.ini_options]` markers: `integration: requires running Ableton Live instance`
  - `addopts = "-m 'not integration'"` — integration tests skipped by default
- **No `pytest.ini`, `tox.ini`, `setup.cfg`, `Makefile`** for test orchestration
- Tests live in `tests/`:
  - `tests/unit/` — 10 test files covering arrangement, bar/beat conversion, browser path normalization, indexing, device commands, external plugins, parameter normalization, plugin aliases, remote script helpers, track commands
  - `tests/integration/` — empty (`__init__.py` only)
  - `tests/conftest.py` — shared fixtures (time signatures)

## Lint / format / type-check

- **None configured at upstream level**
- `pyproject.toml` does not declare ruff, black, flake8, mypy, basedpyright, pyright, isort
- No `.editorconfig`

## Required env vars / secrets

- **None for tests** (unit tests run without Ableton)
- Integration tests would need `ABLETON_HOST` / `ABLETON_PORT` (introduced by this fork's hunk 2 of server.py) but they are gated behind the `integration` marker which is skipped by default

## Branch protection

- Not visible from the cloned repo. To confirm whether `main` requires PR review or status checks, use `gh api repos/uisato/ableton-mcp-extended/branches/main/protection` (likely returns 404 if no protection rules — typical for small OSS).

## Implications for Phase 5 PR submission

1. **No automated gating** — there is no CI that will block a PR. Acceptance is purely maintainer review (human approval on github.com).
2. **PRs MUST still pass `pytest tests/unit/` locally** — this is the de-facto contract; even though upstream has no Actions, the test suite is the only objective quality bar. Phase 3 commits must keep `pytest -m 'not integration'` green.
3. **Phase 5 PR description checklist**:
   - [ ] `pytest tests/unit/` passes locally (paste exit code + count)
   - [ ] No new dependencies added without justification (`pyproject.toml` dependencies list is short — additions need rationale)
   - [ ] `python -c "import MCP_Server.server"` succeeds (smoke import)
   - [ ] If touching `AbletonMCP_Remote_Script/__init__.py`, manual integration test note ("verified against Live 11 / Live 12" + Live version)
   - [ ] If adding tools to `server.py`, include a matching unit test in `tests/unit/`
4. **No lint enforcement** — but Phase 3 should still be self-consistent with surrounding code style (4-space indent, snake_case, no trailing whitespace, EOF newline — the `server.py` EOF-newline hunk in our diff is a good example of the cleanup standard).
5. **Recommend introducing a minimal `.github/workflows/test.yml`** in a separate "infra" PR after the substantive feature PRs land — out of scope for this restructure but worth flagging to maintainer.

## Pyproject snapshot (relevant slice)

```toml
[tool.pytest.ini_options]
markers = [
    "integration: requires running Ableton Live instance",
]
addopts = "-m 'not integration'"
```

Dependencies (runtime):
- `mcp[cli]>=1.3.0`
- `elevenlabs>=0.2.26`
- `python-dotenv>=1.0.0`
- Optional `xy_controller`: `pynput>=1.7.6`, `screeninfo>=0.8.1`

## References

- Plan T1.3a: `.sisyphus/plans/ableton-mcp-clean-fork-restructure.md` lines 933-980
- Raw inventory dump: `docs/triage-raw/upstream-ci.txt`
