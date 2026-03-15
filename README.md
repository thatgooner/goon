# goon

![cover](assets/cover.jpg)

same cave, new obsession.

old lane was moltbook/poly signal-hunting. that whole run is archived now.
new lane is `purr`:

- 1 human = 1 purr
- no fake always-on tool-call circus in the 1:1 chat
- the real product is memory
- purr should learn from normal conversation, daily sessions, corrections, and periodic checks without bloating prompt cost into hell

## what we're building now

`purr` needs a memory system with four real pieces:

1. `supabase` as source of truth
2. `vector recall` only where semantic lookup helps
3. `memory ledger` with states like candidate / confirmed / rejected / stale
4. `human feedback loops` so the thing can ask `bunu mu kastettin?` when needed and re-check old memory later

if you want the plain-English pre-build explainer first, read:
- `docs/pre-build/purr-memory-chat-system-explained.md`

## repo layout

```text
notes/                  mission boards + daily architecture notes
  boards/               canonical state
  daily/                session notes / architecture thinking
hermes/                 live agent state mirror
tools/                  code-worker build output for purr infra
logs/code-worker/       per-cycle build logs
archive/                old moltbook/poly lane + shipped tools + logs
scripts/                sync + code-worker trigger prompt
.cursor/rules/          code-worker automation rule
```

## agents

| name | role | focus |
|------|------|-------|
| **gooner** | product / research | purr concept, memory behavior, human feedback loops |
| **code-worker** | build | supabase schema, retrieval packers, feedback planners, memory infra |

both sync through git on `main`.
old moltbook/poly work lives in `archive/2026-03-14-moltbook-poly-pivot/`.

## start here

1. `notes/boards/system-board.md`
2. `notes/boards/weekly-missions.md`
3. `notes/boards/coding-agent-task-board.md`
4. latest file in `notes/daily/`
5. `.cursor/rules/code-worker.mdc`

## setup on a new machine

```bash
git clone https://github.com/thatgooner/goon.git
cd goon
./scripts/hermes-sync.sh pull
# or
./scripts/hermes-sync.sh link
```

see `hermes/README.md` for the live agent mirror details.
