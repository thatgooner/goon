# Purr memory claim shapes + evidence + selection contract

## why this note exists
we already have:
- Hermes teardown
- prediction/background ops
- lifecycle / contradiction / review rules
- pack artifacts + slot caps
- session-window / episode lineage

what is still missing is the exact shared contract between:
- the extractor that reads new messages
- the ledger that stores truth
- the packer that chooses what reaches the model

right now that contract is implied across multiple notes.
that is good enough for vibes.
it is not good enough for `memory-ledger`, `memory-candidate-extractor`, or `memory-context-packer`.

this gap matters because a memory-first product does not break only when storage is bad.
it breaks when writer and reader disagree about what a memory even is.

---

## direct thesis
Purr should not use one generic `memory blob` model.

it should use **4 layers with a clean handoff**:

1. **immutable evidence refs**
   - exact spans back to raw events
2. **immutable memory events**
   - created / confirmed / challenged / superseded / rejected / decayed
3. **mutable current memory rows**
   - the current best truth state for each memory object
4. **packer-facing read model**
   - a denormalized selection surface built for slot/ranking logic

that is the contract.

not:
- flat prose memories
- substring editing
- packer-side guesswork about trust
- summary text standing in for evidence

Hermes is the warning here:
- rich behavior can happen in the live session
- but if the canonical searchable/reload surface is thinner than the real event trail, evidence quality quietly rots
- if compression/search summaries become the easiest artifact, they start impersonating truth

Purr should keep summaries as navigation aids only.
canonical truth must stay evidence-backed.

---

## note map
1. design rules
2. canonical shared envelope
3. v1 memory kinds + claim shapes
4. evidence contract
5. extractor output contract
6. merge / supersede / conflict rules
7. packer read model + ranking inputs
8. worked examples
9. build acceptance tests

---

## 1. design rules

### rule 1 — every durable memory object is identity-scoped first
mandatory on every durable row:
- `owner_id`
- `purr_id`
- `memory_lane`

never let:
- platform
- chat title
- session label
- raw source string

stand in for identity scope.

### rule 2 — exact evidence spans are first-class
if a memory claim cannot point back to:
- which window
- which message
- which excerpt/span

then it is weak memory, not strong memory.

### rule 3 — summaries are helpers, not proof
allowed:
- episode summary
- retrieval summary
- re-entry recap

not allowed:
- replacing exact evidence refs
- acting as the only source behind durable truth

### rule 4 — packer reads a prepared view
retrieval/packing should not re-derive trust from raw transcript joins every turn.
it should read from a prepared selection surface with:
- state
- trust
- scope
- ranking features
- slot eligibility

### rule 5 — claim shape beats pretty prose
`relationship texture` and `user preference` cannot stay as vague note paragraphs once extraction and packing are separate components.
we need typed claim shapes.

---

## 2. canonical shared envelope
these are the fields every `memory_item` should carry, no matter the kind.

### required envelope
- `memory_id`
- `owner_id`
- `purr_id`
- `memory_lane` (`private_1_1 | public_safe | catnet | system_ops`)
- `kind`
- `state` (`candidate | confirmed | stale | rejected | superseded`)
- `review_status` (`none | queued | due | ask_now | snoozed`)
- `contradiction_status` (`clean | challenged`)
- `pack_policy` (`hot | shadow | suppress | never`)
- `durability_scope` (`profile | relationship | episode | window | ephemeral`)
- `confidence`
- `salience`
- `volatility`
- `subject_key`
- `dedupe_key`
- `owner_surface`
- `episode_id`
- `origin_window_id`
- `created_at`
- `updated_at`
- `last_confirmed_at`
- `last_hit_at`
- `last_miss_at`
- `needs_review_at`
- `expires_at`
- `supersedes`
- `conflicts_with`
- `payload`

### field intent

#### `subject_key`
stable target of the claim.
examples:
- `profile:name`
- `pref:reply_tone`
- `boundary:pep_talks`
- `loop:send_photo`
- `pattern:late_night_avoidance`

#### `dedupe_key`
used to decide whether new evidence should:
- merge into an existing row
- create a sibling row
- supersede old truth

good rule:
`subject_key` = what the claim is about.
`dedupe_key` = what should collapse into the same active memory object.

#### `durability_scope`
prevents everything from pretending to be relationship-global truth.

use:
- `profile` for stable identity facts
- `relationship` for ongoing dynamic truths
- `episode` for chapter-specific meaning
- `window` for short-lived local facts
- `ephemeral` for near-term hints that should decay fast

---

## 3. v1 memory kinds + claim shapes
keep the first set small but typed.

## 3.1 `identity_fact`
used for stable explicit facts about the user.

### payload
- `attribute`
- `value`
- `source_explicitness`
- `sensitivity_level`

### examples
- name
- role/self-description
- city/timezone when clearly stated

### default posture
- promotes faster than inference-based kinds when explicit
- slow review cadence
- allowed in hard factual slots when `confirmed`

### dedupe key
- `identity:<attribute>`

### pack role
- `confirmed` -> `hot`
- `candidate` -> usually `shadow`
- `challenged` -> `suppress`

---

## 3.2 `preference`
used for likes/dislikes/style preferences that affect response behavior.

### payload
- `dimension`
- `value`
- `polarity` (`prefer | avoid`)
- `strength`
- `context_scope` (`global | topic_specific | episode_specific`)

### examples
- prefers colder phrasing
- hates wholesome pep talk energy
- likes short deadpan captions

### default posture
- medium review cadence
- can promote quickly if explicit and high-leverage
- can be softly used before full confirmation if low-risk

### dedupe key
- `preference:<dimension>:<context_scope>`

### pack role
- reply-shaping `confirmed` preferences can be `hot`
- weak or new preferences stay `shadow`

---

## 3.3 `boundary`
used for hard limits or do-not-do rules.

### payload
- `boundary_type`
- `rule_text`
- `severity`
- `applies_to` (`tone | topic | behavior | proactive | public | other`)

### examples
- do not go formal Turkish with the gooner persona
- don't bring up topic x again
- don't do pep-talk mode

### default posture
- highest leverage
- same-session effect matters
- usually hits live override immediately
- should enter hot truth fast if explicit

### dedupe key
- `boundary:<applies_to>:<boundary_type>`

### pack role
- active boundaries are priority lane-A truth
- `challenged` boundary conflict should block normal packing until resolved

---

## 3.4 `relationship_state`
used for ongoing relational texture that affects how Purr talks.

### payload
- `dimension`
- `value`
- `direction`
- `intensity`
- `support_type` (`explicit | repeated_behavior | inferred`)

### examples
- teasing lands when it is specific and earned
- user is touchy around fake-wholesome framing
- current dynamic is playful-hostile, not therapist-safe

### default posture
- should promote slower than identity facts
- often relationship-scope, not profile-scope
- review via indirect reconfirmation, not constant asks

### dedupe key
- `relationship:<dimension>`

### pack role
- usually lane-B texture
- strong repeated signals can be `hot`
- inference-heavy versions stay `shadow`

---

## 3.5 `open_loop`
used for unresolved threads with future pull.

### payload
- `loop_type`
- `topic`
- `expected_resolution`
- `opened_at`
- `urgency`
- `resolver_kind` (`user_followup | purr_followup | external_event`)

### examples
- user said they would send something later
- unfinished confession
- unresolved argument thread

### default posture
- high retrieval priority while unresolved
- decays quickly after resolution or repeated misses
- strong driver for proactive timing only when trust is high

### dedupe key
- `open_loop:<loop_type>:<topic>`

### pack role
- active unresolved loops are `hot`
- resolved loops should fall out fast

---

## 3.6 `episode_anchor`
used for important situational memory that should stay tied to a chapter, not pretend to be evergreen truth.

### payload
- `anchor_type`
- `summary_line`
- `topic_tags`
- `emotional_weight`
- `anchor_window_range`

### examples
- weird late-night confession on friday
- fight about tone drift in one session
- promise made during travel week

### default posture
- episode-scoped
- not main profile truth
- retrieved when situationally relevant

### dedupe key
- usually no aggressive global dedupe
- safest default: new row per major anchor

### pack role
- situational memory lane
- max 1-2 anchors in pack

---

## 3.7 `pattern_signal`
used for recurring rhythms and trigger-response patterns.

### payload
- `pattern_type`
- `trigger_context`
- `predicted_tendency`
- `horizon` (`turn | session | daily | long`)
- `hit_rate`
- `miss_rate`

### examples
- late-night silence often re-enters through meme/apology
- after one joke lane, topic often pivots serious

### default posture
- promote only after repeated evidence
- should decay if misses accumulate
- review more often than stable facts

### dedupe key
- `pattern:<pattern_type>:<trigger_context>:<horizon>`

### pack role
- mostly `shadow`
- can become `hot` only if strong, recent, and directly useful now

---

## 3.8 `next_action_candidate`
used for bounded operational prediction, not durable identity truth.

### payload
- `predicted_action_type`
- `target_topic`
- `horizon`
- `why_now`
- `expected_value`
- `ttl`

### examples
- likely next ask
- likely callback opportunity tonight
- likely mood/topic pivot in next few turns

### default posture
- short TTL
- internal-first
- validated via hit/miss more than direct human review

### dedupe key
- `next_action:<predicted_action_type>:<target_topic>:<horizon>`

### pack role
- mostly retrieval helper only
- at most 0-2 hints in pack
- never state as hard fact

---

## 4. evidence contract
Purr needs exact evidence refs, not only memory prose.

## 4.1 canonical `memory_evidence_ref`
minimum fields:
- `evidence_id`
- `memory_id`
- `owner_id`
- `purr_id`
- `episode_id`
- `window_id`
- `message_id`
- `span_start`
- `span_end`
- `source_type` (`chat | proactive_event | app_event | catnet_event | system_summary | other`)
- `excerpt_text`
- `excerpt_hash`
- `captured_at`
- `evidence_weight`
- `explicitness`
- `speaker_role`

### why exact spans matter
without exact spans, the system starts doing fake grounding:
- summary says it happened
- memory row says it is backed
- but nobody can point to the real line

that is how evidence blur starts.

## 4.2 evidence classes

### direct evidence
best class.
examples:
- user says it explicitly
- user directly corrects Purr
- user directly confirms

### repeated behavioral evidence
good, but weaker than direct statement.
examples:
- same preference signaled across multiple sessions
- same loop pattern keeps hitting

### derived evidence
allowed only as helper.
examples:
- episode summary
- extracted structured interpretation
- timing score rationale

hard rule:
derived evidence can support ranking.
it cannot replace direct evidence.

## 4.3 summary provenance rule
if `source_type=system_summary`, keep a backpointer to the exact raw refs it summarizes.
summaries may compress access.
they may not sever lineage.

---

## 5. extractor output contract
this is what `memory-candidate-extractor` should emit from new events.

## 5.1 canonical candidate output
- `candidate_id`
- `owner_id`
- `purr_id`
- `episode_id`
- `window_id`
- `proposed_kind`
- `memory_lane`
- `subject_key`
- `dedupe_key`
- `payload`
- `explicitness`
- `leverage`
- `sensitivity`
- `volatility`
- `time_horizon`
- `suggested_action` (`ask_now | defer | silent_store | drop`)
- `candidate_conflicts`
- `candidate_supersedes`
- `pack_urgency`
- `evidence_refs`
- `extractor_confidence`

### important split
extractor proposes.
policy decides.

the extractor is allowed to say:
- `this looks like a preference`
- `likely high leverage`
- `probably conflicts with preference:reply_tone`
- `suggested_action=silent_store`

but the lifecycle/feedback policy remains centralized.

## 5.2 extractor quality rules

### should do
- keep outputs typed and compact
- point to exact evidence spans
- name likely conflicts/supersedes
- score leverage and timing fitness

### should not do
- directly mutate durable truth
- invent long essays
- collapse multiple incompatible claims into one blob
- output pack-ready prose instead of structured payloads

---

## 6. merge / supersede / conflict rules
without this, the ledger becomes duplicate sludge.

## 6.1 append evidence to the same row when
- same `dedupe_key`
- same active meaning
- no real contradiction
- new evidence increases confidence or freshness

example:
multiple explicit statements reinforcing `preference:reply_tone=colder`

## 6.2 create a sibling row when
- same broad topic, but different scope
- same dimension, but episode-specific exception
- same signal, but different horizon or trigger

example:
- global preference: hates pep-talk energy
- episode-specific preference: wanted gentler handling on one bad day

## 6.3 supersede old truth when
- direct correction clearly replaces it
- newer explicit truth beats older stable truth
- the old truth was once valid but should stop driving behavior now

example:
- old: `preference:reply_tone=balanced`
- new: `preference:reply_tone=colder`

then:
- old row -> `superseded`
- new row -> `confirmed` or high-confidence `candidate`
- old row stays in audit trail, out of hot pack

## 6.4 mark conflict when
- new evidence pressures active confirmed truth
- resolution is not yet clean
- immediate packing would risk two incompatible truths appearing together

then:
- old row -> `contradiction_status=challenged`
- old pack policy -> `suppress`
- new row enters candidate lane with review pressure

## 6.5 keep episode-only when
- the meaning is real but local
- promoting it relationship-wide would be dishonest

example:
- one-session vulnerability spike
- one-night mood exception
- temporary context-specific preference

---

## 7. packer read model + ranking inputs
this is the missing bridge between the ledger and the prompt.

## 7.1 `pack_candidate_view`
minimum fields:
- `memory_id`
- `owner_id`
- `purr_id`
- `memory_lane`
- `kind`
- `state`
- `review_status`
- `contradiction_status`
- `pack_policy`
- `durability_scope`
- `slot_family`
- `confidence`
- `salience`
- `freshness_score`
- `relevance_tags`
- `response_value`
- `timing_value`
- `evidence_strength`
- `episode_distance`
- `open_loop_weight`
- `suppression_reason`

## 7.2 slot families
route selection before scoring.

### lane A — hard truth
- boundaries
- stable identity facts
- high-impact preferences

### lane B — relationship state
- relationship texture
- active dynamic cues

### lane C — situational memory
- open loops
- episode anchors
- strong recent pattern signals

### lane D — predictive helpers
- next_action_candidate
- low-volume pattern hints

### lane E — evidence fallback
- micro-excerpts
- transcript snippets only if higher lanes cannot justify the move

## 7.3 ranking flow
1. filter by `owner_id` + `purr_id`
2. filter by `memory_lane`
3. filter by scope eligibility (`relationship | episode | window`)
4. suppress rejected/superseded/unsafe rows
5. suppress challenged truth from hard-fact slots
6. route by `slot_family`
7. score within each lane
8. enforce lane caps
9. attach micro-evidence only for selected rows
10. use transcript fallback last

## 7.4 ranking features that matter most

### trust gate
- confirmed > stale > candidate
- challenged truth is often suppressed before scoring

### response value
would this change the next reply in a useful way?

### freshness
is this still alive enough to matter now?

### evidence strength
how much exact support is behind it?

### episode distance
recent related anchors beat distant irrelevant history.

### open-loop pressure
unresolved loops deserve higher retrieval weight than decorative memories.

### prediction restraint
prediction hints should be penalized unless:
- directly relevant now
- high hit-rate
- cheap to express

---

## 8. worked examples

## example 1 — explicit style preference
user message:
`don't go wholesome on me. colder is better.`

extractor output:
- `proposed_kind=preference`
- `subject_key=pref:reply_tone`
- `dedupe_key=preference:reply_tone:global`
- `payload={dimension: reply_tone, value: colder, polarity: prefer, strength: high, context_scope: global}`
- `explicitness=high`
- `leverage=high`
- `suggested_action=silent_store`
- evidence span -> exact message excerpt

ledger effect:
- if old tone preference exists and conflicts, old row becomes `challenged` or `superseded`
- new row becomes fast-promote candidate
- next reply can use live override if needed

pack effect:
- enters lane A or live delta
- should affect response style immediately

## example 2 — hard boundary
user message:
`don't do that formal turkish teacher shit again.`

extractor output:
- `proposed_kind=boundary`
- `subject_key=boundary:tone_formality`
- `payload={boundary_type: no_formal_turkish, severity: high, applies_to: tone}`
- `suggested_action=ask_now` only if wording is ambiguous; otherwise `silent_store`
- `pack_urgency=immediate`

ledger effect:
- store/update active boundary
- mark conflicting tone assumptions challenged

pack effect:
- priority lane-A truth
- immediate live override if current pack was drifting wrong

## example 3 — unresolved loop
user message:
`i'll send it tonight. remind me if i vanish.`

extractor output:
- `proposed_kind=open_loop`
- `subject_key=loop:send_it`
- `payload={loop_type: send_item, topic: send_it, urgency: medium, resolver_kind: user_followup}`
- `suggested_action=silent_store`

ledger effect:
- create active loop
- set review/proactive timing window

pack effect:
- lane C while unresolved
- eligible for proactive planner if confidence and cooldown fit

## example 4 — weak situational inference
user message:
`lol whatever`
plus recent context suggests annoyance.

extractor output:
- maybe `relationship_state` or `pattern_signal`
- `explicitness=low`
- `leverage=medium`
- `suggested_action=drop` or `defer`

ledger effect:
- do not force durable truth from one weak line

pack effect:
- no hard truth
- maybe weak shadow only if later evidence stacks

---

## 9. build acceptance tests
future implementation should not count as correct unless it can pass something like this:

- explicit correction can supersede an old preference without leaving duplicate active truth
- a boundary can affect the next reply without full session-pack rebuild
- an episode anchor keeps exact evidence refs instead of only a summary line
- `pattern_signal` cannot promote from one hit alone
- `next_action_candidate` decays fast and never becomes hard identity truth
- challenged memories are suppressed from factual slots
- packer ranks from a prepared selection view, not transcript joins alone
- transcript fallback appears only when structured memory + micro-evidence are insufficient
- summary-derived evidence always points back to raw refs

---

## strongest conclusions
- the missing spec is the **shared contract** between extraction, storage, and selection.
- Purr needs **typed memory claims**, not one generic memory blob.
- exact **evidence spans** must be first-class, or the system will repeat Hermes-style evidence blur.
- the ledger should be modeled as:
  - immutable evidence refs
  - immutable memory events
  - mutable current memory rows
  - a packer-friendly read model
- `relationship texture` must become typed dimensions, not vague note paragraphs, if extractor and packer are separate components.
- the extractor should propose candidates and suggested actions, but lifecycle policy stays centralized.
- the packer should rank from a gated read model, not infer trust ad hoc from raw transcript joins.

if we lock this contract, the parked tasks stop being vague names and start becoming buildable slices.