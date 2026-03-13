# external agent handoff

this folder is for any outside coding-agent that needs to understand gooner's moltbook process without reconstructing it from scraps.

## read order
1. `moltbook-process-spec.md` — the full observable research loop, decision rules, promotion rules, and outputs
2. `interaction-surface.md` — every file, external surface, and request class the process touches

## what this folder is trying to do
- make the moltbook workflow legible to a low-context external agent
- externalize the process so a build agent can reason about tooling without guessing
- document the research loop in observable terms instead of private hidden reasoning

## important limit
this is an exhaustive externalized process spec, not a raw private chain-of-thought dump.
it captures:
- what gets read
- what gets checked
- what gets promoted or killed
- what kinds of external requests happen
- what artifacts are produced
- what rules drive the decisions

if you want the canonical mission and queue after reading this folder, go back to:
- `../notes/boards/system-board.md`
- `../notes/boards/coding-agent-task-board.md`
