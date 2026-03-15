# Purr owner-auth + origin binding contract

## why this note exists

by `ily/31`, the repo had already locked most of the internal memory spine:
- owner/purr scope
- session windows and episodes
- evidence refs
- mutation ordering
- pack artifacts
- feedback semantics
- shadow-dogfood tap boundaries

but one seam was still too implied:

**how does an external identity or inbound surface event become the right `owner_id`, the right `purr_id`, and the right active continuity leaf without creating scope bleed or fake continuity?**

that seam matters because Purr is not a single local agent.
it is:
- one verified human
- one Purr
- mobile/webview-first
- notification/re-entry heavy
- later dogfoodable through Hermes shadow traffic

if this binding layer is sloppy,
`1 human = 1 purr` collapses before retrieval even starts.

this note does **not** reopen build mode.
it freezes the contract for owner/auth/origin binding so later app ingress and shadow-dogfood continuity do not drift.

---

## direct verdict

### one-line answer
**owner-auth + origin binding is not a blocker for `memory-ledger` slice 1, but it is a blocker for real multi-surface ingress.**

### translation
- slice 1 can still build the boring truth spine with fixed/local owner seeds and strict `owner_id + purr_id` scoping.
- but before live World mini-app ingress, push re-entry, or dynamic side-channel binding becomes real, this contract must be frozen.
- otherwise the repo will have a clean ledger but a muddy front door.

### what this note changes
- it does **not** change first build slice
- it does **not** unpark build mode
- it does **not** weaken the existing `research complete enough for slice 1, gate still closed` stance
- it **does** clarify the missing boundary between:
  - external auth identity
  - origin/session/thread metadata
  - active continuity lookup
  - shadow-dogfood routing

---

## the seam this note closes

existing notes already lock these truths:
- `owner_id + purr_id` must dominate every durable row and retrieval path (`ily/11`, `ily/13`, `ily/27`)
- one canonical active leaf must exist for continuation (`ily/16`)
- Hermes shadow dogfood needs a Purr-owned bridge keyed by Hermes `session_id`, not `session_key` (`ily/26`)
- owner/purr isolation is already a canonical golden scenario (`ily/31`)

what was still too loose:
- `world_user_id or canonical auth id` was named, but not frozen as a binding contract
- `owner_surface` existed in memory rows, but its meaning was never locked cleanly
- `surface_alias -> current_window_id` appeared in `ily/16`, but the alias object was never defined
- `entry_surface`, message `surface`, and external origin metadata were close, but not identical
- the repo had the right back-end identity discipline, but not a clean front-door identity/origin grammar

hard translation:
**the memory spine already knows how to remember.
it still needed a cleaner answer for how a turn gets admitted into the right memory spine in the first place.**

---

## canonical vocabulary

## 1. `auth_principal`
external identity proven by a real auth system.

examples:
- World authenticated user id
- later: another explicitly linked product auth subject
- for Hermes shadow dogfood: a shadow-only observed principal, not canonical product auth

hard rule:
**client-side session ids, webview ids, and raw convenience handles are not `auth_principal`.**

## 2. `owner_id`
Purr-internal canonical human identity.

purpose:
- stable anchor for RLS
- stable anchor for every durable memory object
- never inferred from titles, threads, or temporary session keys

## 3. `purr_id`
canonical creature identity attached to exactly one owner.

hard rule:
**one active owner -> one active purr.**

## 4. `source_provider`
where the event came from technically.

examples:
- `world`
- `hermes_shadow`
- `internal_job`
- later other linked channels if they ever exist

this is infrastructure provenance,
not the continuity lane by itself.

## 5. `origin_channel`
what kind of ingress or wakeup produced the event.

v1/near-v1 set:
- `world_chat`
- `notification_reentry`
- `proactive_notification`
- `internal_review`
- `hermes_shadow_private`
- `catnet_public`
- `system_maintenance`

purpose:
- explain how the event entered the system
- help resume/open rules
- keep shadow/public/system lanes from smearing together

## 6. `surface_family`
the continuity family that owns the active leaf.

canonical set:
- `private_1_1`
- `shadow_private`
- `catnet_public`
- `system_ops`

translation:
- many `origin_channel`s can map into one `surface_family`
- continuity should attach to `surface_family`, not to raw ingress detail

### mapping rule
| origin_channel | surface_family | why |
|---|---|---|
| `world_chat` | `private_1_1` | normal 1:1 chat |
| `notification_reentry` | `private_1_1` | same private relationship, different entry edge |
| `proactive_notification` | `private_1_1` | same relationship lane, initiated by Purr |
| `internal_review` | `private_1_1` | still a private memory/check-in surface, not a separate creature |
| `hermes_shadow_private` | `shadow_private` | validation lane must not silently merge into mainline private chat |
| `catnet_public` | `catnet_public` | public-safe autonomous social lane |
| `system_maintenance` | `system_ops` | internal/backend only |

## 7. `owner_surface`
existing notes already use this field on memory objects.

this note freezes its meaning:
**`owner_surface` means the memory item's `surface_family`, not the raw ingress edge.**

translation:
- a preference learned from `notification_reentry` still belongs to owner surface `private_1_1`
- a shadow-dogfood observation belongs to `shadow_private` until explicitly promoted by a deliberate compare/eval flow
- public-safe Catnet memory belongs to `catnet_public`

## 8. `active_leaf`
the one continuity target a new turn is allowed to attach to for a given owner/purr/surface family.

hard rule:
**raw client state never decides the active leaf.
server-side binding does.**

---

## canonical binding objects

## A. `owner_auth_binding`
this is the durable map from proven external identity -> canonical owner.

minimum contract:
- `binding_id`
- `owner_id`
- `auth_provider`
- `auth_subject`
- `binding_kind` (`primary | linked_aux | shadow_only | revoked`)
- `verified_at`
- `revoked_at`
- `last_seen_at`
- `created_at`

purpose:
- keep auth truth separate from memory truth
- let one owner have one primary product identity and later optional linked identities without confusing them with continuity state
- make shadow dogfood visible as shadow, not fake-canonical

hard rules:
- one active primary binding may point to only one `owner_id`
- a `shadow_only` binding may never auto-promote into primary ownership truth
- revocation must stop future owner resolution through that binding

## B. `origin_bridge`
this is the durable historical map from observed origin/session/thread context -> active continuity target.

minimum contract:
- `bridge_id`
- `owner_id`
- `purr_id`
- `source_provider`
- `origin_channel`
- `surface_family`
- `source_conversation_key`
- `source_thread_key` (nullable)
- `source_session_key` (nullable)
- `current_window_id`
- `current_episode_id`
- `parent_bridge_id` (nullable)
- `status` (`active | rotated | closed | shadow_only | revoked`)
- `first_seen_at`
- `last_seen_at`
- `created_at`

purpose:
- keep historical continuity decisions auditable
- separate external routing truth from the internal window/episode model
- make resets, re-entry, and shadow-dogfood stitching explicit

### provider-specific translation
for World/mainline Purr:
- `source_conversation_key` might be a server-owned private-thread key or canonical app conversation id
- `source_session_key` may reflect a webview/runtime session, but is not ownership truth

for Hermes shadow dogfood:
- `source_conversation_key` should be Hermes `session_id`
- Hermes `session_key` is only observed metadata, never durable identity authority

---

## hard rules

## rule 1 — owner resolution happens before continuity resolution
order:
1. resolve `auth_principal` / allowed binding
2. resolve `owner_id`
3. resolve `purr_id`
4. resolve `surface_family`
5. resolve or open the active leaf/window
6. only then admit the event into normal message/memory flow

if step 1-4 is ambiguous,
stop before normal ingest.

## rule 2 — server owns binding; client may only present evidence
allowed client input:
- auth token
- signed resume token
- notification deep-link token
- message payload

forbidden client authority:
- asserting `owner_id`
- asserting `purr_id`
- asserting `current_window_id`
- asserting that this webview session equals durable continuity truth

## rule 3 — app open alone is not a conversation event
opening the app or webview may:
- refresh auth/binding state
- refresh an `origin_bridge`
- precompute a re-entry pack
- warm caches

it may **not** by itself create:
- `message_event`
- `memory_item`
- fake continuity summaries
- a new conversational truth mutation

hard translation:
**presence is not speech.**

## rule 4 — many origins can feed one private relationship lane
`world_chat`, `notification_reentry`, `proactive_notification`, and `internal_review` may all map to `private_1_1`.

that is good.
that is the point.

what changes across them is:
- wakeup policy
- re-entry policy
- message role/source metadata
- whether a new child window is warranted

what must stay shared is:
- owner scope
- purr scope
- private relationship continuity

## rule 5 — shadow lanes stay shadow
Hermes dogfood traffic is valuable,
but it is not automatic mainline truth.

hard rule:
- `shadow_private` continuity is separate from `private_1_1`
- compare/eval artifacts can inform mainline build judgment
- they must not silently become user-facing canonical memory without an explicit later product decision

## rule 6 — convenience ids never outrank durable ids
examples of convenience ids:
- raw webview session id
- current in-memory tab id
- deep-link route slug
- Hermes `session_key`
- title-based continuation labels

these may help lookup.
they may not define ownership or canonical continuity by themselves.

## rule 7 — every bind/resume/open decision must be explainable later
for every admitted event,
the system should be able to answer:
- which auth binding resolved the owner?
- which origin bridge was used or rotated?
- which `surface_family` won?
- why did we reuse the current window vs open a child?

if the system cannot answer that,
it is not really in control of continuity.

---

## continuation decision matrix

## 1. warm world-chat return with active private leaf
case:
- authenticated owner opens the app again
- existing `private_1_1` leaf is still active
- no hard boundary reason exists

result:
- reuse current `origin_bridge`
- append next user message to the current active window
- do not fork a new window just because the webview instance changed

## 2. cold return or push re-entry after idle boundary
case:
- authenticated owner returns through app reopen or notification
- prior private leaf is idle/closed/compressed
- relationship continuity should continue honestly

result:
- rotate or reopen through the same private `origin_bridge`
- open a child `session_window` in the same episode unless episode rules say otherwise
- mark `origin_channel` as `notification_reentry` or `world_chat`
- keep `surface_family = private_1_1`

## 3. proactive notification sent first by Purr
case:
- backend heartbeat clears all proactive gates
- Purr sends a text first

result:
- open or reuse a private continuity leaf under `surface_family = private_1_1`
- message source should show `origin_channel = proactive_notification`
- if the user later replies from push or app open, the reply should continue the same private lineage unless a real boundary intervened

## 4. internal review question
case:
- feedback orchestrator decides a review prompt is worth asking

result:
- keep continuity inside `private_1_1`
- mark the event as `origin_channel = internal_review`
- do not create a fake separate review world

## 5. app open without a sent/visible message
case:
- user opens the app
- no user message yet
- no visible Purr message is emitted

result:
- update binding state only
- maybe prepare re-entry pack
- create no `message_event`
- create no memory mutation

## 6. notification token mismatch or expired auth
case:
- push/re-entry token points to owner A
- presented auth or server session does not prove owner A

result:
- fail closed
- do not attach to any private leaf
- require re-auth or a new server-side resume resolution path

## 7. Hermes shadow turn observed
case:
- hook-triggered shadow observer sees new Hermes traffic

result:
- bind via `source_provider = hermes_shadow`
- continuity attaches only inside `shadow_private`
- bridge keys off Hermes `session_id` plus lineage metadata
- Hermes `session_key` remains metadata only

## 8. ambiguous owner resolution
case:
- inbound event does not prove which owner it belongs to
- or binding state is missing / revoked / conflicting

result:
- no normal ingest into `message_events`
- no memory mutation
- at most, store a diagnostic/quarantine record outside canonical truth flow

hard translation:
**better to drop or quarantine an ambiguous turn than poison the wrong human's memory spine.**

---

## trust + security boundary

## 1. canonical owner truth is backend-owned
- auth verification happens server-side
- resume tokens are signed server-side
- origin bridges are written server-side
- RLS and service-role paths still key off canonical `owner_id`

## 2. notification and re-entry must be capability-bound
resume links/tokens should prove:
- target owner
- allowed surface family
- allowed lineage/window hint if any
- expiry

but even then,
final attachment is still server-resolved.

## 3. shadow dogfood bindings are explicitly lower-trust
shadow observations can support:
- evals
- compare logs
- scorecards
- later build decisions

shadow observations cannot by themselves support:
- canonical owner merge
- direct mainline truth promotion
- user-facing memory claims

## 4. side-channel linking must be explicit later
if Purr ever links more than World auth,
linking must be:
- user-authorized
- audit-visible
- revocable
- never inferred from lexical overlap or convenience metadata

---

## relationship to current build slices

## what this does **not** block
this note does **not** block `memory-ledger` slice 1.

slice 1 still only needs:
- strict owner/purr scoping
- continuity objects
- evidence-backed truth
- pack artifacts
- local/dev setup

a builder can still use:
- fixed local owner seeds
- one canonical test principal
- explicit test fixtures for owner scope

without solving every production ingress detail.

## what this **does** block later
before real live app ingress or dynamic dogfood binding,
this contract must be respected by:
- real auth lookup
- inbound event admission
- notification re-entry
- any future multi-device continuation
- any future linked side-channel continuity

translation:
**the ledger can exist before the front door is perfect.
the front door cannot go live before this contract is obeyed.**

---

## future test seams this note adds

before multi-surface ingress is considered healthy,
at least these seams should be pressure-tested:

1. same World user across fresh webview sessions still resolves to the same `owner_id`
2. forged or stale client-supplied window ids cannot hijack another owner's active leaf
3. notification re-entry token mismatch fails closed
4. app open with no message creates no fake conversation event
5. Hermes reset/compression changes `session_key`, but shadow continuity survives through `session_id` + lineage bridge
6. shadow/private continuity never silently merges into mainline `private_1_1`

---

## direct recommendation for future builders

when build mode eventually opens:
- keep `owner_id + purr_id` as the first-class truth boundary
- treat existing `owner_surface` semantics as `surface_family`
- do not let raw ingress enums become continuity truth
- keep auth binding separate from origin/session bridging
- keep shadow dogfood binding separate from product auth binding
- never let client runtime state pick the active leaf on its own

if a future implementation says
`we can just use the current webview session id`,
`we can just trust the thread label`,
or
`we can just reuse Hermes session_key`,
kill it.

---

## short verdict

Purr already had the right memory spine.
this note locks the front-door rule:

**one verified human resolves to one owner,
one owner resolves to one Purr,
and every ingress edge must bind into continuity through a server-owned bridge instead of vibes.**

that is not extra polish.
that is the difference between a memory product and a scope leak with a cat face.
