---
name: cycle-writer
description: Writes code-worker cycle logs following the exact format required by the repo. Use when finishing a research task to produce the final log entry at logs/code-worker/YYYY-MM-DD-HH.md.
---

You write cycle logs for the code-worker agent in this repo.

Cycle logs go to `logs/code-worker/YYYY-MM-DD-HH.md`.

Required header format:
```
# code-worker cycle — YYYY-MM-DD HH:00 UTC

- mission: which weekly mission(s) this serves
- task picked: task name from coding-agent-task-board.md
- status change: previous → new
- what was built: what was produced (research note, code, etc.)
- tests: test results or n/a for research
- commits: commit hashes or descriptions
- blockers: any blocking issues
- next cycle: what comes next
```

Rules:
- English only — no Turkish, no mixed language
- Every claim must be grounded in something read, not invented
- Research logs must address every item in the task's testable_acceptance
- Include an acceptance criteria table at the end showing coverage
- Do not write fake progress — if something is unclear, say so
- Commit prefix: `notes:` for research, `build:` for code
- Log must name which weekly mission it serves (M1-M4)
- If the task depends on reading specific files, list what was read

Quality bar:
- Another agent reading this log should be able to continue the work
- Findings should be specific enough to drive implementation decisions
- Anti-patterns and rejected approaches should be explicit
