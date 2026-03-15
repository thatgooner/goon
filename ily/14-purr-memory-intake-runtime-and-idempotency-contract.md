# Purr memory intake runtime + idempotency contract

## why this note exists
`12` locked the claim/evidence/selection contract.
`13` locked the ledger schema, mutation semantics, and invariants.

that solved:
- what a memory object is
- what exact durable rows exist
- what the packer is allowed to read

what is still too loose is the **write path**:
- how a raw event becomes a memory mutation
- what runs inline vs later
- how retries/replays avoid duplicate truth
- how same-turn corrections affect the next reply
- how salvage works before compression/re-entry/idle close
- how hidden/background/worker cognition writes back without becoming fake magic

without this note, builders can still make a nice schema and still quietly rot memory quality at runtime.

---

## the Hermes lessons that force this note
Hermes already taught us some good architecture lessons.
this pass sharpens the runtime warning.

### 1. durable memory and visible memory are not the same thing
Hermes writes memory during a session, but the active prompt snapshot stays frozen.
that is good for cache discipline.
it also means `saved` does not automatically mean `the next reply sees it`.

Purr consequence:
- truth can commit to the ledger immediately
- the next reply may only use:
  - the frozen session pack
  - plus a tiny explicit `live_override` patch built from **committed** mutations
- never from an uncommitted vibe

### 2. pre-loss salvage has to be operational, not optional
Hermes has explicit flush behavior before compression/reset because otherwise recent learnings vanish.
that is a strong instinct.

Purr consequence:
- compression
- idle cutoff
- re-entry handoff
- server restart / boundary events

all need a first-class salvage path with retry safety.
not a best-effort afterthought.

### 3. replaying only visible chat text is not enough
Hermes flush paths can rely heavily on user/assistant text.
that misses hidden/tool-side discoveries unless they were surfaced elsewhere.

Purr consequence:
- the canonical source log must allow hidden/internal evidence classes
- but hidden evidence still needs exact refs and policy checks
- no `the system somehow learned this` truth jumps

### 4. transcript recall is not writeback
Hermes can later rediscover things through transcript/session search.
useful, but weak as a mutation contract.

Purr consequence:
- background workers
- auxiliary analyzers
- future child/side agents

must write back through the same evidence-backed mutation path as normal intake.
not by hoping transcript search remembers it later.

### 5. lineage-safe retrieval matters, but it starts at intake
if exact evidence is muddy on write,
retrieval will eventually fake certainty no matter how smart the packer is.

Purr consequence:
- exact `message_id/window_id/episode_id/span`
  must exist before any memory becomes active truth

---

## direct thesis
Purr needs a **runtime memory contract** with 4 promises:

1. **raw event first**
   - append the source event before extraction/promotion
2. **one event, one orchestration decision**
   - many candidate claims are allowed, but one policy pass decides the mutation plan
3. **replay-safe writes**
   - duplicate delivery, retries, salvage re-runs, and worker retries must not clone truth
4. **commit-before-use**
   - the reply path may use committed truth or an explicit override patch that references committed truth
   - never invisible speculative state

if this contract is weak,
Purr will get:
- duplicate candidates
- ghost overrides
- stale next replies
- salvage races
- worker memories with no provenance

that is not a tuning bug.
that is product rot.

---

## note map
1. design rules
2. canonical runtime artifacts
3. inline turn intake pipeline
4. deferred + boundary jobs
5. worker/background writeback contract
6. idempotency keys and replay rules
7. freshness + live-override contract
8. failure modes to stop
9. build acceptance tests

---

## 1. design rules

### rule 1 — append the source event before extracting memory
first durable write for any new turn/event:
- resolve `owner_id`
- resolve `purr_id`
- resolve `episode_id`
- resolve/create `window_id`
- append `message_event` or equivalent source event row

why:
- evidence cannot point to a thing that does not exist yet
- crash/replay behavior stays honest
- salvage and later audits have a real source trail

### rule 2 — one source event may emit many claims, but one mutation plan decides truth
one inbound message can legitimately produce:
- a new preference
- a contradiction against old truth
- an open loop
- a pattern hit

that is fine.
what must stay single is the **policy decision** that says:
- which rows are new
- which rows are append-evidence
- which old truth gets challenged/superseded
- which claims are dropped
- which ones need `live_override`

### rule 3 — correction detection outranks generic extraction
if the same event looks like both:
- normal preference extraction
- and direct correction / contradiction

then the contradiction-aware path wins.

do not let a generic extractor create duplicate calm truth while a correction path is trying to suppress the old row.

### rule 4 — commit before the next reply can rely on it
response generation may wait for small turn-critical writes.
that is worth it.

hard rule:
- if a memory change affects the truthfulness of the next reply,
  it must commit before the reply plan is finalized

### rule 5 — background workers propose; policy commits
extractors, scorers, salvagers, and future side-workers can propose.
they do not get to silently invent durable truth outside the ledger mutation path.

### rule 6 — boundary jobs are salvage/consolidation jobs, not permission to rewrite history
when compression/re-entry/idle close happens:
- preserve evidence
- salvage unsaved candidates
- materialize continuation artifacts

not:
- rewrite old windows in place
- invent summary truth with no raw backpointer

### rule 7 — idempotency is part of product quality
`exactly once` at distributed runtime is mostly a lie.
so Purr should aim for:
- append-only source events
- unique source/evidence keys
- transactional mutation plans
- replay-safe no-op behavior on duplicates

---

## 2. canonical runtime artifacts
these can be real tables, queue payloads, or internal structs.
the important part is the contract, not the class name.

### 2.1 `source_event`
this is the canonical inbound thing being processed.

minimum fields:
- `source_event_id`
- `owner_id`
- `purr_id`
- `episode_id`
- `window_id`
- `event_type` (`user_message | purr_message | proactive_event | app_event | boundary_event | worker_proposal`)
- `surface`
- `source_provider_id` or canonical external id
- `content_hash`
- `visibility` (`visible | hidden_internal`)
- `created_at`

mapping rule:
- visible chat messages usually map directly to `message_events`
- worker/boundary proposals may map to system-side source events with provenance refs back to the triggering objects

### 2.2 `intake_batch`
one orchestration unit for one source event.

minimum fields:
- `intake_id`
- `source_event_id`
- `pipeline_version`
- `status` (`started | planned | committed | failed | superseded`)
- `started_at`
- `finished_at`

purpose:
- make retries/replays legible
- let one event produce many candidate actions without losing the envelope

### 2.3 `mutation_plan`
this is the normalized decision output after extraction/correction proposals get merged.

minimum sections:
- `new_memory_items[]`
- `append_evidence[]`
- `challenge_ops[]`
- `supersede_ops[]`
- `confirm_ops[]`
- `reject_ops[]`
- `review_updates[]`
- `live_override_ops[]`
- `deferred_jobs[]`

hard rule:
- the reply path should care about the committed results of the mutation plan
- not raw extractor chatter

### 2.4 `live_override_patch`
small explicit runtime artifact for next-reply freshness.

minimum fields:
- `override_id`
- `window_id`
- `source_event_id`
- `memory_ids[]`
- `override_class` (`correction | contradiction | boundary | safety | high_leverage_pref`)
- `created_at`
- `expires_after_turn` or TTL

hard rule:
- every override must point back to committed memory/evidence ids
- no free-floating override text with no durable anchor

---

## 3. inline turn intake pipeline
this is the turn-critical path.
keep it narrow.

## 3.1 pipeline for a new inbound user message

### step 0 — resolve continuity boundary
before extraction:
- find active `session_window`
- or create one if needed
- attach to an existing/new `episode`

### step 1 — append source event
append the raw inbound event to `message_events` / source log first.

minimum guarantee:
- after this step, replays can say `this message already exists`

### step 2 — open an `intake_batch`
attach processing state to the source event:
- `source_event_id`
- `pipeline_version`
- timestamps

### step 3 — run turn-critical analyzers on the same source event
allowed inline analyzers:
- `message_intake_extractor`
- `direct_correction_detector`
- low-cost safety/boundary detector

not allowed inline by default:
- heavy summarization
- broad historical reconsolidation
- embedding refresh
- long-tail semantic search fanout

### step 4 — build one `mutation_plan`
merge analyzer outputs into a single decision.

examples:
- `new preference + supersede old preference`
- `open_loop + no contradiction`
- `drop weak pattern guess`
- `challenge old truth + queue review`

### step 5 — execute the plan transactionally
inside one transaction where possible:
- lock affected exclusive-scope rows
- insert/update `memory_items`
- insert `memory_evidence_refs`
- insert `memory_events`
- update review/cooldown fields

### step 6 — materialize `live_override_patch` if needed
only for turn-critical cases:
- explicit correction
- direct contradiction
- new hard boundary
- high-leverage preference shift
- safety-sensitive update

### step 7 — response packer reads frozen pack + override
reply generation sees:
- stable `session_pack`
- plus `live_override_patch`
- plus any already-allowed hot/open-loop items

it should **not** wait on:
- deferred maintenance jobs
- embedding refresh
- broad salvage/consolidation

### step 8 — enqueue deferred jobs
examples:
- confidence/salience recompute
- candidate consolidation
- review scheduling recalculation
- long-tail pattern updates
- future semantic refresh

---

## 4. deferred + boundary jobs
these matter, but they should not pretend to be turn-critical.

## 4.1 deferred post-turn jobs
safe examples:
- merge repeated weak evidence
- downgrade stale candidates
- recompute response/timing scores
- queue future review work
- materialize pack rebuild requests when needed

hard rule:
- deferred jobs may improve future truth
- they should not make the just-finished reply depend on an uncommitted result

## 4.2 boundary salvage jobs
triggers:
- compression
- idle cutoff
- archive
- re-entry handoff
- process shutdown boundary

canonical order:
1. identify unsalvaged source-event range
2. run salvage extraction on that range
3. commit resulting ledger mutations
4. create continuation artifacts (`child window`, `reentry_pack`, etc.)
5. only then close/supersede the old active window

hard rule:
- `close window` should not race ahead of salvage and hope cleanup catches up later

## 4.3 re-entry handling
when mobile/webview re-entry happens:
- do not reopen old state in place if a new continuation boundary is cleaner
- create honest continuation artifacts
- hydrate from stored pack + committed truth
- never from client-local guesswork alone

---

## 5. worker/background writeback contract
this matters for hidden tooling and future autonomy.

## 5.1 worker outputs are proposals, not truth
worker types may include:
- background extractor
- contradiction resolver
- review scheduler
- proactive planner
- future child/side agents

all of them must emit a proposal envelope with:
- `source_event_id` or triggering object refs
- evidence refs or derivation refs
- proposed memory ops
- confidence / reason metadata

then the normal policy/mutation path decides whether to commit.

## 5.2 no transcript-only writeback
bad pattern:
- worker does hidden reasoning
- no structured proposal gets written
- system hopes future transcript search will recover it

reject this.
that is how hidden intelligence turns into unverifiable sludge.

## 5.3 hidden evidence is allowed, but it must stay policy-bound
examples:
- system-generated review outcome
- proactive timing outcome
- hidden tool result that genuinely affects memory quality

allowed only if:
- it has exact provenance
- it is marked as hidden/internal
- it passes lane policy
- it does not bypass privacy/public-safe boundaries

### public-safe hard rule
private 1:1 evidence does not become Catnet/public-safe memory just because an internal worker touched it.
lane change needs its own explicit policy step.

---

## 6. idempotency keys and replay rules
this is the boring part that saves the product.

## 6.1 source-event identity
first protection layer:
- unique by `(surface, source_provider_id)` when provider ids exist
- otherwise use a canonical content/time hash with sender + window context

result:
- duplicate webhook delivery should no-op at source-event append

## 6.2 intake-batch identity
recommended key:
- `(source_event_id, pipeline_version)`

meaning:
- same event through same pipeline version should not open endless fresh plans
- a newer pipeline version may reprocess deliberately as backfill/recovery, but must declare itself

## 6.3 evidence identity
recommended uniqueness ingredients:
- `memory_id`
- `message_id`
- `span_start`
- `span_end`
- `excerpt_hash`

result:
- replay cannot attach the same exact evidence twice

## 6.4 mutation-intent identity
for new or challenging claims, the runtime should derive a stable mutation key from:
- `source_event_id`
- `proposed_kind`
- `dedupe_key`
- `scope_ref`
- `payload_fingerprint`

why:
- the same event should not create the same candidate twice on retry
- but two different claims from the same event should still be allowed

## 6.5 live-override identity
recommended key:
- `(window_id, source_event_id, override_class)`

result:
- explicit correction replay does not stack duplicate override patches

## 6.6 boundary-salvage checkpoints
recommended checkpoint key:
- `(window_id, last_salvaged_message_id)`
  or a range hash if salvage works in blocks

result:
- salvage reruns are allowed
- already-salvaged ranges no-op cleanly

## 6.7 concurrency rule for exclusive truths
when a mutation touches an exclusive dedupe scope:
- lock the current active row(s)
- resolve challenge/supersede inside the same transaction

example:
- old preference `balanced`
- new explicit correction `colder`

bad result:
- both live as active truth because two workers raced

good result:
- old row becomes `superseded` or `challenged`
- new row becomes the active path
- one transaction

---

## 7. freshness + live-override contract
this is the real fix for the `durable != visible` problem.

## 7.1 three truth layers
Purr should think in 3 layers:

### layer A — committed ledger truth
current canonical memory state.
source of truth.

### layer B — stored pack truth
frozen `session_pack` / `reentry_pack` artifact already driving the window.
good for stability and cache discipline.

### layer C — turn-local override truth
tiny patch for immediate corrections or boundaries.
expires fast.

hard rule:
- layer C must reference layer A
- layer B can lag briefly
- layer A is the real truth

## 7.2 patch vs rebuild rule
use `live_override_patch` when:
- one or two high-leverage truths changed
- next-reply correctness matters now
- full pack rebuild would be wasteful

use pack rebuild when:
- many hard truths changed
- challenged/suppressed states reshaped the pack materially
- re-entry/continuation boundary occurred
- old pack is no longer honest enough to keep reusing

## 7.3 what should never trigger immediate patching
- weak pattern score drift
- low-confidence next-action guesses
- background embedding refresh
- mild salience reranking
- speculative relationship texture changes

those can wait.

## 7.4 reply safety rule
if the override path fails after the durable mutation committed,
reply generation should prefer:
- committed truth fetched directly for the affected scope
  or
- a safe degraded reply

over:
- confidently answering from stale contradicted pack state

---

## 8. failure modes this contract is meant to stop

### 1. duplicate candidate landfill
same webhook or retry creates the same memory row twice.

fix:
- source-event identity
- mutation-intent identity
- exclusive-scope row locking

### 2. ghost override
next reply behaves as if truth changed,
but no durable row/evidence exists yet.

fix:
- commit-before-use
- override must reference committed ids

### 3. lost late-session memory
important turn lands right before compression/reset/re-entry and disappears.

fix:
- first-class salvage checkpoints
- boundary order: salvage before close

### 4. tool/hidden cognition amnesia
internal work discovered something real, but because only visible chat was replayed,
it never became durable truth.

fix:
- hidden/internal evidence class with provenance
- worker writeback through normal mutation APIs

### 5. race-created double truth
generic extractor and correction detector both write incompatible active rows.

fix:
- one mutation plan per source event
- contradiction path outranks generic extraction
- transactional challenge/supersede

### 6. fake recall later
system summary or transcript search makes it sound remembered,
but exact evidence was never written cleanly.

fix:
- source event first
- exact evidence refs on commit
- summary artifacts stay secondary

### 7. side-worker freelancing
future child/aux agent invents memory outside the main policy gate.

fix:
- proposal-only worker contract
- no transcript-only writeback

---

## 9. build acceptance tests
before leaving research-first mode, builders should be able to test these:

### test 1 — duplicate inbound delivery
same provider message delivered twice.
expected:
- one `message_event`
- one `intake_batch` for the same pipeline version
- no duplicate `memory_item`
- no duplicate `memory_evidence_ref`

### test 2 — explicit correction updates the next reply honestly
user says: `no. colder.`
expected:
- old preference row challenged/superseded
- new preference row committed
- one `live_override_patch`
- next reply uses colder tone without full session-pack rebuild

### test 3 — crash after source-event append but before mutation commit
replay/retry the same event.
expected:
- no duplicate `message_event`
- one eventual committed mutation plan
- no double evidence rows

### test 4 — salvage before compression/re-entry
window closes after important unsalvaged turns.
expected:
- unsalvaged range processed first
- resulting memories committed with exact evidence refs
- child/reentry pack created only after salvage

### test 5 — same event emits multiple valid claims
one user message creates:
- preference update
- open loop
- weak pattern hint

expected:
- preference handled through correction/confirm path if needed
- open loop stored if valid
- weak pattern may be dropped or shadowed
- one coherent mutation plan, not 3 unrelated mini-truth worlds

### test 6 — worker proposal without provenance is rejected
background worker proposes a memory with no source refs.
expected:
- no durable memory commit
- explicit rejection/error reason

### test 7 — hidden/internal event can support memory without becoming theater
system-side proactive timing outcome or internal event generates useful evidence.
expected:
- evidence stored with hidden/internal provenance
- no user-visible tool-call ceremony required
- policy still blocks public-lane leakage

### test 8 — correction and generic extractor race the same dedupe scope
simulate concurrent writes.
expected:
- one active truth in the exclusive scope
- no dual-active preference rows
- event log explains the transition

---

## strongest conclusion
Hermes was already a good lesson in:
- frozen hot context
- salvage before loss
- transcript durability

this pass adds the missing runtime lesson:

**memory quality is not just about the ledger shape. it is about how truth enters the ledger under replay, race, and boundary pressure.**

for Purr that means:
- append source events first
- let one source event produce one coherent mutation plan
- make all critical truth changes replay-safe
- let the next reply use only committed truth or explicit committed overrides
- force workers and hidden ops through the same provenance-backed write path

if we get this right,
`memory-ledger`, `memory-candidate-extractor`, `feedback-orchestrator`, and `memory-context-packer` can all stay aligned.

if we get it wrong,
we will build a pretty schema on top of runtime sludge.

---

## immediate repo implication
before active build slices move, code-worker should treat this note as required input for:
- `memory-ledger`
- `memory-candidate-extractor`
- `feedback-orchestrator`
- any live override / pack patch runtime

because the real question is no longer just:
- `what tables exist?`

it is now also:
- `what exact order turns raw events into committed truth without dupes, ghost state, or stale next replies?`
