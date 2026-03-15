# Hermes shadow-dogfood adapter + tap-boundary contract

## why this note exists

ily/23 already said Hermes-first dogfood is a **partial yes**:
- good for backend-memory plumbing validation
- bad for validating Purr taste / creature behavior
- must stay shadow-only

that verdict was right, but still incomplete.

we still did not have the exact answer to:
- **where** the adapter should tap Hermes
- **what** data Hermes actually preserves vs throws away
- **how** to keep the adapter out of Hermes behavior
- **which** ids can be trusted for replay / idempotency in phases 0-2
- **what** failure modes appear if we naively tail Hermes storage like an append-only log

this note closes that gap.

it is not a build note.
it is the research contract for how future dogfood can observe Hermes without turning Hermes into Purr or quietly inheriting Hermes storage bugs.

---

## direct verdict

### best phase-0 boundary
**use Hermes' built-in hook system as a timing trigger, then do a read-only snapshot from `state.db`, with `sessions.json` joined in only for origin metadata.**

in plain english:
- hook events tell us **when** a session starts / resets / finishes a turn
- SQLite tells us **what messages and prompt snapshot Hermes actually persisted**
- `sessions.json` tells us **which platform/chat/thread that session currently belongs to**

### do NOT do this
- do **not** embed the adapter inside Hermes' reply path
- do **not** tail `messages.id` as if Hermes were a clean append-only event log
- do **not** use Hermes `MEMORY.md`, `USER.md`, or injected system-prompt memory blocks as canonical evidence
- do **not** let Purr state feed back into Hermes behavior
- do **not** assume `session_key` is a durable per-user identity

### strongest hidden conclusion
Hermes is good enough to serve as a **shadow source of real conversations**,
but **not** as a trustworthy historical routing ledger.

if we dogfood on Hermes, Purr must own its own historical origin bridge keyed by Hermes `session_id`.
otherwise resets, compression continuations, and DM key coarseness will blur provenance fast.

---

## what Hermes actually gives us

## 1. hook surfaces we can use without patching Hermes

Hermes already ships a hook system under `vendor/hermes-agent/gateway/hooks.py`.
it loads handlers from `~/.hermes/hooks/` and explicitly swallows hook errors so observer failures do not break the main pipeline.

useful events:
- `session:start`
- `session:reset`
- `agent:start`
- `agent:end`
- optional: `agent:step` for debugging only

best use:
- `session:start` -> capture current origin metadata while it still exists in gateway state
- `agent:end` -> snapshot the finished turn from SQLite after Hermes has already persisted it
- `session:reset` -> close the current bridge / mark boundary

important limit:
these hooks are **timing signals**, not rich message payloads.
for example, `agent:start` / `agent:end` expose small context like platform, user_id, session_id, and message/response preview — not full Telegram message ids, raw updates, or stable platform timestamps.

translation:
**hooks tell us when to read. they are not the thing we store as evidence.**

---

## 2. SQLite is the real session/message store

`vendor/hermes-agent/hermes_state.py` is the real transcript/session spine.
it gives us:

### sessions
- `id` = Hermes `session_id`
- `source`
- `user_id`
- `model`
- `model_config`
- `system_prompt`
- `parent_session_id`
- `started_at`, `ended_at`, `end_reason`
- counters
- `title`

### messages
- row `id`
- `session_id`
- `role`
- `content`
- `tool_call_id`
- `tool_calls`
- `tool_name`
- `timestamp`
- `finish_reason`

### why this matters
this is enough for:
- shadow raw-turn ingestion
- evidence refs into Hermes text spans
- pack compare against Hermes' actual stored `system_prompt`
- lineage reconstruction through `parent_session_id`

### hidden caveat
the `messages.timestamp` value is Hermes write-time (`time.time()`),
not necessarily the original platform event time.
so it is good enough for ordering,
but not good enough to pretend we still have exact Telegram-side chronology.

---

## 3. `sessions.json` still matters

`vendor/hermes-agent/gateway/session.py` keeps a JSON index mapping the live `session_key` to:
- `session_id`
- platform
- current origin
- `chat_id`
- `chat_name`
- `chat_type`
- `user_id`
- `user_name`
- `thread_id`
- `chat_topic`
- token counters

this file matters because SQLite **does not** preserve:
- `chat_id`
- `chat_name`
- `chat_type`
- `thread_id`
- `user_name`
- the current session key

so the adapter needs `sessions.json` to recover the routing context around a session **when the session is live**.

### but this file is not enough by itself
`sessions.json` is only a current index.
when a session resets or gets replaced, the mapping gets overwritten.
it is not a historical routing ledger.

translation:
- use it to seed bridge metadata at `session:start`
- do **not** trust it as the long-term source of truth later

---

## what Hermes does NOT preserve cleanly enough

## 1. provider message identity is mostly gone by the time SQLite is written

Hermes' normalized `MessageEvent` object can carry:
- platform `message_id`
- `reply_to_message_id`
- original timestamp
- raw platform payload

Telegram's adapter does populate these fields.

but those fields are not written through into SQLite's `messages` table.
so by the time we read `state.db`, we usually no longer have:
- Telegram `message_id`
- Telegram `reply_to_message_id`
- original provider timestamp
- raw update payload

### consequence
for phases 0-2, the adapter should treat the Hermes-side upstream identity as:
- `hermes_session_id`
- message row id inside that session
- content hash / role / local ordering

not as canonical provider ids.

if later dogfood truly needs provider message ids, that requires a richer observer boundary.
that is a later decision, not a reason to pollute the current research-first lane.

---

## 2. `session_key` is not durable enough for Purr-grade identity

Hermes `build_session_key()` has a convenience rule for DMs:
- with thread_id -> thread-scoped key
- WhatsApp DM -> chat_id-scoped key
- otherwise -> one coarse `agent:main:<platform>:dm`

that is fine for an agent runtime.
it is not serious product identity.

### consequence
Purr dogfood must never anchor continuity on Hermes `session_key`.
use it only as a temporary lookup handle.

hard rule:
**the durable bridge key is Hermes `session_id`, not `session_key`.**

---

## 3. Hermes transcript history is not a pure append-only log

this is the easiest trap.

Hermes can:
- clear and rewrite transcript state
- compress long sessions
- create child sessions with `parent_session_id`
- move continuation to a new `session_id`

that means:
- row ids are not enough to describe semantic continuity
- a naive tailer can double-count rewrites
- a naive tailer can miss deletion/rewrite boundaries
- a naive single-session reader can orphan child-session continuation after compression

### consequence
never design the adapter as:
- "watch new SQLite rows forever and assume they are immutable user events"

instead:
- use hooks as timing edges
- snapshot at safe boundaries
- stitch lineage through `parent_session_id`
- let Purr maintain its own ingest checkpoints and bridge records

---

## 4. Hermes prompt material is useful for compare, dangerous for evidence

Hermes stores the actual `system_prompt` used for the session.
this is valuable for phase-1 pack compare.

it is **not** valuable as user evidence.

why:
- prompt material already contains curated / derived / maintenance content
- Hermes memory files are assistant-facing abstractions, not exact user speech
- Purr note 16 already says maintenance artifacts must never masquerade as normal conversation

### consequence
allowed:
- compare Purr `session_pack` vs Hermes stored `system_prompt`

forbidden:
- create `memory_evidence_refs` from Hermes prompt text
- treat Hermes memory files as raw truth
- let prompt compare write straight into `memory_items`

---

## recommended adapter architecture by phase

## phase 0 — shadow ledger

### adapter job
observe real Hermes turns and mirror them into the normal Purr ledger pipeline without changing Hermes behavior.

### trigger path
1. `session:start`
   - read `sessions.json`
   - capture live origin metadata for the new Hermes `session_id`
   - create / update a small Purr-side bridge record keyed by `hermes_session_id`

2. `agent:end`
   - snapshot the full session from `state.db`
   - diff against the adapter's last ingested checkpoint for that `hermes_session_id`
   - append only the new Hermes messages into Purr `message_events`
   - then run normal Purr extraction / evidence writeback

3. `session:reset`
   - mark the current bridge as closed
   - force next activity to open a new bridge

### what the bridge record must preserve
minimum:
- `hermes_session_id`
- current `session_key` at observation time
- platform
- `chat_id`
- `chat_type`
- `thread_id`
- Hermes `user_id`
- observed start time
- latest observed update time
- optional `parent_hermes_session_id`

this bridge record belongs to Purr-side dogfood infra, not Hermes.
it exists because Hermes does not preserve historical routing metadata strongly enough on its own.

### source-event identity in phase 0
because provider message ids are not reliably persisted into SQLite,
phase-0 ingestion should use a conservative synthetic upstream key like:
- `hermes:{session_id}:{message_row_id}`

plus content hash for sanity checks.

that is enough for:
- replay-safe ingestion
- exact backpointer into Hermes snapshot storage
- deterministic no-op on re-read

---

## phase 1 — read-only pack compare

### adapter job
use the shadow ledger to generate Purr `session_pack` artifacts,
then compare them against Hermes' actual stored prompt snapshot.

### required compare inputs
- Hermes `session_id`
- Hermes stored `system_prompt`
- Purr `session_pack` artifact
- bridge metadata so the compare stays tied to the right owner / purr / window

### compare output belongs in a separate log lane
store:
- Hermes prompt snapshot hash
- Purr `pack_id`
- overlap summary
- Purr-only facts Hermes missed
- Hermes-only facts Purr would suppress
- suppression reasons
- token / slot deltas

### hard rule
compare results are **diagnostic only**.

forbidden:
- compare diff mutating Hermes
- compare diff becoming memory truth automatically
- compare diff bypassing the normal mutation/evidence path

---

## phase 2 — correction override validation

### adapter job
pressure-test the hardest live-memory seam:
can Purr record a real correction from Hermes traffic as a clean challenge/supersede transaction?

### what must happen
- real correction arrives through Hermes chat
- adapter mirrors the turn into Purr `message_events`
- Purr correction logic outranks generic extraction
- old truth is challenged/superseded
- new truth becomes active
- exact evidence refs are attached
- a tiny committed correction overlay / delta artifact can be materialized for validation

### what must NOT happen
- generic extractor racing correction logic into duplicate active truth
- uncommitted correction text floating around as an override without ledger truth
- any visible behavior change in Hermes

---

## adapter invariants

these are the non-negotiables.

### 1. Hermes remains the actor, Purr remains the observer
- Hermes replies exactly as before
- adapter failures must not affect Hermes output
- adapter is a separate process / hook consumer / cron observer

### 2. raw turn first
- read Hermes persisted messages
- append Purr `message_events`
- only then run extraction / contradiction handling / pack generation

### 3. no fake evidence
- evidence refs point to mirrored Hermes raw-turn text
- not to Hermes `system_prompt`
- not to MEMORY.md / USER.md
- not to maintenance summaries

### 4. bridge state is Purr-owned
- Hermes `sessions.json` is only a live lookup source
- historical origin continuity lives on the Purr side

### 5. lineage is explicit
- compression child sessions must carry forward through `parent_session_id`
- pack compare and ingestion cannot pretend each Hermes `session_id` is isolated

### 6. replay safety beats cleverness
- synthetic upstream ids are acceptable early
- silent duplicate writes are not

### 7. compare lane is not truth lane
- pack compare produces evaluation logs
- never direct truth mutation

---

## failure modes if we do this wrong

## 1. append-only fantasy
if we tail SQLite rows like a Kafka log, rewrites/compression will create duplicate or muddy events.

## 2. origin amnesia
if we rely on current `sessions.json` later instead of capturing bridge data at start time,
we lose chat/thread provenance after resets and replacements.

## 3. prompt contamination
if we let Hermes prompt snapshots count as evidence,
Purr will learn from already-derived assistant abstractions instead of exact user speech.

## 4. session-key confusion
if we anchor on `session_key`, Telegram DMs without thread ids can collapse too much.

## 5. dogfood scope creep
if the adapter starts changing Hermes prompting or behavior,
we are no longer validating the Purr memory spine.
we are building a Hermes/Purr hybrid side quest.
kill that immediately.

---

## kill signals

kill or sharply narrow the dogfood adapter if:
- it needs Hermes runtime patches just to function
- it adds measurable reply latency
- bridge maintenance becomes annoying / brittle enough to eat weekly cycles
- pack compare becomes a behavior-feedback loop instead of an observation loop
- evidence refs cannot stay grounded to mirrored raw turns
- session lineage/origin tracking keeps drifting after resets/compression
- there is pressure to make Hermes read from Purr state before Purr itself exists

---

## what this changes for the repo

### it does NOT change
- first build slice stays `memory-ledger`
- Hermes dogfood is still **plumbing validation only**
- no in-loop subagent
- no visible tool theater
- no research rollback to Moltbook/poly

### it DOES add
one new hard implementation truth for later:

**Hermes dogfood needs a tiny external bridge layer of its own.**
not because the memory system should get fancier,
but because Hermes does not preserve historical origin/routing identity strongly enough for Purr-grade replay and compare by itself.

that bridge layer should stay:
- outside Hermes
- narrower than the ledger
- boring
- replay-safe
- disposable if direct Purr integration makes it obsolete later

---

## direct conclusion

Hermes gives us a good enough real-chat exhaust stream for shadow dogfood,
but only if we treat it honestly.

steal from Hermes here:
- hook timing surfaces
- persisted SQLite session/message snapshots
- compression lineage through `parent_session_id`
- stored prompt snapshots for pack compare

reject here:
- trusting `session_key` as real identity
- trusting SQLite rows as a pure append-only log
- trusting prompt memory as evidence
- trusting Hermes to preserve historical chat/thread routing for us

best move:
**hook-triggered, read-only snapshot adapter; Purr-owned session-origin bridge; compare lane separate from truth lane; zero feedback into Hermes behavior.**

that is the cleanest way to dogfood the memory spine without turning research-first mode into a messy hybrid build.
