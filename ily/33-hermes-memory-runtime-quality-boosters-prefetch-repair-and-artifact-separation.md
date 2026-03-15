# Hermes memory runtime quality boosters: prefetch, repair, and artifact separation

## why this note exists

`ily/05`, `ily/07`, `ily/17`, `ily/18`, and the board review already explain the big Hermes truth:
- flat curated memory is too weak for Purr
- prompt snapshots are strong
- recall/search/compression/sinks do not share one clean scope/evidence contract
- same-session freshness and product-grade identity are weak

but one practical seam was still under-explained:

**why does Hermes often feel better than its raw memory model deserves?**

that matters because Purr should not only steal good data shape ideas.
it should also steal the runtime choreography that makes a memory system feel sharp,
without copying the parts that fake continuity or muddy truth.

this pass is code-grounded.
its point is not `Hermes secretly has better memory.`
its point is:

**Hermes gets a lot of perceived continuity from runtime discipline around retrieval timing, continuation repair, artifact hygiene, and boundary maintenance.**

that is worth stealing.

---

## direct verdict

### one-line answer
**Hermes feels stronger than its flat memory because it cheats in the good way: it improves timing, continuity, and working-state survival around the core memory, not just the memory rows themselves.**

### translation
Hermes does at least 6 runtime things that boost perceived memory quality:
1. **next-turn recall prefetch** so context is ready before the user notices delay
2. **continuation repair** so truncated or fake-start replies do not look like dropped context
3. **working-state survival artifacts** so compression does not erase the current job/thread of thought
4. **prompt-plane vs transcript-plane separation** so useful scaffolding can exist without permanently contaminating history
5. **boundary-critical background hygiene** so idle expiry and giant sessions do not silently rot continuity
6. **resume-by-artifact-pointer behavior** so old sessions really continue from the same stored artifact set

### harder truth
none of this fixes Hermes' core weaknesses for Purr:
- truth is still too flat
- scope is still too convenience-driven
- recall is still too summary-heavy
- some maintenance artifacts are still too chat-shaped

so the right read is:

**steal the runtime discipline.
reject the fake-history shortcuts and loose identity model.**

---

## code-grounded seam this closes

previous notes mostly answered:
- what Hermes stores
- where Hermes loses truth
- where Hermes compresses or summarizes too hard
- why Purr needs structured per-owner memory

this note answers a different question:

**what hidden runtime tricks make Hermes feel continuous even when the underlying memory model is only medium-strength?**

that distinction matters because builders can otherwise misread the situation in two bad ways:
- bad read 1: `Hermes feels decent, so maybe flat memory is enough`
- bad read 2: `Hermes memory is weak, so none of its runtime behavior matters`

both are wrong.

the real lesson is:

**user-perceived memory quality is partly a storage problem,
but also a timing/orchestration problem.**

---

## 1. next-turn recall prefetch is doing real quality work

relevant runtime surface:
- `vendor/hermes-agent/run_agent.py::_activate_honcho`
- `vendor/hermes-agent/run_agent.py::_queue_honcho_prefetch`
- `vendor/hermes-agent/run_agent.py::_honcho_prefetch`
- `vendor/hermes-agent/run_agent.py::run_conversation`

### what Hermes does
when Honcho recall is active, Hermes does not only fetch memory on demand.
it pre-warms recall for the **next** turn.
after a turn finishes, it syncs the exchange to Honcho and queues prefetch work.

on a fresh session, some of that context can get baked into the initial prompt snapshot.
on later turns, prefetched recall is often injected at call time rather than permanently rebuilding the session prompt.

### why it feels better than the underlying memory really is
- the next reply starts with memory already waiting
- recall feels immediate instead of visibly delayed
- prompt cache stability survives because the whole session prompt is not rebuilt every turn
- user experiences continuity, not retrieval ceremony

### what Purr should steal
- async **next-turn prefetch** for likely relevant recall artifacts
- strict split between:
  - **bootstrap/session snapshot recall**
  - **later-turn overlay recall**
- owner/purr-scoped turn overlays that stay tiny and disposable

### what Purr should reject
- injecting recall as fake user-style text
- letting convenience session naming decide recall scope
- allowing prefetched recall to bypass the same trust/evidence gates as the main packer

hard translation:

**good memory feel is not only `what you know`.
it is also `did the right context arrive before the turn started?`**

---

## 2. continuation repair hides model flakiness that would otherwise look like memory loss

relevant runtime surface:
- `vendor/hermes-agent/run_agent.py::_looks_like_codex_intermediate_ack`
- `vendor/hermes-agent/run_agent.py::run_conversation` length-continuation loop
- `vendor/hermes-agent/run_agent.py::run_conversation` Codex ack-continuation loop

### what Hermes does
Hermes detects at least two ugly reply-path failures:
1. the model gets cut off by output-length limits
2. the model emits a polite `i'll inspect/check/run that` intermediate ack instead of actually doing the work

Hermes then pushes a synthetic continuation prompt and re-enters the loop so the turn can finish more honestly.

### why it feels like better memory/continuity
from the user side,
a broken or prematurely-ended reply often feels like:
- the agent lost the thread
- the agent forgot the task
- the system is flaky

continuation repair masks that failure.
it keeps the same conversational thread alive instead of exposing raw model stumble.

### what Purr should steal
- a **runtime continuation-repair layer** for truncation or premature stop cases
- typed repair reasons like:
  - `reply_truncated`
  - `tool_run_interrupted`
  - `needs_continuation`
- repair as runtime control logic, not as normal conversation truth

### what Purr should reject
- persisting synthetic continuation nudges as real user/Purr speech
- model-specific regex hacks as the only long-term contract

hard translation:

**a system that can recover a damaged reply feels more continuous than one that simply stores more facts.**

---

## 3. Hermes preserves working state across compression, not just semantic summary

relevant runtime surface:
- `vendor/hermes-agent/run_agent.py::_compress_context`
- `vendor/hermes-agent/run_agent.py::_hydrate_todo_store`
- `vendor/hermes-agent/agent/context_compressor.py::compress`

### what Hermes does
before compression, Hermes tries to salvage memory.
after compression, it does more than add a summary:
- it appends a **todo snapshot**
- it appends a **files already read** artifact so the model does not keep re-reading the same stuff
- on later gateway turns, it can reconstruct short-lived working state by reading the latest todo tool result back out of history

### why it feels better
this is not relationship memory.
it is **operational working memory**.
without it, long tasks feel like the system lost its place every time context got compacted.
with it, Hermes keeps momentum.

### Purr implication
Purr should keep the same idea,
but make it cleaner and more typed:
- `working_plan_artifact`
- `consumed_evidence_artifact`
- `active_open_loops_artifact`
- `turn_overlay_artifact`

these should survive boundaries,
but they must never pretend to be raw conversation.

### what to steal
- compression must preserve current-task state, not only recap old chat
- lightweight working-state rehydration from typed artifacts is worth it

### what to reject
- summary-only survival of operational state
- synthetic chat-looking artifacts mixed into normal transcript truth

hard translation:

**Purr needs two kinds of continuity:
relationship continuity and working-state continuity.
Hermes is better at the second than people give it credit for.**

---

## 4. prompt-visible planes and durable transcript planes are already semi-separated in Hermes

relevant runtime surface:
- `vendor/hermes-agent/run_agent.py::_build_system_prompt`
- `vendor/hermes-agent/run_agent.py::_apply_persist_user_message_override`
- `vendor/hermes-agent/run_agent.py::run_conversation` prefill / ephemeral injection path
- `vendor/hermes-agent/gateway/run.py::_run_agent`
- `vendor/hermes-agent/gateway/run.py` session-meta persistence and replay filtering

### what Hermes does
Hermes lets several useful things exist at API-call time without treating them all as durable history:
- `ephemeral_system_prompt`
- `prefill_messages`
- later-turn recall overlays
- session metadata describing tool context
- user-message persistence overrides so the API may see one thing while storage keeps a cleaner version

### why this matters
this is one reason Hermes can do helpful runtime scaffolding without permanently poisoning continuation.
it is already acting like the system has multiple artifact planes,
even if the contract is not fully explicit or clean.

### what Purr should steal
make the split first-class:
- `session_snapshot` = stable prompt artifact for the active window
- `turn_overlay` = tiny committed same-window freshness patch
- `evidence_recall_bundle` = exact-hit recall artifact
- `working_state_artifact` = task/open-loop/callback state
- `maintenance_artifact` = hidden job output, never equal to raw chat
- `transcript_event` = actual user/Purr or system event history

### what Purr should reject
- loose fake-chat artifacts
- allowing prompt-only scaffolding to leak back in as evidence
- letting one artifact plane silently outrank the others without a typed trust contract

hard translation:

**Hermes already teaches that not everything the model reads should become history,
and not everything in history should be prompt material.**

---

## 5. boundary-critical background hygiene does real memory maintenance

relevant runtime surface:
- `vendor/hermes-agent/gateway/run.py::_session_expiry_watcher`
- `vendor/hermes-agent/gateway/run.py::_flush_memories_for_session`
- `vendor/hermes-agent/gateway/session.py::_is_session_expired`
- `vendor/hermes-agent/gateway/run.py` pre-agent hygiene compression path

### what Hermes does
Hermes does maintenance **before** the next user message is forced to pay for it.
examples:
- expired sessions are watched in the background
- salvage can run before reset/expiry
- very large histories can get hygiene compression before normal handling
- real token counts are reused when available instead of only rough estimates

### why it feels better
this prevents the ugly version of continuity where:
- first message after idle is slow and messy
- large sessions silently degrade until the next user turn explodes
- important late-session details vanish because boundary salvage came too late

### what Purr should steal
Purr should keep a strict boundary-critical lane for:
- pre-expiry salvage
- oversized-window hygiene checks
- idle-close sealing
- re-entry preparation
- retry-safe boundary processing

### what Purr should reject
Hermes still has some fire-and-forget flush behavior around manual reset/resume.
for Purr, that is too weak.
if a boundary matters,
its salvage/writeback path needs explicit success/failure state,
not `hope the async flush made it`.

hard translation:

**memory quality depends on what happens at boundaries,
not just what happens during the happy-path reply loop.**

---

## 6. resume feels strong because Hermes restores the same artifact set

relevant runtime surface:
- `vendor/hermes-agent/gateway/run.py::_handle_resume_command`
- `vendor/hermes-agent/gateway/session.py::switch_session`
- `vendor/hermes-agent/hermes_state.py::resolve_session_by_title`
- `vendor/hermes-agent/hermes_state.py::get_next_title_in_lineage`

### what Hermes does
when a session is resumed,
Hermes does not fake continuity by only searching memory.
it often rebinds the active runtime to the older session artifact set:
- same stored transcript history
- same stored session prompt snapshot
- latest continuation in a title lineage

### why it feels better
this creates real continuation feel:
- not `i vaguely remember that`
- more like `we are back in the same room`

### what Purr should steal
- **resume-by-pointer**, not summary-only reopen
- one canonical active leaf/window per owner/purr/surface family
- explicit window/episode handoff and child-window creation rules

### what Purr should reject
- title suffixes as lineage truth
- thread/platform routing keys as product identity
- convenience `session_key` equivalents outranking canonical continuity binding

hard translation:

**true resume quality comes from reopening the right artifact lineage,
not from hoping search can reconstruct the feeling later.**

---

## 7. convenience continuity routing is useful, but unsafe as product truth

relevant runtime surface:
- `vendor/hermes-agent/gateway/session.py::build_session_key`

### what Hermes does well
Hermes maps many messaging situations into deterministic session keys,
so continuity often `just works` in practice.
that is good runtime ergonomics.

### why it cannot be copied as-is
those keys are still convenience routing,
not product identity.
for Purr,
`1 human = 1 purr` means:
- ownership truth cannot come from thread layout
- memory scope cannot come from platform convenience ids
- active continuity must be server-owned and explainable later

### correct Purr translation
keep this idea only at the outermost ingress/router layer:
- convenience routing helps find the likely bridge
- it never decides owner truth by itself

this aligns with `ily/32`.

---

## steal vs reject

## steal almost directly
- next-turn recall prefetch
- continuation repair for damaged/incomplete turns
- typed working-state survival across compression
- strong separation between prompt-only artifacts and durable transcript/history
- background salvage/hygiene before the next visible turn suffers
- resume-by-exact-artifact-pointer

## reject or redesign hard
- fake user/Purr maintenance turns as durable truth
- recall overlays smuggled in without shared trust gates
- convenience session keys as identity/memory scope
- title-based continuation as serious lineage
- fire-and-forget salvage on important boundaries
- any runtime helper that cannot later explain why it attached a turn to that continuity leaf

---

## what this changes for Purr

### 1. memory quality is not just a ledger problem
Purr still needs the structured ledger first.
that part does not change.

but this pass sharpens a second requirement:
**the runtime around the ledger must also be first-class.**

### 2. the hidden-runtime lane needs explicit artifact contracts
`ily/18` already split runtime into turn-critical, boundary-critical, deferred, and proactive lanes.
this Hermes pass says those lanes should also own typed artifacts cleanly,
not rely on invisible chat-shaped hacks.

### 3. next-turn overlays matter
Purr should treat same-window overlay recall and working-state patches as serious product infrastructure,
not a nice extra.
that is how you get `feels one step ahead` without dumping the ledger into every prompt.

### 4. repair logic is part of the product feel
if a reply truncates,
or a hidden planner path partially fails,
Purr should recover through typed runtime repair instead of exposing raw model stumble as broken continuity.

---

## build-order impact

### does this change slice order?
no.

it does **not** unpark build mode.
it does **not** beat `memory-ledger` as slice 1.

### what it does change
it sharpens later slice taste:
- slice 1/2 should preserve typed event/artifact boundaries so runtime helpers have somewhere honest to write
- slice 3 packer/runtime work should explicitly support tiny turn overlays and working-state artifacts
- shadow dogfood should score not only truth ingestion, but also whether boundary/runtime behavior preserves continuity honestly

hard translation:

**this note changes the quality bar,
not the build order.**

---

## short verdict

Hermes does **not** prove that flat memory is enough.

it proves something more useful:

**a medium-strength memory model can feel surprisingly good when runtime choreography is strong.**

for Purr, the move is:
- keep the stronger structured ledger
- keep the compact pack discipline
- add explicit overlay / repair / working-state / boundary-maintenance artifacts
- never let those helpers blur into fake truth

that is how you steal Hermes' feel
without inheriting Hermes' memory ceiling.
