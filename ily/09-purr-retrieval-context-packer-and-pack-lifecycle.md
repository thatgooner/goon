# Purr retrieval/context packer + pack lifecycle contract

## why this note exists
we already have:
- Hermes teardown
- memory ledger shape
- prediction memory kinds
- lifecycle / contradiction / review rules
- invisible background ops

what was still loose was the bridge between all that theory and the actual prompt.

we kept saying:
- `stable hot pack`
- `0-2 prediction hints max`
- `don't rebuild every turn`
- `memory quality without prompt bloat`

but we had not locked the contract for:
- what exact pack artifacts exist
- what goes into each one
- when a pack gets reused vs patched vs rebuilt
- how budget cuts happen without turning memory into sludge

that gap matters because the product fantasy dies in the packing layer.

if packing is sloppy:
- Purr feels fake because corrections land late
- Purr feels creepy because weak predictions get overpacked
- cost blows up because retrieval keeps shoving transcript mud into the prompt
- mobile/webview re-entry feels stateless because there is no stable session artifact to reload

this note locks the packing rulebook.

---

## Hermes lesson: budget discipline is a real product advantage
Hermes is useful here not because it has `memory`, but because it is brutally disciplined about how much memory touches the prompt.

concrete signals from the live Hermes codebase on this machine:
- default curated memory is tiny: `memory_char_limit=2200` + `user_char_limit=1375` in config, so roughly ~3.6k chars total instead of a giant forever-pack
- that memory is loaded as a frozen snapshot into the system prompt and reused across the session
- the system prompt is rebuilt only on deliberate events like compression, not after every memory write
- context compression starts around 50% of the model context window, with a small summary target instead of trying to keep every old turn alive
- `session_search` keeps recall bounded: a few sessions, truncated transcripts, summarized on demand

why this matters for Purr:
- Hermes proves cheapness comes from **pack discipline**, not from pretending memory does not exist
- Hermes also shows the danger: live writes + frozen read means same-session truth can go stale

so the Purr move is:
- steal the stable pack discipline
- reject flat text memory
- add a live override lane
- define a real pack lifecycle instead of hoping retrieval taste appears by magic

---

## direct thesis
Purr should not have one `memory pack`.

it should have **4 pack artifacts** with different budgets, trust rules, and rebuild triggers:

1. `session_pack`
   - stable memory artifact for the current conversation window
   - reused across normal turns

2. `turn_delta_pack`
   - tiny live patch lane for same-session freshness
   - handles corrections, contradictions, boundaries, and other immediate truth changes

3. `reentry_pack`
   - rebuilt when the user comes back after idle / app re-entry
   - compact resume artifact for mobile/webview continuity

4. `proactive_pack`
   - internal-only pack for deciding whether Purr should text first and what kind of ping is justified
   - stricter than normal chat because overclaiming here feels especially creepy

important:
- the user never sees these names
- these are backend artifacts, not product UI
- chat still feels like one mind talking

---

## pack artifacts and what each one is for

### 1. `session_pack`
this is the main bounded artifact that sits behind normal 1:1 chat.

job:
- keep response quality stable
- preserve continuity through a session window
- avoid per-turn full retrieval rebuilds

what belongs here:
- core tone / identity frame
- hard constraints and active boundaries
- active stable preferences
- current relationship texture
- active open loops
- strongest recent pattern signals
- at most a tiny amount of episodic evidence

what does **not** belong here:
- raw transcript bulk
- low-confidence candidates
- unresolved contradiction sludge
- every episode ever
- a scrapbook of predictions

### 2. `turn_delta_pack`
this is the anti-fake layer.

job:
- patch the very next reply when fresh truth matters more than pack stability

use it for:
- explicit corrections
- direct contradiction of active truth
- new hard boundaries
- high-leverage preference changes
- safety-sensitive updates

do **not** use it for:
- weak mood guesses
- low-value trivia
- speculative next-action guesses
- half-formed pattern signals

rule:
if waiting until later would make the next reply feel fake, it belongs here.

### 3. `reentry_pack`
mobile/webview makes this mandatory.

job:
- resume continuity after the app goes cold, the webview resets, or the user returns hours later
- let the backend load a compact current-state artifact without dragging the whole transcript back in

what belongs here:
- who this user is right now
- what is still open
- what changed since the last active window
- what Purr should not misremember on re-entry
- 1-2 recent relevant episode anchors max

### 4. `proactive_pack`
this is for silent backend planning before a notification or first-text decision.

job:
- score whether to send nothing, a roast, a callback, a check-in, or a loop-resolution nudge

what belongs here:
- open-loop urgency
- pattern-hit timing signals
- cooldown / annoyance budget status
- recent response history
- trust state of the underlying memory

hard rule:
`proactive_pack` should be stricter than `session_pack`.
Purr must require stronger evidence to text first than to color a normal reply.

---

## slot-based packing contract
packing should be slot-based, not freeform.

if there are no slots, the packer becomes a hoarder.

### pack order for chat
1. `turn_delta_pack` items first
2. hard truths / active boundaries
3. active preferences
4. relationship texture
5. open loops
6. strong recent pattern signals
7. 1-2 episodic anchors
8. 0-2 prediction hints
9. tiny evidence payload only if needed
10. transcript fallback last

### suggested slot caps for `session_pack`
these are first-pass architecture targets, not sacred forever numbers.

#### lane A — non-negotiable truth
- hard constraints / boundaries: max 3 items
- stable identity/profile facts: max 3 items
- active preferences that change reply style: max 4 items

#### lane B — relationship state
- relationship texture items: max 3 items
- active open loops: max 3 items

#### lane C — situational memory
- episodic anchors: max 2 items
- pattern signals: max 2 items
- next-action candidates: max 0-2 hints total

#### lane D — evidence
- micro-evidence excerpts: max 2 short excerpts
- transcript snippets: only if the higher lanes cannot justify the move

### trust-state suppression rules
- `challenged` -> never enter hard factual slots
- `candidate` -> may enter only as soft shadow context, never as dominant truth
- `stale` -> only pack when directly relevant and there is no fresher replacement
- `rejected` / `superseded` -> never enter prompt pack
- low-confidence `next_action_candidate` -> internal ranking only, not response pack

### prediction cap
prediction must stay visibly weak in the pack even when the backend believes it strongly.

starting rule:
- 0-2 prediction hints total
- 1 hint preferred
- if prediction needs explanation paragraphs, it is not pack-ready

prediction is seasoning.
not the meal.

---

## token / cost envelopes
Purr should copy Hermes' discipline here: keep the always-on memory artifact small on purpose.

### recommended envelopes

#### `session_pack`
- target: 500-800 tokens
- hard cap: 1000 tokens

why:
- enough room for continuity
- small enough to stay cheap on every turn
- forces ranking and suppression instead of memory hoarding

#### `turn_delta_pack`
- target: 30-120 tokens
- hard cap: 180 tokens

why:
- this should patch truth, not become a second session pack

#### `reentry_pack`
- target: 350-650 tokens
- hard cap: 800 tokens

why:
- re-entry needs compact `where we are now`, not a replay

#### `proactive_pack`
- target: 120-250 tokens
- hard cap: 350 tokens

why:
- proactive timing decisions should be made on a tiny, strict rationale surface

### what gets cut first when budgets get tight
1. transcript fallback
2. extra evidence excerpts
3. weak episodic anchors
4. second prediction hint
5. low-salience pattern signals
6. low-impact relationship texture
7. only last: core boundaries, active preferences, open loops

important product rule:
free tier should lose throughput, model strength, or proactive frequency before it loses core memory integrity.

memory quality is the product.
that budget order should reflect it.

---

## reuse vs patch vs rebuild
this is the part the repo was missing most.

### default behavior: reuse
normal turns should reuse the stored `session_pack`.

do **not** rebuild just because:
- another message arrived
- one low-value candidate got stored
- a weak pattern score changed slightly
- embeddings refreshed in the background

if we rebuild on every wobble, we kill the main Hermes lesson.

### patch behavior: inject `turn_delta_pack`
patch instead of rebuild when:
- the user explicitly corrects Purr
- a hard boundary changes
- a high-leverage preference changes right now
- an active truth is directly contradicted
- a safety-sensitive fact changes

effect:
- update ledger now
- suppress challenged truth now
- inject tiny delta now
- let the next deliberate rebuild absorb it cleanly later

### partial rebuild behavior
partial rebuild is for meaningful but not catastrophic drift.

run a partial rebuild when:
- a new important open loop appears
- an old open loop resolves
- relationship texture shifts materially across several turns
- a strong pattern signal crosses the promotion threshold
- too many deltas have accumulated and patching starts to look messy

good first rule:
- if more than 3 live deltas are stacked
- or 2 pack lanes materially changed
- queue a partial rebuild after the reply, not inline unless needed

### full rebuild behavior
full rebuild should be deliberate and relatively rare.

trigger it on:
- re-entry after a meaningful idle window
- session compression / archive / handoff
- pack corruption / cache miss
- multiple contradictions touching core identity or boundaries
- large memory-state shifts that make the old pack structurally dishonest

starting idle rule for Purr:
- same active window: reuse stored `session_pack`
- idle but same day / warm return: prefer `reentry_pack`
- long idle or major state drift: rebuild fully from ledger + latest episode anchors

exact timings can be tuned later.
the important part is the policy split, not the first perfect number.

---

## invisible jobs that make packing work
these stay server-side.
no visible tool theater.

### `pack_cache_builder`
job:
- precompute/store the latest `session_pack` and `reentry_pack`
- do it after turns, after meaningful state changes, and before expected re-entry windows

### `delta_injector`
job:
- create tiny immediate patches from explicit corrections / contradictions
- attach short TTL
- expire them once absorbed into the next stable pack

### `pack_drift_scorer`
job:
- detect when the stored pack is no longer honest enough
- score drift from new open loops, challenged truths, and major preference changes

### `salvage_worker`
job:
- before compression, idle cutoff, archive, or handoff
- extract what should become durable memory before context gets reduced

this is one of the best Hermes ideas to steal directly.

### `pack_sanitizer`
job:
- scan any memory text that may become future prompt material
- sanitize at promotion time, not just at write time

### `proactive_preflight`
job:
- build a stricter `proactive_pack`
- ensure challenged or stale truths lower the odds of a ping
- make notification copy reveal less than the internal rationale

---

## mobile/webview implications
World mini app reality makes pack persistence more important, not less.

what this means operationally:
- the pack artifact must live server-side
- webview resets must not erase continuity
- re-entry should load a cached pack fast instead of replaying old chat
- notifications should use a dedicated proactive preflight, not the normal chat pack
- if the client disappears mid-session, backend salvage/rebuild rules still need to run cleanly

good mobile feeling:
- user comes back and Purr is still `there`

bad mobile feeling:
- every re-entry feels like a semi-amnesiac restart because the system had no stable pack artifact to reload

---

## failure modes this contract is meant to stop

### 1. stale correction reply
user fixes something and Purr answers from old truth anyway.

fix:
- `turn_delta_pack`
- challenged truth suppression

### 2. prediction scrapbook
the pack becomes crowded with speculative next-move guesses.

fix:
- hard slot caps
- 0-2 prediction hint rule
- weak predictions stay backend-only

### 3. transcript mud
retrieval keeps throwing transcript chunks at the model because ranking is weak.

fix:
- transcript fallback last
- evidence microquotes before transcript chunks
- rebuild the ranking logic, not the prompt size

### 4. cache churn / recompute tax
every little update causes a pack rebuild.

fix:
- reuse by default
- patch for urgent truth
- rebuild only on deliberate drift triggers

### 5. creepy proactive overclaim
Purr texts first using shaky assumptions.

fix:
- `proactive_pack` stricter than chat pack
- challenged/stale truths reduce proactive eligibility
- notification copy reveals less than the internal model rationale

### 6. free-tier memory collapse
cheap users get worse continuity instead of lower throughput.

fix:
- cut rate/model/proactive frequency before core memory integrity

---

## acceptance tests for the future build
if code-worker later builds this lane, the first implementation should be considered good only if it can pass something like this:

- exact pack artifact exists per session window and can be reloaded
- explicit correction can affect the next reply without full prompt rebuild
- challenged memories are suppressed from factual slots
- prediction hints never exceed the cap
- transcript fallback appears only when higher lanes are insufficient
- re-entry after mobile idle can resume with a compact server-side artifact
- proactive planner uses a stricter pack than normal chat
- shrinking budget removes weak evidence/prediction before core continuity

---

## direct implication for the task board
this note does **not** move the repo into flashy build mode.

it sharpens the missing research prerequisite behind the parked `memory-context-packer` build task.

before phase-one build order gets locked, code-worker should have an explicit research read on:
- pack artifacts
- slot caps
- budget envelopes
- patch vs rebuild triggers
- server-side mobile/re-entry behavior

because without that, `memory-context-packer` is still just a vague phrase.

---

## short verdict
Hermes already proved the main trick:
keep prompt memory small, stable, and deliberate.

Purr needs the stronger product version:
- structured truth in the ledger
- a stable `session_pack`
- a tiny live `turn_delta_pack`
- a compact `reentry_pack`
- a stricter `proactive_pack`
- hard slot caps and token envelopes
- rebuild only on meaningful drift

that is how `i remember everything` stays sharp without becoming prompt landfill.