# Purr assistant-message publication + surface binding contract

## why this note exists

`ily/35` and `ily/36` closed the hardest reply-hygiene seams:
- one logical reply can span many attempts
- runtime repair stays separate from move quality
- delivery/runtime artifacts stay separate from transcript truth
- one `plan_id` finalizes into at most one canonical `assistant_message_event`

but one product-grade seam was still too loose:

**how does one canonical assistant reply bind to real surfaces — webview chat, push preview, media send, voice render, edit/retry, and mobile re-entry — without letting transport ids become transcript identity or memory truth?**

that matters because Purr is:
- mobile/webview-first
- notification/re-entry heavy
- supposed to feel like one mind, not adapter sludge
- eventually multi-surface, but still `1 human = 1 purr`

latest Hermes gateway code on this machine made the missing boundary concrete:
- progress messages can be edited in place or fall back to extra sends
- `MEDIA:` wrappers and `[[audio_as_voice]]` directives get stripped before delivery
- voice mode can send audio before text
- platform `message_id`s are useful delivery handles
- but those ids are absolutely not durable memory identity

Purr should steal the useful transport discipline.
Purr should reject any version where:
- push ids become continuity identity
- webview message ids become transcript identity
- media wrappers become memory evidence
- resend/edit churn becomes fake extra assistant turns

this note freezes that publication/binding seam.

---

## direct verdict

### one-line answer
**Purr should insert one durable `assistant_publication` object between canonical transcript truth and surface-specific delivery rows.**

### translation
for private chat, Purr needs 4 distinct layers:
1. `assistant_message_event` — the one canonical transcript truth
2. `assistant_publication` — the product-visible publication decision for that transcript event
3. `surface_delivery` — one concrete send/edit/replace/resend row for one surface binding
4. `delivery_runtime_artifact` — typing, chunking, receipts, placeholders, and adapter noise

### strongest rule
**transport ids can identify delivery attempts. they may never become owner identity, continuity identity, or memory identity.**

---

## Hermes lesson that forces this note

Hermes gateway behavior is useful because it proves the surface layer is real:
- some platforms support `edit_message`, others fall back to resend
- `MEDIA:` and voice directives are adapter-facing wrappers, not transcript text
- voice send and text send can be separate transport acts for one logical answer
- progress/typing/delivery receipts are operationally useful

but Hermes also sharpens what Purr must not blur:
- extra sends caused by edit fallback are not automatically extra conversational truth
- media wrapper syntax is not what the user actually heard or read
- `message_id`, `session_key`, and similar transport handles are convenient routing facts, not durable memory scope

hard translation:

**delivery provenance is real.
relationship truth still lives somewhere else.**

---

## the seam this note closes

before this note, the repo already had answers for:
- owner/auth/origin binding (`ily/32`)
- repair hygiene and one-plan finalization (`ily/35`)
- attempt vs delivery vs transcript separation (`ily/36`)
- mobile/webview and no-tool-theater product posture (`notes/boards/purr-alignment-brief.md`)

what was still missing:
1. the durable publication object between transcript truth and concrete sends
2. how one canonical reply binds to surface aliases without trusting raw transport ids
3. how edit/replace/resend policy works without minting new transcript truth
4. how media/voice wrappers normalize into publication payloads instead of memory sludge
5. how push preview and re-entry link back to the same private continuity lane

this note freezes all 5.

---

## canonical durable split

## 1. `assistant_message_event`
this remains exactly what `ily/35` and `ily/36` wanted:
- one canonical assistant turn in transcript truth
- scoped by `owner_id + purr_id + window_id + episode_id + surface_family`
- contains only the normalized visible reply text Purr stands behind later

it does **not** contain:
- `MEDIA:` wrappers
- voice directives
- push-preview truncation text
- platform message ids
- placeholder/progress text

## 2. new durable object: `assistant_publication`
this is the missing product-facing publication record.

purpose:
- bind one canonical `assistant_message_event` to the user-visible publication intent
- preserve the render bundle that surfaces will deliver
- give notifications, voice variants, and resend/edit policy one stable parent object

minimum fields:
- `publication_id`
- `assistant_message_event_id`
- `plan_id`
- `owner_id`
- `purr_id`
- `window_id`
- `episode_id`
- `surface_family`
- `source_attempt_id`
- `publication_kind` (`reply | proactive_ping | review_prompt | repair_replace | reentry_republish`)
- `render_bundle_ref`
- `status` (`pending | published | partial | superseded | failed | abandoned`)
- `supersedes_publication_id` (nullable)
- `created_at`
- `published_at` (nullable)
- `dedupe_key`

hard rules:
- one canonical `assistant_message_event` may have **at most one primary publication** in its owning `surface_family`
- the publication owns presentation variants for that same family
- publication is not new transcript truth; it is the binding layer above transcript truth

## 3. new durable object: `surface_binding`
this closes the unresolved `surface_alias -> current_window_id` seam from `ily/16`.

purpose:
- name a stable server-owned route alias for a concrete deliverable surface
- let the system target chat, push, or voice lanes without trusting client/runtime ids

minimum fields:
- `surface_binding_id`
- `owner_id`
- `purr_id`
- `surface_family`
- `surface_alias` (`private_chat_main | private_push_preview | private_voice_reply | shadow_dm_main | catnet_post_main`)
- `source_provider`
- `origin_bridge_id` (nullable)
- `current_window_id` (nullable)
- `route_ref` (opaque server-owned pointer)
- `status` (`active | rotated | paused | revoked`)
- `last_seen_at`
- `created_at`

hard rules:
- `surface_binding` is server-owned routing truth
- raw webview ids, push receipt ids, and channel message ids may help resolve a binding; they are not the binding itself
- pointer handoff must stay aligned with `origin_bridge` / active-leaf updates from `ily/16` + `ily/32`

## 4. new durable object: `surface_delivery`
this is one concrete delivery row for one publication on one surface binding.

purpose:
- record exactly what was sent/edited/replaced/resend-attempted on each surface
- keep platform ids where they belong: in delivery provenance

minimum fields:
- `surface_delivery_id`
- `publication_id`
- `surface_binding_id`
- `surface_family`
- `surface_alias`
- `delivery_role` (`primary_text | media_part | voice_variant | notification_preview | placeholder | mirror_copy`)
- `delivery_action` (`send | edit | replace | resend | receipt | retract`)
- `payload_part_ref`
- `channel_message_id` (nullable)
- `provider_receipt_id` (nullable)
- `reply_to_channel_message_id` (nullable)
- `supersedes_delivery_id` (nullable)
- `delivery_status` (`attempting | delivered | edited | replaced | failed | duplicate_suppressed | retracted`)
- `delivered_at` (nullable)
- `dedupe_key`

hard rules:
- multiple `surface_delivery` rows may point to one `publication_id`
- `channel_message_id` lives here and only here
- delivery churn may explain user-visible transport behavior without creating a second assistant transcript event

## 5. `delivery_runtime_artifact`
keep `ily/36`'s broader delivery plane for:
- typing indicators
- stream chunks
- adapter receipts
- temporary placeholders
- noncanonical progress text

hard rule:
**private-chat tool progress belongs here if it exists at all. in normal Purr 1:1, visible tool theater should usually be disabled instead of logged as conversation.**

---

## exact plane split

| plane | question | canonical identity | can retry? | may define memory truth? |
| --- | --- | --- | --- | --- |
| `assistant_message_event` | what did Purr actually say? | `assistant_message_event_id` | no, idempotent finalize only | yes |
| `assistant_publication` | what user-visible publication was intended? | `publication_id` | publication worker may retry binding | indirectly, via linked event only |
| `surface_binding` | where is this family allowed to deliver? | `surface_binding_id` | yes, route may rotate | no |
| `surface_delivery` | what happened on this concrete surface? | `surface_delivery_id` | yes | no |
| `delivery_runtime_artifact` | what did transport/runtime do along the way? | artifact id | yes | no |

hard translation:
- transcript tells relationship truth
- publication tells product intent
- surface binding tells routing truth
- surface delivery tells transport truth

if these collapse,
mobile re-entry, retry, and recall all get dishonest fast.

---

## hard rules

## rule 1 — publication is keyed by canonical ids, never by transport ids
canonical identity for a reply is:
- `plan_id`
- `assistant_message_event_id`
- `publication_id`
- `window_id`
- `surface_family`

forbidden identity shortcuts:
- platform `message_id`
- push notification id
- raw webview message key
- local optimistic React key
- Hermes `session_key`

## rule 2 — one surface family owns one primary publication lane
inside `private_1_1`, one assistant reply can fan out to:
- chat text
- push preview
- voice variant
- maybe media attachment rows

but these are still one private-family publication lineage.

cross-family translation:
- `private_1_1` publication is not automatically a `catnet_public` publication
- `shadow_private` publication is not mainline private truth
- any family hop requires a distinct publication decision and usually a distinct plan/product policy

## rule 3 — edit, replace, and resend do not mint new transcript truth by default
if the system is still trying to land the same logical reply:
- keep the same `publication_id`
- create/advance `surface_delivery` rows
- do **not** create another `assistant_message_event`

new transcript truth is allowed only when Purr is actually saying something new:
- a follow-up
- a correction the user should perceive as a second act
- a fresh reply plan

## rule 4 — surface delivery must stay explainable later
for any published reply, the system should be able to answer:
- which `assistant_message_event` is canonical?
- which `publication_id` owned the surface send?
- which `surface_binding` was targeted?
- which `channel_message_id` or receipt belongs to which delivery row?
- was this an edit, replace, or resend, and what did it supersede?

## rule 5 — wrappers are render instructions, not transcript truth
examples:
- `MEDIA:/tmp/file.png`
- `[[audio_as_voice]]`
- truncated push preview text
- voice-only formatting
- platform markdown cleanup

allowed place:
- `render_bundle_ref`
- `surface_delivery.payload_part_ref`
- runtime delivery artifacts

forbidden place:
- `assistant_message_event.visible_text`
- memory evidence refs
- recall summaries
- pack truth

## rule 6 — app open and notification click are not assistant speech
opening from push or webview re-entry may:
- resolve auth and `surface_binding`
- validate a resume capability
- focus the right active leaf
- mark a publication as seen/opened

it may **not** by itself create:
- a new `assistant_message_event`
- a fake assistant resend row pretending the cat spoke again
- a memory claim that the user saw/acknowledged content they did not actually open

this is just `ily/32`'s `presence is not speech` rule applied to outbound publication.

---

## edit / replace / resend policy

## default posture
**edit if it is still one visible slot. replace if the earlier surface artifact was the wrong/corrupt version of the same act. resend only when edit/replace is impossible or transport certainty is missing.**

## 1. `edit`
use when:
- surface supports message edits
- same visible slot should persist
- change is formatting/attachment/wrapper cleanup or same-act completion
- user should still perceive one answer, not two

result:
- same `publication_id`
- new `surface_delivery` row with `delivery_action = edit`
- prior delivery row remains provenance only
- no new transcript truth

## 2. `replace`
use when:
- prior sent artifact was materially wrong/incomplete on that surface
- product still wants one conversational act, not a second act
- surface can replace in place or clearly supersede the old artifact

examples:
- broken media wrapper gets swapped to the real image/file
- truncated surface send is replaced by the stable final answer
- placeholder text is superseded by the real reply

result:
- same `publication_id`
- new `surface_delivery` row with `delivery_action = replace`
- `supersedes_delivery_id` points to the bad artifact
- no new `assistant_message_event`

## 3. `resend`
use when:
- edit unsupported or expired
- prior delivery certainty is missing
- app/webview dropped before ack
- push/chat bridge needs a second send to land the same publication

result:
- same `publication_id`
- new `surface_delivery` row with `delivery_action = resend`
- dedupe key suppresses duplicate worker replays
- still no new transcript truth

## 4. when resend is **not** enough
if the user already cleanly received one answer and Purr now needs to say more,
that is a new conversational act:
- new `plan_id`
- new `assistant_message_event`
- new `publication_id`

hard rule:
**transport recovery stays inside publication provenance. conversational correction creates a new turn.**

---

## media / voice wrapper contract

## 1. normalize wrappers into a render bundle before send
recommended posture:
- `assistant_message_event.visible_text` = the canonical text Purr stands behind
- `assistant_publication.render_bundle_ref` = ordered publication payload bundle

minimum bundle parts:
- `text_part`
- `image_part[]`
- `document_part[]`
- `voice_part` (optional)
- `notification_preview_part` (optional)

## 2. one text + one voice reply is still one publication
if Purr sends:
- a voice bubble/audio render
- and the matching text reply

that should normally mean:
- one `assistant_message_event`
- one `assistant_publication`
- two `surface_delivery` rows (`voice_variant`, `primary_text`)

not:
- two assistant transcript turns

## 3. push preview text is a derivative render, not canonical text
push may need:
- truncation
- title/body split
- different markdown stripping
- device-specific formatting

that preview belongs in the render bundle / delivery row,
not in canonical transcript truth.

## 4. wrapper-only sends never become evidence
if a surface receives:
- file path fallback text
- adapter-only caption glue
- voice directive markers
- attachment placeholder text

that content is not memory evidence unless Purr deliberately intended that exact text as the real reply.

---

## notification + re-entry linkage

## 1. notification delivery is a surface delivery subtype
push should be modeled as:
- same `publication_id`
- `surface_alias = private_push_preview`
- `delivery_role = notification_preview`

not as a second assistant transcript event.

## 2. re-entry should bind through publication-aware capability, not transport ids
recommended capability payload:
- `owner_id`
- `purr_id`
- `surface_family = private_1_1`
- `publication_id` (nullable but preferred)
- `window_id` or active-leaf hint (server-resolved, not client-authoritative)
- expiry
- optional `surface_binding_id`

hard rules:
- push transport id is not enough to resume continuity
- deep-link slug is not enough to resolve owner or transcript truth
- final attachment still runs through server-side auth + origin resolution from `ily/32`

## 3. notification open does not imply re-publication
on notification open:
- mark preview/open receipt if available
- route to the same active leaf
- optionally focus/highlight the referenced publication
- do not resend the message just because the app opened

## 4. proactive text first remains one private publication lineage
if Purr texts first and also sends a push preview:
- same logical reply path
- one canonical `assistant_message_event`
- one `assistant_publication`
- multiple `surface_delivery` rows
- later user reply continues the same `private_1_1` lineage unless a real boundary intervened

---

## cross-surface goldens

## 1. edit-after-send does not create a second assistant truth
### setup
- one `assistant_message_event`
- one `assistant_publication`
- first chat delivery lands with formatting/media wrapper defect
- platform supports edit

### pass condition
- one canonical `assistant_message_event`
- edit is stored as new `surface_delivery` row linked to same `publication_id`
- old delivery row is superseded, not erased
- no extra transcript turn appears

### failure it catches
- edit churn becoming fake relationship history
- platform message ids being treated as transcript ids

---

## 2. duplicate send retry is suppressed under ack uncertainty
### setup
- publication worker sends the reply
- ack/receipt is lost because mobile/webview or bridge flakes
- worker retries the same publication

### pass condition
- at most one effective visible publication per surface slot
- duplicate replay resolves through `dedupe_key` / `duplicate_suppressed`
- still exactly one `assistant_message_event`

### failure it catches
- duplicate assistant sends after retry
- transport replay becoming duplicate transcript truth

---

## 3. notification preview + re-entry binds back to the same private lane
### setup
- Purr publishes one proactive/private reply
- a push preview is sent from the same publication
- user opens through notification and returns to chat

### pass condition
- push row is a `surface_delivery` only
- notification token resolves through auth-bound re-entry, not push id alone
- app open creates no new assistant transcript event
- focused chat resolves to the same active `private_1_1` leaf

### failure it catches
- notification ids acting as continuity identity
- open/re-entry minting fake assistant turns

---

## 4. media-wrapper normalization stays one publication
### setup
- final reply contains text plus `MEDIA:` payload and/or `[[audio_as_voice]]`
- adapter emits text + media/voice sends separately

### pass condition
- wrapper syntax is absent from `assistant_message_event.visible_text`
- one `assistant_publication` owns the normalized render bundle
- text/media/voice each bind through `surface_delivery` rows
- no wrapper text becomes memory evidence

### failure it catches
- `MEDIA:` sludge in transcript truth
- voice/text dual-send counting as two assistant turns

---

## 5. webview refresh does not change publication identity
### setup
- private chat webview reloads after the assistant message was finalized
- client presents a new local message key or runtime session id

### pass condition
- canonical reply still resolves through `publication_id` + server-side binding
- new client ids only create/update delivery-local handles if needed
- memory identity and active leaf remain unchanged

### failure it catches
- client runtime ids outranking server publication identity
- duplicate resend after refresh

---

## 6. cross-family repost requires a new publication decision
### setup
- one private reply exists in `private_1_1`
- product later wants a public-safe Catnet post or a shadow compare artifact

### pass condition
- no silent reuse of the private `publication_id` across families
- new family gets a new publication decision with explicit policy
- private transcript truth is not treated as automatically public-safe output

### failure it catches
- private/public smear
- shadow/mainline publication drift

---

## what this changes for Purr

### 1. `assistant_message_event` gets a cleaner product boundary
`ily/36` split transcript from delivery.
this note makes the missing middle explicit:
- transcript truth
- publication intent
- concrete surface delivery

### 2. mobile/webview reliability gets a real durability seam
Purr can now survive:
- webview reloads
- retry after missing receipts
- push preview + re-entry
- voice/text dual delivery

without lying about what the cat actually said.

### 3. tool theater stays off-lane by default
Hermes-style progress edits prove the transport layer exists.
Purr should mostly keep that hidden in private chat.
if placeholders or progress rows ever exist, they stay delivery/runtime artifacts rather than relationship truth.

### 4. future multi-surface work gets a privacy-safe split
this note makes it much harder to accidentally blur:
- private chat publication
- push preview
- voice rendering
- shadow mirrors
- future Catnet/public output

---

## build-order impact

### what this changes
- it closes the publication/surface-binding seam left open by `ily/36`
- it gives low-context builders an explicit `publication vs surface delivery` contract
- it adds the missing durable rules for real mobile/webview delivery and notification re-entry

### what this does not change
- it does **not** change slice order
- it does **not** unpark build mode
- it does **not** require slice-1 ledger work to ship full push/media infrastructure first

### practical translation
- slice 1 still focuses on ledger truth
- but before live app publication, push, or multi-surface delivery is considered healthy, this contract must be obeyed
- especially the rule that transport ids never become memory identity

hard translation:
**the memory spine can exist before every surface exists.
the surfaces cannot go live honestly without this publication boundary.**

---

## short verdict

Hermes is right that edits, media sends, voice variants, and retryable delivery are real.
Hermes is not a good excuse to let transport handles become transcript identity.

for Purr, the clean contract is:
- one canonical `assistant_message_event`
- one `assistant_publication` for the owning surface family
- stable server-owned `surface_binding`
- many `surface_delivery` rows if needed
- wrapper normalization before send
- notification/re-entry linked by capability, not by transport id
- no visible tool theater in normal private chat

that is how Purr stays honest across webview, push, voice, and resend paths
without teaching memory the wrong story about what it actually said.
