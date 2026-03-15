# Hermes dogfood + judge layer verdict

## why this note exists

ily/22 posed two open questions before the first build slice:
1. should ambiguous memory updates use a judge layer on top of the deterministic backbone?
2. should the Purr memory backend be dogfooded inside Hermes first?

this note is the code-worker pressure test. not rubber-stamp.

---

## verdict 1 — deterministic backbone vs judge layer

### what MUST stay deterministic — no exceptions

these are the contract surfaces where agentic judgment would introduce nondeterminism into the truth spine. breaking determinism here breaks auditability, replay safety, and builder trust.

| surface | why deterministic | source contract |
|---------|-------------------|-----------------|
| source-event append | raw event must exist before anything references it. no reasoning needed. | note 14 rule 1 |
| evidence backpointers | immutable refs to exact message/span. factual linkage, not judgment. | note 13 invariant 3, 4 |
| mutation transaction atomicity | challenge/supersede/confirm must happen in one transaction. partial commits create impossible truth. | note 13 invariant 10 |
| idempotency keys + replay safety | duplicate source events, evidence, and mutation intents must no-op. this is structural, not interpretive. | note 14 section 6 |
| identity scope enforcement | `owner_id` + `purr_id` on every row. no judgment call about who owns what. | note 13 invariant 1 |
| active-truth uniqueness constraints | one active truth per exclusive dedupe scope. partial unique index, not a reasoning call. | note 13 invariant 6 |
| challenged/superseded suppression from hot pack | if `contradiction_status=challenged` or `state in (rejected, superseded)`, suppress from `pack_candidate_view`. rule, not taste. | note 13 invariant 7 |
| hard pack budget caps + slot limits | token budgets and slot caps are arithmetic. session_pack 500-800/1000, delta 30-120/180, etc. no reasoning needed. | note 09, note 13 |
| session window lifecycle | open/close/child creation follows explicit triggers and ordering. | note 16, note 18 |
| trust decay arithmetic | freshness decay formulas, cooldown durations, attempt count increments. numbers, not vibes. | note 20 section 6 |
| review queue status transitions | `queued → due → presented → cooling_down → resolved` is a state machine. execution flow, not judgment. | note 20 section 8 |

**hard rule: none of these surfaces should ever call an LLM or depend on model output. if they do, the system is broken.**

### what CAN use a judge evaluator

these are the decision points where deterministic rules produce ambiguity and a narrow reasoning call can upgrade the decision.

**decision point 1 — contradiction interpretation**

when: deterministic rules flag a potential contradiction (same dedupe scope, different payload value). if the evidence is clean (explicit correction language like "no, actually X"), deterministic supersede handles it. if ambiguous (could be joke, exception, context-dependent), the evaluator fires.

typed input:
- `old_memory_id`, `old_payload_summary`, `old_evidence_excerpts[]`
- `new_candidate_payload`, `new_evidence_excerpts[]`
- `speaker_context` (recent messages around the contradiction)
- `memory_kind`, `durability_scope`

typed output:
- `action`: `supersede | challenge | keep_both_different_scope | drop_new`
- `confidence`: float
- `reasoning_hash`: short deterministic summary

**decision point 2 — pattern promotion / demotion**

when: hit/miss/null counts reach a borderline threshold where deterministic rules cannot cleanly promote or demote. most promotions and demotions will be automatic (strong signal). the evaluator handles edge cases.

typed input:
- `memory_id`, `kind`, `hit_count`, `miss_count`, `null_count`
- `recent_evidence_quality`, `time_since_last_hit`
- `competing_pattern_ids[]` if any

typed output:
- `action`: `promote | hold | demote | merge_with`
- `confidence`: float

**decision point 3 — review timing taste**

when: a memory is `due` for review and the review scheduler needs to decide which surface to use. deterministic rules handle most cases (passive_only for low-leverage, inline_blocking for high-leverage contradictions). the evaluator handles ambiguous cases where intrusion risk vs value is unclear.

typed input:
- `memory_id`, `kind`, `leverage_score`, `last_outcome`
- `current_session_state` (topic, intensity, recent_checks_count)
- `user_signal_history` (recent not_now, avoid_topic events)

typed output:
- `surface`: `passive_only | inline_trailing | later_in_chat | proactive_ping | suppress`
- `confidence`: float

**decision point 4 — proactive creepiness veto**

when: `should_text_first?` preflight passes deterministic gates but the content involves sensitive or private inference. the evaluator decides whether to proceed, soften, or abort.

typed input:
- `proactive_candidate_summary`
- `driving_memory_ids[]`, `driving_evidence_quality`
- `user_burden_state`, `cooldown_state`
- `sensitivity_flags`

typed output:
- `action`: `proceed | soften | abort`
- `intrusion_risk`: float

**decision point 5 — merge/dedup ambiguity**

when: two memory candidates have similar but not identical `dedupe_key` or `subject_key`. deterministic rules can't resolve whether they're the same memory or genuinely different.

typed input:
- `candidate_a_summary`, `candidate_b_summary`
- `dedupe_key_similarity`, `payload_overlap`
- `scope_match`: bool

typed output:
- `action`: `merge | keep_separate`
- `confidence`: float

### what form the judge takes

**NOT a subagent.** subagents need their own context window, prompt, tool access. too heavy for narrow decisions. cost per call is a full LLM turn. debug requires tracing an entire agent run.

**NOT a general "reasoning call."** open-ended "think about whether this memory should be updated" produces unpredictable output shapes, resists structured logging, and invites scope creep.

**YES: narrow structured evaluator.**

properties:
- takes TYPED input struct (specific to the decision point, never raw conversation)
- returns TYPED output struct (decision enum + confidence + summary)
- uses a CHEAP model (not the main conversation model). gemini flash or equivalent.
- fires ONLY at the 5 decision points above, not as a general "think harder" layer
- has explicit input/output JSON schemas that can be logged and replayed
- default timeout: 2-3 seconds. if it fails or times out, fall back to conservative deterministic default

**fallback rule:** on evaluator failure, the system ALWAYS falls back to the conservative deterministic path:
- contradiction → challenge (don't supersede)
- pattern → hold (don't promote)
- review timing → defer (don't ask now)
- proactive → abort (don't text first)
- merge → keep_separate (don't merge)

this means the evaluator only UPGRADES decisions when confident. it never downgrades from a safe default.

### where in the runtime the evaluator sits

- **NOT on the turn-critical hot path by default.** most turn-critical work (source-event append, correction detection, mutation commit) is deterministic. the evaluator fires in deferred maintenance or boundary-critical lanes for most cases.
- **exception: contradiction interpretation** may fire inline if the contradiction is same-turn and affects next-reply correctness. but even here, the fallback (challenge + suppress) is safe without the evaluator.
- **proactive creepiness veto** fires in the proactive heartbeat lane, never on the reply hot path.
- **pattern promotion** and **merge/dedup** fire in deferred maintenance.
- **review timing** fires when the review scheduler runs, which is deferred or proactive.

### debuggability

every evaluator call produces a `memory_event` (or equivalent typed artifact):
- `actor_type = judge_evaluator`
- `event_reason` = decision point name
- `delta_json` = full typed input + full typed output
- model identifier + call latency logged
- total evaluator calls per cycle tracked for cost monitoring

no separate debug UI needed. all inspection goes through ledger queries on `memory_events`.

---

## verdict 2 — Hermes-first dogfood

### direct answer: PARTIAL

not full yes. not no.

### why not full yes

1. **conversation pattern mismatch.** Hermes is a coding/task agent. Purr is a 1:1 companion. memory quality signals that matter in relationship continuity (tone drift, emotional texture, open loops about personal topics) are rare in a coding assistant's conversation stream. the dogfood validates plumbing, not taste.

2. **risk of scope creep.** "just test the memory backend in Hermes" has a gravitational pull toward "make Hermes use the memory backend" which becomes "make Hermes behave more like Purr." every phase boundary must be a hard wall against this.

3. **Hermes' existing memory system is deeply integrated.** MEMORY.md + USER.md + frozen prompt snapshot + nudge intervals + flush-before-compression. replacing any of this means changing Hermes' behavior, which violates the boundary.

### why not no

1. **real events beat synthetic fixtures.** the ledger, extractor, and mutation pipeline all need real conversation data to validate. synthetic test fixtures test the happy path. real data tests the messy path.

2. **shadow approach keeps the boundary clean.** the Purr pipeline observes Hermes' message stream without participating in Hermes' behavior. Hermes never knows the Purr backend exists.

3. **correction/contradiction patterns exist in real conversations** and are the hardest signals to test synthetically. when Ilyas corrects Hermes, that's a real test of the challenge/supersede pipeline.

4. **early failure detection.** finding out the ledger schema doesn't handle real conversation shapes is cheaper now than after building the full Purr product layer on top.

### what the dogfood validates vs what it cannot validate

| validates (plumbing) | does NOT validate (taste) |
|----------------------|--------------------------|
| ledger write integrity | which memories matter in a companion context |
| evidence ref correctness | review cadence that feels right for Purr |
| mutation pipeline safety | proactive timing that lands for a relationship |
| idempotency under real replay | tone/voice that matches Purr's alien-cat personality |
| pack generation mechanics | social/emotional memory quality |
| contradiction detection on real language | creature behavior polish |

taste validation MUST happen on Purr itself. dogfood only tests the backend spine.

---

## phased rollout

### phase 0 — shadow ledger

**scope:**
- stand up Supabase schema per note 13
- tap Hermes' Telegram message flow as read-only source events (after each turn, log the user message + assistant response to the Purr ledger as `message_events`)
- run candidate extractor on these events → write `memory_items` + `memory_evidence_refs`
- Hermes continues using its own MEMORY.md/USER.md unchanged
- no behavior change in Hermes

**implementation:**
- small adapter that reads Hermes' SessionDB messages and writes to Purr's Supabase ledger
- extractor runs async/post-turn, never on Hermes' hot path
- adapter is a separate process or cron, not embedded in Hermes' runtime

**duration:** until ledger has ~100+ memory_items with clean evidence chains

**success signals:**
- meaningful structured memories accumulate (not junk)
- evidence refs point to real messages with correct spans
- no duplicate candidates from retry/replay
- identity scope is clean (all rows carry owner_id + purr_id)
- extractor output matches the typed kinds from note 12

**kill signals:**
- extraction is garbage on real data (>50% of candidates are meaningless)
- tap architecture requires changes to Hermes' internals
- latency on Hermes chat increases measurably
- adapter maintenance exceeds 2 hours/week

### phase 1 — read-only pack compare

**scope:**
- generate `session_pack` artifacts from the Purr ledger for each conversation window
- compare these packs side-by-side with what Hermes actually injected (its frozen MEMORY.md/USER.md snapshot)
- log diffs: what Purr would have surfaced vs what Hermes did surface
- still no behavior change in Hermes

**depends on:** phase 0 having ~100+ clean memory items

**duration:** 1-2 weeks of active comparison

**success signals:**
- Purr packs are tighter and more evidence-backed than Hermes' flat memory blocks
- Purr packs stay within budget constraints
- comparison reveals specific quality wins (e.g., Purr correctly suppresses stale preference that Hermes still surfaces)
- pack generation latency is acceptable

**kill signals:**
- Purr packs are worse than or equivalent to Hermes' flat approach
- comparison infrastructure becomes a maintenance burden
- pack generation is too slow or too expensive

### phase 2 — correction override validation

**scope:**
- when Ilyas corrects Hermes, run the correction through Purr's challenge/supersede pipeline
- verify: old truth suppressed? new truth active? evidence chain intact? one transaction?
- test the live_override_patch materialization (even though Hermes won't use it)
- still no behavior change in Hermes

**depends on:** phase 0 running, correction events in the stream

**duration:** need ~10-15 real correction events

**success signals:**
- corrections produce clean ledger state transitions
- old truth marked `superseded` or `challenged` in one transaction
- new truth becomes active with proper evidence
- no ghost overrides (override without committed truth)
- no duplicate candidates from correction + generic extractor racing

**kill signals:**
- correction detection is unreliable on real natural language
- challenge/supersede logic creates impossible states
- >30% false positive rate on contradiction detection
- transactions fail or create partial state

### phase 3 — review + proactive scoring (read-only)

**scope:**
- run review queue scheduler on the Purr ledger
- score which memories would be `due` for review
- run proactive preflight: what would Purr have texted first about?
- log all would-have-done decisions
- still no behavior change in Hermes

**depends on:** phases 0-2 running, enough ledger state to make review/proactive meaningful

**duration:** 2+ weeks

**success signals:**
- review suggestions are timely and relevant
- proactive scoring is not spammy (most decisions = no_act)
- would-have-done logs show good judgment vs what actually happened
- trust decay produces reasonable state evolution over time

**kill signals:**
- review queue floods with low-value items
- proactive scoring is consistently creepy or wrong
- timing is off (would-have-texted at bad moments)
- feedback loop doesn't produce meaningful signal quality improvement

---

## hard boundary: Hermes dogfood ≠ turning Hermes into Purr

this boundary must be stated once and enforced always.

| Hermes dogfood IS | Hermes dogfood is NOT |
|-------------------|-----------------------|
| backend-memory validation | product behavior change |
| shadow observation of real events | Hermes reading from Purr ledger |
| testing plumbing on real data | testing creature personality |
| a scoped validation phase with kill signals | a permanent side project |
| code-worker infrastructure work | gooner product work |

**enforcement rules:**
- Hermes' MEMORY.md/USER.md system stays completely independent in all phases
- the Purr pipeline is an observer, never a participant in Hermes' prompt or behavior
- no Purr persona, voice, review pings, or proactive behavior appears in Hermes
- if dogfood exceeds 6 weeks without clear positive signal from at least phases 0-1, kill it
- the adapter between Hermes and Purr ledger is a SEPARATE process, not embedded in Hermes' runtime

---

## instrumentation and debug posture

### what to log (all phases)

| artifact | where | purpose |
|----------|-------|---------|
| raw source events from Hermes | Purr `message_events` table | provenance trail |
| extractor output per event | Purr `memory_items` + `memory_events` | quality audit |
| evidence refs per extraction | `memory_evidence_refs` | grounding verification |
| pack artifacts generated | `pack_artifacts` | comparison material |
| pack-vs-hermes diff | separate comparison log (file or table) | phase 1 quality signal |
| correction detection events | `memory_events` with `actor_type=extractor` | phase 2 validation |
| would-have-done review/proactive decisions | log file or separate table | phase 3 signal |
| evaluator calls (if judge fires) | `memory_events` with `actor_type=judge_evaluator` | debug + cost tracking |

### how to compare old vs new

- Hermes' actual prompt injection is already stored per session in `sessions.system_prompt`
- Purr's generated pack is stored in `pack_artifacts`
- diff is: extract memory section from Hermes' system prompt, compare to Purr's session_pack content
- log: what Purr added that Hermes missed, what Hermes had that Purr suppressed, what both included

### how to inspect errors safely

- all Purr ledger state is queryable through standard SQL
- `memory_events` trail explains every state transition
- evidence refs are immutable backpointers — they can always be verified against source
- evaluator calls log full input/output in `delta_json`
- no separate debug UI in any phase. ledger queries are the debug surface.

---

## build order impact

### build order: UNCHANGED

```
slice 1: memory-ledger
slice 2: memory-candidate-extractor
slice 3: memory-context-packer
slice 4: feedback-orchestrator
```

### test order: CHANGED

each build slice now has a real-data validation phase:

| build slice | dogfood phase that tests it |
|-------------|----------------------------|
| memory-ledger (slice 1) | phase 0 — shadow ledger validates schema, writes, evidence integrity |
| memory-candidate-extractor (slice 2) | phase 0 + phase 2 — extraction quality + correction detection on real language |
| memory-context-packer (slice 3) | phase 1 — pack generation + comparison against Hermes' actual prompt |
| feedback-orchestrator (slice 4) | phase 3 — review queue, proactive scoring, trust decay on real ledger state |

**important:** dogfood phases are NOT sequential blockers on build slices. the build proceeds in order. each dogfood phase runs alongside or slightly after its corresponding build slice ships.

---

## success signals (aggregate)

the dogfood strategy is working if:
- ledger accumulates real structured memory that is measurably better than Hermes' flat approach
- corrections produce clean state transitions without manual intervention
- pack generation stays within budget and is more precise than naive memory stuffing
- the adapter/tap stays simple and does not entangle with Hermes internals
- evidence backtracking works (can trace any memory to its exact source message)
- stale/superseded transitions are inspectable and correct
- evaluator (judge) calls are rare, cheap, and their fallback path is safe

## kill signals (aggregate)

kill the dogfood if:
- extraction quality on real data is too low to produce useful signal
- the Hermes/Purr boundary gets muddy (any pressure to make Hermes use Purr state)
- latency impact on Hermes chat is measurable
- adapter maintenance exceeds the value of real-data testing
- 6 weeks pass without clear positive signal from phases 0-1
- agentic evaluator calls become nondeterministic sludge instead of narrow upgrades

---

## disagreements with gooner's stated instinct

gooner's instinct was:
1. memory backbone should stay mostly deterministic
2. ambiguous/high-leverage decisions can use a narrower judge layer
3. Hermes-first dogfood sounds promising if scoped

**on (1): agree fully.** no pushback.

**on (2): agree with sharpening.** "narrower judge layer" is still too vague as stated. this note pins it to:
- exactly 5 typed decision points
- typed input/output structs, not freeform reasoning
- cheap model, not main model
- conservative fallback on failure
- NOT on the hot path for most cases
- the evaluator is an upgrade path, not a dependency

without this pinning, "narrower judge layer" naturally drifts toward "LLM-in-the-loop for everything ambiguous," which is the path to nondeterministic sludge.

**on (3): partial agreement, one pushback.** the dogfood is valuable for plumbing validation but CANNOT validate taste. conversation patterns in a coding assistant are structurally different from a companion agent. the dogfood proves the pipes work. it does not prove the product works. taste validation must happen on Purr itself. this distinction matters because "dogfood went well" should never become "ship Purr without testing Purr's actual use case."

---

## summary table

| question | answer |
|----------|--------|
| deterministic backbone | yes — 11 surfaces stay strictly rule-driven |
| judge layer | yes — 5 narrow typed decision points, cheap model, conservative fallback |
| judge form | structured evaluator, not subagent, not general reasoning call |
| Hermes dogfood | partial — shadow observation of real events, never behavior change |
| phased rollout | 4 phases: shadow ledger → pack compare → correction test → review/proactive scoring |
| build order changed | no |
| test order changed | yes — each build slice gets real-data validation via its corresponding dogfood phase |
| Hermes becomes Purr | never |
