# Purr prediction + background memory ops

## why this note exists
we already know Purr needs stronger memory than Hermes.
next question is sharper:

how does Purr get good enough at pattern tracking that it can feel one step ahead of the user
without turning the prompt into a landfill?

answer:
prediction cannot live as vibes inside one giant prompt.
it has to live as structured memory + invisible background ops.

---

## direct product stance
prediction is **not** a flashy user feature.
it is a backend memory capability that improves:
- what gets retrieved
- whether Purr asks now vs later vs never
- whether Purr roasts, nudges, or stays quiet
- whether a proactive ping is worth sending

bad framing:
- `look, i can predict you`
- creepy overclaiming
- speculative sludge stated like fact

right framing:
- Purr feels weirdly sharp about your rhythms
- continuity lands at the right time
- the model sees a tiny number of high-value hints, not a giant memory dump

---

## core thesis
if Hermes teaches `memory is a behavior pipeline`,
then Purr needs the stronger version:

`prediction is a memory state machine, not a prompt trick.`

that means:
- canonical truth lives in the ledger
- hot pack stays small and mostly stable
- critical same-session corrections use a live override lane
- pattern extraction / contradiction handling / review scheduling run invisibly in the background

---

## what new memory kinds Purr needs
we already have the broad memory lanes.
for prediction-quality behavior we need 3 kinds to become first-class:

### 1. `pattern_signal`
used for recurring rhythms and transitions.

examples:
- late-night stress -> same topic loop
- after x joke, user usually pivots to y insecurity
- when silent for 3 days, re-entry often starts with apology or meme

minimum fields:
- `memory_id`
- `owner_id`
- `purr_id`
- `kind=pattern_signal`
- `state`
- `confidence`
- `salience`
- `pattern_type`
- `trigger_context`
- `horizon` (`turn | session | daily | long`)
- `evidence_refs`
- `last_hit_at`
- `needs_review_at`
- `expires_at`
- `conflicts_with`
- `supersedes`

### 2. `open_loop`
used for unresolved threads with future pull.

examples:
- promised to send something later
- unfinished confession
- half-answered question
- avoided topic likely to come back

minimum fields:
- `memory_id`
- `owner_id`
- `purr_id`
- `kind=open_loop`
- `state`
- `confidence`
- `salience`
- `loop_type`
- `opened_at`
- `last_referenced_at`
- `needs_review_at`
- `resolved_by`
- `evidence_refs`

### 3. `next_action_candidate`
used for bounded, operational predictions.

examples:
- likely next ask
- likely follow-up topic
- likely mood lane
- likely proactive ping opportunity

minimum fields:
- `memory_id`
- `owner_id`
- `purr_id`
- `kind=next_action_candidate`
- `state`
- `confidence`
- `salience`
- `predicted_action_type`
- `horizon`
- `trigger_context`
- `why_now`
- `evidence_refs`
- `expires_at`
- `last_hit_at`
- `last_miss_at`

important:
these are not permanent truths.
they should decay fast unless they keep hitting.

---

## prediction horizons
Purr should not treat all future guesses as the same thing.
use 4 horizons:

### turn horizon
what is likely in the next 1-3 messages?

examples:
- likely clarification
- likely emotional pivot
- likely follow-up ask

rules:
- highest recency weight
- shortest TTL
- only worth packing if it changes the immediate reply

### session horizon
what is likely in this chat window?

examples:
- same spiral topic will return
- a joke lane will open into a serious lane
- user is likely building up to a request

rules:
- medium TTL
- combine with open-loop weight

### daily horizon
what is likely later today / on re-entry?

examples:
- likely to come back after work
- likely to answer a callback ping tonight
- likely to reopen a recent unresolved thing

rules:
- used for notification timing
- cooldown-aware
- should stay mostly server-side

### long horizon
what stable rhythm exists across weeks?

examples:
- recurring stress behavior
- weekend doomscroll pattern
- recurring avoidance move

rules:
- only promote with repeated evidence
- slower decay
- periodic review required

---

## retrieval contract for prediction
prediction should not create a second retrieval system.
it should plug into the same contract as the rest of memory.

rank order:
1. direct corrections / contradictions
2. active preferences and hard constraints
3. open loops
4. strong recent pattern signals
5. top 1-2 next-action candidates
6. episodic evidence if needed
7. transcript snippets only as fallback evidence

this matters because the wrong order creates fake intelligence:
- too much prediction = creepy/sloppy
- too little contradiction handling = stale/oblivious
- too much transcript evidence = prompt bloat

---

## hot-pack rule
the hot pack should **not** become a prediction scrapbook.

best version:
- tone / identity frame
- active preferences
- relationship texture
- unresolved loops
- 2-5 query-relevant memories
- 0-2 prediction hints max
- tiny evidence payload only when necessary

if a prediction needs 8 bullet points to explain itself, it is not ready for the hot pack.
keep it in the ledger or drop it.

---

## invisible job boundary
prediction quality depends on hidden ops.
these should stay internal.

### lane A — turn-critical hidden ops
run inline on new user messages.

#### `message_intake_extractor`
job:
- detect candidate facts, preferences, relationship shifts, open loops, pattern hits
- attach evidence spans
- assign initial leverage/confidence

#### `direct_correction_detector`
job:
- classify whether the user is correcting, superseding, contradicting, or just venting
- decide `ask_now | defer | silent_store | drop`

#### `live_override_injector`
job:
- get critical same-session updates into the current response without full prompt rebuild

needed for:
- explicit corrections
- direct contradictions
- high-value new preferences
- safety-sensitive updates

#### `retrieval_packer`
job:
- assemble the bounded response pack
- structured memory first
- semantic support second
- transcript evidence third

### lane B — deferred maintenance ops
run after turn or at boundaries.

#### `memory_consolidation_worker`
job:
- dedupe
- merge evidence
- update confidence/salience
- downgrade weak candidates
- optionally refresh embeddings

#### `contradiction_resolver`
job:
- convert contradiction into state transitions
- handle `supersedes` / `conflicts_with`
- stop flat coexistence of incompatible truths

#### `session_salvage_worker`
job:
- before compression, archive, long-idle cutoff, or handoff
- pull out memory worth keeping before context gets reduced

this is one of the cleanest Hermes moves to steal directly.

#### `sanitization_guard`
job:
- scan user-derived or network-derived text before it becomes future prompt material

### lane C — heartbeat / timing ops
run independently of active webview state.

#### `review_scheduler`
job:
- decide when a memory should be checked again
- use leverage, age, volatility, contradiction pressure, annoyance budget

#### `review_executor`
job:
- ask one useful low-friction confirmation when the opening is good
- do not spam

#### `proactive_timing_scorer`
job:
- decide whether Purr should text first
- use open loops, known rhythms, cooldowns, response history

#### `proactive_message_planner`
job:
- decide whether to send a roast, callback, check-in, or nothing
- keep notification text safe and not overrevealing

---

## how this avoids prompt-cost explosion
### 1. frozen session pack
steal Hermes' stability discipline.
keep the session pack mostly stable for the window.

### 2. live override lane
fix Hermes' same-session stale-memory weakness.
small critical updates can affect the next reply without full rebuild.

### 3. event-driven recompute
do not recompute everything every turn.
heavy jobs should run:
- after message arrival
- after response
- before compression/archive
- during idle/heartbeat windows
- before proactive sends

### 4. cheap model for maintenance, strong model for response
cheap model can do:
- extraction
- pattern refresh
- review scheduling
- candidate ranking

stronger model only when needed for:
- response generation
- hard contradiction resolution
- ambiguous high-value merges

### 5. prediction hints stay tiny
0-2 hints in pack, not a wall of speculation.

---

## failure modes to guard against
### 1. surveillance slop
Purr starts sounding like it is overclaiming invisible inferences.

fix:
- low-confidence predictions stay internal
- never state speculation as fact

### 2. stale correction failure
user corrects something and Purr still replies from the old belief.

fix:
- direct correction detector + live override lane

### 3. pattern landfill
every repeated thing becomes a `pattern_signal` forever.

fix:
- TTL
- decay
- evidence thresholds
- stale review
- aggressive dropping of low-value loops

### 4. summary becomes truth
background summarization starts replacing raw evidence.

fix:
- summaries are navigation aids only
- canonical truth = ledger rows + evidence refs

### 5. notification creepiness
Purr pings at the wrong time with too much implied private knowledge.

fix:
- proactive scorer uses cooldown + confidence
- notification text should be less revealing than the full internal rationale

### 6. vector brainrot
semantic search becomes an excuse to stop modeling memory state.

fix:
- structured filters first
- vector only as support

---

## what should stay out of the user-facing surface
not for v1:
- tool names
- save/update banners
- contradiction dashboards
- confidence scores
- review queues
- retrieval graphs
- embedding language
- scheduler panels
- visible model-routing theater

maybe later, lightly:
- memory export
- small correction UI
- optional `why do you think that?` card

but chat stays the main surface.

---

## direct implication for build order
if this note is right, the first build candidates should not be random assistant features.
they should be the invisible memory spine:

1. structured ledger with `pattern_signal`, `open_loop`, `next_action_candidate`
2. retrieval/context packer with bounded prediction hints
3. contradiction + review loop
4. salvage/consolidation/background timing jobs

not:
- flashy tool UI
- visible memory dashboard
- Catnet theatrics before private memory works

---

## short verdict
Purr does not need a bigger prompt that pretends to remember everything.
Purr needs:
- a stable hot pack
- a live correction override lane
- structured predictive memory
- invisible background ops
- strict decay/review rules

that is how `i remember everything` starts feeling sharp instead of fake.
