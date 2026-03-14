# Purr memory-ledger schema + mutation + invariants contract

## why this note exists
`12` locked the shared claim/evidence/selection contract.
that solved the `what is a memory object?` problem.

what is still too loose for the first build slice is:
- what exact durable objects exist in Supabase/Postgres
- which ones are immutable vs mutable
- what must happen atomically on merge / challenge / supersede
- what the packer is allowed to read
- what invariants must never break, even when background jobs or mobile re-entry get weird

without this note, `memory-ledger` is still just a nice task name.
with this note, it becomes a buildable slice.

---

## direct thesis
Purr's first ledger should **not** be `one memories table`.

it should be a small relational spine with clear roles:

1. **relationship/window objects**
   - who this belongs to and which active window/episode it came from
2. **raw message/event objects**
   - exact source events, not just summaries
3. **immutable evidence refs**
   - exact spans back to those source events
4. **immutable memory events**
   - created / confirmed / challenged / superseded / rejected / decayed
5. **mutable current memory rows**
   - the current best truth for each memory object
6. **immutable pack artifacts**
   - what the model actually read for a given window/boundary
7. **packer-facing read views**
   - denormalized selection surfaces built for trust-gated packing

that is enough for v1.

not needed in the first ledger slice:
- vector search infra
- Catnet public-memory tables
- user-facing memory UI
- fancy analytics dashboards
- giant generalized workflow engine

---

## note map
1. v1 scope and non-goals
2. canonical durable objects
3. which objects are immutable vs mutable
4. invariants that must never break
5. mutation flows
6. SQL/RLS/index posture
7. minimal API surface for the first slice
8. acceptance tests

---

## 1. v1 scope and non-goals

## v1 scope
this ledger slice should support:
- `1 human = 1 purr` identity-safe storage
- `episode` and `session_window` continuity
- exact `message_event` source capture
- `memory_item` current truth rows
- `memory_event` audit history
- `memory_evidence_ref` exact span grounding
- `pack_artifact` persistence for `session_pack`, `turn_delta_pack`, `reentry_pack`, `proactive_pack`
- `pack_candidate_view` for trust-gated packing
- state transitions from `candidate -> confirmed -> stale/rejected/superseded`
- contradiction overlays and suppression
- review/proactive scheduling fields on current memory rows

## not in v1
keep these out of the first ledger slice:
- embeddings / pgvector
- Catnet feed or market tables
- multimodal evidence blobs
- per-memory discussion threads
- client-direct write access to memory internals
- speculative scoring systems that are not yet needed for packing or scheduling

hard rule:
if a schema idea does not improve memory integrity, retrieval precision, or builder clarity, it is bloat.

---

## 2. canonical durable objects

## 2.1 identity refs
Purr should treat auth identity as external, but the ledger still needs hard refs.

### `owners`
minimal columns:
- `owner_id` (uuid, pk)
- `world_user_id` (text/uuid, unique)
- `status`
- `created_at`

purpose:
- canonical human identity boundary
- anchor for RLS and every downstream row

### `purrs`
minimal columns:
- `purr_id` (uuid, pk)
- `owner_id` (fk -> owners)
- `voice_profile_version`
- `memory_policy_version`
- `status`
- `created_at`

purpose:
- make `1 human = 1 purr` explicit
- keep creature identity/config separate from raw auth

constraint:
- unique active purr per owner

---

## 2.2 continuity objects

### `episodes`
this is the historical chapter.

minimal columns:
- `episode_id` (uuid, pk)
- `owner_id` (fk)
- `purr_id` (fk)
- `kind` (`daily_chat | deep_talk | conflict | proactive_loop | other`)
- `status` (`open | closed | archived`)
- `parent_episode_id` (nullable fk -> episodes)
- `started_at`
- `ended_at`
- `summary_ref` (nullable)
- `created_at`

purpose:
- group related windows without flattening the whole relationship into one endless chat
- preserve lineage for retrieval and recap

### `session_windows`
this is the hot conversation boundary.

minimal columns:
- `window_id` (uuid, pk)
- `owner_id` (fk)
- `purr_id` (fk)
- `episode_id` (fk)
- `parent_window_id` (nullable fk -> session_windows)
- `entry_surface` (`world_chat | notification_reentry | internal_proactive | other`)
- `window_state` (`active | idle | compressed | archived | superseded`)
- `opened_at`
- `closed_at`
- `closure_reason`
- `stored_session_pack_id` (nullable fk -> pack_artifacts)
- `stored_reentry_pack_id` (nullable fk -> pack_artifacts)
- `pack_version`
- `created_at`

purpose:
- define which exact prompt-driving pack is active right now
- support honest continuation instead of muddy reopen behavior

constraint:
- one active window per `(owner_id, purr_id, entry_surface)` at most if that surface is single-threaded
- never reuse a closed window as if it never ended

---

## 2.3 raw event objects

### `message_events`
this is the canonical source log for memory extraction.

minimal columns:
- `message_id` (uuid, pk)
- `owner_id` (fk)
- `purr_id` (fk)
- `episode_id` (fk)
- `window_id` (fk)
- `role` (`user | purr | system`)
- `surface` (`world_chat | proactive_notification | internal_review | other`)
- `tool_visibility` (`hidden | user_visible | none`)
- `content_text`
- `metadata_json`
- `reply_to_message_id` (nullable fk -> message_events)
- `created_at`

purpose:
- exact source record for extraction and audit
- keeps 1:1 chat, proactive sends, and system events distinct

hard rule:
this is not the packer view.
this is the raw event store.

---

## 2.4 memory truth objects

### `memory_items`
this is the mutable current-best-truth row for each memory object.

minimal columns:
- `memory_id` (uuid, pk)
- `owner_id` (fk)
- `purr_id` (fk)
- `memory_lane` (`private_1_1 | public_safe | catnet | system_ops`)
- `kind`
- `state` (`candidate | confirmed | stale | rejected | superseded`)
- `review_status` (`none | queued | due | ask_now | snoozed`)
- `contradiction_status` (`clean | challenged`)
- `pack_policy` (`hot | shadow | suppress | never`)
- `durability_scope` (`profile | relationship | episode | window | ephemeral`)
- `subject_key`
- `dedupe_key`
- `scope_ref` (nullable text/uuid; see scope rule below)
- `episode_id` (nullable fk)
- `origin_window_id` (nullable fk)
- `owner_surface`
- `confidence`
- `salience`
- `volatility`
- `freshness_score`
- `last_confirmed_at`
- `last_hit_at`
- `last_miss_at`
- `needs_review_at`
- `cooldown_until`
- `attempt_count`
- `expires_at`
- `supersedes_memory_id` (nullable fk -> memory_items)
- `payload_json`
- `created_at`
- `updated_at`

purpose:
- current durable truth surface for retrieval, scheduling, and packing
- compact enough to query directly
- rich enough that packer does not need transcript joins every turn

### `memory_events`
this is the immutable audit trail.

minimal columns:
- `memory_event_id` (uuid, pk)
- `memory_id` (fk -> memory_items)
- `owner_id` (fk)
- `purr_id` (fk)
- `event_type` (`created | evidence_appended | confirmed | challenged | review_due | snoozed | superseded | rejected | decayed | pack_hit | pack_miss`)
- `event_reason`
- `actor_type` (`extractor | feedback_policy | review_scheduler | contradiction_resolver | packer | human_confirmation | system`)
- `from_state`
- `to_state`
- `delta_json`
- `created_at`

purpose:
- immutable history of why a memory changed
- supports audit, debugging, and future analytics without turning `memory_items` into a junk drawer

### `memory_evidence_refs`
this is the exact grounding layer.

minimal columns:
- `evidence_id` (uuid, pk)
- `memory_id` (fk -> memory_items)
- `owner_id` (fk)
- `purr_id` (fk)
- `episode_id` (fk)
- `window_id` (fk)
- `message_id` (fk -> message_events)
- `span_start`
- `span_end`
- `source_type` (`chat | proactive_event | app_event | system_summary | other`)
- `excerpt_text`
- `excerpt_hash`
- `evidence_weight`
- `explicitness`
- `speaker_role`
- `derived_from_evidence_id` (nullable fk -> memory_evidence_refs)
- `captured_at`

purpose:
- preserve exact message-span grounding
- prevent summary artifacts from pretending to be raw proof

hard rule:
`system_summary` evidence is allowed only if it points back to raw evidence through `derived_from_evidence_id` or equivalent summary provenance mapping.

---

## 2.5 pack objects

### `pack_artifacts`
this is the immutable stored pack layer.

minimal columns:
- `pack_id` (uuid, pk)
- `owner_id` (fk)
- `purr_id` (fk)
- `window_id` (nullable fk)
- `episode_id` (nullable fk)
- `pack_type` (`session_pack | turn_delta_pack | reentry_pack | proactive_pack`)
- `source_trigger` (`turn_reply | correction_patch | idle_reentry | proactive_preflight | compression_handoff | other`)
- `pack_version`
- `token_estimate`
- `artifact_json`
- `created_at`

purpose:
- store what the model actually got, not just what the ledger could have produced
- make prompt-driving state explicit and auditable

hard rule:
pack artifacts are immutable.
if truth changes, create a new pack.
do not rewrite old pack bodies.

### `pack_candidate_view`
this is a SQL view or materialized view, not an edit target.

minimum output columns:
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
- `response_value`
- `timing_value`
- `evidence_strength`
- `episode_distance`
- `open_loop_weight`
- `suppression_reason`
- `top_evidence_ids`

purpose:
- give the packer a trust-gated read surface
- centralize suppression logic so it is not re-implemented ad hoc in every caller

---

## 3. immutable vs mutable split

## immutable by default
keep these append-only:
- `message_events`
- `memory_events`
- `memory_evidence_refs`
- `pack_artifacts`

why:
- audit trail stays real
- exact evidence survives corrections and re-entry
- debugging does not depend on guesswork

## mutable by design
only these are allowed to represent the current surface:
- `memory_items`
- `episodes.status` / `ended_at`
- `session_windows.window_state` / close fields / latest pack refs

why:
- the product needs a fast current truth surface
- but current truth must never erase event history

---

## 4. invariants that must never break

## invariant 1 — every durable row is identity-scoped first
required on all major objects:
- `owner_id`
- `purr_id`

never let:
- platform
- chat title
- source string
- client thread label

stand in for real identity scope.

## invariant 2 — every memory row belongs to one clear scope bucket
use `durability_scope` + `scope_ref`.

recommended meaning:
- `profile` -> `scope_ref = owner_id`
- `relationship` -> `scope_ref = purr_id`
- `episode` -> `scope_ref = episode_id`
- `window` -> `scope_ref = window_id`
- `ephemeral` -> transient generated id / null with `expires_at`

why:
- stops episode-local truth from masquerading as relationship-global truth
- makes uniqueness and suppression rules honest

## invariant 3 — no current memory truth without evidence
for v1, every `memory_item` must have at least one linked `memory_evidence_ref`.

only allowed exception:
- explicit imported/bootstrap fact with `source_type=system_summary` or `system_seed` and clear provenance note

## invariant 4 — exact evidence must preserve the exact hit
an evidence ref must keep:
- `message_id`
- `window_id`
- `episode_id`
- span offsets

lineage recap is allowed later.
it must not replace the exact hit source.

## invariant 5 — current state must match the latest durable event chain
`memory_items.state`, `review_status`, `contradiction_status`, and `pack_policy` must be explainable by the latest relevant `memory_events`.

if the event log and current row disagree, the current row is wrong.

## invariant 6 — active truth uniqueness must be explicit
Purr needs one active truth per dedupe scope where exclusivity actually applies.

recommended uniqueness key:
`(owner_id, purr_id, memory_lane, dedupe_key, durability_scope, scope_ref)`

partial uniqueness should apply only when:
- `state in ('candidate','confirmed','stale')`
- and the kind/scope is exclusive

do **not** apply this blindly to `episode_anchor` or other intentionally multi-row kinds.

practical rule:
- preferences, boundaries, identity facts -> usually exclusive
- open loops -> often exclusive by topic
- episode anchors -> usually non-exclusive

## invariant 7 — challenged or superseded truth must not pack like clean truth
if:
- `contradiction_status=challenged`
- or `state in ('rejected','superseded')`

then hard-truth slots in `pack_candidate_view` must suppress it.

## invariant 8 — a pack artifact belongs to one boundary
`pack_artifacts` must always be attributable to a window/boundary/episode context.

no free-floating `session_pack` with unclear ownership.

## invariant 9 — one active purr per owner
`1 human = 1 purr` is not copy.
it is a data rule.

## invariant 10 — all cross-object mutations are atomic
merge / challenge / supersede flows must update:
- current row(s)
- event row(s)
- evidence links if new evidence arrives

inside one transaction.

if not, the packer will eventually read impossible truth.

---

## 5. mutation flows

## 5.1 create candidate from extractor output
trigger:
- new user message or qualifying purr/system event

transaction:
1. ensure `message_event` exists
2. resolve identity + scope (`owner_id`, `purr_id`, `episode_id`, `window_id`)
3. decide whether this is:
   - new memory row
   - append-to-existing
   - sibling row
   - challenge/supersede case
4. insert `memory_item` as `candidate` if new
5. insert `memory_evidence_ref`
6. insert `memory_event(event_type='created')`
7. if `suggested_action` implies review pressure, set `review_status` / `needs_review_at`

result:
- extractor proposes
- policy writes durable candidate state

## 5.2 append evidence to existing row
use when:
- same `dedupe_key`
- same active meaning
- no real contradiction

transaction:
1. lock target `memory_item`
2. insert new `memory_evidence_ref`
3. update `memory_items` freshness/confidence/salience fields
4. insert `memory_event(event_type='evidence_appended')`

hard rule:
append evidence only when meaning really matches.
if scope or meaning drifted, create sibling or challenge instead.

## 5.3 supersede old truth
use when:
- newer explicit truth clearly replaces older truth
- same topic, same scope, different now-correct value

transaction:
1. lock old row
2. create new row or resolve candidate as the new active row
3. mark old row `state='superseded'`, `pack_policy='suppress'`
4. set new row `supersedes_memory_id=old.memory_id`
5. insert evidence for new row
6. write `memory_event('superseded')` on old and `memory_event('confirmed' or 'created')` on new

example:
- old tone preference: balanced
- new explicit truth: colder

## 5.4 challenge active truth
use when:
- new evidence pressures active truth
- resolution is not clean enough to supersede immediately

transaction:
1. lock old row
2. set old row `contradiction_status='challenged'`
3. set old row `pack_policy='suppress'`
4. insert new candidate row with contradiction pressure
5. insert evidence
6. write `memory_event('challenged')` on old and `memory_event('created')` on new

result:
- the system gets quieter before it gets bolder
- no double-active incompatible truth in the hot pack

## 5.5 confirm candidate
use when:
- explicit user confirmation arrives
- or the candidate is explicit/high-leverage/low-ambiguity enough for fast promotion

transaction:
1. lock row
2. update `state='confirmed'`
3. set `review_status='none'` unless future review is needed
4. set `last_confirmed_at`
5. write `memory_event('confirmed')`

## 5.6 reject candidate
use when:
- user denies it
- later evidence cleanly breaks it
- policy decides it should never drive behavior

transaction:
1. lock row
2. update `state='rejected'`, `pack_policy='suppress'`
3. write `memory_event('rejected')`

## 5.7 stale/decay
use when:
- memory has aged out
- repeated misses weaken confidence
- context-specific truth is no longer reliable

transaction:
1. lock row
2. update `state='stale'` or `state='superseded'` depending on reason
3. lower `pack_policy` if needed
4. write `memory_event('decayed')`

hard rule:
`stale` is not the same as `rejected`.
stale means `be quieter about this`, not `pretend it never existed`.

## 5.8 pack hit / miss feedback
use when:
- a memory was included in a pack and clearly helped or missed

transaction:
1. update `last_hit_at` or `last_miss_at`
2. optionally adjust freshness / timing fields
3. write `memory_event('pack_hit' or 'pack_miss')`

why this matters:
- prediction-quality memory improves only if hits/misses feed back into the ledger

---

## 6. SQL / RLS / index posture

## 6.1 database posture
assume Supabase Postgres.
keep v1 boring and strong:
- UUID primary keys
- foreign keys everywhere scope matters
- JSONB only for typed payload details, not for core identity/state columns
- partial unique indexes for active truth where exclusivity applies
- SQL view/materialized view for `pack_candidate_view`

## 6.2 recommended indexes
minimum indexes:

### on `memory_items`
- `(owner_id, purr_id, memory_lane, state)`
- `(owner_id, purr_id, dedupe_key)`
- `(owner_id, purr_id, subject_key)`
- `(owner_id, purr_id, needs_review_at)`
- `(owner_id, purr_id, pack_policy, contradiction_status)`
- `(episode_id)`
- `(origin_window_id)`

### on `memory_events`
- `(memory_id, created_at desc)`
- `(owner_id, purr_id, event_type, created_at desc)`

### on `memory_evidence_refs`
- `(memory_id)`
- `(message_id)`
- `(window_id, message_id)`
- `(episode_id)`

### on `session_windows`
- `(owner_id, purr_id, window_state)`
- `(episode_id, opened_at desc)`

### on `pack_artifacts`
- `(owner_id, purr_id, pack_type, created_at desc)`
- `(window_id, pack_type, created_at desc)`

## 6.3 uniqueness constraints
recommended first-pass constraints:
- unique active purr per owner
- unique `world_user_id` in `owners`
- partial unique active-truth index on `memory_items` for exclusive kinds/scopes
- at most one active window per single-threaded surface if product surface requires it

## 6.4 RLS stance
v1 should be strict.

### client reads
allow only narrow owner-scoped reads if needed later.
for now, default posture should be:
- clients do **not** query raw memory internals directly
- clients read chat outputs and maybe curated exports later

### backend/service role
only backend jobs should write:
- candidates
- state transitions
- evidence refs
- pack artifacts
- review scheduling fields

### hard rule
no anonymous or cross-owner reads of memory rows, evidence rows, or pack artifacts.

memory is the product.
that also means memory is the attack surface.

---

## 7. minimal API surface for the first slice
this slice should expose a small boring interface.
not a giant orchestration framework.

## write-side methods
- `open_session_window(owner_id, purr_id, episode_id, entry_surface)`
- `close_session_window(window_id, closure_reason)`
- `append_message_event(...)`
- `create_memory_candidate(...)`
- `append_memory_evidence(memory_id, evidence...)`
- `confirm_memory(memory_id, reason)`
- `challenge_memory(old_memory_id, new_candidate...)`
- `supersede_memory(old_memory_id, new_memory_id, reason)`
- `reject_memory(memory_id, reason)`
- `mark_memory_stale(memory_id, reason)`
- `store_pack_artifact(...)`

## read-side methods
- `get_active_window(owner_id, purr_id, surface)`
- `get_episode_lineage(episode_id)`
- `get_memory(memory_id)`
- `get_pack_candidates(owner_id, purr_id, window_id, pack_type)`
- `get_latest_pack_artifact(window_id, pack_type)`
- `get_memory_evidence(memory_id)`

hard rule:
read methods for the packer should prefer the view/read-model.
not ad hoc raw joins every turn.

---

## 8. packer contract implications
if this ledger slice is implemented right, the later packer gets a clean deal:
- it reads `pack_candidate_view`
- it suppresses challenged/superseded/rejected truth early
- it can still fetch top evidence refs for selected rows
- it can read stored `session_pack` / `reentry_pack` artifacts without rebuilding every turn

if this ledger slice is implemented wrong, the later packer will compensate with transcript mud, duplicate logic, and fake confidence.

---

## 9. failure modes this note is meant to stop

### 1. one giant `memories` table
result:
- no clean audit trail
- no exact evidence contract
- no honest mutation semantics

### 2. current truth without immutable event history
result:
- impossible debugging
- invisible truth jumps
- hard-to-trust review/scheduler behavior

### 3. summary evidence impersonating raw proof
result:
- evidence blur
- false grounding
- bad retrieval under pressure

### 4. cross-owner or platform-global scope leakage
result:
- product death

### 5. non-atomic contradiction handling
result:
- two incompatible truths stay active
- packer sees impossible state

### 6. pack artifacts not stored durably
result:
- no clue what the model actually read
- mobile re-entry feels stateless
- debugging turns into folklore

### 7. vector rushed into the first slice
result:
- schema work gets muddy
- retrieval quality gets blamed on embeddings instead of truth shape

---

## 10. acceptance tests for the future build
`memory-ledger` should not count as done unless it can pass checks like these:

- every `memory_item` row carries `owner_id` + `purr_id` and valid scope fields
- a memory candidate cannot be created without at least one evidence ref
- explicit correction can supersede an old preference without leaving both active in the same exclusive dedupe scope
- contradiction can challenge active truth and suppress it from pack candidates in one transaction
- `pack_candidate_view` hides challenged/superseded/rejected rows from hard-truth lanes
- `session_pack`, `turn_delta_pack`, `reentry_pack`, and `proactive_pack` can all be stored immutably and queried by boundary
- warm re-entry can open a child `session_window` without mutating old window history
- exact evidence lookup returns the original message/span even if later summaries exist
- a `memory_event` trail explains every current memory state transition
- no client policy allows owner A to read owner B's memory/evidence/pack rows
- vector search is not required for the first ledger migration to be considered complete

---

## strongest conclusions
- the first build slice should be a **relational memory spine**, not a blob store.
- the ledger needs **7 durable object families**: identity refs, continuity objects, raw message events, current memory rows, memory events, evidence refs, and pack artifacts.
- `memory_items` is the mutable surface; `memory_events`, `memory_evidence_refs`, and `pack_artifacts` stay immutable.
- the most important invariant is not just `one memory per thing`.
it is **one active truth per honest dedupe scope, with exact evidence and atomic mutation**.
- `pack_candidate_view` should be treated as a first-class read model so later packer code stays small and disciplined.
- v1 should stay boring: strong Postgres schema, strict scope, exact evidence, no vector detour yet.

if we ship this shape first, later extractor/packer/review jobs have something real to stand on.
if we skip it, every later slice turns into cleanup for a muddy base.