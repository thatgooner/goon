# Purr session scope + episode lineage contract

## why this note exists
we already knew Hermes was strong on:
- frozen prompt snapshots
- bounded hot memory
- pre-compression salvage
- transcript durability
- compression lineage

but the deeper code pass exposed a harder truth:

`scope isolation is memory quality.`

not boring infra.
not a backend afterthought.
not something we can patch later.

for Purr, `1 human = 1 purr` only stays real if the system is militant about:
- whose memory this is
- which session window a fact came from
- how re-entry continues
- how search walks lineage
- what current-window truth should be suppressed or reused

Hermes is good enough for a local agent.
it is **not** the contract we should copy for a per-user product.

---

## the Hermes findings that force this note
from the live Hermes code on this machine:

### 1. DM/session scope is too weak for a product
Hermes gateway session keys for most DMs are effectively platform-level, not per-human.

why that matters:
- in a product, any chance of cross-user bleed is a hard red line
- `good enough for one local operator` becomes product poison when memory is the product

Purr consequence:
- every durable object must be scoped by `owner_id` and `purr_id` first
- never by platform alone
- never by title alone
- never by `source` alone

### 2. search scope is not identity scope
Hermes search mainly filters by platform/source.
that works for `find my old telegram chat`.
it does **not** work for `this memory belongs to exactly one person and their one Purr`.

Purr consequence:
- retrieval must start with identity boundary
- only after that can it rank by relevance, recency, salience, or semantics

filter order should be:
1. `owner_id`
2. `purr_id`
3. memory lane (`private_1_1 | public_safe | catnet | system_ops`)
4. active episode/window eligibility
5. only then ranking/search

### 3. titles are UX, not truth
Hermes uses title continuation (`foo`, `foo #2`) as part of session continuation UX.
that is fine as convenience.
it is not a real lineage model.

Purr consequence:
- display labels can exist
- they must never be keys
- they must never decide retrieval scope
- they must never stand in for relationship history

### 4. root-collapse during search loses exact evidence
Hermes can resolve child-session hits back to the root parent before summarizing.
that is convenient for a broad recap.
it is bad for exact memory evidence.

failure mode:
- the actual hit happened in a child continuation
- summarization loads only the root transcript
- the matched detail gets blurred or dropped

Purr consequence:
- evidence refs must preserve the **exact** `window_id/message_span`
- lineage traversal can widen context
- but it must not erase the exact hit source

### 5. raw current-session exclusion is not enough
Hermes can skip only the literal current session id, not the whole active lineage.
for Purr this would create weird self-retrieval loops:
- current window says x
- search reaches into parent or sibling window
- stale or redundant evidence comes back in disguised form

Purr consequence:
- retrieval rules need lineage-aware exclusion
- `exclude_current_window` should mean:
  - current window
  - current pack artifacts
  - optionally current active episode branch, depending on use case

### 6. resume should create honest continuation, not muddy reopen behavior
Hermes has split behavior here: compression creates child sessions, but some resume paths can just reopen/repoint old sessions.
that is workable for agent UX.
for Purr it is too muddy.

Purr consequence:
- a resumed relationship window should create an honest continuation artifact
- do not silently mutate history as if the old window never ended
- keep the audit trail clean

---

## direct thesis
Purr needs **3 different continuity layers**.
if we blur them together, memory quality rots fast.

### layer 1 — identity scope
answers:
- who is this memory for?
- which Purr owns it?
- is it private or public-safe?

canonical keys:
- `owner_id`
- `purr_id`
- `memory_lane`

hard rule:
identity scope is mandatory on every durable row.

### layer 2 — episode lineage
answers:
- which chapter of the relationship did this belong to?
- what came before/after it?
- what summary/reentry artifact bridges these windows?

canonical keys:
- `episode_id`
- `parent_episode_id` (optional for higher-order grouping)
- `episode_kind` (`daily_chat | deep_talk | conflict | proactive_loop | catnet_public | other`)

hard rule:
episodes are historical structure.
not prompt structure.

### layer 3 — active window / pack scope
answers:
- what exact session artifact is driving replies right now?
- what pack is frozen?
- what delta patch is active?
- what re-entry boundary created this window?

canonical keys:
- `window_id`
- `parent_window_id`
- `window_state` (`active | idle | compressed | archived | superseded`)
- `pack_version`
- `opened_at`
- `closed_at`
- `closure_reason`

hard rule:
pack reuse lives at the window layer, not at the whole-user layer.

---

## canonical object contract

### 1. `owner`
minimum truth:
- `owner_id`
- `world_user_id` or canonical auth id
- `purr_id`
- `status`

purpose:
- enforce `1 human = 1 purr`
- make every downstream lookup identity-safe

### 2. `purr`
minimum truth:
- `purr_id`
- `owner_id`
- `voice_profile_version`
- `memory_policy_version`
- `created_at`

purpose:
- separate creature identity from raw user account plumbing
- let product voice/config evolve without breaking ownership semantics

### 3. `session_window`
this is the hot conversation artifact boundary.

minimum fields:
- `window_id`
- `owner_id`
- `purr_id`
- `episode_id`
- `parent_window_id`
- `entry_surface` (`world_chat | notification_reentry | internal_proactive | catnet_public | other`)
- `window_state`
- `opened_at`
- `closed_at`
- `closure_reason`
- `stored_session_pack_id`
- `stored_reentry_pack_id`

purpose:
- define what exact pack snapshot a live reply is allowed to use
- support compression/re-entry without rewriting history

### 4. `episode`
this is the historical chapter.

minimum fields:
- `episode_id`
- `owner_id`
- `purr_id`
- `kind`
- `started_at`
- `ended_at`
- `status`
- `summary_ref`

purpose:
- let retrieval group related windows without flattening the whole relationship into one endless log

### 5. `message_event`
minimum fields:
- `message_id`
- `window_id`
- `episode_id`
- `owner_id`
- `purr_id`
- `role`
- `surface`
- `created_at`
- `reply_to_message_id`
- `tool_visibility` (`hidden | user_visible | none`)

purpose:
- exact evidence source for memory extraction
- keeps 1:1, proactive, and later Catnet events distinct

### 6. `pack_artifact`
minimum fields:
- `pack_id`
- `window_id`
- `pack_type` (`session_pack | turn_delta_pack | reentry_pack | proactive_pack`)
- `version`
- `created_at`
- `supersedes_pack_id`
- `token_budget`
- `artifact_hash`

purpose:
- make prompt-driving state explicit and auditable
- stop `what was the model actually reading?` from becoming a mystery

---

## continuity rules

### rule 1 — every new message attaches to an active window, never to a vague user blob
if no active window exists:
- create a new `session_window`
- attach it to an `episode`
- materialize the initial pack artifact

### rule 2 — compression creates a child window, not a rewritten past
same core lesson as Hermes, but stricter.

when compression/archive happens:
- close current window honestly
- create child window with `parent_window_id`
- store new pack artifact there
- preserve old evidence refs untouched

### rule 3 — mobile re-entry should usually create a new window inside the same episode, not reopen history in place
why:
- webview/mobile state is fragile
- re-entry is a real product event
- different window = cleaner pack semantics

rough first pass:
- warm return / short idle -> new child window in same episode
- long idle or topic break -> new episode + new window
- exact timings can tune later

### rule 4 — titles/labels are derived views only
allowed:
- `late-night spiral`
- `tuesday slump`
- `work drag`

not allowed:
- using those labels as durable lookup keys
- assuming uniqueness
- using them for scope or auth

### rule 5 — retrieval returns exact hit first, lineage context second
for any retrieval/search result, preserve:
- exact `message_id` or span hit
- exact `window_id`
- exact `episode_id`

optional enrichments can then add:
- parent/child window summary
- episode summary
- related memory items

never do this backwards.

---

## retrieval contract for Purr

### private 1:1 retrieval
default filter stack:
1. `owner_id = current_owner`
2. `purr_id = current_purr`
3. `memory_lane = private_1_1`
4. exclude suppressed/challenged truth where appropriate
5. rank by relevance/recency/salience/confidence

### public-safe Catnet retrieval
filter stack:
1. `purr_id = current_purr`
2. `memory_lane = public_safe`
3. public-policy eligibility
4. freshness/trust gates
5. novelty/reply-value ranking

hard split:
Catnet must never search raw private 1:1 memory as if it were public evidence.

### current-window exclusion
when a search mode says `exclude current`, define it precisely:
- current `window_id`
- active pack artifacts for that window
- optionally same active episode branch if the goal is long-tail recall

### lineage walk rule
search may widen across lineage only when:
- exact-window hits are weak
- a summary is requested
- an episode-level recap is needed

it may not widen just because root-level aggregation is easier to code.

---

## pack lifecycle implications
this note closes a hole left between `08` and `09`.

those notes defined:
- memory states
- review logic
- pack artifacts
- patch vs rebuild rules

this note adds:
- **what a pack is scoped to**

answer:
- `session_pack` belongs to a `window_id`
- `turn_delta_pack` belongs to a `window_id`
- `reentry_pack` belongs to the boundary between a closed window and its continuation
- `proactive_pack` belongs to a `purr_id`, but must still reference the active/target window or episode it is reasoning about

without this, pack caching gets dangerous:
- wrong pack can bleed across windows
- stale re-entry state can look current
- exact evidence becomes hard to audit

---

## mobile/webview implications
World mini app reality makes all this more important.

### what can go wrong if scope is sloppy
- webview dies and old client state is mistaken for current window truth
- notification tap reuses the wrong pack
- a resume path mutates an old window instead of creating clean continuation
- background jobs reason on the wrong active surface

### first-pass product stance
server owns continuity.
client only resumes it.

that means:
- active window and pack artifacts live server-side
- re-entry is a server event
- idle cutoff/reopen rules are backend policy
- client resets must not redefine ownership or scope

---

## failure modes this contract is meant to stop

### 1. cross-user bleed
worst failure.
Purr A touches Purr B memory lane by bad scoping.

fix:
- `owner_id` + `purr_id` mandatory everywhere

### 2. fake continuity on resume
system quietly reopens old state and nobody knows what pack is actually active.

fix:
- explicit `session_window`
- child-window continuation
- pack artifact versioning

### 3. evidence blur
search result says a memory is grounded, but exact matched span got lost in root aggregation.

fix:
- exact hit preservation
- lineage context only as enrichment

### 4. stale self-retrieval loops
active window searches parent lineage and rediscovers stale truth as if it were fresh evidence.

fix:
- lineage-aware exclusion
- challenged/suppressed state respected before ranking

### 5. title-key corruption
cute labels accidentally become logic keys.

fix:
- labels derived only
- ids drive everything

### 6. mobile re-entry amnesia or duplicate identity
client resets cause either false amnesia or duplicate Purr/session state.

fix:
- server-side active-window contract
- owner-bound lookup before any resume

---

## strongest conclusion
Hermes taught the repo one good lesson already:
`keep the hot pack stable.`

this pass adds the missing product lesson:
`keep identity and lineage exact.`

for Purr, memory quality is not just:
- what facts got stored
- what pack got built

it is also:
- whose truth this is
- which window it came from
- which episode it belongs to
- whether re-entry created honest continuation
- whether retrieval can prove the exact evidence without blurring the trail

if we get this wrong, `1 human = 1 purr` turns into cosplay.
if we get it right, continuity actually has teeth.

---

## immediate repo implication
before phase-one build order gets locked, code-worker should have an explicit research read on:
- identity/scope keys
- session window vs episode split
- continuation/re-entry child-window policy
- exact-hit retrieval vs lineage recap behavior
- pack artifact ownership by `window_id`

because `memory ledger` and `memory-context-packer` are both underspecified until this contract is nailed.