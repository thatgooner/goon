# Purr Supabase local-dev operational gate clarification

## why this note exists

by `ily/21` and `ily/27`, the repo had already reached the same blunt conclusion:
- research is complete enough for slice 1
- the build gate is still closed
- the main remaining blocker is operational, not architectural

but the repo's concrete Supabase path was still scattered.

the strongest how-to lived inside parked dogfood docs under `tools/hermes-dogfood-adapter/`, which creates an easy low-context failure:
- somebody sees runnable-looking local Supabase instructions and a phase-0 migration
- they mistake that for authorization
- or worse, they mistake dogfood phase-0 scope for the full `memory-ledger` slice

this note fixes that confusion.

it does **not** open build mode.
it does **not** authorize `memory-ledger`.
it only freezes the operational stance so future builders stop guessing.

---

## direct verdict

### one-line answer
**the repo should treat Supabase as local-first for development, remote later, while keeping build authorization strictly board-gated.**

### translation
- yes, the working assumption should be `Supabase CLI locally first`
- no, existing local setup docs do **not** mean build is open
- yes, the future mainline scaffold/migration home should be repo-root, not tool-local
- no, dogfood phase-0 schema is **not** the full `memory-ledger` target

### hard rule
**until `weekly-missions.md` and `coding-agent-task-board.md` explicitly unpark `memory-ledger`, all Supabase setup material in this repo is reference posture, not build authorization.**

---

## what was already locked before this note

### from `notes/boards/system-board.md`
- Supabase should hold durable source-of-truth state
- retrieval should stay selective and cheap
- research/build passes should only serve active mission lanes

### from `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
- assume Supabase Postgres
- v1 should stay boring and strong
- `pack_candidate_view` belongs in slice 1
- backend/service-role jobs are the write path
- clients should not directly query raw memory internals in v1
- no anonymous or cross-owner reads of memory/evidence/pack rows

### from `ily/21-purr-research-consolidated-state-and-build-handoff.md`
- Supabase setup/connection documentation is the single honest blocker before build
- lack of exact project/local-dev setup is operational debt, not architecture debt

### from `ily/27-purr-build-mode-entry-gates-and-slice-acceptance-matrix.md`
- build remains closed until the board gate flips
- operational gate requires an actual place to run migrations and verify slice 1
- local dev or project setup is mandatory before low-context builders start shipping

### from existing dogfood docs
already implied, but in the wrong place for mainline clarity:
- `supabase init`
- `supabase start`
- `supabase status`
- `supabase db reset`
- env-driven backend connection
- local-first posture before hosted deployment

this note does not invent a new direction.
it just makes that direction explicit and separates it from dogfood/build authorization.

---

## what already exists in repo right now

### 1. a concrete local Supabase workflow already exists
`tools/hermes-dogfood-adapter/README.md` already describes a usable local stack path:
- initialize local Supabase project
- start local services
- inspect endpoints/status
- copy migration into a local migrations folder
- reset/apply against disposable local state

that means the repo is **not** missing operational imagination.
it is missing a canonical mainline statement.

### 2. a runnable phase-0 migration already exists
`tools/hermes-dogfood-adapter/migrations/001_phase0_schema.sql` proves that local Supabase-backed testing is real, not hypothetical.

### 3. env-driven backend write posture already exists in code
current dogfood adapter code expects backend credentials like:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

that is consistent with note 13's `backend/service role writes only` stance.

---

## what must NOT be misread

## 1. parked dogfood artifacts are not authorization
`tools/hermes-dogfood-adapter/` may contain runnable-looking setup, migrations, or code.
that does **not** mean:
- build mode is open
- dogfood may jump ahead of the main slice order
- the tool-local migration is now the canonical mainline schema

## 2. dogfood phase-0 scope is narrower than mainline slice 1
phase-0 dogfood intentionally excludes parts that the actual `memory-ledger` slice must still ship, including:
- `pack_artifacts`
- `pack_candidate_view`
- full mainline acceptance posture around the shared ledger contract

hard translation:
**dogfood phase-0 proves a test lane exists. it does not shrink slice 1.**

## 3. local setup docs are not the same as the canonical home
right now the local Supabase instructions live under a parked tool subtree.
that is fine as reference.
it is the wrong long-term source of truth for the mainline memory spine.

---

## recommended operational stance

## 1. local-first, remote later
for the first real build slice, the official development posture should be:
- local Supabase via CLI first
- hosted Supabase or remote Postgres later

why:
- it removes hosted-project dependency from the first build pass
- it keeps schema work testable and disposable
- it lets low-context builders verify migrations without waiting on infra coordination

hard rule:
**remote hosting is a later deployment decision, not a blocker for slice 1.**

## 2. repo-root is the future canonical home
when build mode eventually opens, the canonical home for mainline Supabase assets should be at repo root, not inside the dogfood adapter.

recommended future home:
- `/home/ubuntu/goon/supabase/` for CLI scaffold + migrations
- repo-level docs for env + startup + reset commands

why:
- `memory-ledger` is a product-core dependency, not a dogfood-adapter-local dependency
- extractor, packer, and feedback slices all depend on the same core data plane
- keeping the canonical scaffold under a parked tool subtree invites scope confusion

hard rule:
**tool-local Supabase assets may remain adapter references, but they should not become the source-of-truth home for the mainline ledger.**

## 3. official default migration posture should be Supabase CLI, not ad hoc SQL first
recommended default path for low-context builders:
1. `npx supabase@latest init`
2. `npx supabase@latest start`
3. `npx supabase@latest status`
4. place checked-in migrations in repo-root `supabase/migrations/`
5. `npx supabase@latest db reset`

`psql` one-offs are still useful for debugging or manual inspection.
but they should be treated as backup/debug path, not the canonical first-run workflow.

why:
- one obvious path beats 3 half-official ones
- local rebuilds stay deterministic
- low-context builders do not need to invent their own migration ritual

## 4. env posture should stay backend/service-role only
minimum expected env contract for backend writers:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

possible later additions can exist, but the core posture is already clear:
- no real creds committed into repo
- no anonymous write paths
- no client-direct raw-memory access in v1
- all truth/evidence/pack writes happen server-side

## 5. build authorization stays separate from setup clarity
this note should make it easier to open build later.
it should **not** silently open build now.

board state still decides:
- when `memory-ledger` leaves `parked`
- when low-context builders may start implementation
- when dogfood can attach to the mainline spine

---

## minimum operational gate checklist before `memory-ledger` can be honestly unparked

before the board flips, low-context builders should have one explicit repo-level answer for all of this:

### local stack
- canonical working directory for mainline Supabase workflow
- canonical init/start/status/reset commands
- explicit statement that local Supabase is the default first environment

### migration path
- canonical location for checked-in migrations
- canonical command for apply/reset
- explicit statement that dogfood phase-0 SQL is reference-only, not the mainline slice-1 contract

### env path
- exact required env var names for backend writes
- where the repo expects them to live
- explicit no-committed-secrets rule

### verification
- one smoke-test query or checklist proving required slice-1 tables/views exist
- explicit list of what slice 1 must include, including `pack_artifacts` and `pack_candidate_view`

### authorization
- explicit sentence that setup clarity does not itself open build mode
- explicit board-state unpark for `memory-ledger`

if any of that is still fuzzy,
the repo is handoff-aware but not honestly operationally open.

---

## what this changes

### changes now
- freezes the local-first Supabase posture as the right research conclusion
- separates `operational path exists` from `build is authorized`
- separates `dogfood reference schema` from `mainline memory-ledger scope`
- names repo-root as the future canonical home for mainline Supabase assets

### does not change
- build order
- dogfood attachment rules
- slice 1 remaining parked state
- research conclusion that the memory spine comes before social lanes, UI, or Catnet work

---

## direct recommendation for future board owners

when the repo is ready to move from research-lock to slice-1 build,
do **not** invent a new posture.
just formalize the one already implied here:
- local-first Supabase CLI workflow
- repo-root canonical scaffold/migrations
- backend/service-role write posture
- explicit board unpark as the authorization event

that is enough.
anything more dramatic is probably theater.

---

## short verdict

the missing blocker was not some grand architecture question.
it was a boring repo-discipline question:

**where does the real Supabase path live, and how do we stop people from mistaking setup clues for permission to build?**

answer:
- local Supabase first
- repo-root canonical home later when build opens
- dogfood docs stay reference-only
- board state still controls authorization
