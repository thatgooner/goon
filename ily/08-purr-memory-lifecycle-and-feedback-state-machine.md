# Purr memory lifecycle + feedback state machine

## why this note exists
we already have:
- Hermes teardown
- session-pack / hot-pack discipline
- prediction + background ops
- broad memory kinds

what was still missing was the operating rulebook.

not `what tables might exist`.
not `memory is important`.

the missing piece was:

`when does a memory become real, when does Purr ask, when does it stay quiet, and when does it stop trusting old truth?`

that is the actual state machine.

without it, the ledger stays vague, retrieval gets sloppy, and proactive timing gets creepy.

---

## direct thesis
Purr should keep the canonical lifecycle small, then layer review + contradiction control on top.

do **not** make this a giant unreadable enum.

do this instead:
- main lifecycle answers: `what is this memory's truth status?`
- review status answers: `does this need human confirmation and when?`
- contradiction status answers: `is active truth currently under pressure?`
- pack policy answers: `should this affect the next reply or stay out of view?`

that gives enough control without turning memory into bureaucratic sludge.

---

## canonical objects

### 1. `memory_item`
the durable row.

minimum fields:
- `memory_id`
- `owner_id`
- `purr_id`
- `kind`
- `state`
- `review_status`
- `contradiction_status`
- `confidence`
- `salience`
- `volatility`
- `created_at`
- `updated_at`
- `last_confirmed_at`
- `last_hit_at`
- `last_miss_at`
- `needs_review_at`
- `expires_at`
- `supersedes`
- `conflicts_with`
- `pack_policy`

### 2. `memory_evidence_ref`
points back to raw truth.

minimum fields:
- `evidence_id`
- `memory_id`
- `session_id`
- `message_id` or span ref
- `source_type` (`chat | proactive_event | app_event | catnet_event | other`)
- `excerpt`
- `captured_at`
- `weight`

### 3. `memory_event`
mutation history, not just latest state.

examples:
- created
- promoted
- challenged
- confirmed
- deferred_for_review
- superseded
- rejected
- decayed
- revived

why this matters:
- lets us audit why Purr thinks something
- stops contradiction handling from becoming invisible text surgery

### 4. `live_override`
small turn-level patch lane for same-session freshness.

used for:
- explicit corrections
- direct contradictions
- high-leverage new preferences
- safety-sensitive updates

TTL should be short.
it is not durable truth by itself.
it is a bridge between fresh evidence and the next response.

### 5. `review_queue`
not every memory needs its own noisy scheduler logic inline.
keep a separate queue artifact that can be recalculated.

minimum fields:
- `queue_id`
- `memory_id`
- `reason`
- `priority`
- `due_at`
- `cooldown_until`
- `attempt_count`
- `last_attempt_at`
- `status`

---

## main lifecycle states
keep the core set tight:

### `candidate`
Purr has enough evidence to keep it, not enough trust to treat it as durable truth.

examples:
- a likely preference from one clear statement
- a pattern signal after 1-2 hits
- a soft relationship read that might be true

### `confirmed`
trusted enough to influence normal behavior without constant re-checking.

examples:
- stable tone preference
- explicit identity fact
- repeated open loop that clearly exists
- a long-horizon pattern with enough evidence

### `stale`
used to be trusted, now needs caution.

this is not rejection.
this means:
- the memory may still be true
- but recency, misses, or volatility mean Purr should stop leaning on it too hard

### `rejected`
not valid truth.
keep only for audit and anti-relearn.

### `superseded`
was once valid, later replaced by a newer truth.

important difference:
- `rejected` = wrong / not supported
- `superseded` = once worked, no longer the active truth

---

## overlay states

### review status
small overlay:
- `none`
- `queued`
- `due`
- `ask_now`
- `snoozed`

### contradiction status
small overlay:
- `clean`
- `challenged`

### pack policy
derived or stored helper:
- `hot` = safe to enter bounded response pack
- `shadow` = can softly influence ranking, but not as hard truth
- `suppress` = keep out of active factual pack until resolved
- `never` = rejected/superseded/unsafe for prompt use

---

## intake decision machine
for each extracted memory candidate, score these:
- `leverage` — would being wrong change reply quality, tone, or future behavior?
- `explicitness` — direct user statement vs inference
- `contradiction_pressure` — does it clash with active confirmed truth?
- `volatility` — likely to change often or be context-bound?
- `sensitivity` — creepy/private/safety-sensitive if stated too strongly?
- `timing_fitness` — is this a good moment to interrupt and ask?

then force one of 4 actions.

### 1. `ask_now`
use when:
- the user directly corrected active truth
- contradiction blocks the next reply
- the fact/preference is high-leverage and needed immediately
- boundary/safety implications are real

examples:
- `no, not like that. colder.`
- `that isn't true anymore.`
- `don't bring that up again.`

effect:
- create/update row immediately
- mark old truth `challenged` if needed
- inject a `live_override`
- if user confirms clearly, promote fast

### 2. `defer`
use when:
- valuable but not needed this turn
- ambiguous enough that asking now would feel clumsy
- better to confirm through a later opening

examples:
- medium-value preference with unclear permanence
- uncertain relationship inference
- pattern signal with only partial evidence

effect:
- store as `candidate`
- set `review_status=queued`
- attach `needs_review_at`
- keep it out of hard factual pack for now

### 3. `silent_store`
use when:
- explicit
- low-risk
- low-ambiguity
- not creepy if softly used
- not currently contradicted

examples:
- clear tone preference
- obvious like/dislike
- straightforward factual detail with low downside

effect:
- store as `candidate`
- `review_status=none`
- `pack_policy=shadow`
- can influence retrieval lightly before full confirmation

### 4. `drop`
use when:
- low evidence
- low leverage
- highly transient
- duplicate with no new evidence
- speculative prediction with no operational value
- too creepy to keep as durable truth

effect:
- no durable memory item
- or keep only in ephemeral extraction logs

---

## promotion + contradiction transitions

### new memory path
1. raw event/message arrives
2. extractor proposes candidate
3. system chooses `ask_now | defer | silent_store | drop`
4. if not dropped, memory row gets evidence refs + initial state

### promotion rules
`candidate -> confirmed` when one of these is true:
- explicit user confirmation
- explicit direct statement with low ambiguity and high leverage
- repeated consistent evidence across separate turns/sessions
- contradiction resolved in favor of the new item

### rejection rules
`candidate -> rejected` when:
- user denies it
- later evidence breaks it cleanly
- it expires with weak support and no leverage

### staleness rules
`confirmed -> stale` when:
- volatility window expires
- repeated misses suggest drift
- surrounding behavior shifts enough that confidence should drop

`stale -> confirmed` when:
- user reconfirms it
- repeated indirect evidence supports it again

`stale -> rejected` when:
- new evidence makes it clearly false

### contradiction rules
when new evidence conflicts with a confirmed memory:
- old item becomes `contradiction_status=challenged`
- old `pack_policy` drops to `suppress`
- new item enters as `candidate` with high contradiction pressure

resolution outcomes:
- explicit correction -> old becomes `superseded`, new becomes `confirmed`
- ambiguity remains -> both stay out of hard factual pack; review gets queued
- new evidence was just a joke/contextual exception -> old returns to `clean`, new becomes episode-only or `rejected`

hard rule:
never pack two incompatible truths as equal active facts.

---

## what must hit the live override lane
this is the fix for Hermes' `live write / frozen read` weakness.

the session pack can stay mostly frozen.
truth cannot.

send to `live_override` when the user gives:
- explicit correction
- direct contradiction
- new hard boundary
- high-leverage preference change
- safety-sensitive update

what should **not** hit live override:
- low-confidence pattern guesses
- low-leverage profile trivia
- speculative next-action candidates
- weak mood inference

rule of thumb:
if waiting until later would make the very next reply feel fake, it belongs in live override.

---

## retrieval packing rules
retrieval should obey the state machine.
not fight it.

### pack order
1. `live_override`
2. confirmed hard truths / active constraints
3. open loops
4. strong recent pattern signals
5. at most 1-2 shadow candidates
6. tiny evidence payload if needed
7. transcript snippets only as fallback evidence

### suppression rules
- `challenged` items -> suppress from factual pack
- `stale` items -> only include if directly relevant, with lower weight
- `candidate` items -> never dominate the pack
- `rejected` / `superseded` -> never enter hot pack

### prediction rule
prediction memory is allowed in the pack only if:
- it is relevant now
- it changes response choice or timing
- it fits within the 0-2 hint cap

if a prediction needs a paragraph to justify itself, keep it out.

---

## review scheduling policy
verification has to help without breaking the spell.
so the scheduler needs an annoyance budget, not just a due date.

### cadence by memory kind

#### profile / stable facts
review only on contradiction or rare drift checks.
rough cadence:
- 90-180 days
- often passive reconfirmation is enough

#### preferences
review faster because drift is normal.
rough cadence:
- 14-45 days for active/high-impact preferences
- sooner after repeated misses

#### relationship memory
prefer indirect reconfirmation through live conversation.
rough cadence:
- 30-60 days if behaviorally important

#### open loops
review by promise weight and time sensitivity.
rough cadence:
- hours to 7 days
- resolve fast or decay fast

#### pattern signals
never promote from one hit.
require repeated evidence.
rough cadence:
- turn/session horizon: hours to 14 days
- long horizon: 30-60 days with miss tracking

#### next-action candidates
usually do not ask the human directly.
validate via hit/miss internally.
TTL should be short.

### anti-spam caps
starting rule:
- max 1 explicit memory check inside an active session window
- max 1 proactive review ping per day
- max 3 review attempts per memory before heavy cooldown

if the moment is emotionally bad, crowded, or low-value, defer.

---

## proactive timing gates
proactive behavior should use memory state as a gate, not just a ranking feature.

### good triggers
only allow proactive sends when supported by:
- confirmed open loops
- repeated pattern signals
- recent hit-rate on similar timing
- response history + cooldown fit

### bad triggers
never trigger proactive sends from:
- raw candidates
- challenged memories
- stale truths with no reconfirmation
- low-confidence next-action guesses

important brake:
`contradiction_status=challenged` should usually reduce proactive score.
if Purr is not sure what is true anymore, it should get quieter before it gets bolder.

### notification copy rule
the notification should reveal less than the internal rationale.

Purr can think:
- `he usually re-enters after going quiet like this when that topic is still unresolved`

but send:
- `you vanished again. cute.`

not:
- `you are following your 3-day avoidance pattern about topic x`

---

## failure modes this state machine is meant to stop

### 1. same-session stale correction failure
user fixes something and Purr still answers from old truth.

fix:
- live override lane

### 2. candidate landfill
every little signal becomes durable memory.

fix:
- drop aggressively
- require repeated evidence
- use TTL/decay

### 3. contradiction sludge
multiple incompatible truths sit together forever.

fix:
- `challenged` + `suppress`
- explicit supersede paths

### 4. needy review behavior
Purr keeps asking whether it remembers correctly.

fix:
- annoyance budget
- defer by default
- indirect reconfirmation whenever possible

### 5. creepy prediction overclaim
internal guesses leak out as fake certainty.

fix:
- low-confidence predictions stay internal
- next-action candidates decay fast

### 6. proactive misfire
Purr pings with stale or shaky assumptions.

fix:
- challenged/stale states reduce proactive score
- proactive sends require stronger evidence than normal retrieval

---

## direct implications for the invisible build order
if this note is right, the first build slices still stay the same,
but now their contracts are tighter:

1. structured ledger
   - must support lifecycle, contradiction overlays, evidence refs, and review queue state
2. retrieval/context packer
   - must respect `live_override`, `pack_policy`, and suppression rules
3. contradiction + feedback loop
   - must implement `ask_now | defer | silent_store | drop`
4. salvage/review/timing jobs
   - must update confidence, decay, due dates, and proactive eligibility

this still does **not** justify flashy tools.
it sharpens the memory spine.

---

## short verdict
Hermes taught the right discipline:
- stable session behavior pack
- durable raw history
- on-demand recall
- memory salvage before compression

but for Purr that is still not enough.

Purr needs one more layer of seriousness:
- memory truth must have lifecycle
- contradictions must become state transitions
- verification must have taste
- same-session corrections must stay live
- proactive behavior must be gated by trust, not vibes

that is how `i remember everything` stops sounding fake.