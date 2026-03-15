# hermes memory review

purpose: inspect Hermes memory management hard before we copy anything into purr.

## tldr

Hermes memory is good because it is layered, cheap, durable, and disciplined.
It is not enough for purr as-is because it is tiny, mostly flat text, and built for one agent/user environment rather than a product with rich per-user memory.

best reusable idea:
- small always-on memory + full session history + on-demand recall

worst thing to copy blindly:
- treating memory as a few flat note files with no lifecycle state, confidence, or per-user structure

---

## what Hermes actually has

Hermes is not one memory system. It has layers.

### layer 1 — curated always-on memory
files:
- `~/.hermes/memories/MEMORY.md`
- `~/.hermes/memories/USER.md`

used for:
- user preferences
- environment facts
- project conventions
- short durable notes

important traits:
- bounded by char limit
- human-readable
- injected into the system prompt at session start
- mutated during the session, but prompt stays frozen until next session / compression rebuild

why this is good:
- low token cost
- stable behavior
- easy to audit
- hard to bloat if the limits stay strict

### layer 2 — full transcript memory
file/backend:
- `~/.hermes/state.db`

used for:
- session history
- full messages
- search later

important traits:
- SQLite + WAL
- FTS5 full-text search
- session metadata and lineage

why this is good:
- durable
- local and simple
- much cheaper than trying to keep everything in prompt memory

### layer 3 — session_search recall
used for:
- finding old conversations on demand
- summarizing old sessions only when needed

important traits:
- lexical search first
- then cheap summarization
- keeps long-tail memory out of the hot prompt

why this is good:
- cost-aware
- lets the agent recall old context without dragging huge history into every turn

### layer 4 — skills as procedural memory
Hermes separates facts from procedures.

memory = what is true / important
skills = how to do something

why this is good:
- stops the core memory from becoming a junk drawer
- keeps reusable workflows in a separate lane

---

## where Hermes is especially strong

### 1. frozen snapshot pattern
Hermes loads memory once and keeps the prompt stable for the session.

why it matters:
- prompt caching stays valid
- behavior does not drift every time memory changes
- writes can still happen immediately without exploding costs

for purr:
- this is one of the best things to steal
- purr should also have a hot memory pack that is stable for a session/window, not rebuilt on every little event

### 2. bounded memory discipline
Hermes forces memory to stay small.

why it matters:
- keeps quality high
- forces consolidation
- prevents “save everything forever in prompt” brainrot

for purr:
- same principle should survive
- but the hot pack should be generated from a bigger structured store, not be the whole store itself

### 3. persistent-memory safety scanning
Hermes scans memory content for prompt injection / exfil patterns because memory gets re-injected later.

why it matters:
- persistent memory is an attack surface
- especially if any memory can be derived from untrusted content

for purr:
- absolutely reuse this mindset
- if purr ever stores user-generated or network-derived memory summaries, sanitize them before they become prompt material

### 4. proactive memory capture
Hermes does not just hope the model remembers to save memory.
It has:
- memory nudges after enough turns
- memory flush before compression
- session end / reset flush behavior

why it matters:
- memory capture is operationalized
- the model gets a final chance to preserve what matters before context disappears

for purr:
- same principle, but likely event-driven and server-side
- important memory extraction should not depend only on the live chat loop

### 5. transcript store separate from hot memory
This is probably the cleanest Hermes move.

why it matters:
- transcripts are the raw mine
- hot memory is the refined metal
- search/summarize bridges the two

for purr:
- same exact philosophy should hold
- raw chat should live in durable storage
- only selected memory items or compact retrieval packs should hit the LLM prompt

### 6. stored prompt snapshot reuse across continued sessions
Hermes does not just freeze the prompt in RAM.
It stores the full assembled system prompt in SQLite and reuses that exact prompt on later session continuation instead of rebuilding from disk.

why it matters:
- prevents cache breakage across gateway/CLI continuation
- avoids re-injecting memory changes the model already wrote itself
- makes the active prompt a session artifact, not a live view of files

for purr:
- we should likely persist the exact session hot pack / prompt pack per conversation window
- continuation should reload that pack unless a deliberate rebuild event happens

### 7. compression with lineage, not overwrite
When Hermes compresses, it ends the old session, creates a new child session, and links them with `parent_session_id`.

why it matters:
- transcript audit trail stays intact
- search still has access to the pre-compression raw session
- the active conversation gets smaller without pretending old detail never existed

for purr:
- relationship history should also keep lineage/episode structure
- summaries should never become the only surviving truth

### 8. structural integrity guards during compression
Hermes does not only summarize semantics.
It also protects tool-call structure:
- avoids splitting tool-call/result groups at boundaries
- removes orphan tool results
- inserts stub tool results if needed so the API still accepts the compressed history

why it matters:
- long-context systems break in ugly ways if compression corrupts message structure
- this is hidden infra quality, but it is real quality

for purr:
- any background cognition / hidden tool lane needs the same integrity mindset
- summary or archive jobs must not break causal/evidence structure

---

## where Hermes is weak for purr

### 1. flat free-text memory entries
Hermes memory entries are basically note blocks.
Good for an assistant. weak for a richer memory product.

missing fields purr needs:
- memory id
- owner id
- purr id
- kind
- state
- confidence
- salience
- created_at
- last_confirmed_at
- evidence refs
- supersedes/conflicts_with
- review schedule

### 2. tiny scope
Hermes has very small memory caps.
Good for assistant continuity.
Not enough for:
- long-running relationship memory
- episodic memory
- emotional patterns
- social memory / catnet memory
- corrections over time

### 3. weak per-user product isolation by default
Hermes is basically one environment, one agent state, one memory area.
Fine for local agent use.
Not enough for a product where every human has a separate purr.

### 4. lexical recall only at search layer
FTS5 is useful but lexical.
Semantic memory needs more.

for purr:
- vector should support fuzzy/semantic recall
- but vector should not replace structured memory state

### 5. no explicit lifecycle
Hermes memory is mostly add/replace/remove.
Purr needs real lifecycle states:
- candidate
- confirmed
- rejected
- stale

without this, “i remember everything” becomes “i accumulate noise forever.”

### 6. same-session memory goes stale on purpose
Hermes chooses prompt stability over same-session freshness.
That is a rational assistant tradeoff.
For purr, it becomes a product risk.

failure pattern:
- user corrects something now
- memory write succeeds
- active prompt still reasons from the old snapshot

for purr:
- session pack can stay mostly frozen
- but we need a live turn-level override lane for direct corrections / contradictions / high-value new facts

### 7. memory mutation is substring-based text editing
Hermes updates memory by matching short text substrings inside flat entries.

why this breaks for purr:
- ambiguous matches are common as memory grows
- contradictions become text-management problems instead of state transitions
- there is no first-class provenance / evidence / supersedes graph

### 8. recall is lexical first, summary second
Hermes recall is good enough for agent continuity, but not enough for product-grade relational memory.

limits:
- FTS5 is lexical
- `session_search` skips the current session
- returned memory is a summarized recap, not canonical structured truth

for purr:
- recall should unify current session, recent episodes, and long-term memory under one retrieval contract
- semantic help should exist, but structured filtering has to lead

### 9. compression summaries can become lossy stand-ins
Hermes compression is careful, but summaries are still summaries.
If the summary model fails, middle turns may even be dropped.

for purr:
- summaries can be navigation aids
- they must not become the main truth source for relationship memory
- canonical truth needs ledger rows + evidence refs back to raw history

---

## what purr should steal from Hermes

steal these almost directly:
- layered memory model
- frozen hot-memory snapshot pattern
- bounded hot context
- durable transcript store
- proactive memory flush / capture moments
- memory security scanning
- separation of factual memory from procedural logic

---

## what purr should not steal directly

do NOT copy as-is:
- flat MEMORY.md / USER.md as the main product memory
- substring-based edits as the main mutation model
- lexical search as the only recall lane
- one global memory namespace
- no confidence / no review / no staleness model

---

## purr-grade version of the same architecture

### hot layer
small prompt pack for current interaction:
- core tone + relationship facts
- active preferences
- unresolved loops
- a tiny number of relevant episodes

### ledger layer
Supabase source of truth:
- structured memory items
- feedback events
- review checks
- session/message references

### recall layer
retrieval service:
- filter by owner/purr
- rank by relevance + recency + confidence + salience + unresolved status
- vector only where semantic help is real

### raw layer
messages/sessions:
- durable transcript store
- source for later extraction and audit

---

## code-grounded hidden warnings from the deeper pass

new repo note: `ily/07-hermes-memory-code-grounded-hidden-logic.md`

most important additions from reading the actual Hermes code:
- the `live write / frozen read` split is real and worth stealing, but it causes same-session stale truth unless Purr has a live override lane
- the periodic memory-nudge loop is effectively broken because `_turns_since_memory` resets at the start of each turn before it can accumulate
- `session_search` is not truly per-user scoped and can resolve child-session hits back to the root parent, which can miss the exact matched evidence
- title-based continuation (`foo`, `foo #2`) is useful UX, but not a serious lineage model
- write-time sanitization exists, but load-time prompt injection of existing memory is still a gap

translation for Purr:
- steal the session-pack discipline
- reject flat text truth
- make retrieval owner-scoped
- make lineage explicit
- make extraction/salvage operational instead of relying on chat-loop nudges

## new hard conclusion from the latest code-grounded pass
Hermes is strong on prompt-discipline and salvage,
but it is still too loose on **scope identity** for a memory-first product.

most important adds:
- some Hermes session/retrieval behavior is scoped by platform/source, not by a hard per-user product boundary
- child-session search can collapse back to a root parent and blur the exact matched evidence
- titles/continuations are useful UX, but they are not a serious identity or lineage contract
- current-session exclusion is too ID-local; it is not a clean lineage-aware exclusion rule

translation for Purr:
- `1 human = 1 purr` means every durable object and every retrieval path must start with `owner_id` + `purr_id`
- session windows, episodes, and pack artifacts need explicit ids and parent links
- retrieval must preserve exact hit evidence first, then add lineage recap second
- mobile re-entry should create honest continuation artifacts, not muddy reopen behavior

related deeper note:
- `ily/11-purr-session-scope-and-episode-lineage-contract.md`

## new hard conclusion from the extractor/evidence pass
Hermes is not only weak on flat truth shape.
it is also weak on **canonical evidence preservation**.

most important adds from the deeper operational pass:
- Hermes can preserve richer per-session artifacts than what its main searchable/reload path actually keeps
- session search and compression are useful for recall, but they are lossy and should not be mistaken for evidence
- memory flush/salvage is a strong idea, but it is audit-weak when the flush turn is stripped after saving
- gateway-side transcript rewrite/compression paths can drop tool/provenance richness and leave a thinner historical record behind

translation for Purr:
- keep exact evidence refs as first-class durable objects
- keep summary artifacts as navigation aids only
- make salvage produce explicit memory events, not invisible truth jumps
- never let the canonical searchable store be thinner than the real event trail that memory depends on

related deeper note:
- `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`

## new hard conclusion from the runtime-boundary pass
Hermes is not only a warning about flat truth shape.
it is also a warning about **freshness and writeback boundaries**.

most important adds from the latest pass:
- saved memory and model-visible memory diverge because the active prompt/session artifact stays frozen for stability
- pre-loss flush/salvage is necessary, but best-effort flush paths are still a real failure surface
- replaying only visible user/assistant text can miss hidden/tool-side learnings
- transcript/session recall is useful, but it is not a real worker writeback contract

translation for Purr:
- the next reply may use committed ledger truth plus a tiny committed live override, not uncommitted inference
- salvage before compression/re-entry/idle close has to be first-class and retry-safe
- hidden/internal evidence can exist, but only with exact provenance and lane policy
- background/worker cognition must write back through the same mutation/evidence contract as normal intake

related deeper note:
- `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`

## new hard conclusion from the prompt-artifact + trust-boundary pass
Hermes is not only a warning about flat truth shape, scope, and freshness.
it is also a warning about **artifact hygiene**:
what the model reads,
what recall treats as evidence,
and what maintenance jobs are allowed to masquerade as normal conversation.

most important adds from the latest pass:
- exact prompt snapshot reuse is one of Hermes' best ideas and should survive as Purr session-epoch artifacts
- compression/working-state helpers can create synthetic conversation-shaped artifacts, which is operationally useful but dangerous if search/recall starts treating them like real chat
- session search can lose the exact child hit by collapsing back to a root parent summary
- load-time prompt material is a trust boundary too; write-time scanning alone is not enough
- continuation only works cleanly if every append/resume/re-entry pointer agrees on the same active lineage leaf

translation for Purr:
- make `session_snapshot`, `turn_overlay`, `evidence_recall`, and `maintenance_artifact` separate typed planes
- never let compaction/salvage summaries pretend to be user or Purr speech
- preserve exact-hit evidence first, then optional lineage recap
- dual-gate prompt-bound material on both write and promotion into packs
- make continuation handoff atomic across pack lookup, transcript append, resume, and recall exclusion

related deeper note:
- `ily/16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md`

## new hard conclusion from the failure-matrix pass
Hermes is not only a warning about flat truth shape, scope drift, freshness, and artifact hygiene.
it is also a warning about **cross-lane alignment**:
prompt artifacts,
recall outputs,
compression survival artifacts,
and mutable memory sinks do not all follow the same scope/trust/evidence rules.

most important adds from the latest pass:
- exact cached system-prompt reuse is one of Hermes' strongest ideas, but not all prompt-bound inputs are snapshotted equally
- the raw FTS/session store is better than the public recall surface; `session_search` can throw away exact-hit evidence by collapsing to root-session summaries
- compression has strong salvage intent, but summary failure can still drop middle turns and structural repair can create fake transcript-shaped artifacts
- context files, local memory files, and Honcho-derived recall do not share one unified admission/safety policy before they touch the model
- gateway/session convenience keys are stronger in the runtime than hard per-user memory identity, which is acceptable for an agent and unacceptable for Purr

translation for Purr:
- every prompt-bound lane must share one admission and authority-label contract
- exact-hit evidence has to survive before recap or lineage summary
- maintenance artifacts must stay typed and filterable, never disguised as normal chat
- owner_id + purr_id must dominate every recall/resume/pack lookup path
- summary failure must fail closed on truth preservation, not silently thin the usable record

related deeper note:
- `ily/17-hermes-memory-failure-matrix-prompt-recall-and-sinks.md`

## new hard conclusion from the feedback-orchestrator pass
Hermes is not only a warning about flat truth shape, freshness, scope drift, and cross-lane trust gaps.
it is also a warning about **missing revalidation semantics**.

most important adds from the latest pass:
- Hermes memory is mostly write-oriented; it has no serious first-class loop for `still true`, `drifted`, `user ignored this`, or `quietly reconfirmed by behavior`
- silence has no durable semantics because there is no typed feedback-orchestration layer separating `no_signal` from contradiction
- there is no product-grade split between truth state, queue execution state, and review outcome artifacts
- passive reconfirmation and trust decay are not first-class mutation paths, so old truths either stay flat text or get replaced by ad hoc edits

translation for Purr:
- verification must be an explicit hidden orchestration layer, not just a due date
- silence should usually mean `no_signal`, not `false`
- passive reconfirmation needs typed writeback just like explicit correction does
- review outcomes must propagate into pack policy and proactive eligibility, not only the memory row itself

related deeper note:
- `ily/20-purr-feedback-orchestrator-review-outcomes-and-trust-decay-contract.md`

## new hard conclusion from the runtime-quality-booster pass
Hermes is not only a lesson in prompt discipline, trust gaps, and truth-shape limits.
it is also a lesson in **runtime choreography**:
how recall arrives,
how damaged replies get repaired,
how working state survives compression,
and how continuity is preserved at boundaries.

most important adds from the latest pass:
- Hermes often feels sharper because recall can be prefetched for the next turn instead of fetched only after the user is waiting
- continuation repair hides truncation and intermediate-ack failures that would otherwise feel like lost context
- compression preserves more than semantic recap; it also carries todo/working-state artifacts so long tasks keep momentum
- prompt-visible overlays and durable transcript history are already semi-separated, even if the contract is still messy
- background expiry/hygiene jobs do real continuity work before the next visible turn suffers
- resume quality comes from restoring the same stored artifact set, not from flat memory becoming magically better

translation for Purr:
- steal next-turn prefetch, boundary-critical hygiene, working-state survival, and resume-by-artifact-pointer behavior
- make overlay/maintenance artifacts typed instead of chat-shaped hacks
- keep repair logic as runtime control events, not fake conversation truth
- never let convenience routing keys or title lineage outrank canonical owner/purr continuity

related deeper note:
- `ily/33-hermes-memory-runtime-quality-boosters-prefetch-repair-and-artifact-separation.md`

## new hard conclusion from the repair / outcome hygiene pass
Hermes is not only a lesson in runtime choreography.
it is also a warning about **repaired-turn contamination**.

most important adds from the latest pass:
- Hermes repair loops can preserve continuity by continuing truncated or ack-style bad replies, but the synthetic continuation/control text can persist as normal conversation-shaped history
- one logical answer can splinter across multiple assistant/runtime turns without a strong durable `one plan -> many attempts -> one final reply` contract
- compression can later summarize repair/control artifacts, which turns runtime scaffolding into fake relationship history
- restored history can keep the repair-shaped text while losing the metadata that said `this was incomplete/repair-only`

translation for Purr:
- keep `repair_outcome` separate from `move_outcome`, `prediction_outcome`, and `pack_outcome`
- store generation attempts and repair/control artifacts in typed runtime lanes, not transcript truth
- allow one logical reply to span many attempts under one plan id, but finalize into at most one canonical assistant message
- never let synthetic continuation prompts, retry nudges, or partial control text become evidence, recall proof, or pack-worthy memory

related deeper note:
- `ily/35-purr-reply-repair-boundary-and-outcome-hygiene.md`

## new hard conclusion from the transcript-normalization pass
Hermes is not only a lesson in runtime choreography and repair hygiene.
it is also a warning about **publication truth drift**:
what the user actually sees,
what the runtime retries,
what the transcript stores,
and what restore/resume later reloads can quietly diverge.

most important adds from the latest pass:
- one logical Hermes reply can persist as multiple assistant attempts plus synthetic continuation/control prompts
- returned final reply text can diverge from the persisted transcript because truncation/fallback paths assemble a visible answer without one matching canonical assistant row
- prior assistant content can get rewritten into synthetic tool filler like `Calling the tool...`
- SQLite restore keeps a thinner normalized conversation than JSON/raw session logs, so cold resume fidelity depends on which store got read
- rewrite/undo/compress paths can permanently normalize history down to the thinner store and erase richer runtime provenance

translation for Purr:
- split `reply_execution_attempt`, `delivery_artifact`, and canonical `assistant_message_event` into different durable planes
- one `plan_id` may span many attempts, but it finalizes into at most one canonical assistant transcript event
- transport wrappers, stream chunks, synthetic continuation prompts, and tool scaffolding must never become relationship evidence
- restore must read canonical transcript truth plus pending attempt state plus snapshot pointers, not guess from whichever raw log kept the most sludge
- finalization has to be idempotent so retry/resume never duplicate assistant truth

related deeper note:
- `ily/36-purr-reply-execution-attempts-and-transcript-normalization-contract.md`

## new hard conclusion from the publication / surface-binding pass
Hermes is not only a lesson in transcript normalization.
it is also a warning about **surface identity drift**:
what the transcript stores,
what the user actually receives,
what platform ids point at,
and what resume/re-entry later targets
can all diverge if delivery provenance has no durable binding layer.

most important adds from the latest pass:
- Hermes keeps useful delivery/runtime behavior (`edit_message`, media sends, voice sends, progress sends), but it does not preserve one durable `publication -> surface delivery` contract
- platform `message_id`s are useful handles for delivery/edit/reply, but they are not safe owner/session/memory identity
- multi-send bundles (text + media + voice + push-like updates) can all represent one logical answer without a stored parent publication object
- retries, edit fallback, and re-entry can create extra sends or lose thread/message linkage without changing transcript truth
- gateway/session convenience ids are stronger in Hermes runtime than a product-grade server-owned surface binding model

translation for Purr:
- keep canonical transcript truth separate from `assistant_publication`, `surface_binding`, and `surface_delivery`
- make surface routing server-owned and auth-bound; never let raw transport ids or client runtime ids become continuity truth
- let edit/replace/resend churn stay inside delivery provenance under one publication lineage
- normalize media/voice/push wrappers into render bundles before send, not into transcript truth or memory evidence
- treat notification open and mobile/webview re-entry as routing events, not assistant or user speech

related deeper note:
- `ily/37-purr-assistant-message-publication-and-surface-binding-contract.md`

## direct conclusion

Hermes already teaches the main lesson:
never confuse raw history with usable memory.

for purr the move is not “build a bigger MEMORY.md.”
it is:
- keep Hermes’ layering discipline
- move the real store to structured per-user data
- generate compact memory packs on demand
- make correction and verification first-class
- keep reply execution traces, delivery traces, and transcript truth in separate planes

that is the lane.
