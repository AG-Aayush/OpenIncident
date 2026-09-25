# Contributing to OpenIncident

## Workflow
1. Fork or branch from `main` (never commit directly to `main`).
2. Branch naming: `feat/short-description`, `fix/short-description`, `chore/short-description`.
3. Make your changes, keeping commits focused.
4. Run locally before pushing:
   ```
   ruff check .
   black .
   pytest
   ```
5. Open a Pull Request into `main` using the PR template.
6. At least one review + passing CI checks are required before merge.

## Commit style
Use short, imperative commit messages, e.g. `Add rollback_deployment tool`, `Fix retry logic in agent loop`.

## Code style
- Formatted with `black`, linted with `ruff`.
- Type hints required for public functions.
- Keep tool functions in `src/tools/`, agent reasoning in `src/agent/`, orchestration/policy logic in `src/orchestrator/` and `src/policy/`.
