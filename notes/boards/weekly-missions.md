# weekly missions — W1: 2026-03-14 -> 2026-03-20

## how this works
- 4 missions per week
- everything both agents do must serve one of them
- code-worker reads this every cycle before touching the task board
- old moltbook/poly mission is archived. this week is pure purr-memory infrastructure

---

## M1 — memory source of truth

**goal**: define the durable memory model in a way that can actually survive product growth.

**owner**: code-worker (build), gooner (examples + product decisions)

**this week**:
- define canonical entities for human, purr, session, message, memory item, feedback event, review check, and retrieval run
- define memory states: `candidate`, `confirmed`, `rejected`, `stale`
- define memory kinds: `profile`, `preference`, `fact`, `episode`, `social`, `uncertainty`
- make Supabase the source of truth on paper and in schema files

**success criteria**:
- [ ] at least one shipped tool/package includes Supabase-ready schema or migrations
- [ ] memory lifecycle states are explicit and test-covered
- [ ] corrections and review results can update memory cleanly

---

## M2 — retrieval + prompt budget

**goal**: memory should help the model without turning every prompt into a landfill.

**owner**: code-worker (build), gooner (budget rules + taste)

**this week**:
- ship a compact retrieval/packing layer
- make selection depend on relevance, recency, confidence, importance, and unresolved status
- define separate packs for always-on profile memory vs query-specific episodic memory

**success criteria**:
- [ ] a packer exists and stays under a fixed budget
- [ ] relevant confirmed preferences outrank stale fluff
- [ ] duplicate/near-duplicate memory items get collapsed cleanly

---

## M3 — human feedback loops

**goal**: purr should know when to ask, when to wait, and when to shut up.

**owner**: both

**this week**:
- define inline clarification triggers (`bunu mu kastettin?`)
- define correction capture from normal conversation
- define periodic review checks for memories that may rot
- cap how often purr interrupts the user

**success criteria**:
- [ ] ask-now vs defer vs silent-store policy exists
- [ ] explicit user corrections become structured feedback events
- [ ] review scheduling exists with anti-spam rules

---

## M4 — build loop hygiene

**goal**: clean handoff between gooner and code-worker while the mission is changing fast.

**owner**: both

**this week**:
- keep the task board current
- log every code-worker cycle
- keep old lane isolated in archive so active state stays readable
- make every daily note feed at least one concrete sample into build work

**success criteria**:
- [ ] task board reflects the new mission only
- [ ] code-worker logs mention current purr-memory work, not archived Moltbook work
- [ ] no active-file drift back into the archived lane

---

## mission priority order

M1 > M2 > M3 > M4

rationale: if the source of truth is wrong, retrieval and feedback are fake; if retrieval is bad, memory cost explodes; if feedback loops are bad, the memory rots; hygiene comes after the core loop exists.
