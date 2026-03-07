# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Create venv and install (first time)
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Run tests
.venv/bin/pytest

# Run a single test
.venv/bin/pytest tests/path/to/test_file.py::test_name

# Format and lint
.venv/bin/black src/
.venv/bin/ruff check src/

# Run the game
.venv/bin/space-invaders
```

## Environment Notes

- System Python is externally managed (Debian); always use `.venv/`
- Package directory is `src/space_invaders/` (underscore); CLI command is `space-invaders` (hyphen)
- All imports within the package must be relative (e.g. `from . import constants`)
- `AssetManager.ASSETS_DIR` resolves 4 `parent` hops from `assets.py` — only correct for editable installs (`pip install -e`). Non-editable installs will not find the `assets/` directory.

## Project Structure

- `src/space_invaders/main.py` — entry point (`main()` function)
- `context.md` — Session working memory; read at start, update at end
- `WHERE_AM_I.md` — High-level milestone state
- `sprint-plan.md` — Current sprint tasks and priorities
- `result-review.md` — Log of completed work
- `AGENTS.md` — Full agent operating guide with guardrails and autonomy modes
- `skills/` — Task-specific skill files to load when relevant

## AgentFlow Methodology

This project uses **AgentFlow** — a documentation-driven human-AI collaboration system. These files are shared memory across sessions and AI models.

**Startup sequence** (in order):
1. Read `AGENTS.md` for guardrails
2. Read `context.md` for current state
3. Check `result-review.md` for recent completions
4. Read `sprint-plan.md` for current tasks

**Load skill files when triggered:**
- Implementing a feature/fix → `skills/development-loop.md`
- Testing work → `skills/test-as-lee.md`
- Before committing → `skills/documentation.md`
- Creating a backlog item → `skills/backlog.md`
- Closing a sprint → `skills/code-review.md`

**Autonomy mode** is set in `context.md` (default: Mode 2 — implement with check-ins, ask on decisions not routine code).

**Session end requirements:** Update `WHERE_AM_I.md`, `sprint-plan.md`, and `result-review.md`.

## Guardrails

- Do not add external runtime dependencies without explicit permission
- Do not make breaking API changes without explicit permission
- Do not delete files without confirming necessity
- Do not commit directly to protected branches
- Do not move files out of `backlog/candidates/` (human curates)

## Commit Convention

```
feat: add --dry-run flag to scaffold command
fix: handle missing config file gracefully
docs: update session context
refactor: extract parser into module
test: add unit tests for main entry point
```

One commit per logical unit of work. Never commit broken code.
