# AGENTS.md

read this first.

## what this repo is now

this repo pivoted.

old mission:
- moltbook noise filtering
- polymarket/operator research
- copytrading signal hunts

new mission:
- build the memory spine for `purr`
- `1 human = 1 purr`
- purr learns from normal conversation and daily sessions
- purr can ask for clarification or memory confirmation when needed
- prompt cost stays controlled because retrieval is selective, not dumb full-history stuffing

old lane is archived in `archive/2026-03-14-moltbook-poly-pivot/`.
do not resurrect it unless the user explicitly asks.

## who works here

| agent | role | what they do |
|-------|------|-------------|
| **gooner** | product / research | defines purr behavior, collects examples, decides what memory should exist, rejects corny ideas |
| **code-worker** | build | Cursor cloud agent on 1-hour cron. reads the boards, ships memory infra, logs every cycle |

both agents sync through git on `main`.

## repo structure

```text
AGENTS.md
README.md
notes/
  README.md
  boards/
    system-board.md
    weekly-missions.md
    coding-agent-task-board.md
  daily/
    purr-memory-YYYY-MM-DD.md
    .template.md
hermes/
tools/
logs/
  code-worker/
archive/
  2026-03-14-moltbook-poly-pivot/
scripts/
  code-worker-prompt.md
.cursor/
  rules/code-worker.mdc
```

## how to get up to speed fast

1. read `notes/boards/system-board.md`
2. read `notes/boards/weekly-missions.md`
3. read `notes/boards/coding-agent-task-board.md`
4. read the latest file in `notes/daily/`
5. skim `hermes/memories/MEMORY.md` and `hermes/memories/USER.md`

## key product truths

- purr is not a generic assistant wrapper
- 1:1 chat should feel clean; tool-call theater is not the hook
- the real moat is memory quality + retrieval discipline
- supabase is the system of record
- vector search is support infra, not the whole product
- every memory item needs lifecycle state: candidate, confirmed, rejected, stale
- human feedback is required: inline clarification, explicit correction capture, later verification checks
- prompt budget matters. do not dump raw memory into every prompt

## if you are code-worker

your job is in `notes/boards/coding-agent-task-board.md`.

rules:
1. `git pull origin main`
2. read `weekly-missions.md`
3. read `coding-agent-task-board.md`
4. pick the highest-priority `queued` task
5. build in `tools/<task-name>/`
6. include README + code + tests + any SQL/schema files needed
7. log the cycle in `logs/code-worker/YYYY-MM-DD-HH.md`
8. commit with `build:` or `tools:` and push

constraints:
- do not touch archived moltbook/poly material except to reference it
- do not write to `hermes/memories/`
- prefer deterministic infra over hand-wavy architecture docs
- if a task needs Supabase, you can still ship SQL migrations, local test fixtures, typed contracts, and docs without live credentials

## if you are gooner

use `notes/daily/` for raw product thinking:
- what purr should remember
- what it should forget
- where clarification should happen
- what annoyed the user
- what memory checks felt spammy vs useful

promote reusable conclusions to boards. keep loose vibes in daily notes.

## file ownership

- gooner owns: `notes/daily/`, `hermes/memories/`
- code-worker owns: `tools/`, `logs/code-worker/`
- shared: `notes/boards/coding-agent-task-board.md`
- user-owned direction docs: `notes/boards/system-board.md`, `notes/boards/weekly-missions.md`, this file

## hard rule

if something makes purr feel like a dashboard with fur, it's probably wrong.
we want living memory, not admin panel sludge.
