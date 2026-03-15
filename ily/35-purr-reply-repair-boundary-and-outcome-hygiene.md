# Purr reply-repair, boundary handoff, and outcome hygiene

## why this note exists

`ily/33` made one useful Hermes point impossible to ignore:
- continuation repair is real runtime quality work
- truncation recovery and ack-repair can make a medium memory system feel less flaky
- boundary hygiene matters as much as steady-state memory

`ily/34` then closed the reply-planner calibration seam:
- `prediction_outcome`
- `move_outcome`
- `pack_outcome`
- replay-safe writeback

but one seam was still too loose:

**what happens when the private reply itself is partial, repaired, retried, rolled back, or carried across a boundary before it is honestly final?**

that matters because without one clean contract here, builders will accidentally do one of the stupid versions:
- count synthetic continuation control text as real chat evidence
- treat `repair succeeded` like `move helped`
- let one logical reply splinter into multiple assistant turns with no shared identity
- let compression/re-entry summarize repair sludge as if it were relationship truth

latest Hermes code on this machine sharpened the risk:
- truncation repair appends synthetic continuation prompts into history
- Codex intermediate-ack repair also appends synthetic control prompts
- compression can summarize those artifacts later
- SQLite restore can keep the text while losing the metadata that said `this was incomplete/repair-only`

Purr should steal the continuity boost.
Purr should reject the transcript pollution.

---

## direct verdict

### one-line answer
**reply repair is its own backend-only hygiene plane. it is not the same thing as move quality, prediction quality, or transcript truth.**

### translation
Purr should split this seam into 5 layers:
1. `reply_move_plan` — why we chose this reply move
2. `reply_execution_attempt` — one actual model/tool generation attempt
3. `repair_outcome` — whether truncation/retry/rollback/boundary repair succeeded
4. `move_outcome` — whether the chosen reply move helped
5. `assistant_message_event` — the final durable user-visible reply, if one honestly exists

### strongest rule
**one logical private reply may span many attempts, but it should finalize into at most one canonical assistant transcript event. synthetic repair/control text never becomes evidence.**

---

## Hermes lesson that forces this note

Hermes gets real continuity mileage from repair behavior in `vendor/hermes-agent/run_agent.py`:
- truncated replies can be continued
- Codex intermediate `i'll inspect / let me check` fluff can trigger a repair loop
- incomplete replies can get another pass instead of just dying
- compression and resume try to keep the task moving

that part is worth stealing.

what is **not** worth stealing:
- Hermes often persists synthetic continuation prompts as normal conversation-shaped turns
- interim partial assistant text can remain in history instead of being normalized into one final turn
- compaction can later summarize those repair artifacts
- restored history can lose `finish_reason` / repair metadata while keeping the raw text

hard translation:

**Hermes proves repair helps continuity.
it also proves repaired control text must not be allowed to masquerade as conversation truth.**

---

## the seam this note closes

before this note, the repo already had answers for:
- how memory claims commit safely (`ily/14`)
- how prompt/session artifacts stay typed (`ily/16`)
- how hidden runtime lanes split by deadline (`ily/18`)
- how reply-move outcomes write back (`ily/34`)

what was still missing:
1. how one `plan_id` survives multiple generation attempts
2. what a repaired/partial reply writes durably before finalization
3. when `repair_outcome` closes vs when `move_outcome` closes
4. how compression/re-entry carries unfinished reply state without transcript contamination
5. which goldens catch repair-specific failure seams

this note freezes all 5.

---

## canonical object split

## 1. `reply_move_plan`
this stays exactly what `ily/15` / `ily/34` already wanted:
- the hidden private-chat decision artifact
- created before generation
- one plan per intended user-visible reply

it answers:
- what move was chosen
- which drivers mattered
- what prompt-visible admissions were allowed

it does **not** answer:
- whether generation got truncated
- whether continuation repair was needed
- whether the reply actually landed well

## 2. new typed artifact: `reply_execution_attempt`
this is the missing runtime artifact for one actual generation attempt.

minimum fields:
- `attempt_id`
- `plan_id`
- `owner_id`
- `purr_id`
- `window_id`
- `epoch_id`
- `attempt_index`
- `provider_name`
- `provider_run_id` (nullable)
- `attempt_kind` (`initial | continuation | retry | boundary_resume | fallback`)
- `started_at`
- `completed_at`
- `finish_state` (`completed | truncated | incomplete | tool_interrupted | empty | rolled_back | failed`)
- `repair_needed` (bool)
- `prompt_artifact_refs[]`
- `output_artifact_ref` (nullable)
- `superseded_by_attempt_id` (nullable)
- `dedupe_key`

purpose:
- preserve execution provenance without pretending each attempt is a separate chat turn
- let one logical reply span multiple model calls cleanly
- give repair logic something real to point at

hard rule:
**`reply_execution_attempt` is execution provenance, not transcript truth.**

## 3. new typed artifact: `repair_outcome`
purpose:
- answer whether repair/handoff logic successfully rescued a damaged reply path

minimum fields:
- `repair_outcome_id`
- `plan_id`
- `owner_id`
- `purr_id`
- `trigger_attempt_id`
- `final_attempt_id` (nullable)
- `repair_kind` (`truncate_continue | intermediate_ack_recover | empty_retry | rollback_abort | boundary_carry | boundary_abort`)
- `result_kind` (`resolved | replaced | rolled_back | abandoned | carried_across_boundary`)
- `boundary_key` (nullable)
- `synthetic_control_artifact_refs[]`
- `preserved_output_refs[]`
- `closed_at`
- `dedupe_key`

hard rule:
**`repair_outcome` says whether the reply path was repaired. it does not say the move was good.**

## 4. `move_outcome`
this stays the calibration artifact from `ily/34`.

it answers:
- did the chosen move help, hurt, or do nothing useful

it does **not** answer:
- whether a repair loop happened
- whether truncation recovery succeeded
- whether synthetic control prompts existed

important:
- a repaired reply can still have `move_outcome = hurt`
- an unrepaired/abandoned attempt does not automatically imply `move_outcome = hurt`
- move quality closes only when there is enough honest evidence about the user-visible result

## 5. `assistant_message_event`
this is the only durable transcript truth for the reply itself.

hard rule:
- one logical plan may have many attempts
- it may have many repair/control artifacts
- it may have zero or one final `assistant_message_event`
- it may never leave 3 fake assistant turns plus 2 fake system nudges pretending to be the relationship history

---

## partial-turn state machine

one `plan_id` can move through these states:
- `drafting`
- `repair_pending`
- `boundary_frozen`
- `resumed`
- `finalized`
- `rolled_back`
- `abandoned`

meaning:
- `drafting` = initial attempt running
- `repair_pending` = a real attempt produced damaged/partial output and repair is now required
- `boundary_frozen` = hot window/epoch is rotating before finalization
- `resumed` = the same logical reply continues in a later attempt or child window
- `finalized` = one canonical assistant message exists
- `rolled_back` = bad partial attempt was discarded from transcript truth
- `abandoned` = no final assistant reply was committed for this plan

hard rule:
**a state transition may create execution/repair artifacts without creating transcript truth.**

---

## repair vs transcript truth

## 1. synthetic control text is never evidence
examples:
- continuation nudges
- retry instructions
- `continue where you left off`
- `execute the tool calls now`
- provider-specific repair control prompts

allowed place:
- maintenance/runtime artifacts only

forbidden place:
- `message_events` as if the user actually said them
- evidence refs
- retrieval packs
- recall summaries used as relationship proof

## 2. transport chunks are not transcript truth
if streaming exists later:
- stream chunks are delivery artifacts
- they are not canonical assistant turns
- transcript finalization happens only when the logical reply is complete enough to commit honestly

## 3. interim partial output may be preserved without being promoted
if a truncated attempt produced useful visible text:
- keep it as an `output_artifact`
- let repair reference or reuse it
- do not treat it as a separate assistant message unless the product truly delivered that partial reply as the canonical visible turn

default posture:
**assemble or replace. do not stack partials into fake history.**

---

## closure rules

## 1. `repair_outcome` closes on runtime rescue truth
close it when the system can answer:
- was the damaged attempt rescued?
- replaced?
- rolled back?
- carried across a boundary?
- abandoned?

this can close before `move_outcome`.

## 2. `move_outcome` closes on user-visible interaction truth
close it only when there is enough evidence about the actual reply result:
- same-turn reaction
- next-turn follow-up
- later resolution
- honest boundary close if the conversation ends

## 3. `prediction_outcome` still closes on horizon truth
same as `ily/34`:
- turn/session closures in deferred maintenance
- daily/long closures in heartbeat

important split:
- `repair_outcome` teaches runtime hygiene quality
- `move_outcome` teaches tactic quality
- `prediction_outcome` teaches signal quality
- `pack_outcome` teaches prompt-admission quality

if these collapse,
calibration rots.

---

## same-plan continuation rule

### canonical rule
**all attempts spawned to finish one intended reply attach to the same `plan_id`.**

that includes:
- truncation continuation
- intermediate-ack repair
- retry after empty/incomplete output
- boundary resume in a child window

recommended posture:
- one `plan_id`
- many `attempt_id`s
- optional one `repair_outcome`
- zero or one final `assistant_message_event`
- later zero or one `move_outcome`

what Purr should not copy from Hermes:
- multiple durable assistant turns for one logical answer just because the provider needed two calls
- synthetic repair prompts saved as user speech
- losing the repair metadata on restore while keeping the polluted text

---

## boundary / compression handoff rules

## 1. unfinished reply cannot be summarized as if it already happened
if compaction, idle close, or mobile re-entry hits mid-repair:
- freeze the active `plan_id`
- freeze all related `attempt_id`s
- write a typed boundary maintenance artifact
- carry forward the plan into the child `window_id` / `epoch_id` if repair should continue
- only finalize transcript truth after the resumed attempt honestly resolves

## 2. boundary carry is a repair result, not a chat turn
if the reply survives into the next window:
- `repair_outcome.repair_kind = boundary_carry`
- state becomes `boundary_frozen -> resumed`
- no fake `assistant said...` summary turn is created just to explain the carry

## 3. rollback before compaction is allowed
if the damaged partial attempt is not trustworthy:
- mark it `rolled_back`
- keep runtime provenance
- do not compact it into relationship truth

## 4. child window must inherit the same logical reply identity
compaction/re-entry can rotate:
- `window_id`
- `epoch_id`
- snapshot artifact

it may not silently fork the logical reply into a new unrelated plan.

hard rule:
**boundary handoff may rotate windows. it may not erase or duplicate reply identity.**

---

## pack / evidence hygiene rules

## 1. repaired text is not proof that prompt admission was right
`pack_outcome` only learns from prompt-visible admission quality.
repair success does not equal `pack_hit`.

## 2. repair success is not proof that the move helped
possible case:
- truncation got repaired cleanly
- final reply still landed badly

result:
- `repair_outcome = resolved`
- `move_outcome = hurt`

## 3. repair failure is not proof that the signal was wrong
possible case:
- provider died mid-reply
- move idea was still good
- runtime failed before we got the clean final answer

result:
- do not let runtime failure fake a prediction miss

## 4. synthetic control artifacts are never eligible recall evidence
no quote retrieval
no relationship recap
no later `why do we think this` proof

---

## repair-focused goldens

## 1. truncation continuation stays one logical reply
### setup
- one `reply_move_plan`
- first attempt truncates after useful partial output
- second attempt continues and finishes

### pass condition
- both attempts share one `plan_id`
- first attempt is stored as execution artifact only
- final transcript has one assistant message
- synthetic continuation control text never becomes evidence

### failure it catches
- multi-turn transcript pollution from one reply
- fake evidence from repair prompts

---

## 2. retry after bad intermediate ack does not count as relationship truth
### setup
- first attempt emits workspace/control fluff or empty ack-like text
- repair logic retries and second attempt gives the real reply

### pass condition
- ack/control output is typed as repair/runtime artifact only
- no assistant transcript event is committed for the bad attempt
- `repair_outcome` closes independently from later `move_outcome`

### failure it catches
- counting intermediate repair chatter as real conversation
- teaching the packer from provider stumble text

---

## 3. failed repair rolls back cleanly
### setup
- first attempt truncates
- continuation retry also fails or becomes unsafe
- system falls back to rollback/abandon or replacement reply path

### pass condition
- stale partial attempt is `rolled_back` or `abandoned`
- no duplicate assistant turn is left in transcript truth
- no fake `move_outcome` is written just because repair happened
- retrying the worker does not duplicate closure artifacts

### failure it catches
- rollback contamination
- replay inflation
- runtime failure being mis-scored as tactic failure

---

## 4. compression handoff preserves plan identity without summary poison
### setup
- reply is mid-repair when compaction/re-entry boundary fires
- child window/epoch opens
- repair resumes after handoff

### pass condition
- same `plan_id` survives across the boundary
- attempts before and after handoff remain linked
- boundary carry is stored as typed maintenance/repair artifact
- no compaction summary pretends the unfinished reply already happened
- final transcript still contains at most one canonical assistant turn

### failure it catches
- child-window fork drift
- summary contamination
- duplicate final replies after re-entry

---

## 5. restore/resume does not lose repair hygiene metadata
### setup
- an incomplete or repaired reply path is persisted
- runtime restores the active context later

### pass condition
- restore path still knows which attempts were incomplete/repair-only
- no repair artifact is reinterpreted as plain conversation evidence
- resumed continuation can attach to the same logical reply safely

### failure it catches
- metadata loss on restore
- polluted recall from repair-shaped history

---

## what this changes for Purr

### 1. runtime quality gets its own honest score surface
repair quality is now measurable without corrupting planner calibration.

### 2. transcript truth gets stricter
Purr can still recover from ugly provider behavior,
but the relationship history stays clean.

### 3. boundary hygiene now includes unfinished replies explicitly
compaction/re-entry is not only about packs and memory salvage.
it is also about not lying about half-finished assistant turns.

### 4. future builders get a clean storage split
later infra can now separate:
- execution attempts
- repair artifacts
- transcript truth
- move calibration
- signal calibration

instead of stuffing all of it into one message log and hoping ranking sorts it out.

---

## build-order impact

### what this changes
- it closes the missing repair/outcome hygiene seam left open by `ily/33` + `ily/34`
- it gives low-context builders a direct answer on repaired turns, retries, rollback, and boundary carry
- it raises the quality bar for runtime artifacts, transcript normalization, and later dogfood/evals

### what this does not change
- it does **not** change slice order
- it does **not** unpark build mode
- it does **not** make reply repair user-visible theater

hard translation:
**repair should improve continuity quietly. it should not become fake memory.**

---

## short verdict

Hermes is right that reply repair matters.
Hermes is wrong to let repaired control text drift toward transcript truth.

for Purr, the clean contract is:
- one plan
- many attempts if needed
- typed repair artifacts
- at most one canonical assistant reply
- separate runtime-hygiene scoring from move/prediction/pack scoring
- no synthetic control text in evidence or recall

that is how Purr gets continuity under failure
without teaching itself the wrong lessons about memory, move quality, or relationship truth.
