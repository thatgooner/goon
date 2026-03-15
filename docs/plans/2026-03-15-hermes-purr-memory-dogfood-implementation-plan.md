# Hermes → Purr memory dogfood: implementation plan

**status:** plan only — no code in this document
**date:** 2026-03-15
**author:** code-worker (synthesized from 5 subagent investigations)
**governing verdicts:** ily/23 (judge layer), ily/25 (worker H)

---

## subagent synthesis

### what the 5 subagents agreed on

1. **external SQLite reader is the correct tap approach.** no Hermes code changes needed. Hermes' SessionDB uses WAL mode; concurrent readers are safe. the adapter reads from `~/.hermes/state.db` as a separate process.

2. **adapter lives in goon repo** at `tools/hermes-dogfood-adapter/`, not embedded in Hermes' runtime. keeps isolation clean. kill = stop the cron.

3. **deterministic UUID5 mapping** from Hermes integer/string IDs to Purr UUIDs. reproducible, crash-safe, no coordination needed.

4. **phase 0 needs most Purr tables** (`owners`, `purrs`, `episodes`, `session_windows`, `message_events`, `memory_items`, `memory_events`, `memory_evidence_refs`) but NOT `pack_artifacts` or `pack_candidate_view`.

5. **narrow evaluator not needed before phase 3.** phases 0-2 run fully deterministic with conservative fallbacks.

6. **worker H (memory-health-auditor) not needed before post-phase-3.** not enough events earlier.

7. **Hermes' `sessions.system_prompt`** is the correct comparison source for phase 1 pack comparison. the frozen memory snapshot is already stored per session.

8. **config-driven owner_id/purr_id** for single-user dogfood. hardcoded UUIDs in config, not dynamic lookup.

### where they disagreed

1. **file watcher vs message-only extraction.** hermes-analyst suggested watching MEMORY.md/USER.md for changes. shadow-ledger-architect said extractor should work from `message_events` only. **resolution:** extractor works from message_events. file watching is unnecessary complexity — we already have the messages. for phase 1 comparison, we read Hermes' memory from `sessions.system_prompt`, not from live files.

2. **optional Hermes callback vs pure external reader.** hermes-analyst noted that adding an optional callback in `SessionDB.append_message` would give synchronous, low-latency observation. shadow-ledger-architect preferred pure external reader. **resolution:** pure external reader. no Hermes changes. the latency of polling (~5-30s) is acceptable for shadow mode. synchronous observation is not needed when we're not affecting behavior.

3. **cron job vs background daemon.** shadow-ledger-architect said cron. test-planner assumed a continuously running poll loop. **resolution:** poll loop with configurable interval (default 30s), run as a background process. simpler than cron for ongoing operation, but launched manually or via systemd. not a true daemon with PID files — just `python run.py` in a tmux/screen.

### final controller decisions

- **architecture:** external Python process in `tools/hermes-dogfood-adapter/`, reads Hermes SQLite, writes to Supabase. no Hermes changes.
- **scheduling:** poll loop with 30s interval, not cron
- **ID mapping:** UUID5 deterministic from Hermes IDs
- **extraction source:** message_events only, not MEMORY.md files
- **comparison source:** sessions.system_prompt for phase 1
- **supabase:** local dev first (`supabase init` + `supabase start`), remote later
- **kill switch:** env var `PURR_SHADOW_ENABLED=0`

---

## 1. goal

test the Purr memory backbone on real conversation data by running it in shadow/observation mode alongside Hermes. the shadow system reads Hermes' conversation events, writes structured memory to a separate Supabase ledger, and never affects Hermes' behavior.

what "shadow dogfood" means concretely:
- every Hermes user/assistant message gets logged to the Purr ledger as a `message_event`
- an extractor runs on those events and produces `memory_items` with exact `memory_evidence_refs`
- in later phases, packs are generated, corrections are tested, and review/proactive scoring is evaluated
- all of this is read-only observation. Hermes never reads from or depends on the Purr ledger.

why this matters:
- validates ledger schema on real data, not just synthetic fixtures
- catches extraction quality problems early
- tests idempotency under real replay/crash conditions
- tests correction detection on real natural language
- provides comparison data: is Purr's structured memory better than Hermes' flat MEMORY.md?

---

## 2. non-goals

- **do NOT turn Hermes into Purr.** Hermes' behavior, prompt, memory, and personality stay unchanged.
- **do NOT modify Hermes' codebase.** zero changes to `vendor/hermes-agent/`.
- **do NOT let Hermes read from the Purr ledger** in any phase.
- **do NOT implement Catnet, markets, or social memory.**
- **do NOT implement full proactive product behavior** (proactive scoring in phase 3 is read-only/would-have-done logging).
- **do NOT use the narrow evaluator or worker H in phases 0-2.**
- **do NOT build user-facing UI, dashboards, or memory admin panels.**

---

## 3. phased rollout

### phase 0 — shadow ledger

**what:** log every Hermes message to the Purr ledger. run extractor. accumulate structured memory.

**Purr schema in scope:**
- `owners`, `purrs` (identity refs, seeded once)
- `episodes`, `session_windows` (mapped from Hermes sessions)
- `message_events` (mapped from Hermes messages)
- `memory_items` (extractor output)
- `memory_events` (audit trail)
- `memory_evidence_refs` (evidence grounding)

**Purr schema NOT in scope:**
- `pack_artifacts`, `pack_candidate_view`

**mutations in scope:**
- create candidate, append evidence, confirm, reject

**mutations NOT in scope:**
- supersede, challenge, stale/decay, pack hit/miss

**gate to phase 1:**
- ≥100 memory_items with clean evidence chains
- ≥95% evidence refs point to valid message_events
- 0 duplicate candidates from replay
- ≤30% extractor junk ratio (manual audit of 20 random items)
- adapter p99 latency ≤500ms
- all above sustained for 7 days

### phase 1 — read-only pack compare

**what:** generate Purr `session_pack` artifacts and compare them to what Hermes actually injected via its MEMORY.md/USER.md frozen snapshot.

**new schema:**
- `pack_artifacts`
- `pack_candidate_view`

**new logic:**
- pack generation from ledger
- comparison engine: extract Hermes memory from `sessions.system_prompt`, compare to Purr `session_pack`

**gate to phase 2:**
- ≥20 pack comparison sessions
- 100% pack budget compliance (≤1000 tokens)
- overlap_f1 ≥0.5 (shared memory coverage)
- at least 3 specific quality wins documented (Purr caught stale truth, better evidence, etc.)
- all above sustained for 7 days

### phase 2 — correction override validation

**what:** when Ilyas corrects Hermes, run the correction through Purr's challenge/supersede pipeline. verify state transitions.

**new mutations:**
- supersede, challenge
- live_override_patch (materialized but not consumed by Hermes)
- live-override idempotency

**new logic:**
- correction detection from message content + Hermes memory tool usage
- challenge/supersede flow

**gate to phase 3:**
- ≥10 real correction events processed
- purr_caught_ratio ≥0.6 (Purr detected the correction)
- no impossible states (no double-active truth in exclusive scope)
- transactions succeed atomically
- all above sustained for 7 days

### phase 3 — review + proactive scoring (read-only)

**what:** run review queue scheduler and proactive preflight on the Purr ledger. log would-have-done decisions.

**new logic:**
- review scheduler, review queue
- trust decay arithmetic
- proactive preflight scoring
- stale/decay mutations
- pack hit/miss feedback
- narrow evaluator (5 decision points) — optional, can start without
- would-have-done logging

**gate to "dogfood successful":**
- review suggestions good_ratio ≥0.7 (human-labeled sample)
- proactive scoring no_act rate ≥0.7 (most wakeups = no action)
- trust decay produces reasonable evolution
- no spam, no creepiness in would-have-done logs
- sustained for 14 days

### worker H (memory-health-auditor)

**when:** after phase 3, after feedback-orchestrator ships. not before. needs weeks of accumulated events.

---

## 4. exact hook points

### where the adapter reads from

**Hermes SQLite database:** `~/.hermes/state.db`

| Hermes table | what we read | purpose |
|-------------|-------------|---------|
| `sessions` | `id`, `source`, `user_id`, `parent_session_id`, `started_at`, `ended_at`, `end_reason`, `system_prompt`, `title` | map to episodes + session_windows; extract memory snapshot for comparison |
| `messages` | `id`, `session_id`, `role`, `content`, `tool_call_id`, `tool_calls`, `tool_name`, `timestamp` | map to message_events; feed extractor |

**read method:** standard SQLite connection in read-only mode (`?mode=ro` or `PRAGMA query_only=ON`). Hermes uses WAL mode, so concurrent reads are safe.

### where the adapter writes to

**Supabase (Postgres):** Purr ledger tables. connection via `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` env vars.

### what the adapter does NOT touch

- `vendor/hermes-agent/` — zero file modifications
- `~/.hermes/memories/MEMORY.md` — not read by adapter (comparison reads from `sessions.system_prompt` instead)
- `~/.hermes/memories/USER.md` — not read by adapter
- Hermes' SQLite is read-only. no writes, no schema changes, no triggers added.

---

## 5. architecture choice

```
┌─────────────────────────────┐      ┌─────────────────────────────┐
│        Hermes Agent         │      │     Purr Shadow Adapter     │
│  (unchanged, no mods)       │      │  tools/hermes-dogfood-      │
│                             │      │  adapter/                   │
│  SQLite: ~/.hermes/state.db │─────>│                             │
│  (WAL mode, read-only tap)  │ read │  1. poll for new messages   │
│                             │      │  2. map to Purr schema      │
│  MEMORY.md / USER.md        │      │  3. run extractor           │
│  (not read by adapter)      │      │  4. write to Supabase       │
└─────────────────────────────┘      └──────────────┬──────────────┘
                                                    │ write
                                     ┌──────────────▼──────────────┐
                                     │     Supabase (Postgres)     │
                                     │     Purr Ledger Tables      │
                                     │                             │
                                     │  message_events             │
                                     │  memory_items               │
                                     │  memory_events              │
                                     │  memory_evidence_refs       │
                                     │  pack_artifacts (phase 1+)  │
                                     └─────────────────────────────┘
```

**why this shape:**
- **isolation:** adapter is a completely separate process. killing it has zero effect on Hermes.
- **simplicity:** one Python script, one SQLite read connection, one Supabase write connection.
- **crash safety:** adapter maintains a checkpoint (last processed message ID). crash → restart → resume from checkpoint. idempotency prevents duplicates.
- **no Hermes changes:** Hermes vendor code stays frozen.

**why NOT other options:**
- embedded in Hermes runtime: violates isolation boundary. crash in adapter could affect Hermes.
- microservice/daemon: overengineered for single-user dogfood.
- cron: less responsive than a poll loop; harder to manage checkpoint state.
- file watcher on MEMORY.md: misses context. extractor should work from messages, not flat file changes.

---

## 6. data contract mapping

### identity mapping

| concept | value | source |
|---------|-------|--------|
| `owner_id` | fixed UUID in config (e.g., `550e8400-...`) | represents Ilyas |
| `purr_id` | fixed UUID in config (e.g., `6ba7b810-...`) | represents Ilyas's purr |
| future multi-user | `(source, user_id)` → `owner_id` lookup table | not needed yet |

### session → episode / window mapping

| Hermes concept | Purr concept | mapping rule |
|---------------|-------------|-------------|
| root session (no `parent_session_id`) | new `episode` + new `session_window` | `episode_id = uuid5(NS, f"hermes.episode.{session_id}")`, `window_id = uuid5(NS, f"hermes.window.{session_id}")` |
| child session (has `parent_session_id`) | new `session_window` in same `episode` | `window_id = uuid5(NS, f"hermes.window.{session_id}")`, `episode_id` = parent's episode, `parent_window_id` = parent's window_id |
| session end_reason = "compression" | window_state = "compressed" | |
| session ended_at IS NOT NULL | window_state = "archived" or "compressed" | depends on end_reason |

### message → message_event mapping

| Hermes field | Purr field | transform |
|-------------|-----------|-----------|
| `messages.id` (integer) | `message_id` (uuid) | `uuid5(NS, f"hermes.msg.{session_id}.{id}")` |
| `messages.session_id` | `window_id` | via session→window mapping |
| `messages.role` | `role` | `user`→`user`, `assistant`→`purr`, `system`→`system`, `tool`→`system` |
| `messages.content` | `content_text` | direct |
| `messages.timestamp` | `created_at` | unix float → timestamptz |
| `messages.tool_calls` | `metadata_json` | JSON, includes tool names/args |
| `messages.tool_name` | `metadata_json.tool_name` | for tool-result messages |
| — | `owner_id` | from config |
| — | `purr_id` | from config |
| — | `episode_id` | from session→episode mapping |
| — | `surface` | `telegram` → `world_chat` (from session source) |
| — | `tool_visibility` | `tool_name IS NOT NULL` → `hidden`, else `none` |

### evidence ref generation

| field | source |
|-------|--------|
| `evidence_id` | `uuid5(NS, f"hermes.evidence.{memory_id}.{message_id}.{span_start}.{span_end}")` |
| `message_id` | from message mapping |
| `window_id` | from session→window mapping |
| `episode_id` | from session→episode mapping |
| `span_start`, `span_end` | from extractor output (character offsets into message content) |
| `excerpt_text` | substring of message content |
| `excerpt_hash` | SHA256 of excerpt |
| `source_type` | `chat` for user/assistant messages |
| `speaker_role` | from message role |

### idempotency keys

| object | idempotency key | mechanism |
|--------|----------------|-----------|
| `message_events` | `message_id` (deterministic UUID5) | `ON CONFLICT (message_id) DO NOTHING` |
| `memory_items` | `(owner_id, purr_id, dedupe_key, durability_scope, scope_ref)` where `state IN (candidate, confirmed, stale)` | partial unique index |
| `memory_evidence_refs` | `(memory_id, message_id, span_start, span_end)` | unique constraint |
| `memory_events` | `(memory_id, event_type, created_at)` + `intake_batch` tracking | intake_batch identity |
| `episodes` | `episode_id` (deterministic UUID5) | `ON CONFLICT DO NOTHING` |
| `session_windows` | `window_id` (deterministic UUID5) | `ON CONFLICT DO NOTHING` |

---

## 7. instrumentation / debugging

### phase 0 metrics

| metric | how measured | success threshold | failure threshold |
|--------|------------|-------------------|-------------------|
| `message_events_written` | count in Supabase | ≥1 per Hermes session | 0 after 48h of active usage |
| `memory_items_extracted` | count in Supabase | ≥100 after 1 week | <20 after 1 week |
| `evidence_refs_valid` | JOIN message_events ON evidence_id | ≥95% valid | <80% valid |
| `duplicate_candidates` | count where replay created dupes | 0 | >0 |
| `identity_scope_violations` | rows missing owner_id or purr_id | 0 | >0 |
| `extractor_junk_ratio` | manual audit of 20 random items weekly | ≤30% junk | >50% junk |
| `adapter_latency_p99` | per-poll-cycle timing | ≤500ms | >2000ms for 3 consecutive days |

### phase 1 metrics

| metric | how measured | success threshold |
|--------|------------|-------------------|
| `pack_budget_compliance` | token_estimate ≤1000 for session_packs | 100% |
| `overlap_f1` | shared content between Hermes memory snapshot and Purr pack | ≥0.5 |
| `purr_quality_wins` | manual count of cases where Purr pack is better | ≥3 documented |
| `hermes_stale_detected` | Purr correctly suppressed something Hermes still carries | ≥1 |

### pack comparison methodology

1. **extract Hermes memory:** parse `sessions.system_prompt` for text between `MEMORY (your personal notes)` header and `USER PROFILE (who the user is)` header. split by `§` delimiter.
2. **generate Purr pack:** run packer against `pack_candidate_view` for the corresponding window. output as structured JSON.
3. **compare:** for each Hermes memory entry, check if Purr pack contains equivalent content. for each Purr pack item, check if Hermes has it. compute precision/recall/F1.
4. **log:** write comparison as JSONL to `logs/dogfood/pack-compare-YYYY-MM-DD.jsonl`.

### kill switch

- **env var:** `PURR_SHADOW_ENABLED=0` in adapter config. adapter checks on every poll cycle. if disabled, exits cleanly.
- **verification:** after kill, check Hermes latency is unchanged. check no Purr imports exist in Hermes process.
- **data preservation:** shadow data stays in Supabase for post-mortem. optional `pg_dump` before any cleanup.

### debug surface

- **SQL queries** against Supabase for all inspection. no separate dashboard.
- **adapter log file:** `logs/dogfood/adapter-YYYY-MM-DD.log` with per-cycle timing, counts, and errors.
- **comparison log:** `logs/dogfood/pack-compare-YYYY-MM-DD.jsonl` for phase 1.
- **weekly markdown report:** auto-generated summary of key metrics. human reviews.

---

## 8. safety boundaries

### deterministic surfaces — do not touch

all 11 surfaces from ily/23 remain sacred. the dogfood adapter must:
- use source-event append before any extraction (note 14 rule 1)
- maintain evidence backpointers with exact refs (note 13 invariant 3-4)
- use atomic transactions for mutations (note 13 invariant 10)
- enforce identity scope (`owner_id` + `purr_id`) on every row (note 13 invariant 1)
- use idempotency keys for replay safety (note 14 section 6)
- respect active-truth uniqueness (note 13 invariant 6)
- suppress challenged/superseded from pack candidates (note 13 invariant 7)
- respect hard pack budgets (note 09, 13)

### what the adapter must NEVER do

- modify `vendor/hermes-agent/` files
- write to `~/.hermes/state.db`
- write to `~/.hermes/memories/`
- inject data into Hermes' prompt
- change Hermes' behavior in any phase
- run an in-loop subagent
- call an LLM during phases 0-2 (extractor in phase 0 may use a cheap model, but NOT as a subagent)
- bypass the mutation pipeline for truth writes

### narrow evaluator boundaries

- NOT used in phases 0-2
- in phase 3, optional for the 5 typed decision points from ily/23
- conservative fallback on failure (challenge, hold, defer, abort, keep_separate)
- typed input/output, cheap model only

### worker H boundaries

- NOT used in phases 0-3
- consider only after feedback-orchestrator ships and enough events accumulate
- lives in deferred maintenance lane, not a separate layer

---

## 9. testing plan

### local dev validation

1. **create test SQLite** matching Hermes schema (sessions + messages tables)
2. **seed with fixtures:**
   - 1 root session with 12+ messages (user + assistant turns)
   - 1 correction event: user message containing "actually no, I meant X"
   - 1 memory tool usage: assistant calls memory tool with add/replace
   - 1 child session (compression continuation with parent_session_id)
3. **run local Supabase:** `supabase init` → `supabase start` → run phase 0 migration
4. **run adapter** against test SQLite → verify message_events, memory_items, evidence_refs in Supabase
5. **idempotency test:** run adapter again → verify zero duplicates

### live shadow validation

1. **point adapter at real `~/.hermes/state.db`** in read-only mode
2. **backfill:** process all existing sessions in `started_at` order
3. **ongoing:** poll every 30s for new messages
4. **automated sanity checks** (run daily):
   - message count parity: Hermes messages count ≈ Purr message_events count
   - no orphan evidence refs (every ref points to a valid message_event)
   - no duplicate message_ids
   - all rows carry owner_id + purr_id
   - no memory_items without at least one evidence ref

### failure modes

| failure | detection | recovery | severity |
|---------|-----------|----------|----------|
| SQLite locked during read | adapter logs read error | retry with exponential backoff (WAL should prevent this) | low |
| Supabase connection fails | adapter logs write error | no checkpoint update; idempotency prevents dupes on retry | medium |
| extractor produces garbage | weekly manual audit; junk_ratio metric | tune extraction rules; if >50%, pause and investigate | medium |
| duplicate messages from re-read | idempotency check on UUID5 message_id | `ON CONFLICT DO NOTHING` handles it | low |
| child session before parent seen | process by started_at order; defer if out of order | queue and retry after parent processed | low |
| adapter crashes mid-batch | checkpoint not updated for partial batch | restart; idempotency handles already-written items | low |
| Hermes schema changes | adapter SQL query fails | update adapter reader; add schema version check | medium |
| extractor hallucination (false memories) | manual audit; evidence ref validation | reject items without valid evidence | high |
| Supabase disk full | write errors | expand storage or truncate old data | medium |
| adapter poll loop hangs | no new metrics for >1 hour | kill and restart process | low |

---

## 10. implementation slices

### build order: UNCHANGED

```
slice 1: memory-ledger (Supabase schema + API)
slice 2: memory-candidate-extractor
slice 3: memory-context-packer
slice 4: feedback-orchestrator
```

### test order: CHANGED — dogfood phases run alongside build slices

| build slice | dogfood phase | relationship |
|-------------|---------------|-------------|
| memory-ledger (slice 1) | phase 0 | dogfood validates schema on real data |
| extractor (slice 2) | phase 0 + phase 2 | dogfood validates extraction quality + correction detection |
| packer (slice 3) | phase 1 | dogfood validates pack generation + comparison |
| feedback-orchestrator (slice 4) | phase 3 | dogfood validates review/proactive scoring |

### dogfood-specific implementation slices

the dogfood adapter is NOT one of the main build slices. it is a parallel validation track:

```
dogfood slice A: adapter foundation (reader + mapper + writer + cron)
dogfood slice B: basic extractor (runs in phase 0)
dogfood slice C: pack generator + comparator (runs in phase 1)
dogfood slice D: correction detector + challenge/supersede (runs in phase 2)
dogfood slice E: review/proactive scorer + would-have-done logger (runs in phase 3)
```

slices A and B can be built BEFORE or IN PARALLEL with main slice 1 (memory-ledger), because the adapter uses the same Supabase schema.

---

## 11. exact files to create / modify

### create

```
tools/hermes-dogfood-adapter/
├── README.md                          # setup, run instructions, architecture overview
├── config.yaml                        # owner_id, purr_id, hermes_db_path, supabase creds, poll_interval
├── requirements.txt                   # supabase-py, pydantic, python-dotenv
├── run.py                             # main entry: poll loop, checkpoint management
├── sync/
│   ├── __init__.py
│   ├── hermes_reader.py               # read sessions + messages from Hermes SQLite
│   ├── purr_writer.py                 # idempotent writes to Supabase
│   ├── mapper.py                      # Hermes objects → Purr objects (UUID5, field mapping)
│   └── checkpoint.py                  # track last-processed message ID
├── extractor/
│   ├── __init__.py
│   ├── basic_extractor.py             # message → memory candidates (phase 0)
│   └── correction_detector.py         # detect corrections in messages (phase 2)
├── comparator/
│   ├── __init__.py
│   ├── hermes_memory_parser.py        # extract memory from sessions.system_prompt
│   └── pack_comparator.py            # compare Hermes memory vs Purr pack (phase 1)
├── migrations/
│   ├── 001_phase0_schema.sql          # owners, purrs, episodes, session_windows, message_events,
│   │                                  # memory_items, memory_events, memory_evidence_refs
│   └── 002_phase1_packs.sql           # pack_artifacts, pack_candidate_view
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   └── seed_hermes_test_db.sql    # synthetic Hermes sessions + messages
│   ├── test_mapper.py                 # UUID5 mapping, field transforms
│   ├── test_idempotency.py            # re-run safety
│   └── test_extractor.py              # extraction quality on fixtures
└── logs/                              # gitignored; runtime logs go here
    └── .gitkeep
```

```
logs/dogfood/                          # gitignored; comparison + adapter logs
└── .gitkeep
```

### modify

```
notes/boards/coding-agent-task-board.md    # add dogfood implementation tasks
```

### create later (phase 1+)

```
tools/hermes-dogfood-adapter/comparator/   # phase 1 pack comparison
tools/hermes-dogfood-adapter/reviewer/     # phase 3 review/proactive scoring
```

### do not touch

```
vendor/hermes-agent/                       # no changes to Hermes
hermes/memories/                           # gooner-owned
notes/daily/                               # gooner-owned
```

---

## 12. task breakdown

### dogfood slice A — adapter foundation

**task A1: Supabase local dev setup + phase 0 migration**
- input: ily/13 schema spec
- output: `migrations/001_phase0_schema.sql`, `README.md` section on local setup
- done when: `supabase start` + migration creates all phase 0 tables; can insert/query manually

**task A2: Hermes SQLite reader**
- input: `vendor/hermes-agent/hermes_state.py` (schema reference)
- output: `sync/hermes_reader.py` — functions to read sessions and messages from SQLite in read-only mode
- done when: can read all sessions + messages from a test SQLite file; handles empty DB gracefully

**task A3: mapper (Hermes → Purr)**
- input: data contract mapping from this plan (section 6)
- output: `sync/mapper.py` — UUID5 mapping, field transforms, session→episode/window logic
- done when: given a Hermes session dict and message list, produces correct Purr-shaped dicts with deterministic UUIDs

**task A4: Purr Supabase writer**
- input: Purr schema from migration
- output: `sync/purr_writer.py` — idempotent inserts for message_events, memory_items, memory_events, memory_evidence_refs
- done when: duplicate inserts produce zero duplicates; crash mid-batch is safe to retry

**task A5: checkpoint management**
- input: adapter needs to track what's already synced
- output: `sync/checkpoint.py` — stores last-processed Hermes message timestamp/ID in a local file or Supabase table
- done when: adapter restarts from where it left off; no messages missed or double-processed

**task A6: poll loop + config**
- input: tasks A2-A5
- output: `run.py` + `config.yaml` — main loop that polls Hermes SQLite every N seconds, maps, writes, checkpoints
- done when: runs continuously; logs per-cycle timing; respects PURR_SHADOW_ENABLED kill switch

**task A7: test fixtures + integration test**
- input: Hermes SQLite schema
- output: `tests/fixtures/seed_hermes_test_db.sql` + `tests/test_mapper.py` + `tests/test_idempotency.py`
- done when: `pytest` passes with synthetic data; idempotency is verified

### dogfood slice B — basic extractor

**task B1: basic message → memory extractor**
- input: message_events in Purr ledger
- output: `extractor/basic_extractor.py` — takes a message, extracts memory candidates with evidence refs
- done when: given a user message "I prefer dark mode", produces a preference memory_item with evidence ref pointing to the exact message
- uncertainty: extraction mechanism (rule-based? cheap LLM? hybrid?) is not yet locked. start with rule-based patterns for v0, upgrade later.

**task B2: wire extractor into poll loop**
- input: tasks A6, B1
- output: updated `run.py` — after writing message_events, runs extractor, writes memory_items + evidence_refs
- done when: end-to-end flow works on test fixtures

### dogfood slice C — pack comparator (phase 1)

**task C1: Hermes memory parser**
- input: `sessions.system_prompt` text
- output: `comparator/hermes_memory_parser.py` — extracts MEMORY and USER sections from Hermes prompt
- done when: given a raw system prompt string, returns list of memory entries and list of user entries

**task C2: pack generator**
- input: Purr ledger data, pack contract from ily/09/13
- output: generates `session_pack` artifacts from `pack_candidate_view`
- done when: produces a token-budget-compliant pack artifact

**task C3: comparison engine**
- input: tasks C1, C2
- output: `comparator/pack_comparator.py` — compares Hermes memory entries to Purr pack items, computes overlap_f1
- done when: produces JSONL comparison log with per-item diffs

### dogfood slice D — correction detector (phase 2)

**task D1: correction detector**
- input: message content, existing memory state
- output: `extractor/correction_detector.py` — detects explicit corrections ("no, actually X", "that's wrong")
- done when: detects corrections in test fixtures with >60% recall

**task D2: challenge/supersede flow**
- input: correction detector output, ledger mutation contracts from ily/13
- output: wire correction events through the challenge/supersede mutation pipeline
- done when: correction produces atomic state transition; old truth suppressed, new truth active

### dogfood slice E — review/proactive scorer (phase 3)

**task E1: review scheduler**
- input: memory_items with review fields, contracts from ily/20
- output: computes `needs_review_at`, manages review queue
- done when: produces sensible review schedule on real ledger data

**task E2: would-have-done logger**
- input: review/proactive scoring output
- output: log table or file recording what Purr would have done
- done when: can generate weekly would-have-done report

---

## open uncertainties

these are explicitly uncertain. they do not block phase 0 but need resolution:

1. **extractor mechanism.** rule-based for v0 is safe but low quality. cheap LLM (gemini flash) would be better but adds cost and latency. decision: start rule-based, evaluate quality after phase 0 gate, upgrade to LLM if junk ratio is too high.

2. **Supabase hosting for live dogfood.** local dev uses `supabase start`. live dogfood against real Hermes data needs a real Supabase project or self-hosted Postgres. decision needed before live shadow begins.

3. **multi-user future.** current plan hardcodes owner_id/purr_id for Ilyas. if a second user joins, the config needs a mapping table. not a phase 0 concern but should be noted.

4. **extractor evidence span accuracy.** generating exact character offsets (span_start, span_end) from message content requires the extractor to pinpoint where in the message the memory claim appears. rule-based extraction can do substring matching. LLM extraction would need output parsing. decision: accept approximate spans in v0, tighten later.
