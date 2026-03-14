# coding-agent task board

MISSION CHANGE — READ THIS FIRST:
- old moltbook/poly lane is archived under `archive/2026-03-14-moltbook-poly-pivot/`
- active mission is now `purr` memory infrastructure
- if you are code-worker, do NOT keep building old classifiers unless the user explicitly reopens that lane

read `weekly-missions.md` first. every task here must serve an active weekly mission.

priority model:
- high = directly serves this week's missions, has full spec, ready to build
- parked = valid later work, not for this week

## task spec quality rules

every buildable task must have:
- `sample_inputs:` at least 2-3 concrete examples
- `input_format:` what the tool receives
- `output_format:` what the tool returns
- `testable_acceptance:` criteria code-worker can verify independently

status values: `queued` | `in_progress` | `done` | `blocked`
when code-worker picks a task: set status to `in_progress`, add `picked_cycle: YYYY-MM-DD-HH`

---

## high — build this week

### memory-ledger
- mission: M1 (memory source of truth)
- why: purr needs a canonical memory object with lifecycle state, evidence refs, and review scheduling. this is the spine.
- sample_inputs:
  - candidate memory: `{"event_type":"candidate","payload":{"owner_id":"u1","kind":"preference","summary":"user likes colder phrasing","confidence":0.82,"evidence_refs":["session:s1:msg:4"]}}`
  - correction: `{"event_type":"feedback","payload":{"memory_id":"m1","feedback":"reject","reason":"user said this is wrong"}}`
  - review result: `{"event_type":"review_result","payload":{"memory_id":"m1","result":"confirmed","checked_at":"2026-03-14T10:00:00Z"}}`
- input_format: `{ "event_type": "candidate"|"feedback"|"review_result", "payload": dict }`
- output_format: `{ "memory_id": str, "owner_id": str, "kind": "profile"|"preference"|"fact"|"episode"|"social"|"uncertainty", "state": "candidate"|"confirmed"|"rejected"|"stale", "summary": str, "confidence": float, "evidence_refs": [str], "needs_review_at": str | null }`
- testable_acceptance: candidate create must work. feedback reject must move state to `rejected`. review confirm must move state to `confirmed` and schedule next review. ship Supabase-ready SQL schema/migrations in the tool directory.
- status: queued
- owner: code-worker
- pick order: 1

### memory-candidate-extractor
- mission: M1 + M3
- why: purr should learn from normal chat, but only structured memory candidates should survive.
- sample_inputs:
  - explicit preference: `[{"role":"user","content":"kisa cevap ver"}]`
  - correction: `[{"role":"user","content":"hayir ben bunu demedim, daha soguk olsun"}]`
  - fluff: `[{"role":"user","content":"haha iyiymis"}]`
- input_format: `{ "messages": [{"role": str, "content": str}], "session_id": str }`
- output_format: `{ "candidates": [{"kind": str, "summary": str, "confidence": float, "reason": str, "needs_confirmation": bool, "evidence_refs": [str]}] }`
- testable_acceptance: explicit preferences/corrections must produce candidates. generic fluff must produce none. ambiguous statements must set `needs_confirmation=true`.
- status: queued
- owner: code-worker
- pick order: 2

### memory-context-packer
- mission: M2 (retrieval + prompt budget)
- why: the model needs the right memory, not all memory.
- sample_inputs:
  - query about tone with 20 mixed memory items and budget 700 chars
  - query about a recent topic with old confirmed profile memories plus fresh episode memories
  - duplicate preference memories that should collapse into one line
- input_format: `{ "query": str, "memory_items": [dict], "budget_chars": int, "session_context": {"owner_id": str, "purr_id": str | null} }`
- output_format: `{ "selected": [dict], "packed_text": str, "used_chars": int, "dropped_ids": [str] }`
- testable_acceptance: must stay under budget. confirmed relevant preferences must outrank stale episodes. duplicate memories must collapse. output must be deterministic for the same input.
- status: queued
- owner: code-worker
- pick order: 3

### feedback-orchestrator
- mission: M3 (human feedback loops)
- why: purr needs a policy for when to ask `bunu mu kastettin?` and when to chill.
- sample_inputs:
  - high-confidence correction with direct conflict to existing confirmed memory
  - low-confidence ambiguous candidate during a fast back-and-forth chat
  - minor preference candidate right after two recent clarification prompts
- input_format: `{ "candidate": dict, "conversation_state": {"turns_since_last_check": int, "recent_checks": int, "message_velocity": "low"|"mid"|"high"}, "existing_memory": [dict] }`
- output_format: `{ "action": "ask_now"|"defer"|"store_silent"|"drop", "prompt": str | null, "reason": str }`
- testable_acceptance: direct contradictions to confirmed memory must prefer `ask_now` or `defer`, not silent-store. low-signal candidates during high-velocity chat must avoid interrupting. repeated recent checks must reduce ask frequency.
- status: queued
- owner: code-worker
- pick order: 4

### memory-review-queue
- mission: M3 + M2
- why: memory rots unless some of it gets rechecked.
- sample_inputs:
  - a confirmed preference last checked 90 days ago
  - a rejected memory from yesterday
  - an uncertainty memory never confirmed but referenced often
- input_format: `{ "memory_items": [dict], "now": str, "daily_check_cap": int }`
- output_format: `{ "queue": [{"memory_id": str, "priority": float, "reason": str, "suggested_prompt": str}], "skipped": [str] }`
- testable_acceptance: stale confirmed items and high-use uncertainty items should enter the queue. fresh rejected items should stay out. queue length must respect the cap.
- status: queued
- owner: code-worker
- pick order: 5

---

## parked — later

### social-memory-graph
- mission: future catnet work
- why parked: first ship the single-purr memory spine
- status: parked

### multimodal-memory-ingest
- mission: future
- why parked: text loop first, images/audio later
- status: parked

### purr-world-sim
- mission: future social simulation
- why parked: do not build the city before memory works
- status: parked
