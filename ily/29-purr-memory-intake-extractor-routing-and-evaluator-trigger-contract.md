# Purr memory-intake extractor routing + evaluator trigger contract

## why this note exists

by note 28 the repo had already locked:
- ledger truth shape
- runtime write ordering
- pack discipline
- hidden job lanes
- narrow evaluator boundaries
- dogfood observability honesty

but one real seam was still only implied:

**how the intake path should route work between deterministic detectors, the generic candidate extractor, the narrow evaluator, and the later auditor — without turning the memory loop into model sludge.**

this note closes that seam.

it does **not** reopen build mode.
it does **not** pick a vendor/model provider.
it does **not** weaken the deterministic spine.

it freezes the routing contract for slice 2 (`memory-candidate-extractor`) and clarifies what stays rule-owned vs what may use a cheap structured model.

---

## direct verdict

### one-line answer
**Purr should use a hybrid intake posture:** deterministic prefilters first, a cheap structured extractor for bounded candidate generation, and the already-approved narrow evaluator only for a tiny set of ambiguous decisions.

### translation
- do **not** make the main reply model the memory truth engine
- do **not** make every message hit a reasoning call
- do **not** rely on rules alone for all candidate extraction once language gets natural and messy
- do **not** reopen the rejected `subagent inside the memory loop` idea

### the actual lane split
1. **deterministic detectors** own obvious routing and hard safety boundaries
2. **`message_intake_extractor`** may use a cheap structured model to emit typed candidates + exact evidence spans
3. **policy / mutation planner** stays deterministic and remains the only path that can commit truth changes
4. **narrow evaluator** is allowed only at already-locked ambiguity points
5. **`memory-health-auditor`** stays later, deferred, and never sits in the hot loop

hard translation:
**the extractor may propose. the planner decides. the ledger commits. the evaluator arbitrates edge cases. the auditor only watches later.**

---

## what was already locked before this note

this note is a bridge, not a reset.

### from note 12 — claim-shape contract
already locked:
- extractor output must be typed
- every candidate needs exact evidence refs
- `subject_key` / `dedupe_key` discipline exists
- extractor does not get to invent durable truth directly

### from note 14 — intake runtime contract
already locked:
- source event append before extraction
- one source event -> one coherent mutation plan
- correction detection outranks generic extraction
- background workers may propose, but policy commits
- reply path reads committed outputs, not raw extractor chatter

### from note 23 — evaluator boundary
already locked:
- no subagent in the memory loop
- no freeform "think harder" layer
- yes to a **narrow typed evaluator**
- cheap model only
- conservative fallback on failure
- most evaluator calls stay off the hot path

### from note 25 — auditor follow-up
already locked:
- no separate referee brain above the system
- only a later deferred `memory-health-auditor`
- auditor emits bounded findings/recommendations, not direct truth writes

### from note 27 — repo discipline
already locked:
- build order stays `memory-ledger -> memory-candidate-extractor -> memory-context-packer -> feedback-orchestrator`
- extractor-model choice was still open
- that openness was **not** a blocker for slice 1
- build gate remained closed until board-level unpark

this note closes the extractor-routing ambiguity without changing any of that.

---

## the missing seam this note closes

before this pass, the repo knew:
- what extraction should output
- where extraction sits in the runtime
- where evaluator calls are allowed

but it did **not** state one canonical answer to these:
- is extraction rule-only, cheap-model, or hybrid?
- which intake problems belong to the extractor vs the evaluator?
- can ambiguous correction language use a cheap model or must it stay rules-only forever?
- are inline extraction and deferred extraction the same actor or two tiers?
- what should degrade first on cost pressure without breaking memory quality?

answer now:
- **hybrid posture**
- **two extractor tiers** (`inline` + `deferred`) sharing one typed output contract
- **deterministic routing first**
- **cheap structured model allowed for candidate generation**
- **evaluator reserved for ambiguity arbitration, not generic extraction**
- **cost pressure hits frequency/depth/escalation first, not correction integrity**

---

## canonical intake actors + ownership

## 1. `direct_correction_detector`

### job
own the first routing question:
- is this message an explicit correction?
- is it a contradiction?
- is it a supersede/update?
- is it just emotion, sarcasm, or venting?

### posture
- deterministic first
- if same-turn ambiguity genuinely affects next-reply correctness, the already-approved contradiction evaluator may assist
- safe fallback is always available: challenge/suppress the old truth instead of pretending certainty

### must never do
- create broad new candidate sets unrelated to the correction
- write durable truth directly
- compete with generic extraction in the same dedupe scope without one shared mutation plan

---

## 2. `message_intake_extractor`

### job
turn one committed source event into a **typed proposal bundle**:
- obvious facts
- preferences
- relationship-state hints
- open loops
- episodic moments
- pattern hits
- next-action hints

with:
- exact evidence spans
- initial leverage/confidence posture
- clear proposed kind
- suggested merge/supersede linkage if obvious

### posture
- cheap structured model **allowed**
- deterministic helpers encouraged before and after the call
- output must fit a strict schema, not freeform prose

### why this should not stay rules-only forever
pure rules are good for:
- explicit correction phrases
- hard negation markers
- obvious preference templates
- direct promise/follow-up language

but weak at:
- messy natural language preference statements
- indirect but still useful relationship cues
- conversationally embedded open loops
- multi-clause utterances where one message contains several candidate kinds
- separating "one-off vent" from "real durable preference candidate"

so the extractor should be **cheap-model capable**,
not because it owns truth,
but because bounded structured parsing of messy language is exactly the kind of thing rules-only systems underperform at.

### must never do
- decide final promotion/supersede on its own
- bypass evidence refs
- emit prompt-shaped summaries instead of typed rows
- become a hidden second chat model deciding reply behavior

---

## 3. `deferred_background_extractor`

### job
re-read recent raw events outside the reply-critical path for things that are valuable but not urgent:
- low-leverage candidates skipped inline
- repeated weak pattern hits
- cross-turn pattern consolidation
- better evidence merge opportunities
- salvage before idle close / re-entry / compression boundaries

### posture
- same typed output contract as inline extractor
- may use the same cheap extractor model
- should run in batches and under queue control
- should be allowed to produce **better proposals**, not special proposal types

### hard rule
inline and deferred extraction are **two scheduling modes of one contract**,
not two different truth systems.

---

## 4. `mutation_planner` / policy layer

### job
take all detector/extractor outputs for one `source_event` and decide one coherent mutation plan.

### posture
- deterministic
- replay-safe
- schema-backed
- owns dedupe/scope guardrails
- owns ordering: correction first, then generic candidate handling

### hard rule
if there is ever conflict between extractor enthusiasm and ledger discipline,
**ledger discipline wins.**

this layer is why a cheap extractor is safe.

---

## 5. `narrow_evaluator`

### job
arbitrate only the already-approved ambiguity points.

### allowed decision classes
1. contradiction interpretation
2. pattern promotion / demotion
3. review timing taste
4. proactive creepiness veto
5. merge / dedup ambiguity

### posture
- cheap model
- typed input/output only
- conservative fallback on failure
- mostly deferred, not hot path

### critical non-rule
**the evaluator is not the extractor.**

it should not:
- scan every message for memories
- invent generic candidate rows
- decide broad memory truth from raw conversation
- become a default second pass on every message

it is a narrow appeals court,
not the intake clerk.

---

## 6. `memory-health-auditor`

### job
later only:
watch multi-event failure patterns after enough history exists.

### posture
- deferred
- mostly SQL / deterministic detection
- only rare bounded ambiguous interpretation may use the same narrow-evaluator pattern

### hard rule
auditor findings may recommend actions.
they do not write truth directly.

auditor is not part of normal message intake.

---

## routing matrix

| situation | owning lane | hot path? | model allowed? | fallback posture |
|---|---|---:|---|---|
| explicit correction (`no that's wrong`, `I meant X`) | `direct_correction_detector` -> mutation planner | yes | only if same-turn ambiguity needs contradiction interpretation | challenge/suppress old truth, hold new truth as candidate if needed |
| obvious explicit preference/fact | deterministic prefilter + `message_intake_extractor` | yes | yes, cheap structured extractor allowed | if extractor unavailable, keep minimal rule-detected candidate or defer |
| clear open loop / promise / callback request | deterministic prefilter + extractor | yes | yes | if uncertain, store as low-trust `open_loop` candidate or defer |
| multi-clause message with mixed candidate kinds | extractor | yes | yes | emit fewer candidates, not more; fail conservative |
| weak pattern hint from one turn | extractor proposal only | usually yes, but low leverage | yes | keep as low-trust `pattern_signal` or drop |
| repeated weak pattern across turns | deferred background extractor + planner | no | yes | hold until stronger evidence or decay |
| merge / dedup ambiguity between nearby claims | evaluator decision point 5 | usually no | yes, cheap evaluator | keep rows separate / hold merge |
| ambiguous contradiction meaning | evaluator decision point 1 | sometimes yes | yes, but only if next-turn correctness matters | safe challenge/suppress |
| review timing taste | evaluator decision point 3 | no | yes | defer review |
| proactive creepiness veto | evaluator decision point 4 | no, heartbeat only | yes | no-act |
| temporal churn / oscillation across weeks | later auditor | no | usually no | emit finding only |

---

## deterministic-first routing stack

## tier 0 — deterministic prefilters
run before any cheap model call.

examples:
- explicit negation / correction markers
- strong preference verbs (`hate`, `love`, `always`, `never`) with direct target
- direct promise/follow-up language
- duplicate-source-event detection
- obvious no-memory noise cases
- exclusive dedupe-scope lookup for likely correction targets

purpose:
- catch easy wins cheaply
- protect correction integrity
- keep obvious junk away from the extractor
- reduce model-call rate

## tier 1 — cheap structured extraction
allowed when the event survives tier 0 and memory value is plausible.

input should be bounded:
- single source event
- nearby turn context only if needed
- candidate target rows only if relevant
- strict JSON schema

output should be bounded:
- max small set of candidate proposals
- exact evidence refs
- confidence/leverage posture
- optional `needs_review` / `needs_merge_check` flags

## tier 2 — deterministic mutation planning
always required before truth changes.

planner responsibilities:
- enforce one-source-event / one-plan coherence
- apply correction-first precedence
- enforce dedupe/active-truth uniqueness
- decide create vs merge vs supersede vs hold
- commit event trail + evidence refs atomically

## tier 3 — narrow evaluator escalation
only if the planner encounters one of the 5 approved ambiguity classes.

if evaluator fails:
- do not invent certainty
- do not broaden scope
- choose the safe conservative state

---

## inline vs deferred extraction contract

## inline extractor
use when:
- the candidate may matter for the next reply
- the memory is explicit/high leverage
- the message contains a likely correction/open loop/preference/fact worth same-turn capture

### inline hard rule
inline extraction must stay **small and boring**.

it is not allowed to:
- rescan the whole user history
- perform broad semantic retrieval first
- run multiple model calls per normal message
- generate a reflection essay about the conversation

## deferred extractor
use when:
- the candidate does not affect next-turn correctness
- pattern accumulation needs more than one event
- salvage/re-entry maintenance is running
- cost pressure suggests batching is smarter than inline work

### deferred hard rule
if deferred work finds something that should have affected the last reply,
that is a quality miss to log — not permission to silently rewrite history without evidence.

---

## what belongs to extractor vs evaluator

## extractor owns
- broad candidate generation from one source event
- classifying likely memory kind
- attaching exact evidence spans
- initial confidence/leverage posture
- suggesting obvious merge/supersede targets when trivial

## evaluator owns
- deciding among a small set of already-shaped ambiguous options
- resolving contradiction meaning when rules are not enough
- resolving merge ambiguity when rows are genuinely close
- judging borderline pattern promotion/demotion
- judging timing taste for review/proactive only

## planner owns
- all durable mutation ordering
- all transaction-safe write decisions
- all dedupe/invariant enforcement
- all commit-before-use freshness

best shorthand:
- extractor = `what might be here?`
- planner = `what is safe to do with it?`
- evaluator = `which safe option fits this ambiguous edge case?`

---

## model-routing posture

## 1. provider/model choice stays open
this note locks **posture**, not vendor.

so the contract is:
- extractor/evaluator models must be cheap enough for frequent background use
- reply model stays separate from intake truth work
- no note in this repo should assume one provider forever

## 2. extractor and evaluator may share the same cheap model class
that is acceptable if:
- schemas differ
- call sites differ
- logging differs
- budgets differ
- they remain logically separate actors

shared cheap model is fine.
shared role is not.

## 3. main reply model should not double as normal intake engine
exceptions may exist in ultra-early prototype conditions,
but the architecture should treat that as temporary debt,
not the design.

why:
- cost creep
- invisible coupling between reply style and memory truth
- hard-to-debug truth writes
- pressure to let reply-chain reasoning become evidence

## 4. free-tier degradation order
when cost pressure hits, degrade in this order:
1. batch more deferred extraction
2. reduce non-critical extractor frequency on low-leverage events
3. keep inline correction integrity intact
4. keep evidence-backed candidate generation for high-leverage events intact
5. reduce evaluator usage on borderline cases by choosing safe holds more often
6. only then consider weaker cheap-model routing

hard rule:
**do not save money by letting explicit correction freshness rot.**

---

## acceptance posture for slice 2

the extractor slice should be considered aligned only if it satisfies all of this:

### truth integrity
- zero direct durable writes from extractor/evaluator actors
- every committed candidate/update path goes through the mutation planner
- replaying the same source event does not create duplicate truth/evidence

### evidence integrity
- every non-dropped candidate has exact evidence refs
- no prompt text, memory file text, or maintenance artifact is used as evidence
- summary text never substitutes for raw evidence

### routing discipline
- explicit correction path outranks generic extraction every time
- evaluator call sites stay inside the approved 5 classes
- inline extractor remains one bounded pass, not an agent loop

### cost discipline
- most messages should resolve with deterministic routing + at most one cheap extractor call
- evaluator usage should be rare enough to look like escalation, not default behavior
- starting posture: target evaluator under ~5% of source events overall and under ~1% inline-hot-path events

### product discipline
- no visible tool ceremony
- no user-facing `I am running memory analysis` sludge
- no broad mood-guessing promoted into hard truth

---

## failure modes this note is trying to block

## 1. rules-only fantasy
team pretends deterministic rules will parse messy natural language well enough forever.

result:
- missed useful candidates
- brittle phrasing dependence
- fake confidence from simplistic heuristics

fix:
- cheap structured extractor allowed

## 2. extractor creep
extractor starts deciding truth directly.

result:
- hard-to-replay writes
- invisible truth drift
- no audit-safe mutation boundary

fix:
- planner owns commits

## 3. evaluator creep
narrow evaluator becomes a default second brain for every message.

result:
- cost blowup
- latency blowup
- impossible debugging
- quiet architecture drift back toward subagent theater

fix:
- 5 decision points only

## 4. reply-model contamination
main conversation model silently doubles as memory extractor.

result:
- style reasoning contaminates truth judgments
- hard separation between `what sounded good` and `what is evidenced` disappears

fix:
- separate intake routing posture

## 5. cost panic shortcuts
team tries to save money by skipping evidence or correction freshness.

result:
- memory quality collapses exactly where the product depends on it

fix:
- degrade batching/escalation before integrity

---

## hard non-goals

this note does **not** authorize:
- opening build mode
- adding a general judge/referee agent
- dogfood adapter work ahead of the main slice order
- provider-specific lock-in
- prompt-derived evidence
- semantic history fanout on every user turn
- visible memory-analysis UI in normal 1:1 chat

---

## what changes after this note

### it does change
- the repo now has a canonical answer to `rule-only vs cheap-model vs hybrid` for intake: **hybrid**
- the repo now has a canonical extractor/evaluator split
- `memory-candidate-extractor` can be built later without guessing whether it should be a rule engine, a mini-agent, or a freeform LLM parser

### it does not change
- first build slice stays `memory-ledger`
- build gate stays closed until the boards explicitly open it
- dogfood stays subordinate
- evaluator remains narrow
- auditor remains later

---

## direct conclusion

the missing decision was never `should Purr have a judge layer?`
that was already answered.

the missing decision was:
**how does normal message intake stay sharp enough to capture real memory signals without letting the whole truth spine dissolve into LLM soup?**

the answer is now simple:
- route obvious boundaries with rules
- let a cheap structured extractor parse the messy middle
- keep truth commits deterministic
- escalate only rare ambiguity to the narrow evaluator
- keep the auditor out of the hot loop entirely

that is the smallest honest intake shape that still feels like a serious memory product instead of a brittle regex toy or a vibes-driven second brain.
