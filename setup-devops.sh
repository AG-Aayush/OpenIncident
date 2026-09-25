#!/usr/bin/env bash
# Run this from inside the OpenIncident repo root: bash setup-devops.sh
set -e

echo "Creating project structure..."
mkdir -p src/agent src/orchestrator src/tools src/policy tests
mkdir -p .github/workflows .github/ISSUE_TEMPLATE

# --- .gitignore -------------------------------------------------------
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.env
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/

# Editors / OS
.vscode/
.idea/
.DS_Store

# Logs / local data
*.log
data/
EOF

# --- pyproject.toml with ruff + black config --------------------------
cat > pyproject.toml << 'EOF'
[project]
name = "openincident"
version = "0.1.0"
description = "AI-powered incident response agent"
requires-python = ">=3.11"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.pytest.ini_options]
testpaths = ["tests"]
EOF

# --- pre-commit config --------------------------------------------------
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

# --- CI workflow: lint + test on every PR --------------------------------
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff black pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Lint (ruff)
        run: ruff check .

      - name: Format check (black)
        run: black --check .

      - name: Run tests
        run: pytest -q
EOF

# --- PR template ---------------------------------------------------------
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## Summary
<!-- What does this PR do and why? -->

## Related issue
Closes #

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Refactor
- [ ] Documentation
- [ ] CI / tooling

## Checklist
- [ ] Lint (`ruff check .`) passes
- [ ] Format (`black --check .`) passes
- [ ] Tests added/updated and passing
- [ ] Docs updated if behavior changed
EOF

# --- Issue templates -------------------------------------------------------
cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Report a problem with OpenIncident
labels: bug
---

**Describe the bug**

**Steps to reproduce**

**Expected behavior**

**Environment** (OS, Python version, Ollama model)
EOF

cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest an idea for OpenIncident
labels: enhancement
---

**Problem this solves**

**Proposed solution**

**Alternatives considered**
EOF

# --- CODEOWNERS ---------------------------------------------------------
cat > CODEOWNERS << 'EOF'
# Default owner for everything in the repo
* @AG-Aayush
EOF

# --- CONTRIBUTING.md ------------------------------------------------------
cat > CONTRIBUTING.md << 'EOF'
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
EOF

# --- LICENSE (MIT) ---------------------------------------------------------
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 AG-Aayush

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# --- placeholder package files so directories aren't empty ---------------
touch src/agent/__init__.py src/orchestrator/__init__.py src/tools/__init__.py src/policy/__init__.py tests/__init__.py

echo "Done. Files created:"
git status --short
