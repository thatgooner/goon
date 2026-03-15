# Memory health auditor verdict

## why this note exists

ily/23 locked:
- deterministic backbone: 11 sacred surfaces
- narrow typed evaluator: 5 decision points, cheap model, conservative fallback
- no in-loop subagent

ily/24 asked whether a slower, higher-level referee/audit layer ABOVE the deterministic system could add value.

this note is the pressure test. the answer is not what ily/24 expected.

---

## direct verdict: PARTIAL YES — but not a "referee layer"

the concept is useful. the framing is wrong.

"referee layer" implies a new architectural layer sitting above the memory system. that framing invites scope creep, unclear authority, and a gravitational pull toward "let it think about memory in general."

the right answer is simpler: **add worker H to the existing deferred maintenance lane from note 18.**

note 18 section 3 already defines 7 deferred maintenance workers:
- A. consolidation worker (dedupe, merge evidence)
- B. contradiction resolver (finish ambiguous cases)
- C. review scheduler + queue updater
- D. pack drift scorer
- E. prediction calibration worker
- F. semantic refresh worker
- G. prompt-promotion gate

none of them watch for TEMPORAL PATTERNS across multiple memory events. each handles individual items or individual decisions. that leaves a real gap.

---

## the gap these 7 workers leave open

| failure pattern | why no existing worker catches it |
|----------------|----------------------------------|
| contradiction churn — same dedupe_key challenged/superseded >3× in 2 weeks | contradiction resolver B finishes individual cases but doesn't count recurrence |
| pattern oscillation — same memory promoted then demoted then promoted | prediction calibration E closes horizons individually, doesn't detect cycling |
| repeated user corrections on same topic | correction detector runs per-turn, doesn't aggregate across events |
| evaluator low-confidence cluster — 5 narrow-evaluator calls at <0.4 confidence on same memory family | evaluator falls back conservatively each time; no one notices the cluster |
| stale truth pack leakage — memory with low freshness persists across >3 pack rebuilds | pack drift scorer D checks individual pack freshness, not cross-pack survival patterns |
| proactive veto repeats — same topic cluster aborted by creepiness veto >3× | proactive heartbeat has cooldowns but doesn't permanently suppress a repeatedly-vetoed topic |

these are all detectable with SQL queries against `memory_events` + `memory_items` + `pack_artifacts`. no LLM needed for detection. each is a temporal pattern that individual workers miss because they look at one event or one item at a time.

---

## why this is NOT a new layer

it is a new worker in an existing lane.

| "referee layer" framing (rejected) | deferred maintenance worker H (accepted) |
|------------------------------------|------------------------------------------|
| sits above the memory system | sits inside the deferred maintenance lane alongside workers A-G |
| implies separate authority model | shares the same mutation/event contract as all other workers |
| suggests its own context/reasoning loop | uses typed input from SQL queries, typed output as audit findings |
| sounds like it supervises other workers | it reads the same `memory_events` table everyone writes to |
| implies a new architectural boundary | fits inside the boundary note 18 already defined |

reframing matters because "worker H" inherits all the constraints of the deferred maintenance lane:
- does not block the reply hot path
- proposes through the normal mutation path
- shares scope/evidence/mutation contracts
- inspectable through `memory_events`
- debuggable through ledger queries

"referee layer" inherits none of those constraints by default and would need them all re-defined.

---

## what worker H does

### name: `memory-health-auditor`

### job
detect temporal failure patterns across memory events that single-event workers miss. emit typed audit findings. recommend bounded repair actions that execute through the normal mutation pipeline.

### schedule
not per-turn. not per-message. periodic:
- after every N memory events (e.g., every 50 events)
- or on a time schedule (e.g., every 6-12 hours if there was activity)
- or on explicit trigger when a threshold trips (see trigger section below)

### detection method
primarily deterministic SQL. examples:

```
-- contradiction churn
SELECT dedupe_key, COUNT(*) as churn_count
FROM memory_events
WHERE event_type IN ('challenged', 'superseded')
  AND created_at > now() - interval '14 days'
  AND owner_id = $1 AND purr_id = $2
GROUP BY dedupe_key
HAVING COUNT(*) > 3;
```

```
-- pattern oscillation
SELECT me.memory_id, COUNT(*) as flip_count
FROM memory_events me
WHERE me.event_type IN ('confirmed', 'decayed')
  AND me.created_at > now() - interval '14 days'
  AND me.owner_id = $1
GROUP BY me.memory_id
HAVING COUNT(*) > 4;
```

```
-- stale truth in packs
SELECT mi.memory_id, COUNT(DISTINCT pa.pack_id) as pack_appearances
FROM memory_items mi
JOIN pack_artifacts pa ON pa.artifact_json::jsonb @> ...
WHERE mi.freshness_score < $threshold
  AND mi.owner_id = $1
GROUP BY mi.memory_id
HAVING COUNT(DISTINCT pa.pack_id) > 3;
```

most detection requires zero LLM calls. only genuinely ambiguous multi-event interpretation (rare) might use a cheap model call following the same narrow-evaluator pattern from ily/23.

### output format
typed `audit_finding` structs:

```
audit_finding:
  finding_id: uuid
  owner_id: uuid
  purr_id: uuid
  finding_type: contradiction_churn | pattern_oscillation | correction_cluster |
                evaluator_uncertainty | stale_pack_leak | proactive_veto_cluster
  severity: low | medium | high
  affected_memory_ids: uuid[]
  evidence_event_ids: uuid[]
  window: time range the pattern was detected over
  recommendation: enum (see below)
  detail_json: supporting data
  created_at: timestamp
```

### recommendations the auditor can emit

| recommendation | what it does | authority |
|---------------|-------------|-----------|
| `raise_cooldown` | increase cooldown on affected dedupe scope | feeds into review scheduler (worker C) |
| `suppress_proactive_topic` | block proactive candidate generation for a topic cluster | feeds into proactive preflight gate |
| `force_pack_rebuild` | flag that affected packs should rebuild instead of reuse | feeds into pack drift scorer (worker D) |
| `lower_confidence_floor` | raise the threshold for pattern promotion on oscillating items | feeds into prediction calibration (worker E) |
| `flag_for_human_review` | mark a memory cluster as needing human attention on next natural opportunity | feeds into review scheduler (worker C) via queue priority boost |
| `request_contradiction_rerun` | re-run contradiction resolver on a specific dedupe scope | triggers worker B |

**critical: every recommendation feeds into an existing worker or queue. the auditor does not execute repairs itself.**

---

## what it must NEVER do

| forbidden | why |
|-----------|-----|
| source-event append | that belongs to the intake pipeline. the auditor reads events, never creates source events. |
| evidence ref creation | that belongs to the extractor. the auditor reads evidence, never creates it. |
| direct truth writes | all memory_item mutations go through the normal mutation pipeline. the auditor recommends, workers execute. |
| per-turn running | that's the hot path. the auditor is a periodic batch process. |
| blocking the reply path | deferred lane rule: never block the current reply. |
| accessing raw conversation text | the auditor works on memory_events, memory_items, and pack_artifacts. it never touches message content directly. structured metadata only. |
| hidden second brain | it does not maintain its own memory state, its own context window, or its own model of the user. it reads the ledger everyone shares. |
| overriding evaluator decisions retroactively | evaluator decisions are committed. the auditor can recommend future threshold changes, not undo past decisions. |
| bypassing mutation contracts | if a finding needs a state change, that change goes through the same transaction/idempotency/evidence path as any other mutation. |

---

## trigger conditions

### trigger 1 — contradiction churn
- signal: >3 challenge/supersede events on the same `dedupe_key` within a 14-day window
- detection: SQL count on `memory_events`
- severity: medium (high if the memory kind is boundary/safety)

### trigger 2 — evaluator low-confidence cluster
- signal: >3 narrow-evaluator calls with confidence < 0.4 on the same memory family within a window
- detection: SQL query on `memory_events` where `actor_type = judge_evaluator` and `delta_json->confidence < 0.4`
- severity: medium

### trigger 3 — pattern oscillation
- signal: >2 promote/demote cycles on the same `memory_id` within a 14-day window
- detection: SQL alternation check on event_type sequence
- severity: low (medium if the pattern drives proactive behavior)

### trigger 4 — repeated user corrections on same topic
- signal: >2 explicit corrections touching the same `subject_key` within a window
- detection: SQL count on `memory_events` where `actor_type = human_confirmation` or `event_type IN (challenged, superseded)` with matching subject_key
- severity: high (this means the system keeps getting it wrong)

### trigger 5 — stale truth pack leakage
- signal: memory with `freshness_score` below threshold appearing in `pack_artifacts` across >3 consecutive pack generations
- detection: SQL join across `pack_artifacts` and `memory_items`
- severity: medium

### trigger 6 — proactive veto repeats
- signal: >3 `abort` outcomes from the proactive creepiness evaluator on the same topic cluster
- detection: SQL count on evaluator events with proactive veto decision points
- severity: medium (high if the topic is sensitive)

all triggers are SQL-first. no LLM needed for detection. LLM only if the pattern is detected but the interpretation is genuinely ambiguous (should be rare — most patterns have obvious remedies).

---

## is a true subagent useful here?

**no.**

| criterion | subagent | typed audit process |
|-----------|----------|---------------------|
| needs its own context window | yes — that's what makes it a subagent | no — reads typed structs from SQL |
| needs its own conversation loop | yes — multi-turn reasoning | no — one-shot detection + recommendation |
| cost per run | high — full LLM turn with system prompt + context | low — SQL queries + maybe a cheap LLM call for ambiguous interpretation |
| debug surface | trace entire agent run | inspect typed findings in `memory_events` or audit log |
| authority model | tempting to give it write access | explicitly constrained to recommendations only |
| scope creep risk | high — "let the subagent think about memory quality" | low — typed triggers with explicit thresholds |
| failure mode | becomes a hidden second brain that disagrees with the deterministic system | fails safe — if auditor misses a pattern, the system continues with its existing workers |

the "strong one-shot structured reviewer" option from ily/24 is closer but still wrong. "one-shot" implies it runs once and produces a verdict. the auditor runs periodically and produces incremental findings. the right abstraction is a scheduled typed audit process, not a reviewer.

---

## how to prevent it from becoming sludge

### cost
- detection is SQL. near-zero marginal cost.
- LLM calls only for ambiguous interpretation. budget: max 2-3 cheap-model calls per audit run. if more patterns need interpretation, batch them.
- total cost per audit run should be <$0.01 at gemini-flash rates.

### latency
- irrelevant. the auditor runs in the deferred lane, never on the hot path. it can take minutes.

### debuggability
- every `audit_finding` is a typed struct logged to a table or `memory_events` with `actor_type = health_auditor`.
- findings include the evidence event IDs that triggered them.
- recommendations include which worker they feed into.
- full replay: re-run the SQL queries on the same event window, get the same findings.

### authority boundaries
- **reads:** `memory_events`, `memory_items`, `memory_evidence_refs`, `pack_artifacts`
- **writes:** `audit_finding` structs (new table or typed `memory_event`)
- **recommends to:** workers B, C, D, E, proactive preflight gate
- **never writes to:** `memory_items`, `message_events`, `memory_evidence_refs`

### rollback
- if a recommendation was wrong (e.g., raised cooldown too aggressively), the affected worker can lower it on the next normal cycle.
- auditor recommendations are soft — they adjust thresholds and priorities, not truth.
- worst case: a bad recommendation causes a memory to cool down longer than needed. that's annoying, not catastrophic. compare to: a subagent writing bad truth directly, which IS catastrophic.

---

## does this help Hermes dogfood?

### short answer: AFTER, not before.

### reasoning

| dogfood phase | auditor useful? | why |
|---------------|----------------|-----|
| phase 0 (shadow ledger) | no | not enough events to detect temporal patterns. auditor needs weeks of data. |
| phase 1 (pack compare) | no | still accumulating. auditor would produce noise on sparse data. |
| phase 2 (correction override) | maybe | if correction events accumulate fast enough, trigger 4 could fire. but probably too few events in this phase. |
| phase 3 (review + proactive scoring) | yes | by this point there should be enough memory events for pattern detection. the auditor can validate its own trigger logic on real data. |

**the auditor should not be built before dogfood phases 0-2.** it would add complexity with no data to audit. build it after the feedback-orchestrator ships and enough real events accumulate.

during late dogfood (phase 3+), the auditor can run against the shadow ledger data as a validation exercise: "would the auditor have caught the quality problems we observed manually?"

---

## build-order impact

### existing build order: UNCHANGED

```
slice 1: memory-ledger
slice 2: memory-candidate-extractor
slice 3: memory-context-packer
slice 4: feedback-orchestrator
```

### new future parked slice

```
slice 5 (parked): memory-health-auditor
```

position: after feedback-orchestrator (slice 4), before review-queue refinement and social graph.

reasoning:
- depends on working ledger (slice 1) for `memory_items` and `memory_events` tables
- depends on extractor (slice 2) generating events to audit
- depends on packer (slice 3) generating `pack_artifacts` to check for stale leakage
- depends on feedback-orchestrator (slice 4) generating review outcomes and trust transitions

related to review-queue but distinct:
- review queue manages individual memory verification decisions (which memories to ask about, when, how)
- health auditor detects system-level failure patterns across many events
- they share the review scheduler as a downstream consumer but serve different purposes

---

## option comparison

| option | verdict | reasoning |
|--------|---------|-----------|
| A — no referee | rejected | the gap is real. existing workers A-G handle individual items; nobody watches for temporal patterns across events. |
| B — offline auditor (audit log only, no authority) | rejected alone | detection without action is a dashboard. someone still needs to act on findings. |
| C — escalation path | rejected | escalation needs a receiver. in v1 there's no meaningful receiver except the system itself. |
| D — repair worker | rejected alone | "repair" implies direct write authority, which the auditor must not have. |
| **B+D hybrid — offline auditor with bounded repair recommendations** | **accepted** | detects patterns (B), recommends bounded actions that execute through existing workers (D), never writes truth directly. |

the accepted form is: **worker H in the deferred maintenance lane.** scheduled typed audit process. SQL-first detection. typed findings. recommendations feed into existing workers. no direct truth authority.

---

## ily/23 boundary check

does this note break any ily/23 decisions?

| ily/23 decision | preserved? | how |
|-----------------|-----------|-----|
| deterministic backbone is sacred | yes | auditor reads events, never touches the 11 deterministic surfaces |
| no in-loop subagent | yes | auditor is a deferred batch process, not in-loop |
| narrow typed evaluator for 5 decision points | yes | auditor is a different thing — it watches patterns across events, not individual ambiguous decisions |
| conservative fallback on evaluator failure | yes | auditor failure = no findings emitted. system continues as before. |
| Hermes dogfood is shadow observation only | yes | auditor runs on the Purr ledger, never touches Hermes |

**no ily/23 decisions are changed or weakened.**

---

## summary table

| question | answer |
|----------|--------|
| is the concept useful? | PARTIAL YES — the gap is real, but the framing is wrong |
| correct framing | not "referee layer" — it's worker H in the deferred maintenance lane |
| runtime form | scheduled typed audit process. SQL-first. not a subagent. not a one-shot reviewer. |
| true subagent useful? | no. overkill. high cost, scope creep risk, unclear authority. |
| what it must never do | source-event append, evidence refs, direct truth writes, per-turn running, hidden second brain |
| triggers | 6 typed: contradiction churn, evaluator uncertainty, pattern oscillation, repeated corrections, stale pack leak, proactive veto repeats |
| helps Hermes dogfood? | after phase 3, not before. would add noise during early phases. |
| build order impact | new parked slice 5, after feedback-orchestrator. does not change slices 1-4. |
| ily/23 broken? | no. all 5 decisions preserved. |
