begin;

create extension if not exists pgcrypto;

-- phase 0 only:
-- - includes the shadow-ledger tables needed for Hermes -> Purr dogfood
-- - intentionally excludes pack_artifacts + pack_candidate_view (phase 1)
-- - expects the adapter to provide deterministic UUIDs for Hermes-mapped rows
-- - memory_items and memory_evidence_refs should be inserted in the same transaction
-- - duplicated lineage ids are guarded with composite keys so owner/purr/episode/window/message references stay aligned
-- - append-only child tables use restrict/no action semantics on parent deletes

create type owner_status_enum as enum ('active', 'inactive', 'archived');
create type purr_status_enum as enum ('active', 'inactive', 'archived');
create type episode_kind_enum as enum ('daily_chat', 'deep_talk', 'conflict', 'proactive_loop', 'other');
create type episode_status_enum as enum ('open', 'closed', 'archived');
create type entry_surface_enum as enum ('world_chat', 'notification_reentry', 'internal_proactive', 'other');
create type window_state_enum as enum ('active', 'idle', 'compressed', 'archived');
create type message_role_enum as enum ('user', 'purr', 'system');
create type message_surface_enum as enum ('world_chat', 'proactive_notification', 'internal_review', 'other');
create type tool_visibility_enum as enum ('hidden', 'user_visible', 'none');
create type memory_lane_enum as enum ('private_1_1', 'public_safe', 'catnet', 'system_ops');
create type memory_state_enum as enum ('candidate', 'confirmed', 'rejected');
create type review_status_enum as enum ('none', 'queued', 'due', 'ask_now', 'snoozed');
create type contradiction_status_enum as enum ('clean');
create type pack_policy_enum as enum ('hot', 'shadow', 'suppress', 'never');
create type durability_scope_enum as enum ('profile', 'relationship', 'episode', 'window', 'ephemeral');
create type memory_event_type_enum as enum (
  'created',
  'evidence_appended',
  'confirmed',
  'review_due',
  'snoozed',
  'rejected'
);
create type evidence_source_type_enum as enum ('chat', 'proactive_event', 'app_event', 'system_summary', 'system_seed', 'other');

create table public.owners (
  owner_id uuid primary key,
  world_user_id text not null unique,
  status owner_status_enum not null default 'active',
  created_at timestamptz not null default now()
);

create table public.purrs (
  purr_id uuid primary key,
  owner_id uuid not null references public.owners (owner_id) on delete cascade,
  voice_profile_version text not null default 'v1',
  memory_policy_version text not null default 'v1',
  status purr_status_enum not null default 'active',
  created_at timestamptz not null default now(),
  constraint purrs_owner_pair_unique unique (owner_id, purr_id)
);

create unique index purrs_one_active_per_owner_idx
  on public.purrs (owner_id)
  where status = 'active';

create table public.episodes (
  episode_id uuid primary key,
  owner_id uuid not null references public.owners (owner_id) on delete cascade,
  purr_id uuid not null,
  kind episode_kind_enum not null default 'daily_chat',
  status episode_status_enum not null default 'open',
  parent_episode_id uuid references public.episodes (episode_id) on delete set null,
  started_at timestamptz not null,
  ended_at timestamptz,
  summary_ref text,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint episodes_owner_purr_fk
    foreign key (owner_id, purr_id)
    references public.purrs (owner_id, purr_id)
    on delete cascade,
  constraint episodes_owner_purr_episode_unique unique (owner_id, purr_id, episode_id),
  constraint episodes_time_order_chk check (ended_at is null or ended_at >= started_at)
);

create index episodes_owner_purr_status_idx
  on public.episodes (owner_id, purr_id, status, started_at desc);

create table public.session_windows (
  window_id uuid primary key,
  owner_id uuid not null references public.owners (owner_id) on delete cascade,
  purr_id uuid not null,
  episode_id uuid not null,
  parent_window_id uuid references public.session_windows (window_id) on delete set null,
  source_provider text not null default 'hermes',
  source_session_id text not null,
  entry_surface entry_surface_enum not null default 'world_chat',
  window_state window_state_enum not null default 'active',
  opened_at timestamptz not null,
  closed_at timestamptz,
  closure_reason text,
  pack_version text not null default 'phase0',
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint session_windows_owner_purr_fk
    foreign key (owner_id, purr_id)
    references public.purrs (owner_id, purr_id)
    on delete cascade,
  constraint session_windows_owner_purr_episode_fk
    foreign key (owner_id, purr_id, episode_id)
    references public.episodes (owner_id, purr_id, episode_id)
    on delete restrict,
  constraint session_windows_source_unique unique (source_provider, source_session_id),
  constraint session_windows_owner_purr_episode_window_unique unique (owner_id, purr_id, episode_id, window_id),
  constraint session_windows_time_order_chk check (closed_at is null or closed_at >= opened_at)
);

create unique index session_windows_one_open_surface_idx
  on public.session_windows (owner_id, purr_id, entry_surface)
  where window_state in ('active', 'idle');

create index session_windows_owner_purr_state_idx
  on public.session_windows (owner_id, purr_id, window_state);

create index session_windows_episode_opened_idx
  on public.session_windows (episode_id, opened_at desc);

create table public.message_events (
  message_id uuid primary key,
  owner_id uuid not null references public.owners (owner_id) on delete restrict,
  purr_id uuid not null,
  episode_id uuid not null references public.episodes (episode_id) on delete restrict,
  window_id uuid not null references public.session_windows (window_id) on delete restrict,
  source_provider text not null default 'hermes',
  source_message_id text not null,
  role message_role_enum not null,
  surface message_surface_enum not null default 'world_chat',
  tool_visibility tool_visibility_enum not null default 'none',
  content_text text not null,
  metadata_json jsonb not null default '{}'::jsonb,
  reply_to_message_id uuid references public.message_events (message_id) on delete set null,
  created_at timestamptz not null,
  inserted_at timestamptz not null default now(),
  constraint message_events_owner_purr_fk
    foreign key (owner_id, purr_id)
    references public.purrs (owner_id, purr_id)
    on delete restrict,
  constraint message_events_owner_purr_episode_window_fk
    foreign key (owner_id, purr_id, episode_id, window_id)
    references public.session_windows (owner_id, purr_id, episode_id, window_id)
    on delete restrict,
  constraint message_events_owner_purr_episode_window_message_unique
    unique (owner_id, purr_id, episode_id, window_id, message_id),
  constraint message_events_source_unique unique (source_provider, window_id, source_message_id)
);

create index message_events_window_created_idx
  on public.message_events (window_id, created_at, message_id);

create index message_events_episode_created_idx
  on public.message_events (episode_id, created_at, message_id);

create index message_events_owner_purr_created_idx
  on public.message_events (owner_id, purr_id, created_at, message_id);

create table public.memory_items (
  memory_id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.owners (owner_id) on delete cascade,
  purr_id uuid not null,
  memory_lane memory_lane_enum not null default 'private_1_1',
  kind text not null,
  state memory_state_enum not null default 'candidate',
  review_status review_status_enum not null default 'none',
  contradiction_status contradiction_status_enum not null default 'clean',
  pack_policy pack_policy_enum not null default 'shadow',
  durability_scope durability_scope_enum not null,
  is_exclusive boolean not null default true,
  subject_key text not null,
  dedupe_key text not null,
  scope_ref uuid,
  episode_id uuid references public.episodes (episode_id) on delete set null,
  origin_window_id uuid references public.session_windows (window_id) on delete set null,
  owner_surface entry_surface_enum not null default 'world_chat',
  confidence numeric(5,4) not null default 0.5000,
  salience numeric(5,4) not null default 0.5000,
  volatility numeric(5,4) not null default 0.5000,
  freshness_score numeric(5,4) not null default 0.5000,
  last_confirmed_at timestamptz,
  last_hit_at timestamptz,
  last_miss_at timestamptz,
  needs_review_at timestamptz,
  cooldown_until timestamptz,
  attempt_count integer not null default 0,
  expires_at timestamptz,
  supersedes_memory_id uuid references public.memory_items (memory_id) on delete set null,
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint memory_items_owner_purr_fk
    foreign key (owner_id, purr_id)
    references public.purrs (owner_id, purr_id)
    on delete cascade,
  constraint memory_items_owner_purr_episode_fk
    foreign key (owner_id, purr_id, episode_id)
    references public.episodes (owner_id, purr_id, episode_id)
    on delete restrict,
  constraint memory_items_owner_purr_episode_window_fk
    foreign key (owner_id, purr_id, episode_id, origin_window_id)
    references public.session_windows (owner_id, purr_id, episode_id, window_id)
    on delete restrict,
  constraint memory_items_owner_purr_memory_unique unique (owner_id, purr_id, memory_id),
  constraint memory_items_kind_nonempty_chk check (char_length(trim(kind)) > 0),
  constraint memory_items_subject_key_nonempty_chk check (char_length(trim(subject_key)) > 0),
  constraint memory_items_dedupe_key_nonempty_chk check (char_length(trim(dedupe_key)) > 0),
  constraint memory_items_confidence_chk check (confidence between 0 and 1),
  constraint memory_items_salience_chk check (salience between 0 and 1),
  constraint memory_items_volatility_chk check (volatility between 0 and 1),
  constraint memory_items_freshness_chk check (freshness_score between 0 and 1),
  constraint memory_items_attempt_count_chk check (attempt_count >= 0),
  constraint memory_items_origin_window_requires_episode_chk check (
    origin_window_id is null or episode_id is not null
  ),
  constraint memory_items_scope_consistency_chk check (
    (durability_scope = 'profile' and scope_ref = owner_id)
    or (durability_scope = 'relationship' and scope_ref = purr_id)
    or (durability_scope = 'episode' and episode_id is not null and scope_ref = episode_id)
    or (durability_scope = 'window' and origin_window_id is not null and scope_ref = origin_window_id)
    or (durability_scope = 'ephemeral' and expires_at is not null)
  )
);

create unique index memory_items_active_truth_with_scope_unique_idx
  on public.memory_items (owner_id, purr_id, dedupe_key, durability_scope, scope_ref)
  where is_exclusive = true
    and scope_ref is not null
    and state in ('candidate', 'confirmed');

create unique index memory_items_active_truth_without_scope_unique_idx
  on public.memory_items (owner_id, purr_id, dedupe_key, durability_scope)
  where is_exclusive = true
    and scope_ref is null
    and state in ('candidate', 'confirmed');

create index memory_items_owner_purr_lane_state_idx
  on public.memory_items (owner_id, purr_id, memory_lane, state);

create index memory_items_owner_purr_dedupe_idx
  on public.memory_items (owner_id, purr_id, dedupe_key);

create index memory_items_owner_purr_subject_idx
  on public.memory_items (owner_id, purr_id, subject_key);

create index memory_items_owner_purr_needs_review_idx
  on public.memory_items (owner_id, purr_id, needs_review_at);

create index memory_items_owner_purr_pack_policy_idx
  on public.memory_items (owner_id, purr_id, pack_policy, contradiction_status);

create index memory_items_episode_idx
  on public.memory_items (episode_id);

create index memory_items_origin_window_idx
  on public.memory_items (origin_window_id);

create table public.memory_events (
  memory_event_id uuid primary key default gen_random_uuid(),
  memory_id uuid not null,
  owner_id uuid not null references public.owners (owner_id) on delete restrict,
  purr_id uuid not null,
  event_type memory_event_type_enum not null,
  event_reason text,
  actor_type text not null,
  from_state memory_state_enum,
  to_state memory_state_enum,
  intake_batch_key text,
  delta_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint memory_events_owner_purr_fk
    foreign key (owner_id, purr_id)
    references public.purrs (owner_id, purr_id)
    on delete restrict,
  constraint memory_events_owner_purr_memory_fk
    foreign key (owner_id, purr_id, memory_id)
    references public.memory_items (owner_id, purr_id, memory_id)
    on delete restrict,
  constraint memory_events_actor_type_nonempty_chk check (char_length(trim(actor_type)) > 0)
);

create index memory_events_memory_created_idx
  on public.memory_events (memory_id, created_at desc);

create index memory_events_owner_purr_event_created_idx
  on public.memory_events (owner_id, purr_id, event_type, created_at desc);

create unique index memory_events_intake_batch_dedupe_idx
  on public.memory_events (intake_batch_key, memory_id, event_type)
  where intake_batch_key is not null;

create table public.memory_evidence_refs (
  evidence_id uuid primary key default gen_random_uuid(),
  memory_id uuid not null,
  owner_id uuid not null references public.owners (owner_id) on delete restrict,
  purr_id uuid not null,
  episode_id uuid not null references public.episodes (episode_id) on delete restrict,
  window_id uuid not null references public.session_windows (window_id) on delete restrict,
  message_id uuid not null references public.message_events (message_id) on delete restrict,
  span_start integer not null,
  span_end integer not null,
  source_type evidence_source_type_enum not null default 'chat',
  excerpt_text text not null,
  excerpt_hash text not null,
  evidence_weight numeric(5,4) not null default 1.0000,
  explicitness text not null default 'explicit',
  speaker_role message_role_enum not null,
  derived_from_evidence_id uuid references public.memory_evidence_refs (evidence_id) on delete set null,
  captured_at timestamptz not null default now(),
  constraint memory_evidence_refs_owner_purr_fk
    foreign key (owner_id, purr_id)
    references public.purrs (owner_id, purr_id)
    on delete restrict,
  constraint memory_evidence_refs_owner_purr_memory_fk
    foreign key (owner_id, purr_id, memory_id)
    references public.memory_items (owner_id, purr_id, memory_id)
    on delete restrict,
  constraint memory_evidence_refs_owner_purr_episode_window_message_fk
    foreign key (owner_id, purr_id, episode_id, window_id, message_id)
    references public.message_events (owner_id, purr_id, episode_id, window_id, message_id)
    on delete restrict,
  constraint memory_evidence_refs_span_chk check (span_start >= 0 and span_end > span_start),
  constraint memory_evidence_refs_excerpt_hash_nonempty_chk check (char_length(trim(excerpt_hash)) > 0),
  constraint memory_evidence_refs_evidence_weight_chk check (evidence_weight > 0 and evidence_weight <= 1),
  constraint memory_evidence_refs_explicitness_chk check (explicitness in ('explicit', 'implicit', 'inferred')),
  constraint memory_evidence_refs_system_summary_backpointer_chk check (
    source_type <> 'system_summary' or derived_from_evidence_id is not null
  ),
  constraint memory_evidence_refs_unique_hit unique (memory_id, message_id, span_start, span_end)
);

create index memory_evidence_refs_memory_idx
  on public.memory_evidence_refs (memory_id);

create index memory_evidence_refs_message_idx
  on public.memory_evidence_refs (message_id);

create index memory_evidence_refs_window_message_idx
  on public.memory_evidence_refs (window_id, message_id);

create index memory_evidence_refs_episode_idx
  on public.memory_evidence_refs (episode_id);

create or replace function public.set_memory_items_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create trigger trg_memory_items_set_updated_at
before update on public.memory_items
for each row
execute function public.set_memory_items_updated_at();

create or replace function public.raise_append_only_violation()
returns trigger
language plpgsql
as $$
begin
  raise exception '% is append-only; % is not allowed', tg_table_name, tg_op
    using errcode = '55000';
end;
$$;

create trigger trg_message_events_append_only
before update or delete on public.message_events
for each row
execute function public.raise_append_only_violation();

create trigger trg_memory_events_append_only
before update or delete on public.memory_events
for each row
execute function public.raise_append_only_violation();

create trigger trg_memory_evidence_refs_append_only
before update or delete on public.memory_evidence_refs
for each row
execute function public.raise_append_only_violation();

create or replace function public.ensure_memory_item_has_evidence()
returns trigger
language plpgsql
as $$
begin
  if not exists (
    select 1
    from public.memory_evidence_refs mer
    where mer.memory_id = new.memory_id
  ) then
    raise exception 'memory_item % must have at least one memory_evidence_ref before commit', new.memory_id
      using errcode = '23514';
  end if;

  return null;
end;
$$;

create constraint trigger trg_memory_items_require_evidence
after insert or update on public.memory_items
deferrable initially deferred
for each row
execute function public.ensure_memory_item_has_evidence();

commit;
