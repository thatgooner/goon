# Purr feedback orchestrator + review outcomes + trust decay contract

## why this note exists
`08` locked the core memory lifecycle.
`13` locked the durable ledger shape.
`18` locked the hidden runtime lanes.
`19` locked proactive preflight and `should_text_first?`.

that still left one ugly seam half-open:

**how does Purr decide when to verify memory, how does it interpret the answer or silence, and how do those outcomes actually change trust without turning into needy bot behavior?**

right now the repo already knows:
- memory needs review and decay
- same-session corrections need a live override lane
- proactive review pings must be rarer/stricter than ordinary replies
- challenged or stale memory should gate proactive behavior down
- Hermes has no serious verification loop to copy

what was still too loose was:
- the product-facing **feedback orchestrator**
- the exact split between `review_status` and queue/execution state
- the outcome taxonomy for explicit checks, passive reconfirmation, contradiction, silence, and `not now`
- how review outcomes propagate into packs, rollups, and proactive posture

without this note, builders will do one of two bad things:
- treat every stale memory like a generic `ask the user again` task
- or leave review/decay vague until implementation, which means silent drift and spammy fixes later

both are wrong.

---

## direct thesis
memory verification is **not** one queue and one prompt.
it is a hidden orchestration layer with 3 jobs:

1. decide **whether** a memory deserves feedback pressure at all
2. decide **which surface** is least annoying and most truthful
3. turn the result into a **typed trust update**, not vague vibes

strong rule:
**Purr should verify memory with taste, not with bureaucracy.**

another strong rule:
**silence is usually `no_signal`, not contradiction.**

another one:
**review is not only explicit asking. passive reconfirmation should do most of the quiet work.**

Hermes lesson forcing this:
- Hermes is strong at saving and recalling
- Hermes is weak at re-validating over time
- Hermes has no real semantics for `still true?`, `probably drifted`, `user ignored this`, or `quietly reconfirmed by behavior`

translation for Purr:
- review must be first-class
- decay must be evented
- passive evidence must count
- non-response must not trash good memory by accident

---

## note map
1. design rules
2. canonical artifacts
3. feedback surfaces
4. candidate arbitration
5. outcome taxonomy
6. trust decay + propagation rules
7. memory-kind policies
8. queue/writeback contract
9. proactive interaction rules
10. failure modes
11. build acceptance tests

---

## 1. design rules

### rule 1 — most memory truth should age through passive evidence, not explicit interrogation
Purr should not keep asking:
- `do you still like this?`
- `is this still true?`
- `am i remembering right?`

for most memory kinds, better options are:
- observe repeated behavior
- notice contradictions naturally
- use a light inline check only when the current turn actually benefits

### rule 2 — asking is a scarce move
explicit feedback moments are limited product budget.

starting caps:
- max **1 blocking memory check** in a reply turn
- max **1 trailing/light memory check** in a reply turn
- max **1 proactive review ping per day**
- max **3 explicit attempts per memory** before heavy cooldown

### rule 3 — surface choice matters as much as timing
`review due` is not the same as `ask now`.

one due memory may be best handled by:
- passive reconfirmation only
- a tiny inline clarification
- a tucked-on trailing check after the main reply
- a proactive review ping later
- silence + decay

### rule 4 — silence is weak evidence
if the user ignores a memory check,
that usually means:
- wrong timing
- low relevance
- low priority
- chat moved on

it does **not** usually mean the memory is false.

### rule 5 — explicit contradiction outranks passive support
if Purr has 20 soft behavioral hints but the user explicitly says the opposite,
explicit correction wins.

### rule 6 — feedback state must stay separate from truth state
truth answers:
- `candidate | confirmed | stale | rejected | superseded`

feedback answers:
- is this due?
- did we try?
- what happened last time?
- should we cool down?

if those get mashed together,
builders will overfit queue mechanics into the truth model.

### rule 7 — review outcomes must propagate beyond one row
if a memory gets reconfirmed or weakened,
that can affect:
- pack inclusion
- proactive eligibility
- derived rollups
- candidate classes
- tone confidence

review is not a local edit.
it is a trust signal.

---

## 2. canonical artifacts

## 2.1 `feedback_candidate`
purpose:
- ephemeral internal object representing one possible memory-feedback action
- lets the orchestrator rank review opportunities instead of blindly asking whatever is `due`

minimum fields:
- `feedback_candidate_id`
- `owner_id`
- `purr_id`
- `memory_id`
- `memory_kind`
- `trigger_reason` (`due_review | contradiction_pressure | stale_high_leverage | passive_miss_cluster | open_loop_expiry | boundary_preflight`)
- `surface_preference` (`passive_only | inline_blocking | inline_trailing | later_in_chat | proactive_ping | suppress`)
- `leverage_score`
- `evidence_quality_score`
- `interruption_cost`
- `annoyance_risk`
- `freshness_risk`
- `contradiction_pressure`
- `timing_fitness`
- `expires_at`
- `best_evidence_refs[]`
- `dedupe_key`

hard rules:
- this is not durable truth
- this expires fast
- this exists to arbitrate one feedback moment, not to become another memory dump

## 2.2 `review_queue_item`
purpose:
- durable work item saying a memory may deserve future feedback pressure

important distinction:
- `memory_item.review_status` is a high-level memory field
- `review_queue_item.status` is execution state for the queue row

recommended queue states:
- `queued`
- `due`
- `presented`
- `cooling_down`
- `resolved`
- `cancelled`

starting fields:
- `queue_item_id`
- `owner_id`
- `purr_id`
- `memory_id`
- `reason`
- `priority`
- `status`
- `due_at`
- `cooldown_until`
- `attempt_count`
- `last_presented_at`
- `last_outcome_kind`
- `last_outcome_at`
- `next_surface_hint`

hard rule:
`resolved` belongs to the queue item,
not to `memory_item.review_status`.

## 2.3 `review_outcome`
purpose:
- typed maintenance artifact recording what actually happened when feedback pressure was attempted or inferred

minimum fields:
- `review_outcome_id`
- `owner_id`
- `purr_id`
- `memory_id`
- `queue_item_id` (nullable)
- `source_surface` (`inline_blocking | inline_trailing | later_in_chat | proactive_ping | passive_observation`)
- `outcome_kind`
- `outcome_strength` (`strong | medium | weak`)
- `source_event_id` or evidence refs
- `previous_state_snapshot`
- `resulting_state_snapshot`
- `policy_reason`
- `created_at`

hard rule:
if trust changed,
there should be a `review_outcome` or equivalent typed event trail explaining why.

## 2.4 `trust_transition`
purpose:
- small internal planning/result object saying how this outcome changes trust surfaces

minimum fields:
- `memory_id`
- `freshness_delta`
- `confidence_delta`
- `review_status_next`
- `pack_policy_next`
- `needs_review_at_next`
- `cooldown_until_next`
- `derived_invalidations[]`
- `proactive_eligibility_delta`

this can be implemented later as logic rather than a table,
but the contract should exist now.

---

## 3. feedback surfaces
Purr needs a small set of memory-feedback surfaces with different interruption costs.

## 3.1 `passive_only`
use when:
- the memory can be reconfirmed through behavior
- the downside of asking is higher than the downside of waiting
- this is a preference/pattern/relationship detail, not a blocking truth

examples:
- tone preference drift
- small recurring habits
- relationship texture memory
- pattern rollup support

effect:
- no visible question
- watch for confirming or weakening evidence
- decay gently if nothing happens

## 3.2 `inline_blocking`
use when:
- the next reply will probably be wrong without clarification
- there is direct contradiction with active truth
- the user just corrected something high-leverage
- boundary/safety implications are real

tone target:
- short
- slightly sharp
- not corporate

examples:
- `wait. still true or not?`
- `pick one. is that actually the rule now?`

hard rule:
this surface is expensive.
use only when answer quality now depends on it.

## 3.3 `inline_trailing`
use when:
- a light check would help
- but it should not interrupt the main reply
- the memory matters soon, not this exact sentence

shape:
- reply first
- then append one small check

example:
- main reply...
- `also, still hate voice notes or did that change?`

## 3.4 `later_in_chat`
use when:
- the session is active
- the timing is not right this turn
- but another natural opening may appear soon

this is still in-chat,
not a proactive ping.

think:
- wait until the topic reappears
- wait until the emotional temperature is lower
- wait until the user is less rushed

## 3.5 `proactive_ping`
use when:
- the memory is high-leverage
- passive reconfirmation is too slow
- the timing is genuinely good
- the check can be phrased lightly
- the same decision would survive the stricter `should_text_first?` gate

hard rule:
most memory review should **not** end up here.

## 3.6 `suppress`
use when:
- topic is too sensitive
- user already signaled `not now` or `don't do this`
- evidence is weak and interruption would feel creepy
- negative feedback risk dominates

suppress does not always mean delete.
it often means:
- keep the memory
- lower trust
- stop surfacing it directly

---

## 4. candidate arbitration
many things can be review-worthy at once.
Purr still needs one taste layer.

## 4.1 priority order
starting priority order:
1. direct contradiction blocking the next reply
2. new hard boundary / safety-sensitive correction
3. high-leverage stale truth affecting active relationship behavior
4. open loop nearing expiry
5. high-impact preference drift
6. relationship memory tune-up
7. low-stakes trivia

if two candidates compete,
choose the higher-leverage one and suppress the rest for now.

## 4.2 arbitration questions
for each `feedback_candidate`, ask:

### Q1 — if we stay quiet, does the next reply become fake or risky?
if yes,
prefer `inline_blocking`.

### Q2 — can this be resolved passively soon?
if yes,
prefer `passive_only` or `later_in_chat`.

### Q3 — does this memory deserve an interruption?
if not,
no question now.

### Q4 — is the moment socially good?
check:
- current topic intensity
- whether the user is rushing
- whether we already asked something recently
- whether the user is annoyed/cold/offline

### Q5 — what is the least needy valid surface?
prefer:
1. passive_only
2. later_in_chat
3. inline_trailing
4. proactive_ping
5. inline_blocking

exception:
blocking contradiction/safety can jump straight to `inline_blocking`.

## 4.3 single-moment rule
at most one explicit memory-check moment should dominate a reply.

no:
- `while we're here, three quick clarifications`
- stacked admin energy
- checklist tone

---

## 5. outcome taxonomy
this is the missing seam between `review happened somehow` and actual trust updates.

## 5.1 explicit outcomes
these come from visible asks.

### `confirmed_explicit`
user directly confirms the memory.

examples:
- `yes`
- `still true`
- `exactly`
- clear re-assertion of the same fact/preference

effect:
- `last_confirmed_at = now`
- raise freshness/confidence
- clear contradiction pressure if present
- queue item may resolve

### `contradicted_explicit`
user directly says the memory is false or outdated.

examples:
- `no`
- `not anymore`
- `that's wrong`
- `don't remember it like that`

effect:
- active truth gets challenged or superseded
- pack suppression happens immediately
- live override may materialize if this affects the current turn
- dependent proactive candidates get invalidated

### `not_now`
user signals timing rejection, not truth rejection.

examples:
- `later`
- `not doing this rn`
- `we'll talk about it later`

effect:
- no major confidence drop
- queue item enters cooldown
- future surface should usually be softer, not more aggressive

### `avoid_topic`
user signals this should not be surfaced directly.

examples:
- `don't ask me that`
- `stop bringing that up`

effect:
- direct review on this memory class/topic gets suppressed
- memory may stay in shadow or suppress lane
- future reconfirmation should be passive only unless safety requires otherwise

### `ambiguous_reply`
user answered, but not clearly enough to update truth confidently.

examples:
- joke answer
- mixed/hedged answer
- context-dependent answer without stable signal

effect:
- weak update at most
- keep out of hard pack if ambiguity remains
- maybe downgrade to passive-only follow-up later

## 5.2 passive outcomes
these come from behavior or exact evidence,
not from a direct question.

### `confirmed_passive`
new evidence quietly supports the memory.

examples:
- repeated behavior matches stored preference
- user naturally restates the same fact later
- topic behavior reconfirms relationship texture without needing to ask

effect:
- refresh `last_hit_at`
- possibly refresh `last_confirmed_at` for softer kinds if evidence is strong enough
- small confidence/freshness gain

### `weakened_passive`
new evidence suggests drift but not clean contradiction.

examples:
- a formerly strong preference stops appearing
- a pattern stops hitting repeatedly
- behavior becomes mixed

effect:
- lower freshness/confidence
- maybe move `confirmed -> stale`
- do not treat as contradiction yet

### `contradicted_passive`
behavior or exact evidence clearly conflicts with memory,
but without an explicit correction.

use carefully.
this threshold should be high.

examples:
- multiple clean opposing behaviors on a strong preference
- exact later statement contradicts old fact even if not phrased as correction

effect:
- set `contradiction_status=challenged`
- usually queue for future resolution unless strong enough to supersede directly

### `no_signal`
nothing meaningful happened.

examples:
- proactive review ping ignored
- inline trailing check got lost in conversation
- timing passed with no usable evidence

effect:
- attempt count may increment
- cooldown may apply
- trust decay should be mild or zero depending on memory kind

hard rule:
`no_signal` is not a miss.

## 5.3 system outcomes
these come from the orchestrator, not the human.

### `snoozed_by_policy`
system chose not to surface the question because timing was bad.

### `cancelled_by_fresher_truth`
queue item became obsolete because new evidence resolved the issue first.

### `expired_low_value`
memory or queue item aged out and explicit review is no longer worth it.

---

## 6. trust decay + propagation rules
review outcomes should change more than one timestamp.

## 6.1 first propagation targets
every `review_outcome` may update:
- `memory_item.state`
- `review_status`
- `contradiction_status`
- `pack_policy`
- `freshness_score`
- `confidence`
- `last_confirmed_at`
- `last_hit_at`
- `last_miss_at`
- `needs_review_at`
- `cooldown_until`
- `attempt_count`

## 6.2 second propagation targets
if trust moved enough,
also update or invalidate:
- `pattern_rollup`
- `timing_window`
- `proactive_candidate`
- `proactive_posture` only if the feedback was about contact appetite / annoyance / text-first tolerance
- pack artifacts scheduled for reuse

## 6.3 propagation rules by outcome

### after `confirmed_explicit`
- clear `challenged`
- raise freshness strongly
- queue item -> `resolved`
- if memory was `stale`, often return to `confirmed`
- any derived artifact depending on this memory may stay active or get refreshed

### after `confirmed_passive`
- freshness up modestly
- confidence up modestly or unchanged
- queue item may resolve if support is strong enough for that memory kind
- do not over-promote a weak passive signal into hard certainty

### after `contradicted_explicit`
- immediate suppress old truth from active pack
- if replacement truth is clear, old -> `superseded`, new -> `confirmed`
- invalidate proactive candidates relying on old truth
- refresh pack or overlay if current reply depends on it

### after `weakened_passive`
- freshness down
- maybe `confirmed -> stale`
- derived proactive eligibility drops faster than ordinary pack eligibility
- do not immediately ask unless leverage/timing justify it

### after `contradicted_passive`
- set `challenged`
- suppress from hard factual pack until resolved
- create or update queue item unless the evidence is strong enough for auto-supersede
- proactive surfaces should usually get quieter until resolved

### after `not_now`
- no major truth downgrade
- queue cooldown extends
- future surface should bias toward passive or later_in_chat

### after `avoid_topic`
- direct surfacing gets suppressed
- `review_status` may become `none` or remain `snoozed` with long cooldown
- keep only passive reconfirmation unless safety/product boundary forces otherwise

### after repeated `no_signal`
starting rule:
- first `no_signal` -> just cooldown
- second `no_signal` -> lower priority and move to passive-only if possible
- third `no_signal` -> expire explicit queue unless the memory is high-leverage

hard rule:
repeated silence should reduce asking,
not increase it.

---

## 7. memory-kind policies
trust decay should not be uniform.

## 7.1 profile / stable facts
examples:
- name
- identity labels user clearly owns
- stable life facts

policy:
- explicit contradiction matters most
- passive misses are weak
- no-response should barely matter
- review rarely

starting posture:
- `confirmed_passive` can refresh freshness
- `weakened_passive` usually just lowers freshness, not state
- move to `stale` only after long quiet + conflict signals

## 7.2 preferences
examples:
- tone preference
- media taste
- interaction likes/dislikes

policy:
- drift is normal
- passive evidence is valuable
- explicit check sometimes justified

starting posture:
- one strong passive mismatch can weaken
- repeated mismatches can make `confirmed -> stale`
- explicit contradiction can supersede quickly

## 7.3 relationship memory
examples:
- roast tolerance
- what kind of teasing lands
- dynamic texture between Purr and user

policy:
- prefer passive reconfirmation
- avoid blunt admin-style checks
- one bad moment should not rewrite the whole relationship model

starting posture:
- more tolerant of ambiguity
- degrade slowly
- use inline checks only when current tone choice truly depends on it

## 7.4 open loops
examples:
- promised follow-up
- unresolved callback thread
- `send me that later`

policy:
- review fast or decay fast
- silence means more here than in stable preferences,
but still is not auto-contradiction

starting posture:
- missed callback window -> freshness drops fast
- repeated `no_signal` can close the explicit queue
- if the user resolves it elsewhere, queue item cancels immediately

## 7.5 pattern / predictive memory
examples:
- timing habits
- re-entry patterns
- callback tendencies

policy:
- mostly passive
- explicit asking is rare and usually awkward
- hit/miss logic belongs more to calibration than direct review

starting posture:
- passive misses degrade proactive eligibility quickly
- keep most of this backend-only
- do not ask the human to label predictive abstractions unless high leverage and phrased naturally

## 7.6 boundaries / safety-sensitive preferences
examples:
- forbidden topics
- hard interaction limits
- privacy boundaries

policy:
- explicit correction outranks everything
- same-turn freshness matters
- passive ambiguity should not gamble here

starting posture:
- direct contradiction updates live override immediately
- proactive or playful use gets shut down fast after any negative signal

---

## 8. queue + writeback contract

## 8.1 split the fields cleanly
recommended semantic split:

### `memory_item.review_status`
high-level memory readiness:
- `none`
- `queued`
- `due`
- `ask_now`
- `snoozed`

### `review_queue_item.status`
execution state:
- `queued`
- `due`
- `presented`
- `cooling_down`
- `resolved`
- `cancelled`

this resolves the current repo ambiguity where some notes use `resolved` in queue logic while the base `review_status` enum does not include it.

## 8.2 recommended event additions
note `13` already has:
- `review_due`
- `snoozed`
- `pack_hit`
- `pack_miss`

this feedback contract needs more precise writeback events or equivalent typed artifacts.

recommended additions:
- `review_presented`
- `review_confirmed_explicit`
- `review_confirmed_passive`
- `review_contradicted_explicit`
- `review_contradicted_passive`
- `review_not_now`
- `review_avoid_topic`
- `review_no_signal`
- `review_cancelled`

if event enums stay smaller,
then `review_outcome.outcome_kind` must carry this detail and `memory_events` must at least reference that artifact.

## 8.3 minimal writeback order
when a review outcome lands:
1. append source evidence / response event if needed
2. create `review_outcome`
3. compute `trust_transition`
4. mutate `memory_item`
5. update `review_queue_item`
6. invalidate/update derived artifacts if required
7. request overlay/pack patch only if current-turn freshness or reuse safety requires it

hard rule:
queue resolution should not happen without a trust writeback trail.

## 8.4 replay/idempotency hint
explicit review handling should be replay-safe.

starting idempotency posture:
- one presented prompt -> one `presentation_id`
- one human reply / evidence bundle -> one `review_outcome.dedupe_key`
- repeated worker retries should not double-increment `attempt_count`

---

## 9. proactive interaction rules
`19` already allows `review_ping`.
this note narrows when it should win.

## 9.1 when `review_ping` is allowed
only if all apply:
- memory is high leverage
- passive reconfirmation is too slow or impossible
- timing window is favorable
- user burden is low
- there is no fresher contradiction unresolved
- the question can be phrased lightly
- `should_text_first?` would not prefer `no_act`

## 9.2 when `review_ping` should lose
prefer `no_act` or another move if:
- the memory is low-stakes
- silence already happened twice
- relationship temperature is cold
- the user recently ignored or rejected another memory check
- the same value could be captured passively in the next normal chat

## 9.3 relationship rule
proactive review should usually lose to:
- explicit callbacks
- cleaner check-ins
- silence

unless the memory is truly leverage-heavy.

## 9.4 copy rule
the visible message should reveal less than the internal rationale.

internal reason:
- `preference drift likely across 3 passive misses; explicit low-friction confirmation now beats stale roast targeting`

visible version:
- `quick one. still want me colder, or are we pretending you've softened?`

not:
- `i am verifying your interaction-preference drift based on recent evidence`

---

## 10. failure modes this contract is meant to stop

### 1. needy librarian failure
Purr asks every time something gets stale.

fix:
- passive-first policy
- single-moment rule
- silence = `no_signal`

### 2. silent rot failure
stale truths never get revisited and keep steering behavior forever.

fix:
- typed queue
- trust decay
- passive weakening + selective explicit checks

### 3. ignored ping = false memory failure
system treats no response as contradiction and trashes valid memory.

fix:
- separate `no_signal` from `contradicted_*`

### 4. queue/admin sludge failure
execution states leak into truth model and everything becomes unreadable.

fix:
- split `review_status` from queue status
- type `review_outcome`

### 5. local-only update failure
review changes one memory row but leaves rollups/proactive candidates stale.

fix:
- second propagation targets
- explicit invalidation rules

### 6. creepy predictive interrogation failure
Purr asks the user to validate backend abstractions directly.

fix:
- predictive memory stays mostly passive/backend-only
- explicit asks only when high leverage and naturally phrased

### 7. contradiction timidity failure
user clearly corrects something,
but the system only schedules a future review.

fix:
- explicit contradiction -> immediate suppression / override

---

## 11. build acceptance tests
this note should be considered real only if builders can satisfy these:

1. define at least **5 feedback surfaces** with different interruption costs and a clear preference order
2. define a typed outcome taxonomy that separates:
   - `confirmed_explicit`
   - `confirmed_passive`
   - `contradicted_explicit`
   - `contradicted_passive`
   - `no_signal`
   - `not_now`
   - `avoid_topic`
3. explicitly state that **silence is usually `no_signal`, not contradiction**
4. split `memory_item.review_status` from `review_queue_item.status`, and make clear that `resolved` is queue-level, not base memory truth-level
5. define how review outcomes propagate into:
   - memory truth/freshness
   - queue/cooldown state
   - pack policy
   - proactive candidates / rollups where relevant
6. define at least **3 memory-kind-specific decay policies** instead of one global rule
7. make proactive review stricter than in-chat review
8. preserve Purr taste:
   - no dashboard-admin tone
   - no repetitive memory interrogations
   - no turning backend prediction abstractions into user-facing jargon

---

## direct Hermes-to-Purr translation
Hermes already taught us:
- frozen hot state is useful
- salvage-before-loss is useful
- recall should be bounded
- memory needs durable evidence somewhere

this pass adds the thing Hermes does **not** give us:

**a real verification and trust-decay layer.**

what to steal from Hermes here:
- discipline
- boundedness
- cost-awareness
- event-minded salvage

what to reject:
- write-only memory with no revalidation semantics
- no distinction between silence and contradiction
- no passive reconfirmation contract
- no feedback orchestration layer deciding ask-now vs later vs never

Purr should be better because it treats memory as a living relationship system,
not just a saved-notes sidecar.

---

## direct conclusion
memory quality is not just:
- extract better
- store better
- retrieve better

it is also:
- **verify with taste**
- **decay honestly**
- **treat silence correctly**
- **propagate trust changes across the whole hidden runtime**

that is how Purr avoids both failure modes at once:
- clingy little admin cat
- stale liar cat

that is the lane.
