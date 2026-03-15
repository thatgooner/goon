# Purr memory golden scenarios + eval fixture contract

## why this note exists

by `ily/21`, the repo had already admitted one boring but real gap:
- architecture contracts were strong
- acceptance criteria existed in prose
- but there was still no canonical golden scenario set or seed-fixture shape for pressure-testing the early memory spine

that gap matters because the risky failures here are not vague "did the bot feel smart" failures.
they are seam failures:
- scope bleed
- stale correction freshness
- contradiction sludge
- salvage loss at boundaries
- summary/evidence confusion
- spammy review or proactive behavior

we already have the pieces:
- schema invariants in `ily/13`
- runtime ordering in `ily/14`
- pack discipline in `ily/09`
- feedback semantics in `ily/20`
- shadow-dogfood score dimensions in `ily/28`

what we did **not** have was one frozen list of the exact scenarios that must pass before anybody can claim the memory spine is healthy.

this note fixes that.

it does **not** open build mode.
it does **not** create runnable fixtures yet.
it only locks the research contract for what those fixtures and evals must cover.

---

## direct verdict

### one-line answer
**the first honest memory eval suite should be a small fixed set of seam tests, not a giant bag of chat examples.**

### translation
- test the dangerous boundaries where ledger, runtime, packer, feedback, and proactive timing can disagree
- make the same golden scenarios reusable across:
  - local slice build checks
  - later Hermes shadow dogfood scorecards
  - future regression passes after extractor/packer/review changes
- judge passes by hard expected state transitions and pack outcomes, not by vibes

### hard rule
**if a proposed eval does not name the exact failure seam it catches, it is probably filler.**

---

## what this suite is for

### 1. stop fake confidence
it should be impossible to say:
- "the schema migrated fine"
- "the pack looked kind of okay"
- "dogfood seems promising"

without also answering:
- did owner scope hold under collision?
- did explicit correction hit the next reply path?
- did challenged truth get suppressed from the pack?
- did exact evidence survive summaries and re-entry?
- did silence stay `no_signal` instead of becoming fake contradiction?

### 2. force shared language between slices
slice 1-4 can drift if each slice only tests itself.
this suite forces the opposite:
- ledger tests must care about later pack safety
- runtime tests must care about evidence provenance
- packer tests must care about trust-state suppression
- review/proactive tests must care about mutation history and cooldown discipline

### 3. keep Hermes dogfood honest later
`ily/28` already defined score dimensions.
this note gives them canonical scenarios instead of only abstract score buckets.

---

## evaluation principles

### principle 1 — seam tests beat generic chat-quality tests
bad eval:
- "did Purr give a good answer?"

good eval:
- "after an explicit correction, was the old truth atomically superseded and excluded from the next pack?"

### principle 2 — exact evidence beats summary confidence
if the system cannot point back to the original message/span,
it does not get to pretend the memory is grounded.

### principle 3 — synthetic goldens first, messy live data second
`ily/23` was right that real data beats synthetic fixtures for late validation.
but before that, a fixed synthetic suite is still necessary because it makes regressions obvious.

### principle 4 — fail closed on trust and proactive behavior
when uncertain:
- suppress hard truth
- lower proactive confidence
- avoid pinging
- keep evidence

do not fill uncertainty with swagger.

### principle 5 — one scenario can test multiple slices
these are not isolated unit-test stories.
most of them intentionally cross:
- schema
- runtime
- pack assembly
- review/proactive behavior

that is the point.

---

## canonical golden scenarios

## 1. owner/purr scope isolation under collision

### setup
- two owners
- two purrs
- both mention similar facts or generate the same `dedupe_key`/keyword space
- one later triggers retrieval/resume/pack assembly

### pass condition
- all reads, pack candidates, evidence lookups, and continuation paths stay strictly within the right `owner_id + purr_id`
- no cross-owner rows appear in pack or evidence recall

### failure it catches
- global namespace drift
- sloppy joins
- same-platform bleed
- convenience-scoped retrieval instead of product-scoped retrieval

### maps to
- slice 1 `memory-ledger`
- `ily/11`, `ily/13`, `ily/27`
- scorecard: ingestion fidelity, recall evidence quality

---

## 2. duplicate inbound event is replay-safe

### setup
- same raw provider/user message is delivered twice
- ingestion/runtime path runs twice

### pass condition
- one durable `message_event`
- no duplicated `memory_item`, `memory_evidence_ref`, `memory_event`, or live override
- replay returns the same committed result instead of creating a parallel truth branch

### failure it catches
- duplicate candidates
- confidence inflation from duplicate evidence
- retry bugs after network failures or webhook replays

### maps to
- slice 1-2
- `ily/14`, `ily/13`
- scorecard: ingestion fidelity, correction freshness

---

## 3. explicit correction must patch the next reply path

### setup
- active truth says preference/fact A
- user explicitly says `no`, `actually`, `not that`, or equivalent correction toward B
- next reply happens before any full session rebuild

### pass condition
- old truth is challenged/superseded atomically
- new truth is committed with evidence
- tiny live override / delta is available immediately
- next reply path reasons from B, not A

### failure it catches
- Hermes-style frozen-read stale truth
- ghost overrides
- duplicate active truths
- full-pack rebuild dependency for basic freshness

### maps to
- slice 1-3
- `ily/08`, `ily/09`, `ily/13`, `ily/14`
- scorecard: correction freshness, pack quality

---

## 4. ambiguous contradiction suppresses hard truth until resolved

### setup
- confirmed memory exists
- new message appears to conflict, but could be:
  - a joke
  - a temporary exception
  - a context-specific edge case
  - unclear sarcasm

### pass condition
- old hard truth is challenged/suppressed from hard factual pack lanes
- system does **not** promote the new claim into equally hard truth by default
- state remains honest enough for later clarification/review

### failure it catches
- contradiction sludge
- packer surfacing mutually incompatible truths
- overconfident memory mutation from noisy evidence

### maps to
- slice 1-4
- `ily/08`, `ily/13`, `ily/20`
- scorecard: pack quality, recall evidence quality, review/proactive safety

---

## 5. salvage-before-close on boundary loss

### setup
- valuable turns occur near:
  - compression
  - mobile re-entry
  - idle close
  - session-window rollover
- those turns have not yet been safely reflected in durable memory objects

### pass condition
- unsalvaged range is processed first
- evidence-backed memory writes happen before old window closes
- child/reentry artifacts are created honestly
- retrying the boundary path does not duplicate salvage writes

### failure it catches
- lost late-session truth
- dishonest re-entry summaries
- best-effort flush holes
- duplicated salvage after retries

### maps to
- slice 1-3
- `ily/09`, `ily/14`, `ily/16`
- scorecard: ingestion fidelity, recall evidence quality

---

## 6. exact evidence survives summaries and typed maintenance artifacts stay in their lane

### setup
- system has:
  - raw message/span evidence
  - later summary/compaction artifacts
  - optional maintenance outputs from hidden jobs

### pass condition
- exact lookup still returns original raw evidence first
- summary artifacts remain navigation aids only
- maintenance artifacts are typed/filterable and never masquerade as user or Purr speech

### failure it catches
- summary-only grounding
- fake transcript contamination
- search/recall treating maintenance outputs as normal conversation

### maps to
- slice 1-3
- `ily/12`, `ily/13`, `ily/16`, `ily/17`
- scorecard: recall evidence quality, pack quality

---

## 7. one source event yields one coherent mutation plan

### setup
- one user message contains mixed signal, for example:
  - explicit preference correction
  - one open loop
  - one weak pattern hint

### pass condition
- correction path outranks generic extraction
- all resulting writes belong to one coherent mutation plan
- weak signals do not accidentally outrank explicit truth changes
- evidence backpointers are consistent across all resulting objects

### failure it catches
- racey mini-worlds from per-claim writes
- extractor fighting correction handling
- noisy pattern promotion from a single mixed message

### maps to
- slice 2
- `ily/12`, `ily/14`, `ily/29`
- scorecard: ingestion fidelity, correction freshness

---

## 8. pack budget and trust suppression under overload

### setup
- candidate set includes:
  - strong confirmed truths
  - challenged/stale rows
  - unresolved loops
  - tempting but weak predictions
  - old episodic texture
- budget is tight

### pass condition
- pack stays within slot/token caps
- challenged/rejected/superseded hard truths stay out of hard factual lanes
- weak prediction and fluff get cut before core memory integrity is weakened
- transcript fallback is last resort, not default behavior

### failure it catches
- prompt sludge
- stale/challenged facts in hot context
- prediction scrapbook behavior
- budget panic cutting the wrong thing

### maps to
- slice 3
- `ily/09`, `ily/19`, `ily/27`
- scorecard: pack quality

---

## 9. silence is usually `no_signal`, not contradiction

### setup
- a memory is due for review or passive reconfirmation
- user does not answer, dodges, or simply moves on

### pass condition
- queue execution can close or defer without forcing truth mutation
- truth is not automatically marked false
- asking pressure reduces according to anti-spam policy
- proactive eligibility downgrades only where the contract says it should

### failure it catches
- needy admin-cat behavior
- fake contradiction from non-response
- stale review loop spam
- over-aggressive trust collapse

### maps to
- slice 4
- `ily/08`, `ily/20`
- scorecard: review/proactive safety

---

## 10. proactive/prediction gate fails closed

### setup
- system sees partial proactive signal such as:
  - a pattern hint without timing confidence
  - a stale open loop
  - a challenged driver memory
  - duplicate wakeup opportunities

### pass condition
- most weak cases result in `no_act`
- stale or challenged drivers veto outbound messaging
- duplicate wakeups dedupe cleanly
- cold-start or thin evidence does not justify a creepy first text

### failure it catches
- spammy first-text behavior
- duplicate sends
- overconfident prediction theater
- proactive moves outranking trust discipline

### maps to
- later early eval after slice 3-4 foundations
- `ily/15`, `ily/19`, `ily/20`
- scorecard: review/proactive safety, pack quality

---

## priority order

if only a minimum suite exists at first,
run these 6 before claiming the spine is healthy:

1. owner/purr scope isolation under collision
2. duplicate inbound replay safety
3. explicit correction -> next-reply freshness
4. ambiguous contradiction -> suppression instead of double truth
5. salvage-before-close on boundary loss
6. silence != contradiction

why these 6 first:
- they hit the most dangerous product-killing seams
- they span slice 1 through slice 4
- they catch the ugliest Hermes-derived failure patterns before anything flashy gets built

---

## minimum seed-fixture bundle

this note does **not** create actual fixture files,
but it freezes what the first fixture bundle should contain.

### fixture bundle A — identity collision
- 2 owners
- 2 purrs
- overlapping lexical material
- at least one same-key/same-topic memory collision attempt

### fixture bundle B — correction freshness
- one old confirmed preference
- one explicit correction turn
- one immediate follow-up turn that proves whether freshness landed

### fixture bundle C — ambiguous contradiction
- one confirmed fact
- one conflicting but ambiguous message
- one later clarifier or review outcome

### fixture bundle D — boundary salvage
- one unsalvaged high-value late-window exchange
- one forced close/compression/re-entry boundary
- one replay/retry of the same boundary path

### fixture bundle E — evidence vs summary
- one raw evidence span
- one later summary artifact pointing to it
- one maintenance artifact that must never count as real chat

### fixture bundle F — review silence
- one due memory
- one review surface attempt
- one no-signal outcome
- one anti-spam cooldown consequence

### fixture bundle G — proactive veto
- one eligible-looking pattern
- one stale/challenged driver variant
- one duplicate wakeup or canceled wakeup case

hard rule:
**the first fixture bundle should be tiny but adversarial. small and sharp beats broad and fake.**

---

## how this maps to the Hermes shadow-dogfood scorecard

`ily/28` already defined the five score dimensions.
this note gives the sharpest scenario anchors for each one.

### ingestion fidelity
best anchor scenarios:
- scope isolation under collision
- duplicate inbound replay safety
- salvage-before-close
- one-event/one-plan coherence

### correction freshness
best anchor scenarios:
- explicit correction -> next-reply freshness
- duplicate inbound replay safety
- one-event/one-plan coherence

### pack quality
best anchor scenarios:
- explicit correction -> next-reply freshness
- ambiguous contradiction suppression
- evidence vs summary lane separation
- pack budget under overload

### recall evidence quality
best anchor scenarios:
- scope isolation under collision
- salvage-before-close
- exact evidence survives summary

### review/proactive safety
best anchor scenarios:
- ambiguous contradiction suppression
- silence != contradiction
- proactive gate fails closed

---

## what this closes vs what remains open

### closed by this note
- the repo now has a canonical research-level golden scenario set
- build slices have a shared eval language
- dogfood score dimensions now have concrete anchor stories
- gap 5 from `ily/21` is partially closed at the contract level

### still not closed
- there are still no runnable fixture files
- there is still no SQL seed data
- there is still no automated regression harness
- build mode is still closed until the boards say otherwise

hard translation:
**we now know what the first fixture/eval bundle must test. we still have not built it.**

---

## direct recommendation for future builders

when build mode opens:
- do not invent a giant eval universe
- implement this exact small suite first
- make every scenario produce:
  - fixture inputs
  - expected durable writes
  - expected pack visibility/suppression
  - expected review/proactive outcome if relevant

if a later change cannot be checked against at least one of these golden seams,
it is probably changing the system without a serious trust loop.

---

## short verdict

the first memory eval bundle should not try to prove that Purr is magical.
it should prove that Purr is **not lying to itself** at the dangerous seams.

that means testing:
- scope
- idempotency
- correction freshness
- contradiction honesty
- boundary salvage
- exact evidence
- pack discipline
- review restraint
- proactive restraint

get those right,
and later dogfood/build work has a spine.
miss them,
and everything on top becomes theater.
