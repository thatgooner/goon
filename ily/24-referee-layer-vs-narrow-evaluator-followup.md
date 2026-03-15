# Referee layer vs narrow evaluator — follow-up question

## why this note exists

ily/23 gave a strong answer:
- deterministic backbone stays deterministic
- ambiguous/high-leverage decisions can use a narrow structured evaluator
- not a subagent
- Hermes-first dogfood is only partial / backend-validation

That answer is strong.
But there is one follow-up pressure test worth doing before implementation planning:

> what if the memory system itself stays deterministic, but there is still a higher-level **referee layer** above it that occasionally reviews clusters of memory decisions, catches suspicious state transitions, and acts like a strategic quality-control layer?

This is different from "put subagents inside the memory loop."

The proposal to evaluate is:
- core memory loop remains deterministic
- hot-path ambiguity still uses either deterministic fallbacks or a narrow evaluator
- but **outside** the core loop, a slower referee layer could inspect memory events / candidate clusters / correction history / pack quality and say:
  - this promotion looks wrong
  - this memory family keeps oscillating
  - this pack is carrying stale truth
  - this review cadence is too aggressive
  - this proactive candidate keeps landing in creepy territory

So the open question is not:
- should subagents run the memory system?

The open question is:
- is there a useful place for a slower, above-the-system referee/reviewer layer?

---

## the exact thing to pressure-test

Evaluate whether a **referee layer** would be useful if it is:
- outside the deterministic truth spine
- outside the normal hot path
- not required for every turn
- not allowed to directly mutate truth without going through the same mutation contracts
- mostly used for audit, escalation, repair suggestions, and quality-control on difficult clusters

Possible shapes to compare:

### option A — no referee layer
Only deterministic backbone + narrow typed evaluator at the 5 decision points from ily/23.

### option B — referee as periodic auditor
A slower offline reviewer that scans recent memory events / clusters and flags suspicious cases.
No direct authority. Only recommendations / audit logs.

### option C — referee as escalation path
Most cases use the normal system. Hard ambiguous cases can be escalated into a deeper referee pass with stronger reasoning.
Still not on every turn.

### option D — referee as repair worker
Looks for ongoing failure patterns:
- repeated challenge/supersede churn
- unstable pattern promotion/demotion
- stale memories surviving too long in packs
- merge mistakes
- proactive candidates repeatedly vetoed as creepy

Then proposes repair actions through the normal mutation/event system.

---

## what code-worker should answer

### 1. is this concept actually useful?
Direct yes / no / partial.

Not vibes. Explain whether this adds real value beyond the narrow evaluator from ily/23.

### 2. if useful, where should it sit?
Answer clearly:
- offline audit only?
- escalation path only?
- both?
- neither?

### 3. what must it NEVER do?
Examples to evaluate:
- never own source-event append
- never own evidence refs
- never bypass mutation contracts
- never directly write truth outside the ledger event system
- never run every turn
- never become a hidden second brain that competes with the deterministic system

### 4. if it exists, what should trigger it?
Examples:
- repeated contradiction churn on same memory family
- repeated pack suppressions
- repeated evaluator low-confidence outputs
- unstable pattern promotion/demotion
- suspicious merge/separate oscillation
- repeated user corrections on same topic

### 5. what runtime form should it take?
Pressure-test all 3:
- real subagent
- stronger one-shot structured reviewer
- scheduled audit process with typed inputs only

Which one is actually worth it?
Which one is overkill?

### 6. how would we keep it from becoming sludge?
Need a real answer for:
- cost
- latency
- debuggability
- authority boundaries
- logging
- rollback

### 7. does this help Hermes-first dogfood?
Would a referee layer make the Hermes dogfood more useful?
Or would it just muddy the first test and add noise too early?

### 8. build-order impact
Does this create a new future slice?
If yes, where does it belong relative to:
- memory-ledger
- candidate-extractor
- context-packer
- feedback-orchestrator
- review queue

---

## strong boundary

The boundary from ily/23 still stands unless code-worker gives a compelling reason otherwise:
- deterministic backbone is still sacred
- narrow evaluator still beats a general subagent for in-loop decisions
- Hermes dogfood still should not become "turn Hermes into Purr"

So this follow-up should only approve a referee layer if it is clearly:
- higher-level
- slower
- bounded
- inspectable
- non-invasive to the truth spine

---

## what a good answer looks like

A good answer should say something like one of these:
- "No, the narrow evaluator already covers the needed ambiguity; a referee layer adds sludge."
- "Partial yes: only as an offline auditor after build slice 4, never before."
- "Yes, but only as a scheduled typed repair/audit worker with no direct write authority."

A bad answer would be:
- "maybe a subagent can think harder about memory in general"
- "let's just add a second brain"
- anything that makes the memory system harder to replay, inspect, or trust
