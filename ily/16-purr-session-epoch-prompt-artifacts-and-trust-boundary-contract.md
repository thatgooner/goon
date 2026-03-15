# Purr session-epoch, prompt-artifacts, and trust-boundary contract

## why this note exists
`09` locked pack artifacts.
`11` locked session scope and lineage.
`14` locked runtime intake and salvage ordering.
`15` locked the hidden private-chat move planner.

that got us most of the way.
what was still too loose was the seam between them:

- what the model actually reads
- what is durable truth but not prompt-visible yet
- what is only a maintenance artifact
- when a session pack is reused vs rebuilt
- how compression/re-entry handoff stays honest
- how prompt-bound memory stays safe when it comes from more than one sink

latest Hermes code pass on this machine made that gap obvious.
Hermes is strongest exactly where it treats prompt state like a controlled artifact.
it is weakest where maintenance or recall starts pretending to be normal conversation truth.

Purr cannot leave that boundary fuzzy.
if we do,
we get:
- stale-but-authoritative prompt state
- fake user/assistant artifacts polluting recall
- search/resume disagreement across lineage
- compaction that quietly deletes middle truth
- hidden memory sinks poisoning future packs

this note locks the missing contract.

---

## the Hermes lessons that force this note

### 1. exact prompt snapshot reuse is real and worth stealing
Hermes stores and reloads the exact prompt snapshot for continued sessions instead of rebuilding from live files every turn.
that is one of the best things in the system.

what it teaches:
- the active prompt is an artifact
- stable artifacts are good for cache discipline and behavior stability
- continuation should reuse the same artifact until a deliberate epoch change happens

Purr consequence:
- keep an immutable session-epoch snapshot pack
- do not treat the live ledger as if it should be re-poured into the model every turn

### 2. fake chat artifacts are a hidden contamination path
Hermes compression/salvage can materialize synthetic summary-style messages or working-state reminders as normal conversation-shaped entries.
that helps the runtime survive.
it also muddies provenance.

what it teaches:
- maintenance artifacts are necessary
- pretending they are real user/assistant turns is not acceptable for a memory-first product

Purr consequence:
- maintenance artifacts must be typed and filterable
- they must never masquerade as first-party speech

### 3. compaction cannot be allowed to become deletion
Hermes can drop middle history if summary generation fails.
for an assistant this is already risky.
for Purr it is disqualifying.

what it teaches:
- compaction is not just a cost tool
- compaction is a truth-preservation operation
- fallback policy matters as much as the happy path

Purr consequence:
- if abstraction fails, use extractive checkpointing or refuse compaction
- never silently delete unsummarized middle history

### 4. recall must preserve exact-hit evidence before lineage recap
Hermes session search can collapse child-session hits back to a root parent and summarize the wrong scope.
that is convenient UX.
it is weak evidence discipline.

what it teaches:
- recall and lineage recap are different jobs
- the exact hit has to survive

Purr consequence:
- recall should return exact evidence first
- lineage summary is allowed only as a second layer

### 5. prompt-bound material needs trust policy on read, not only on write
Hermes scans tool-mediated memory writes,
but load-time prompt material and mirrored/secondary sinks can bypass the same safety policy.

what it teaches:
- `future prompt material` is the real trust boundary
- every source that can later touch the model needs the same policy

Purr consequence:
- sanitize and classify at write time
- sanitize and classify again before promotion into any pack
- keep sink parity across local rows, background jobs, and future remote memory mirrors

### 6. continuation pointer handoff is a real systems problem
Hermes gets the high-level idea right: new child continuation after compression.
but once a system has multiple stores and multiple session handles,
child creation alone is not enough.

what it teaches:
- the runtime, persistence layer, and re-entry alias all need the same canonical leaf
- otherwise prompt artifact reuse and transcript persistence drift apart

Purr consequence:
- session-window continuation has to be an atomic pointer handoff
- search, resume, pack lookup, and transcript append all need the same leaf identity

---

## direct thesis
Purr needs a **session-epoch contract** with **typed prompt-artifact planes**.

strong rule:
**not every durable thing is prompt material. not every prompt-visible thing is conversation truth.**

v1 should explicitly separate 5 planes:

1. **durable ledger truth**
   - typed memory rows, evidence refs, events, packs, windows
2. **session snapshot artifact**
   - immutable prompt-driving pack for one active epoch
3. **turn overlay artifact**
   - tiny committed freshness patch for the next reply only
4. **evidence recall artifact**
   - exact quoted spans and minimal lineage context for retrieval/re-entry
5. **maintenance artifact**
   - salvage, compaction, scheduler, review, and planner outputs that are searchable/auditable but not first-party chat turns

if these planes blur together,
Purr will look smart until the first contradiction, re-entry, or recall test.
then it will start lying with confidence.

---

## note map
1. design rules
2. canonical artifact planes
3. session epoch contract
4. reuse vs patch vs rebuild rules
5. compaction and continuation handoff
6. recall/resume truth contract
7. prompt-material trust boundary
8. failure modes to forbid
9. build acceptance tests

---

## 1. design rules

### rule 1 — immutable snapshot, mutable ledger
- ledger truth can change at any time through committed mutations
- the active session snapshot stays stable for one epoch
- same-turn freshness comes from a tiny committed overlay, not a full rebuild

### rule 2 — typed maintenance only
- summaries
- salvage outputs
- planner artifacts
- review outcomes
- scheduler notes

may all exist.
but they must never be stored as fake `user` or fake `purr` speech.

### rule 3 — exact evidence outranks recap
whenever recall or resume is trying to explain `why do we think this`,
show/use:
1. exact evidence span
2. owning window/episode ids
3. then optional lineage recap

never the reverse.

### rule 4 — compaction is allowed to reduce prompt cost, not truth quality
compaction may:
- create a new epoch snapshot
- create extractive/abstractive maintenance artifacts
- close an old hot window

compaction may not:
- erase unsalvaged evidence
- replace exact evidence with summary-only truth
- invent fake chat turns

### rule 5 — promotion to prompt is a second trust gate
something can be durably stored and still not be safe to inject.

promotion checks must look at:
- provenance
- visibility lane
- sensitivity
- confidence
- contradiction state
- safety scan result

### rule 6 — one canonical active leaf
for a given `(owner_id, purr_id, surface)` there is one active conversation leaf.
all of these must point to it:
- transcript append path
- latest session snapshot lookup
- re-entry alias
- recall current-lineage exclusion
- resume target

### rule 7 — if fallback cannot preserve truth, stop
if pack rebuild, summary, or recall synthesis fails in a way that would drop evidence,
fail closed.
no heroic silent deletion.

---

## 2. canonical artifact planes

## 2.1 durable ledger truth
this is everything the system may know or infer durably.
examples:
- `memory_items`
- `memory_events`
- `memory_evidence_refs`
- `message_events`
- `session_windows`
- `episodes`
- `pack_artifacts`
- `reply_move_plan`
- future `review_outcomes`

important:
- durable does not mean prompt-visible
- maintenance artifacts may live here too, but with their own type/lane

## 2.2 `session_snapshot_artifact`
this is the immutable prompt-driving body for one epoch.
think:
- the exact pack bytes or structured artifact that defined the current hot session state
- stable across normal turns
- reused on continuation/re-entry until a real rebuild trigger happens

minimum fields:
- `snapshot_id`
- `owner_id`
- `purr_id`
- `window_id`
- `epoch_id`
- `artifact_type` (`session_snapshot`)
- `pack_version`
- `artifact_body`
- `artifact_hash`
- `source_memory_cutoff`
- `created_at`

hard rule:
- immutable once issued

## 2.3 `turn_overlay_artifact`
this is the small freshness patch allowed to affect the next reply.

examples:
- direct correction
- contradiction suppression
- new hard boundary
- one high-leverage preference shift
- one planner hint authorized by `15`

minimum fields:
- `overlay_id`
- `window_id`
- `epoch_id`
- `source_event_id`
- `overlay_class` (`correction | contradiction | boundary | planner_hint | safety`)
- `driving_memory_ids[]`
- `expires_after_turns`
- `created_at`

hard caps:
- max 3 memory ids
- max 1 planner hint
- short TTL

hard rule:
- overlay must reference committed ledger rows only

## 2.4 `evidence_recall_artifact`
this is what recall/re-entry uses when it needs proof, not just vibes.

minimum fields:
- `recall_artifact_id`
- `owner_id`
- `purr_id`
- `lineage_id`
- `hit_window_id`
- `hit_message_id`
- `hit_evidence_ids[]`
- `quoted_excerpt`
- `lineage_recap` (optional)
- `created_at`

hard rule:
- the quoted excerpt must come from exact evidence refs
- lineage recap may not replace the excerpt

## 2.5 `maintenance_artifact`
this is the lane Hermes muddies and Purr must not.

allowed kinds:
- `compaction_summary`
- `extractive_checkpoint`
- `salvage_run`
- `review_outcome`
- `scheduler_decision`
- `pack_rebuild_request`
- `lineage_bridge`
- `tool_stub`

minimum fields:
- `maintenance_id`
- `owner_id`
- `purr_id`
- `window_id` or `episode_id`
- `kind`
- `source_trigger`
- `provenance_refs`
- `body`
- `visibility` (`internal_only | recall_visible | ops_visible`)
- `created_at`

hard rule:
- never emitted as chat role `user` or `purr`
- must be filterable out of normal conversational recall

---

## 3. session epoch contract

## 3.1 what an epoch is
an epoch is the time window during which one immutable session snapshot stays authoritative.

an epoch ends when:
- compaction succeeds
- explicit re-entry boundary creates a new child window
- a manual rebuild-worthy policy change lands
- a catastrophic integrity issue forces rebuild

an epoch does **not** end for:
- ordinary memory writes
- normal review scheduling
- background salience updates
- weak prediction changes

## 3.2 canonical ids
Purr should keep these separate:
- `episode_id` = historical chapter
- `window_id` = hot conversational boundary
- `epoch_id` = prompt snapshot generation boundary inside a window lineage
- `lineage_id` = stable family id joining related windows/epochs for recall/resume

hard rule:
- current-lineage exclusion in recall uses `lineage_id`, not just one `window_id`

## 3.3 epoch read model
one reply may read:
- `session_snapshot_artifact`
- zero or one `turn_overlay_artifact`
- exact evidence recall bundle if retrieval justifies it
- one `reply_move_plan` if planner says so

it may not read:
- raw extractor chatter
- unsanitized maintenance bodies
- speculative background notes with no provenance

---

## 4. reuse vs patch vs rebuild rules

## 4.1 reuse the snapshot when
reuse the current `session_snapshot_artifact` if:
- no correction/boundary contradiction landed
- retrieval result fits inside existing slots
- no compaction boundary fired
- no epoch-integrity issue exists

this should be the default.

## 4.2 patch with overlay when
use `turn_overlay_artifact` when:
- a same-turn correction changes reply truth
- a challenged memory must be suppressed immediately
- a safety/boundary flag needs to override old tone/assumption
- one planner hint materially changes the move

hard rule:
- overlay is cheaper than rebuild
- overlay is also narrower than rebuild

## 4.3 rebuild the snapshot when
issue a new epoch snapshot only when:
- compaction handoff completes
- re-entry boundary creates a new child continuation
- snapshot slot composition is materially wrong now
- policy/version change requires fresh artifact generation
- integrity checker flags contamination or drift

## 4.4 never rebuild for decorative reasons
do not rebuild just because:
- a new weak pattern signal appeared
- salience changed a little
- a deferred worker recomputed scores
- background maintenance wants everything to feel fresh

Hermes' best lesson here still holds:
restraint is part of quality.

---

## 5. compaction and continuation handoff

## 5.1 direct thesis
compaction is a **fork-and-handoff** operation,
not an in-place rewrite.

## 5.2 required order
when a compaction or re-entry boundary fires:
1. freeze intake range to salvage
2. run salvage on unsalvaged source-event range
3. commit resulting ledger mutations
4. materialize maintenance artifacts (`compaction_summary` or `extractive_checkpoint`)
5. create child `window_id` and new `epoch_id`
6. build new `session_snapshot_artifact`
7. atomically update the active-leaf pointer / alias
8. only then mark the old window as `compressed | superseded | archived`

hard rule:
- never close old hot state before the child snapshot exists

## 5.3 fallback ladder
if abstractive compaction summary fails:
1. try extractive checkpoint from exact evidence / open loops / active truths
2. if that fails, do **not** destroy the old epoch
3. leave rebuild pending and keep the old active state

hard rule:
- `summary failed -> drop middle anyway` is forbidden

## 5.4 transcript and recall hygiene
compaction may produce:
- summary artifact
- lineage bridge artifact
- pack artifact

it may not produce:
- fake `user` messages like `here is what happened earlier`
- fake `purr` messages pretending the cat already said the summary

## 5.5 pointer handoff contract
the same atomic transaction or tightly-coupled commit boundary should update:
- `session_windows.active_leaf`
- `surface_alias -> current_window_id`
- `stored_session_pack_id`
- any resume/re-entry pointer
- any current-lineage exclusion pointer

if one moves and the others do not,
search, recall, append, and resume will disagree.

---

## 6. recall/resume truth contract

## 6.1 recall and resume must share lineage semantics
resume should target the latest active leaf in a lineage.
recall should summarize or retrieve from the lineage without losing the exact hit.

that means:
- no root-only collapse when the hit lives in a child
- no current-window-only exclusion when the whole lineage is still active

## 6.2 recall output contract
minimum recall result for a meaningful hit:
- `lineage_id`
- `hit_window_id`
- `hit_message_id`
- `hit_evidence_ids[]`
- `quoted_excerpt`
- `source_time`
- optional `lineage_recap`

not enough:
- summary-only prose with no proof handle

## 6.3 synthetic artifacts in recall
maintenance artifacts may help navigation.
but recall must make them visually/structurally distinct from:
- human speech
- purr speech
- raw evidence

## 6.4 current-lineage exclusion rule
if the active lineage is still the one being chatted in,
recall should not bounce back a stale root summary as if it were a separate old memory.

useful exceptions may exist for:
- explicit `show earlier in this lineage`
- explicit audit/debug mode

but the default consumer recall surface should exclude the active lineage family.

---

## 7. prompt-material trust boundary

## 7.1 what counts as prompt-bound material
all of these count:
- session snapshot pack body
- overlay body
- evidence recall excerpts
- planner hint lines
- maintenance artifacts that are allowed into recall-visible surfaces
- any future mirrored/remote memory summary

if it can touch the model,
it belongs to the trust boundary.

## 7.2 dual-gate policy
### gate A — write-time admission
on initial write/store:
- validate source lane
- classify sensitivity
- safety-scan content
- enforce structured provenance

### gate B — promotion-time admission
before prompt/recall injection:
- re-scan or revalidate content
- check current contradiction/challenge state
- verify visibility lane
- strip or quarantine unsafe/irrelevant fields

hard rule:
- write-safe once does not mean prompt-safe forever

## 7.3 sink parity rule
local storage,
background worker proposals,
future remote mirrors,
and future Catnet-safe summaries must all pass equivalent trust policy.

no privileged backdoor sink.

## 7.4 authority-label rule
prompt-bound memory should not all speak with the same authority.
when injected, the system should still know if something is:
- explicit user claim
- repeated observed pattern
- unresolved hypothesis
- maintenance inference
- exact quoted evidence

that label may be hidden in the structure,
but it must exist.

---

## 8. failure modes to forbid

### forbidden 1 — fake conversation salvage
no synthetic maintenance note may be stored as if the user or Purr literally said it.

### forbidden 2 — child-hit collapse without proof
no recall path may throw away the child hit and summarize only the root ancestor.

### forbidden 3 — compaction-without-preservation
no system may close an old epoch if salvage/checkpoint creation failed.

### forbidden 4 — stale-root resume
no resume alias may point to a stale ancestor while transcript append points to a new child.

### forbidden 5 — load-only trust gap
no prompt-bound store may bypass read-time validation just because it was already saved earlier.

### forbidden 6 — sink mismatch
no mirrored or worker-generated memory sink may bypass the same provenance/safety policy as the main intake path.

### forbidden 7 — summary pretending to be evidence
summary artifacts may support navigation.
they may not count as exact proof unless they point back to exact evidence refs.

---

## 9. build acceptance tests
phase-one build work should not be considered correct unless it can pass tests like these:

### test 1 — same-turn correction without full rebuild
- old session snapshot says preference A
- new user message corrects to preference B
- ledger commits B
- next reply uses overlay and does not state A
- snapshot id stays unchanged

### test 2 — compaction creates honest child continuation
- active window has unsalvaged recent turns
- compaction fires
- salvage commits before old window closes
- child window + new epoch + new snapshot are created
- resume/re-entry alias points to the child

### test 3 — summary failure does not delete history
- compaction summary generation fails
- system falls back to extractive checkpoint or keeps old epoch active
- no evidence rows or accessible history disappear

### test 4 — recall preserves exact child hit
- matching evidence lives in a child continuation
- recall result returns child `window_id`, exact `message_id`, and quoted excerpt
- optional lineage recap may mention the root, but does not replace the hit

### test 5 — maintenance artifacts stay distinct
- salvage and review artifacts exist
- normal recall/chat replay does not present them as user/Purr speech
- audit mode can still inspect them

### test 6 — prompt-bound trust gate catches stale unsafe material
- a saved but later-flagged artifact exists
- promotion-time scan blocks/quarantines it from the next pack
- durable audit row still records the block

### test 7 — active leaf pointer stays aligned
- after child continuation handoff,
  transcript append,
  snapshot lookup,
  resume,
  and current-lineage exclusion all resolve to the same active leaf

---

## direct conclusion
Hermes' strongest hidden lesson is not just `freeze the prompt`.
it is:

**treat what the model reads as a first-class artifact plane.**

Hermes gets part of that right with exact prompt snapshot reuse.
it gets sloppier when:
- maintenance artifacts blur into fake chat
- recall loses the exact child hit
- load-time trust boundaries stay weak
- lineage handoff can drift across stores

Purr should steal the discipline,
then make it stricter.

that means:
- immutable session epochs
- tiny committed overlays
- exact-hit evidence recall
- typed maintenance artifacts
- atomic continuation handoff
- dual-gated prompt-material safety

if we lock this,
`memory is the product` stops being a slogan and starts becoming a systems contract.
