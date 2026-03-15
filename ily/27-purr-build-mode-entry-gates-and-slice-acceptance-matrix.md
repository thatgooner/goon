# Purr build-mode entry gates + slice acceptance matrix

## why this note exists

notes 08-26 already lock the memory architecture.
what the repo still lacked was a single low-context answer to this question:

**when does research stop being "keep thinking" and become "safe to unpark the first build slice" without inviting random tool creep?**

that gap matters because the repo now has both:
- strong research-lock signals
- strong handoff/build-plan signals

without one explicit transition contract, a low-context builder can misread handoff docs as permission to start shipping.

this note fixes that.
it does **not** reopen architecture.
it defines the gate between research mode and eventual build mode.

---

## direct verdict

### current repo state
**research is complete enough for slice 1, but the build gate is still closed.**

translation:
- the architecture body is good enough to build from
- the first build slice is still `memory-ledger`
- dogfood stays a later validation track
- nobody should start implementation just because a handoff note or plan exists

### one-line rule
**until `weekly-missions.md` and `coding-agent-task-board.md` explicitly unpark `memory-ledger`, treat every build/dogfood document as spec only, not authorization.**

### what this changes
this does not change build order.
it changes repo discipline:
- research notes can say `ready`
- plans can say `here is how`
- but build opens only through shared board state

---

## what is already locked enough to build from

these are no longer real blockers for slice 1.

### locked
- identity scope: `owner_id` + `purr_id` on every durable object and retrieval path
- session/episode lineage contract
- typed memory claim shapes
- evidence backpointer rules
- lifecycle + contradiction handling
- pack artifact families and budget posture
- hidden cognition lane split
- prompt-artifact trust boundary
- feedback/review semantics
- Hermes steal vs reject map
- Hermes shadow-dogfood boundary
- first build slice = `memory-ledger`
- main slice order = `memory-ledger -> extractor -> packer -> feedback-orchestrator`

### not locked, but not blockers for slice 1
- exact extractor model choice
- free-tier cost knobs
- later `memory-health-auditor` timing
- later dogfood adapter implementation details beyond the already-locked boundary contract
- Catnet execution details beyond the already-locked autonomy/safety stance

hard translation:
**if somebody claims slice 1 cannot start because extractor-model choice or later auditor design is still open, that is fake blockage.**

---

## research-lock exit gates

all four gates below must be true before build mode opens.

## gate 1 — board gate
shared boards must explicitly say build is open.

minimum required changes:
- `notes/boards/weekly-missions.md` must stop using research-first-only phrasing and explicitly say the build gate is open for slice 1 only
- `notes/boards/coding-agent-task-board.md` must move `memory-ledger` from `parked` to `queued` or `in_progress`
- if dogfood work is allowed later, it must still remain clearly subordinate to the main slice order

if this gate is not flipped:
- no implementation
- no adapter shipping
- no "just setting up a quick tool"
- no speculative infra branch pretending to be harmless

## gate 2 — operational gate
there must be an actual place to run and verify the ledger.

minimum required truth:
- Supabase local-dev or project setup exists
- migration execution path is documented
- env/config loading path is documented
- low-context builder can run the schema work without guessing where the database lives

if this gate is not flipped:
- the repo is still handoff-ready, not build-ready

## gate 3 — reading gate
before a builder starts slice 1, the minimum source stack must be named and frozen.

required reading for slice 1:
- `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
- `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
- `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`
- `ily/11-purr-session-scope-and-episode-lineage-contract.md`
- `ily/08-purr-memory-lifecycle-and-feedback-state-machine.md`
- `notes/boards/purr-alignment-brief.md`
- `notes/boards/coding-agent-task-board.md`

if a builder starts without that stack, they are building from vibes.
kill it.

## gate 4 — scope gate
the repo must preserve the early-build boundary.

still forbidden when slice 1 opens:
- vectors / pgvector in the v1 ledger slice
- Catnet implementation
- user-facing memory UI/dashboard
- visible tool ceremony
- Hermes behavior coupling
- dogfood adapter creep into the mainline architecture
- any build that weakens evidence/backpointer discipline to move faster

---

## canonical build sequence

mainline product order stays:

1. `memory-ledger`
2. `memory-candidate-extractor`
3. `memory-context-packer`
4. `feedback-orchestrator`
5. later: `memory-health-auditor`
6. much later: social memory / Catnet / multimodal / world-sim lanes

### dependency truth
- extractor needs a real ledger to write into
- packer needs a pack-candidate read model to read from
- feedback needs state transitions and queueable truth objects
- proactive quality depends on packer + feedback, not raw transcript sludge
- dogfood validates the spine; it does not replace the spine

---

## slice acceptance matrix

## slice 1 — `memory-ledger`

### purpose
turn the research contracts into durable boring truth infrastructure.

### must consume
- `ily/13`
- `ily/14`
- `ily/12`
- `ily/11`
- `ily/08`

### must ship
- runnable SQL migration(s)
- core durable tables/views from note 13
- active-truth uniqueness rules
- owner-scoped RLS posture
- evidence-backed truth invariants
- immutable pack artifact storage
- minimal typed read/write API surface
- local fixtures/seed data
- setup README for Supabase/local dev

### must not ship
- vector search
- extractor LLM logic
- final pack generation logic
- proactive jobs
- UI
- Catnet schema

### proof of done
- challenged/superseded truth is suppressed correctly
- exclusive dedupe scope cannot leave duplicate active truth
- exact evidence lookup survives later summaries
- child session window can open without mutating old history
- no cross-owner read path exists

### dogfood relation
none yet. slice 1 does not require adapter build to be considered complete.

---

## slice 2 — `memory-candidate-extractor`

### purpose
turn raw message events into typed candidate/update intents with evidence refs.

### must consume
- `ily/12`
- `ily/14`
- `ily/08`
- `ily/17`

### must ship
- deterministic intake ordering on top of ledger writes
- typed candidate/update output contract
- correction-first handling
- idempotent mutation planning hooks
- provenance-safe evidence creation
- evaluation fixtures for junk / miss / contradiction cases

### must not ship
- fuzzy auto-truth promotion without evidence
- silent override path outside mutation contract
- prompt-derived evidence
- agentic subagent memory loop

### proof of done
- same source event can replay with no duplicate truth
- explicit correction outranks generic extraction
- all created candidates are evidence-backed
- ambiguous cases fail safe instead of inventing truth

### dogfood relation
phase 0 shadow-ledger can start validating raw-turn mirroring after slice 1 and gains real value once slice 2 exists.

---

## slice 3 — `memory-context-packer`

### purpose
build bounded model-visible artifacts from ledger truth without flattening the whole database into prompt sludge.

### must consume
- `ily/09`
- `ily/12`
- `ily/16`
- `ily/18`
- `ily/19`

### must ship
- `session_pack`, `turn_delta_pack`, `reentry_pack`, `proactive_pack`
- slot caps / token budgets
- patch vs rebuild rules
- exact-hit evidence before recap
- trust gates for prompt-bound material

### must not ship
- full-ledger prompt dumping
- maintenance artifacts disguised as user/purr chat
- summary-only recall pretending to be evidence

### proof of done
- same-turn correction can appear via committed overlay without full pack rebuild
- pack reuse is honest and bounded
- re-entry pack preserves continuity without muddy lineage
- exact evidence survives ahead of recap text

### dogfood relation
phase 1 pack compare becomes meaningful here.

---

## slice 4 — `feedback-orchestrator`

### purpose
make memory verification and trust decay real without turning Purr into a needy admin loop.

### must consume
- `ily/08`
- `ily/18`
- `ily/19`
- `ily/20`
- `notes/boards/purr-alignment-brief.md`

### must ship
- review queue / scheduling posture
- explicit + passive + no-signal outcome handling
- propagation into truth state, pack policy, and proactive eligibility
- anti-spam caps
- clean split between queue execution state and memory truth state

### must not ship
- silence = contradiction
- spammy review cadence
- generic survey-bot behavior
- review outcome writes that bypass the normal event trail

### proof of done
- no-signal stays distinct from contradiction
- passive reconfirmation can strengthen truth safely
- challenged/stale truth affects pack policy and proactive behavior correctly
- review cadence stays bounded

### dogfood relation
phase 2 correction validation and later phase 3 review/proactive validation become meaningful here.

---

## parked slice 5 — `memory-health-auditor`

### purpose
watch temporal quality failures after enough real memory events exist.

### why parked
it depends on slices 1-4 creating enough event history to audit.

### hard rule
this stays a deferred maintenance worker, not a new second-brain layer.

---

## dogfood track attachment rules

dogfood is a **validation track**, not a parallel product rewrite.

### attach points
- after slice 1+2: phase 0 shadow ledger is useful
- after slice 3: phase 1 pack compare is useful
- after slice 4: phase 2 correction validation and phase 3 feedback/proactive scoring are useful

### hard rule
if dogfood work starts creating pressure to change Hermes behavior, route live prompt state through Purr, or build adapter-specific abstractions that do not help the mainline memory spine, it has gone off-lane.
kill it.

---

## product invariants every build slice must preserve

these are not optional taste notes.
these are acceptance boundaries.

### invariant 1 — `1 human = 1 purr`
no shared/global memory shortcuts.
no fuzzy scope.
no runtime convenience key acting like product identity.

### invariant 2 — evidence before elegance
exact evidence backpointers beat pretty summaries.
if a summary helps navigation, fine.
it never becomes the truth source.

### invariant 3 — commit-before-use freshness
next-turn behavior may use committed ledger truth and tiny committed overlays.
not uncommitted inference.
not model vibes.

### invariant 4 — bounded prompt material
memory quality comes from selection, not stuffing.
if a slice increases prompt volume without improving recall precision, it failed.

### invariant 5 — typed maintenance artifacts
maintenance, salvage, compaction, and compare artifacts must stay visibly typed in the backend.
they must never masquerade as normal chat truth.

### invariant 6 — no dashboard-pet drift
if a build slice starts optimizing for inspectable feature theater over continuity quality, it is off-lane.

---

## anti-patterns / kill conditions during build entry

kill or block a build pass if it does any of this:
- opens a new infra lane before `memory-ledger` is shipped
- introduces vector search into slice 1
- uses Hermes memory files or prompt text as evidence
- treats dogfood compare output as direct truth mutation
- adds UI/admin/dashboard work ahead of memory quality
- weakens owner scope to make querying easier
- solves correction freshness by rebuilding the whole prompt every turn
- creates a second hidden agent/subagent inside the memory loop
- starts Catnet implementation because "the architecture is already written"

---

## low-context builder read order when build finally opens

when the build gate actually flips, the shortest correct read order is:

1. `notes/boards/coding-agent-task-board.md`
2. `notes/boards/weekly-missions.md`
3. `notes/boards/purr-alignment-brief.md`
4. `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md`
5. `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md`
6. `ily/12-purr-memory-claim-shapes-evidence-and-selection-contract.md`
7. `ily/11-purr-session-scope-and-episode-lineage-contract.md`
8. `ily/08-purr-memory-lifecycle-and-feedback-state-machine.md`

optional context after that:
- `ily/17`
- `ily/18`
- `ily/20`
- `ily/26-hermes-shadow-dogfood-adapter-and-tap-boundary-contract.md`

---

## direct answers

### is research actually done enough for build?
yes.
for slice 1, the architecture debt is already paid.

### is the repo in build mode right now?
no.
not until the shared boards explicitly open it.

### does dogfood get to jump the queue because the plan exists?
no.
dogfood follows the spine.
it validates slices.
it does not authorize them.

### what is the single honest transition sentence?
**research complete, build gate closed. open build only through explicit board-state change plus operational setup.**

---

## short verdict

the repo does not need more vague architecture poetry.
it needed a clean handoff rule.

that rule is now simple:
- the research body is sufficient
- the mainline build order is fixed
- dogfood is subordinate
- the gate opens only when the shared boards say it opens

until then, stay in disciplined research-lock behavior.
