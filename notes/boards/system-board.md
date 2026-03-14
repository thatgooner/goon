# system board

## what this system is for
- build the memory spine for `purr`
- make `1 human = 1 purr` feel real through continuity, not gimmicks
- learn from normal chat, daily sessions, corrections, and review checks
- keep prompt cost under control with selective retrieval
- produce enough shared state that any low-context build agent can continue the work

## canonical folders
- `notes/boards/` = canonical state
- `notes/daily/` = raw architecture / product notes
- `tools/` = code-worker build output
- `archive/2026-03-14-moltbook-poly-pivot/` = old lane, frozen unless user says otherwise

## canonical files
- `notes/boards/system-board.md` = mission + priorities + routing rules
- `notes/boards/weekly-missions.md` = this week's concrete missions
- `notes/boards/coding-agent-task-board.md` = build queue for code-worker
- `notes/daily/purr-memory-YYYY-MM-DD.md` = raw session/product thinking for that day

## current mission
- purr needs strong memory before anything else
- supabase should hold the durable source-of-truth state
- vector retrieval should help semantic recall, not become an excuse for lazy prompt stuffing
- memory items need lifecycle and confidence, not just raw notes
- the system must know when to ask the human `is this what you meant?`
- the system must know when to revisit old memory and confirm it still holds

## current priorities
### high
- define the canonical memory model
- define memory lifecycle states and feedback paths
- keep retrieval compact and cheap
- capture explicit user corrections cleanly
- make memory verification feel useful, not needy

### mid
- shape daily/session note format so code-worker gets better examples
- tune thresholds for when to ask now vs later vs never
- define social/episode memory lanes for future catnet behavior

### low
- UI/dashboard thinking
- social simulation details
- growth/distribution ideas

## routing rules
- raw product idea -> today's daily note
- durable architecture truth -> system board
- build spec / tool / schema work -> coding-agent task board
- old moltbook/poly reference -> archive only
- if a memory idea would increase prompt cost without clear recall value, kill it

## mission tests
before promoting anything, ask:
- does this improve what purr remembers?
- does this improve when purr asks for confirmation?
- does this improve prompt efficiency or retrieval precision?
- does this define memory state, confidence, or decay more clearly?
- does this help code-worker ship real infra instead of vibes?

## dead thread rule
kill a thread when it produces:
- no schema change
- no retrieval gain
- no feedback-loop insight
- no concrete build task

## known truths right now
- hermes-style flat memory is not enough on its own
- purr needs layered memory: profile, preference, episode, social, uncertainty
- confirmation and correction are part of the product, not edge cases
- silent accumulation without verification will rot
- full memory dumps into the prompt will get too expensive too fast

## operational rules
### mission gates
- every build/research pass must name which weekly mission it serves
- if a pass doesn't clearly help an active mission, don't start it

### zero-gain rule
- if a pass changes nothing in schema, retrieval, feedback design, or task clarity, it's a zero-gain pass
- 3 zero-gain passes in a row = hard pivot or user escalation

### tool adoption protocol
- when code-worker ships a tool, gooner should try it in the next relevant architecture pass
- if not used, explain why in the daily note

### sync protocol
- gooner and code-worker coordinate through git on `main`
- gooner pulls before push
- file ownership:
  - gooner owns: `notes/daily/`, `hermes/memories/`
  - code-worker owns: `tools/`, `logs/code-worker/`
  - shared: `notes/boards/coding-agent-task-board.md`
- commit prefixes: gooner uses `notes:` or `research:`, code-worker uses `build:` or `tools:`

## active files
- weekly missions: [weekly-missions.md](weekly-missions.md)
- tasks: [coding-agent-task-board.md](coding-agent-task-board.md)
- daily note: [purr-memory-2026-03-14.md](../daily/purr-memory-2026-03-14.md)
- archive: [../../archive/2026-03-14-moltbook-poly-pivot/](../../archive/2026-03-14-moltbook-poly-pivot/)
