# Purr reply-execution attempts, canonical transcript truth, and normalization contract

## why this note exists

`ily/35` closed the repaired-turn hygiene seam:
- one reply move can span many attempts
- `repair_outcome` stays separate from `move_outcome`
- synthetic continuation/control text must not become memory evidence

but one layer under that was still too loose:

**what is the exact durable difference between an execution attempt and the final assistant transcript event, especially under streaming, tool loops, retry, rollback, restore, and resume?**

that matters because the latest Hermes read on this machine made the failure mode ugly and concrete:
- one logical answer can persist as several assistant attempts plus synthetic user control prompts
- returned `final_response` can diverge from stored transcript history
- prior assistant content can get rewritten into synthetic `Calling the tool...` filler
- SQLite restore, JSON logs, and live in-memory state do not preserve the same fields
- retry / rewrite / resume paths can normalize history differently from what the user actually saw

if Purr copies that shape, it will poison its own evidence layer.
then `feels one step ahead` becomes:
- duplicate assistant truth
- fake continuation chat
- wrong reply-quality calibration
- bad recall evidence
- impossible resume semantics

this note closes that transcript-normalization seam.

it does **not** open build mode.
it does **not** unpark any build slice.

---

## direct verdict

### one-line answer
**Purr must treat `reply_execution_attempt` and `assistant_message_event` as different durable object families. one plan may have many attempts, but it finalizes into at most one canonical assistant transcript event.**

### translation
Purr needs 4 separate planes here:
1. `reply_move_plan` — why this reply was chosen
2. `reply_execution_attempt` — one actual generation/tool run attempt
3. `delivery_artifact` — stream chunks, adapter edits, media wrappers, typing/progress, transport ids
4. `assistant_message_event` — the single canonical transcript truth, if a real user-visible reply was honestly finalized

### strongest rule
**the transcript is not a scratchpad for retries. if a provider needs 3 calls, or a tool loop restarts, or streaming dies halfway, transcript truth still gets at most one canonical assistant message for that plan.**

---

## Hermes lesson that forces this note

latest Hermes inspection surfaced 5 concrete failures we should translate into hard Purr rules:

### 1. one logical reply can splinter into many stored conversation rows
Hermes can append:
- partial assistant attempts
- synthetic user continuation prompts
- tool-loop scaffolding
- later final assistant content

so the stored transcript is often a runtime trace, not clean relationship history.

### 2. returned reply text can diverge from persisted transcript text
Hermes can assemble a final returned reply from truncated chunks or fallback buffers,
while the stored messages remain split across attempts.

### 3. prior assistant content can be rewritten after the fact
Hermes can rewrite a prior assistant-with-tools turn into synthetic filler like `Calling the tool...`
while separately returning the salvaged real text to the user.

### 4. restore paths do not preserve the same fields as live runtime
Hermes' SQLite restore keeps only a reduced conversation shape.
JSON logs keep richer artifacts.
live runtime can know even more.
so resume fidelity depends on **which store got read**, not on one canonical contract.

### 5. transcript rewrite paths can permanently normalize history down to the thinner store
retry / undo / compression-style rewrite paths can erase richer fields and keep only the thinner normalized conversation view.

hard translation:

**Hermes proves reply continuity work is real.
Hermes also proves runtime trace and transcript truth must be separated before restore/resume/eval start lying.**

---

## the seam this note closes

before this note, the repo already had answers for:
- hidden move planning (`ily/15`)
- prompt / snapshot / artifact planes (`ily/16`)
- hidden runtime lanes (`ily/18`)
- reply calibration writeback (`ily/34`)
- repair hygiene and boundary carry (`ily/35`)

what was still missing:
1. the exact durable difference between an attempt and a transcript event
2. how streaming, adapter delivery, and media wrappers stay out of transcript truth
3. how tool-call retries attach to one plan without duplicating assistant truth
4. how restore/resume rebuilds one canonical reply state instead of inferring from mixed logs
5. how finalization stays idempotent under retry/resume/fallback

this note freezes all 5.

---

## canonical durable split

## 1. `reply_move_plan`
this stays the hidden planning artifact from `ily/15` / `ily/34`.

it answers:
- what move was chosen
- which drivers shaped it
- what prompt-visible admissions were allowed

it does **not** answer:
- how many generation attempts happened
- whether streaming broke
- whether a tool loop retried
- whether a transcript message was finalized

## 2. `reply_execution_attempt`
this is one actual backend attempt to produce the reply.

minimum fields:
- `attempt_id`
- `plan_id`
- `owner_id`
- `purr_id`
- `window_id`
- `epoch_id`
- `attempt_index`
- `attempt_kind` (`initial | continuation | retry | restore_resume | fallback`)
- `provider_name`
- `provider_run_id` (nullable)
- `input_artifact_refs[]`
- `output_artifact_ref` (nullable)
- `finish_state` (`completed | truncated | incomplete | tool_interrupted | transport_interrupted | empty | rolled_back | failed`)
- `tool_batch_refs[]`
- `superseded_by_attempt_id` (nullable)
- `closed_at`
- `dedupe_key`

purpose:
- keep execution provenance
- let one logical reply span many model calls or tool loops cleanly
- give repair/finalization workers something stable to reason over

hard rule:
**`reply_execution_attempt` is execution provenance, not transcript truth.**

## 3. `tool_batch_artifact`
Purr does **not** need user-facing tool theater in private chat,
but execution still needs honest internal provenance.

minimum role:
- record the tool calls a given attempt actually launched
- record the result bundle that came back
- preserve retry boundaries when the same logical reply re-runs tools

minimum fields:
- `tool_batch_id`
- `attempt_id`
- `batch_index`
- `tool_calls[]`
- `tool_results[]`
- `batch_state` (`completed | partial | failed | superseded`)
- `dedupe_key`

hard rule:
**tool batches are attempt artifacts. they do not become canonical transcript events in 1:1 chat.**

## 4. `delivery_artifact`
this is the missing boundary between transport/runtime behavior and transcript truth.

examples:
- stream chunks
- partial adapter sends
- message edits/replacements
- typing/progress events
- `MEDIA:` wrappers or voice directives
- platform message ids / delivery receipts
- mirror/source labels
- user-visible temporary placeholder text

minimum fields:
- `delivery_artifact_id`
- `plan_id`
- `attempt_id` (nullable)
- `surface_family`
- `channel_message_id` (nullable)
- `delivery_kind` (`stream_chunk | partial_send | edit | replace | media_wrapper | receipt | mirror_notice | typing`)
- `payload_ref`
- `is_canonical_publication` (bool)
- `superseded_by_delivery_id` (nullable)
- `dedupe_key`

hard rule:
**delivery artifacts explain what transport did. they do not define relationship truth by themselves.**

## 5. `assistant_message_event`
this is the only canonical transcript truth for the assistant reply.

minimum fields:
- `assistant_message_event_id`
- `plan_id`
- `owner_id`
- `purr_id`
- `window_id`
- `epoch_id`
- `author = purr`
- `visible_text`
- `source_attempt_id`
- `publication_delivery_id` (nullable)
- `normalization_version`
- `finalization_key`
- `created_at`

hard rules:
- one `plan_id` may finalize into **zero or one** canonical assistant transcript event
- the canonical event contains the normalized visible reply only
- synthetic continuation prompts, stream chunks, repair nudges, and tool scaffolding never become transcript truth

---

## exact plane split

| plane | question | canonical write surface | may retry? | allowed to affect transcript truth? |
| --- | --- | --- | --- | --- |
| `reply_move_plan` | why did we choose this reply? | durable planner artifact | no | only indirectly, through later finalization |
| `reply_execution_attempt` | what actual generation run happened? | execution artifact | yes | no |
| `tool_batch_artifact` | what tool work happened inside an attempt? | execution artifact | yes | no |
| `delivery_artifact` | what did transport/display do? | delivery/runtime artifact | yes | only if explicitly linked as the final publication |
| `assistant_message_event` | what is the canonical assistant message in transcript truth? | transcript/event store | no, idempotent finalization only | yes |

hard translation:
- attempts teach execution provenance
- tool batches teach hidden work provenance
- delivery artifacts teach transport provenance
- transcript events teach relationship truth

if these collapse,
restore and eval both rot.

---

## finalization contract

## 1. finalization is a separate step, not an accident of logging
Purr must not assume that `the last assistant-looking output` is the transcript.

finalization happens only when the system can honestly say:
- this plan has a publishable visible reply
- the chosen attempt is the winner
- any partial earlier attempts are superseded or rolled back
- the normalized visible text is stable

## 2. one plan -> at most one canonical assistant message
allowed:
- many attempts
- many tool batches
- many delivery artifacts
- zero or one final transcript event

forbidden:
- one logical reply leaving 3 assistant transcript rows because the provider needed 3 tries
- a tool-phase stub and the final answer both counting as transcript truth for the same plan
- post-hoc rewriting of an already-canonical assistant transcript row into synthetic filler

## 3. finalization must be idempotent
recommended key:
- `finalization_key = plan_id + transcript_leaf_id`

rule:
- only one successful finalization may commit an `assistant_message_event`
- repeated retries / resumes / worker restarts must resolve to the same canonical event
- later duplicate finalization attempts become no-ops or explicit `duplicate_finalize_suppressed`

hard rule:
**retrying finalization may re-check truth. it may not duplicate transcript truth.**

## 4. finalization chooses a winning attempt, not a blended fantasy
if a reply took several attempts:
- one attempt becomes `source_attempt_id`
- earlier attempts remain execution provenance only
- if final visible text uses preserved partial output, that merge must happen in a typed normalization step before transcript commit

forbidden:
- inferring canonical text later by concatenating random attempt rows in transcript history

---

## normalization rules for the canonical assistant message

## 1. transcript text is normalized visible payload only
canonical `assistant_message_event.visible_text` may include:
- the actual user-visible reply
- only the visible payload Purr intends to stand behind later

it may **not** include:
- continuation prompts
- retry instructions
- tool control text
- `Calling the tool...`
- `continue where you left off`
- streaming fragments
- adapter-only formatting wrappers
- reasoning-only text not meant as the actual reply

## 2. transport wrappers are not transcript truth
examples:
- `MEDIA:`
- voice rendering directives
- mirror/source labels
- chunk-by-chunk streamed partials
- temporary `working on it` placeholders

these live in `delivery_artifact`, not in `assistant_message_event`.

## 3. if a partial was actually shown, it is still not automatically canonical
showing partial text on a flaky surface does **not** force it into transcript truth.

default posture:
- preserve the partial as `delivery_artifact`
- preserve its provenance via `reply_execution_attempt`
- finalize transcript only when the canonical visible reply is known

only if the product explicitly decides that a partial delivered message is itself a durable conversational act should it become a transcript event.
that should be rare in private chat.

## 4. canonical publication can point at delivery without being equal to it
`assistant_message_event.publication_delivery_id` may reference the delivery artifact that actually published the final answer.
that gives auditability without letting transport define truth.

---

## tool/result retry boundaries

## 1. tool retries stay inside execution provenance
if a reply attempt calls tools, fails, and retries:
- keep the same `plan_id`
- create a new `attempt_id`
- attach new `tool_batch_artifact` rows to the new attempt
- leave transcript truth untouched until one attempt actually finalizes

## 2. tool-call scaffolding is never assistant transcript truth
forbidden transcript rows:
- `Calling the tool...`
- synthetic `please retry this tool`
- provider/workspace planning fluff
- internal tool-error wrappers unless the user actually sees/gets that as the final answer

## 3. tool batch supersession must be explicit
if attempt 1 launched a tool batch but attempt 2 replaced it:
- mark attempt-1 batch `superseded`
- preserve it for audit/debug
- do not let it remain the apparent causal parent of the final transcript event unless it really was

## 4. tool result errors are not reply-quality truth
tool/runtime failure can damage a reply path,
but it should not by itself count as:
- `move_outcome = hurt`
- `prediction_outcome = miss`
- canonical assistant transcript content

that belongs in execution / repair surfaces first.

---

## restore and resume normalization contract

## 1. restore must read canonical objects, not guess from mixed logs
cold restore should use:
- canonical `assistant_message_event` / transcript events
- still-open `reply_move_plan`s
- unresolved `reply_execution_attempt`s
- current prompt/snapshot artifact pointer

it should **not** rebuild the truth by parsing whichever store happened to keep the richer raw message dict.

## 2. system snapshot is a separate plane
Hermes correctly teaches that prompt snapshot continuity matters.
Purr should keep that.

but the rule must be explicit:
- transcript truth is one plane
- session snapshot / epoch prompt artifact is another plane
- restore needs both
- neither should silently overwrite the other

## 3. resume cannot mint a second assistant truth for the same plan
if a plan was mid-attempt before boundary/re-entry:
- reopen the same `plan_id`
- keep old attempts as provenance
- create a new `attempt_id` if execution resumes
- still finalize into at most one canonical assistant transcript event

## 4. normalization survives store differences
if audit/raw logs preserve extra runtime fields,
that is fine.

but canonical replay must not depend on:
- JSONL vs DB differences
- adapter-specific wrappers
- whether reasoning fields survived
- whether mirror metadata existed

hard rule:
**extra debug richness is allowed. restore truth must not depend on it.**

---

## suggested state machine

one `plan_id` can move through:
- `planned`
- `executing`
- `awaiting_finalization`
- `finalized`
- `rolled_back`
- `abandoned`

meanings:
- `planned` = move chosen, no attempt started yet
- `executing` = at least one live attempt exists
- `awaiting_finalization` = one candidate visible reply exists, but canonical commit not finished
- `finalized` = one canonical `assistant_message_event` exists
- `rolled_back` = attempts happened, no transcript truth committed
- `abandoned` = plan closed without a canonical assistant reply

hard rule:
**attempts and delivery can churn inside `executing` / `awaiting_finalization` without creating transcript truth.**

---

## steal vs reject from Hermes

## steal
- exact session snapshot reuse for continuation
- explicit execution provenance for tool calls and finish states
- continuation / retry / repair as real runtime quality work
- the idea that cold resume needs more than just vague memory search

## reject hard
- synthetic user continuation prompts stored as normal transcript truth
- partial assistant attempts left as if they were separate conversation turns
- rewriting prior assistant content into synthetic filler
- depending on different stores to preserve different truths
- letting returned final text diverge from canonical transcript text

---

## transcript-normalization goldens

## 1. duplicate finalization under retry/resume
### setup
- one `plan_id`
- first finalization succeeds
- worker retries or resume path replays the same finalization

### pass condition
- exactly one canonical `assistant_message_event`
- duplicate finalize attempt is suppressed by `finalization_key`
- no second assistant transcript row appears

### failure it catches
- duplicate assistant truth after retry or resume

---

## 2. streaming interruption does not become transcript shards
### setup
- streaming emits 3 partial chunks
- transport dies before clean close
- later attempt resumes and produces the final reply

### pass condition
- chunks remain `delivery_artifact`s only
- interrupted attempt remains `reply_execution_attempt`
- final transcript still has at most one canonical assistant message
- no chunk text is later treated as recall evidence by itself

### failure it catches
- transcript pollution from transport chunks
- false evidence from partial stream text

---

## 3. tool-call retry stays inside one plan without duplicate assistant truth
### setup
- attempt 1 calls tools and fails mid-batch
- attempt 2 retries the reply and launches a new tool batch
- attempt 2 produces the publishable answer

### pass condition
- both attempts share one `plan_id`
- tool batches are attached to the right attempts
- failed tool scaffolding never becomes transcript truth
- exactly one canonical assistant transcript event exists

### failure it catches
- `Calling tools...` transcript sludge
- duplicated assistant rows from tool retry loops

---

## 4. restore/resume normalization ignores store richness drift
### setup
- raw audit log has richer runtime fields than canonical restore store
- a reply was mid-attempt before resume

### pass condition
- restore rebuilds from canonical transcript + pending attempt state + snapshot pointer
- lack of extra debug fields does not change transcript truth
- resumed execution still finalizes into one canonical assistant message only

### failure it catches
- JSONL-vs-DB truth drift
- resume behavior depending on noncanonical log richness

---

## 5. prior assistant content cannot be rewritten into tool filler
### setup
- attempt 1 produced real assistant text plus tool activity
- fallback/repair path later wants to simplify transport behavior

### pass condition
- prior assistant transcript truth is never overwritten into `Calling the tool...`
- transport filler, if needed, stays a delivery artifact only
- canonical transcript either keeps the original final text or rolls it back explicitly

### failure it catches
- post-hoc mutation of transcript truth
- losing the real assistant utterance while keeping synthetic scaffolding

---

## 6. returned final reply must match canonical transcript text
### setup
- final visible answer is assembled from several attempts or normalized before publish

### pass condition
- the final user-visible reply has one matching `assistant_message_event.visible_text`
- audit artifacts can still show how it was assembled
- no gap exists where the user saw one text but transcript truth stores another

### failure it catches
- display/transcript drift
- wrong evidence for later recall or eval

---

## what this changes for Purr

### 1. transcript truth gets much stricter
Purr now has an explicit answer for:
- what counts as conversation truth
- what stays execution provenance
- what stays delivery/runtime noise

### 2. restore/resume becomes explainable
instead of `load whichever log is richer`,
Purr gets a clean replay contract:
- transcript events
- pending attempts
- prompt snapshot pointer

### 3. reply eval gets cleaner inputs
`ily/34` and `ily/35` now sit on top of a cleaner base:
- `move_outcome` no longer risks scoring transcript sludge
- `repair_outcome` no longer risks masquerading as assistant truth
- later goldens can judge reply quality without log-format confusion

### 4. future builders get one honest publication boundary
there is now a clear seam between:
- generation
- transport
- final transcript commit

that is the only way to make retries, streaming, tools, and resume coexist without polluting relationship memory.

---

## build-order impact

### what this changes
- it closes the transcript-normalization seam left open after `ily/35`
- it gives low-context builders an explicit `attempt vs transcript vs delivery` contract
- it sharpens future eval and dogfood expectations around replay fidelity

### what this does not change
- it does **not** change slice order
- it does **not** unpark build mode
- it does **not** make private-chat runtime machinery visible to the user

hard translation:
**this raises the honesty bar for reply persistence. it does not change the repo's research-first gate.**

---

## short verdict

Hermes is right that retries, continuation, tool loops, and resume matter.
Hermes is wrong to let those runtime traces drift into transcript truth.

for Purr, the clean contract is:
- one plan
- many attempts if needed
- typed tool and delivery artifacts
- at most one canonical assistant transcript event
- idempotent finalization
- restore from canonical truth, not whichever log happened to keep more sludge

that is how Purr keeps private-chat continuity sharp
without teaching itself the wrong story about what it actually said.