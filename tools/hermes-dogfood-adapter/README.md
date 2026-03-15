# hermes-dogfood-adapter

Shadow-only adapter workspace for Hermes -> Purr memory dogfood.

This A1 slice only ships the local Supabase setup path plus the phase-0 schema migration.
It does not change Hermes runtime behavior and it does not add any code under `vendor/hermes-agent/`.

## phase 0 scope

The phase-0 migration creates these tables:

- `owners`
- `purrs`
- `episodes`
- `session_windows`
- `message_events`
- `memory_items`
- `memory_events`
- `memory_evidence_refs`

Out of scope for phase 0:

- `pack_artifacts`
- `pack_candidate_view`
- RLS/auth client policies

Notes:

- `message_events`, `memory_events`, and `memory_evidence_refs` are append-only in this migration.
- Parent deletes into those append-only tables now use `RESTRICT`/`NO ACTION` semantics rather than cascades, so historical ledger rows cannot be silently removed through a parent delete.
- `memory_items` is the mutable current-truth row.
- `memory_items` must have at least one evidence ref before commit. Insert the memory row and its evidence rows in the same SQL transaction.
- The adapter should provide deterministic UUIDs for Hermes-mapped rows (`episode_id`, `window_id`, `message_id`).
- Repeated lineage columns (`owner_id`, `purr_id`, `episode_id`, `window_id`) are intentionally duplicated for indexing, and the migration enforces lineage consistency with composite foreign keys across episodes, windows, messages, memory provenance, and evidence rows.
- If a memory row points at an `origin_window_id`, it must also carry the matching `episode_id` so provenance can be enforced through the composite window lineage key.
- If an evidence row uses `source_type = 'system_summary'`, it must point back to raw evidence via `derived_from_evidence_id`.

## tiny glossary

- `subject_key`: the semantic slot or topic being tracked, for example `drink.preference.coffee`.
- `dedupe_key`: the conflict/uniqueness key for “active truth” within a scope. Multiple memories can share a `subject_key`, but exclusive live rows should not share the same `dedupe_key` inside the same durability scope.
- `scope_ref`: the concrete row id that anchors a scoped memory. In phase 0, that means owner id for `profile`, purr id for `relationship`, episode id for `episode`, and window id for `window`. It may be null for scopes like `ephemeral`.
- `source_session_id`: the adapter-provided external session identifier from Hermes/source-provider land. It is distinct from internal `window_id`, which is the deterministic UUID stored in Postgres.

## local Supabase setup

Run everything from this directory unless noted otherwise:

```bash
cd /home/ubuntu/goon/tools/hermes-dogfood-adapter
```

### 1. prerequisites

Local Supabase needs a container runtime.
Install one of:

- Docker Engine
- Docker Desktop
- another Docker-compatible local engine supported by Supabase CLI

Verify it works:

```bash
docker version
```

For the Supabase CLI, use either a global install or `npx`.
This repo does not commit a generated `supabase/` project scaffold yet.

Option A — no global install:

```bash
npx supabase@latest --version
```

Option B — global install with npm:

```bash
npm install -g supabase
supabase --version
```

### 2. initialize the local Supabase project once

If this directory does not already contain `supabase/config.toml`, initialize it:

```bash
npx supabase@latest init
```

That creates the local `supabase/` folder used by `supabase start` and `supabase db reset`.

### 3. start the local stack

```bash
npx supabase@latest start
```

Useful defaults after startup:

- Studio: `http://127.0.0.1:54323`
- Postgres: `postgresql://postgres:postgres@127.0.0.1:54322/postgres`

If you want the exact current endpoints/keys, run:

```bash
npx supabase@latest status
```

### 4. apply the phase-0 migration

Preferred path: copy the checked-in migration into Supabase's local migrations folder, then reset/apply.

```bash
mkdir -p supabase/migrations
cp migrations/001_phase0_schema.sql supabase/migrations/001_phase0_schema.sql
npx supabase@latest db reset
```

`db reset` recreates the local database and reapplies all local migrations. Use it on a disposable local stack.

If you already have `psql` installed and want a one-off apply without resetting the whole local DB:

```bash
PGPASSWORD=postgres psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" \
  -v ON_ERROR_STOP=1 \
  -f /home/ubuntu/goon/tools/hermes-dogfood-adapter/migrations/001_phase0_schema.sql
```

### 5. quick table-existence check

Open the Supabase Studio SQL editor or use `psql`, then run:

```sql
select table_name
from information_schema.tables
where table_schema = 'public'
  and table_name in (
    'owners',
    'purrs',
    'episodes',
    'session_windows',
    'message_events',
    'memory_items',
    'memory_events',
    'memory_evidence_refs'
  )
order by table_name;
```

You should see all 8 phase-0 tables.

## manual insert/query verification

The example below is intentionally small but exercises the important path:

- seed one owner + one purr
- seed one episode + one session window
- insert a Hermes-mapped user message and assistant reply
- insert one candidate memory
- attach one audit event
- attach one exact evidence ref

Important: keep the `memory_items`, `memory_events`, and `memory_evidence_refs` inserts in one transaction so the deferred evidence invariant passes.

```sql
begin;

insert into owners (owner_id, world_user_id)
values ('00000000-0000-0000-0000-000000000001', 'hermes:ilyas');

insert into purrs (purr_id, owner_id, voice_profile_version, memory_policy_version)
values (
  '00000000-0000-0000-0000-0000000000a1',
  '00000000-0000-0000-0000-000000000001',
  'dogfood-v1',
  'phase0'
);

insert into episodes (
  episode_id,
  owner_id,
  purr_id,
  kind,
  status,
  started_at
)
values (
  '10000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-0000000000a1',
  'daily_chat',
  'open',
  now()
);

insert into session_windows (
  window_id,
  owner_id,
  purr_id,
  episode_id,
  source_provider,
  source_session_id,
  entry_surface,
  window_state,
  opened_at
)
values (
  '20000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-0000000000a1',
  '10000000-0000-0000-0000-000000000001',
  'hermes',
  'demo-session-1',
  'world_chat',
  'active',
  now()
);

insert into message_events (
  message_id,
  owner_id,
  purr_id,
  episode_id,
  window_id,
  source_provider,
  source_message_id,
  role,
  surface,
  tool_visibility,
  content_text,
  created_at
)
values (
  '30000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-0000000000a1',
  '10000000-0000-0000-0000-000000000001',
  '20000000-0000-0000-0000-000000000001',
  'hermes',
  '1',
  'user',
  'world_chat',
  'none',
  'I prefer cold brew in the morning.',
  now()
), (
  '30000000-0000-0000-0000-000000000002',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-0000000000a1',
  '10000000-0000-0000-0000-000000000001',
  '20000000-0000-0000-0000-000000000001',
  'hermes',
  '2',
  'purr',
  'world_chat',
  'none',
  'Got it. Morning coffee preference = cold brew.',
  now()
);

insert into memory_items (
  memory_id,
  owner_id,
  purr_id,
  memory_lane,
  kind,
  state,
  review_status,
  contradiction_status,
  pack_policy,
  durability_scope,
  is_exclusive,
  subject_key,
  dedupe_key,
  scope_ref,
  episode_id,
  origin_window_id,
  owner_surface,
  confidence,
  salience,
  volatility,
  freshness_score,
  payload_json
)
values (
  '40000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-0000000000a1',
  'private_1_1',
  'preference',
  'candidate',
  'none',
  'clean',
  'shadow',
  'profile',
  true,
  'drink.preference.coffee',
  'drink.preference.coffee',
  '00000000-0000-0000-0000-000000000001',
  '10000000-0000-0000-0000-000000000001',
  '20000000-0000-0000-0000-000000000001',
  'world_chat',
  0.9100,
  0.7800,
  0.2000,
  0.9000,
  '{"value":"cold brew","source":"manual-check"}'::jsonb
);

insert into memory_events (
  memory_id,
  owner_id,
  purr_id,
  event_type,
  event_reason,
  actor_type,
  to_state,
  intake_batch_key,
  delta_json
)
values (
  '40000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-0000000000a1',
  'created',
  'manual verification',
  'extractor',
  'candidate',
  'manual-check-1',
  '{"note":"phase0 smoke test"}'::jsonb
);

insert into memory_evidence_refs (
  evidence_id,
  memory_id,
  owner_id,
  purr_id,
  episode_id,
  window_id,
  message_id,
  span_start,
  span_end,
  source_type,
  excerpt_text,
  excerpt_hash,
  evidence_weight,
  explicitness,
  speaker_role
)
values (
  '50000000-0000-0000-0000-000000000001',
  '40000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-0000000000a1',
  '10000000-0000-0000-0000-000000000001',
  '20000000-0000-0000-0000-000000000001',
  '30000000-0000-0000-0000-000000000001',
  9,
  18,
  'chat',
  'cold brew',
  'manual-cold-brew-demo',
  1.0000,
  'explicit',
  'user'
);

commit;
```

Then run these checks:

```sql
select source_session_id, window_state
from session_windows;
```

```sql
select source_message_id, role, content_text
from message_events
order by created_at, source_message_id;
```

```sql
select memory_id, kind, state, dedupe_key, scope_ref
from memory_items;
```

```sql
select
  mi.memory_id,
  mi.kind,
  me.event_type,
  mer.excerpt_text,
  mer.span_start,
  mer.span_end
from memory_items mi
join memory_events me on me.memory_id = mi.memory_id
join memory_evidence_refs mer on mer.memory_id = mi.memory_id;
```

Expected result:

- one active window tied to `demo-session-1`
- two `message_events`
- one `memory_item` in `candidate` state
- one `memory_event` with `event_type = 'created'`
- one exact evidence ref grounded to the user message span

## optional negative check: evidence invariant

This should fail on commit because the `memory_item` has no evidence ref:

```sql
begin;

insert into memory_items (
  owner_id,
  purr_id,
  memory_lane,
  kind,
  state,
  review_status,
  contradiction_status,
  pack_policy,
  durability_scope,
  subject_key,
  dedupe_key,
  scope_ref,
  owner_surface,
  expires_at
)
values (
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-0000000000a1',
  'private_1_1',
  'ephemeral_note',
  'candidate',
  'none',
  'clean',
  'shadow',
  'ephemeral',
  'demo.ephemeral',
  'demo.ephemeral',
  null,
  'world_chat',
  now() + interval '1 hour'
);

commit;
```

## current limits of this phase-0 slice

- no pack tables yet
- no `pack_candidate_view` yet
- no Supabase auth/RLS policy layer yet
- no adapter code yet
- no extractor code yet

That is intentional for A1. This slice only makes local Supabase setup and the phase-0 ledger schema concrete.
