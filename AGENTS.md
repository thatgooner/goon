# AGENTS.md

## Cursor Cloud specific instructions

This is a **documentation-only repository** — a personal knowledge base of Markdown research notes. There is no source code, no build system, no dependencies, no tests, and no application to run.

### Repository structure

- `notes/boards/` — canonical shared state (system-board, codex-task-board)
- `notes/daily/` — raw day-by-day research files (`research-YYYY-MM-DD.md`)
- `notes/watchlists/` — living watchlists (operator tracker)
- `assets/` — static assets (cover image)

### How to work in this repo

- Read `notes/README.md` for routing rules and folder meanings.
- Read `notes/boards/system-board.md` for the current mission and priorities.
- New raw findings go into today's daily note (`notes/daily/research-YYYY-MM-DD.md`).
- Build tasks go to `notes/boards/codex-task-board.md`.
- Operator candidates go to `notes/watchlists/poly-operator-tracker.md`.
- Do not create new board files unless clearly necessary.

### Development environment

- **No dependencies to install.** Git is the only tool required.
- **No lint, test, or build commands.** The repo contains only Markdown and images.
- **No services to start.** There is no application.
