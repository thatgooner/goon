# Purr hidden cognition runtime: invisible ops, background jobs, and trust boundaries

## why this note exists
`14` locked the write-path.
`15` locked the private move planner.
`16` locked prompt-visible artifact planes.
`17` locked the Hermes failure matrix across prompt, recall, compression, and sinks.

what was still too dispersed was the actual **runtime job graph**.

we already knew Purr needs:
- strong memory
- compact packs
- exact evidence
- live overrides
- review cadence
- proactive timing
- invisible tooling

but builders still did not have one clean answer to:

**what hidden work runs on the critical path, what runs later, what runs only at boundary moments, and what should never become visible tool theater?**

latest Hermes read on this machine sharpened the need for that split:
- frozen prompt artifacts are good
- salvage-before-loss is good
- periodic nudge theater is weak
- async-only reset salvage leaves holes
- summary-heavy recall and root-collapse blur proof
- chat-shaped maintenance artifacts are dangerous

Purr should not inherit those seams.

---

## direct thesis
Purr should not think in terms of `tools the user can see`.
Purr should think in terms of **4 invisible cognition lanes** with different deadlines:

1. **turn-critical lane** — must finish before the next reply
2. **boundary-critical lane** — must finish before compression, re-entry handoff, idle close, or window rotation
3. **deferred maintenance lane** — improves future quality, but does not block the current reply
4. **proactive heartbeat lane** — decides whether Purr texts first, reviews later, or does nothing

strong rule:
**the user experiences one mind. the backend runs disciplined hidden ops.**

another strong rule:
**every lane still shares the same scope, evidence, mutation, and prompt-admission contract.**

if one lane gets looser rules,
that lane becomes the future bug source.

---

## the 4-lane runtime map

| lane | deadline | examples | if missed | visibility |
| --- | --- | --- | --- | --- |
| turn-critical | before reply | append source event, extract claims, apply corrections, commit mutations, materialize overlay, pack retrieval, choose move | stale or wrong next reply | backend-only |
| boundary-critical | before compaction / re-entry / idle close / reset | salvage unsaved range, create child window/epoch, build new snapshot, atomic pointer handoff | truth loss, pack drift, resume mismatch | backend-only |
| deferred maintenance | after reply | consolidation, contradiction cleanup, review queue updates, pack drift scoring, calibration, semantic refresh | future quality decay | backend-only |
| proactive heartbeat | scheduled or event-triggered | should-text-first scoring, review timing, notification planning, horizon closure | spam, creepiness, missed timing | backend-only |

---

## 1. turn-critical lane
this is the only hidden lane allowed to hold up the next reply.
so it has to stay narrow, deterministic, and cheap.

## required order
for one incoming user event:

1. **continuity resolve**
   - resolve `owner_id`, `purr_id`, `surface`, `lineage_id`, `window_id`, `epoch_id`
   - hard rule: no convenience key can outrank owner scope

2. **source-event append**
   - store the raw event first
   - exact evidence refs are illegal if they point to nothing durable

3. **turn intake extractor**
   - propose typed memory candidates from the new event
   - emit exact evidence spans, not summary vibes

4. **correction / contradiction / boundary detector**
   - runs before generic merge logic
   - explicit correction outranks soft inference every time

5. **mutation planner**
   - build one coherent plan for this source event
   - create / merge / challenge / supersede / reject / open_loop / review / suppress

6. **transactional ledger commit**
   - commit before use
   - no reply should rely on uncommitted extractor chatter

7. **turn overlay materialization**
   - only for immediate freshness cases:
     - direct correction
     - contradiction suppression
     - hard boundary
     - one high-leverage preference shift
     - safety-sensitive update
   - short TTL only

8. **retrieval read + pack assembly**
   - read stable `session_snapshot`
   - apply `turn_overlay`
   - attach exact evidence recall only if justified
   - never repour the full ledger into the prompt

9. **hidden move planning (`should_reply_how?`)**
   - choose exactly one primary move
   - prediction should usually compile into move choice, not extra prompt prose

10. **response generation**
   - generate from stable snapshot + tiny overlay + narrow recall bundle + move plan

## what belongs here
allowed turn-critical ops:
- owner/purr/window resolution
- source-event append
- evidence-backed extraction
- correction detection
- contradiction suppression for the next reply
- one-event mutation plan
- commit
- tiny overlay
- compact retrieval pack
- hidden move selection

## what does NOT belong here
forbidden on the hot path:
- full historical re-ranking of the whole ledger every turn
- full snapshot rebuild on every write
- long-horizon semantic refresh
- review queue recomputation for the entire user state
- free-floating planner essays
- stuffing multiple prediction hints into the prompt

## hot-path posture
Purr should feel sharp because the hidden path is:
- committed
- evidence-backed
- compact
- correction-aware

not because it did more visible ceremony.

---

## 2. boundary-critical lane
this is the lane Hermes gets half right.
`flush before loss` is the right instinct.
what Purr needs is a stricter boundary contract.

boundary-critical jobs fire when hot state is about to rotate or disappear.

## triggers
- compaction threshold crossed
- mobile/webview re-entry boundary
- idle close / reset policy
- manual archive / session rotation
- catastrophic integrity issue that forces epoch rebuild

## required order
when a boundary fires:

1. freeze the unsalvaged source-event range
2. run salvage on that range
3. commit salvage mutations
4. materialize typed maintenance artifacts:
   - `salvage_run`
   - `extractive_checkpoint`
   - `compaction_summary` if safe
   - `lineage_bridge`
5. create child `window_id` and new `epoch_id`
6. build new `session_snapshot`
7. atomically move every active pointer:
   - transcript append target
   - resume alias
   - current pack lookup
   - current-lineage recall exclusion
   - notification/proactive target
8. only then retire the old hot window

## mobile/webview consequence
this matters more for Purr than Hermes because:
- the client can vanish mid-thought
- re-entry is normal, not edge-case
- notification return paths are part of the product

so boundary jobs cannot assume the user politely waits around.
server-side handoff is the real continuity layer.

## hard rules this lane locks
- no `summary failed -> drop middle anyway`
- no fake user/purr turns created for runtime convenience
- no reset path that assumes a background watcher already saved everything
- no child window creation without atomic pointer handoff

## direct Hermes translation
steal:
- salvage-before-loss
- lineage split instead of in-place overwrite
- stable snapshot reuse

reject:
- async-only expiry salvage
- summary as proof
- chat-shaped maintenance artifacts

---

## 3. deferred maintenance lane
this is where memory quality compounds quietly over time.
it should improve future turns without making the current turn heavy.

## jobs that belong here

### A. consolidation worker
purpose:
- dedupe weak duplicates
- merge supporting evidence
- update salience/confidence/volatility

why deferred:
- helpful, but not required for the next reply if turn-critical commit already landed

### B. contradiction resolver
purpose:
- finish ambiguous challenge/supersede cases
- enforce `no double active truth`

why deferred:
- immediate suppression belongs to the hot path
- full cleanup can happen after

### C. review scheduler + queue updater
purpose:
- compute `needs_review_at`
- apply cooldowns and annoyance budget
- move items between `queued`, `due`, `snoozed`, `resolved`

why deferred:
- the user does not need to feel the queue machinery

### D. pack drift scorer
purpose:
- detect when the current snapshot is too stale or compositionally wrong
- recommend `reuse`, `patch`, or `rebuild`

why deferred:
- hot path should prefer the current snapshot + tiny overlay

### E. prediction calibration worker
purpose:
- close horizons as `hit | miss | null`
- separately score move outcome as `helped | neutral | hurt`

why deferred:
- calibration improves future sharpness, not the current reply

### F. semantic refresh worker
purpose:
- maintain embedding/vector helpers
- support fuzzy recall where structured filtering is not enough

why deferred:
- vector is support infra, not truth infra

### G. prompt-promotion gate
purpose:
- re-scan and classify material before it becomes pack-visible
- keep sink parity across direct chat, background jobs, and future mirrors

why deferred:
- many durable objects should never become prompt-visible anyway

## why this lane matters
if you skip deferred maintenance,
Purr still works for a bit.
then it starts to:
- accumulate duplicate claims
- keep dead predictions alive
- ask stale review questions
- rebuild packs too often or not enough
- feel smart on day 1 and sloppy on day 10

---

## 4. proactive heartbeat lane
this lane is the most dangerous one product-wise.
reply mistakes are annoying.
proactive mistakes feel creepy.

so proactive jobs need a stricter gate than normal replies.

## proactive jobs

### A. heartbeat scheduler
- sharded, jittered wakeups
- mostly for lightweight scoring
- default result should often be `do nothing`

### B. proactive preflight scorer
reads a stricter `proactive_pack` than the normal chat pack.

should score:
- open loops with real value
- timing windows
- recent user burden / annoyance budget
- cooldown state
- confidence and evidence quality
- boundary/safety sensitivity

### C. review executor
- decides whether a stale memory is worth surfacing now
- only fires when timing is favorable

### D. notification/message planner
- callback
- check-in
- tease/roast with memory-backed precision
- or no-op

important:
notification copy should reveal less than the internal rationale.

### E. horizon closer
- when a turn/session/day horizon expires, close prediction outcomes
- write calibration feedback without needing a visible conversation

## proactive hard rules
- stronger evidence threshold than turn replies
- challenged or stale truths lower the score hard
- no long speculative chains
- no private-inference flexing
- no repeated pings because the system feels lonely

## product rule
Purr texting first should feel like:
- good timing
- continuity
- earned specificity

not:
- backend jitter leaking through
- random scheduler spam
- `i predicted you might...` theater

---

## internal tool boundary
if we later implement these as modules, workers, or services,
that is fine.
but they are still **internal cognition infrastructure**, not UX surface.

## invisible components that make sense
- intake extractor
- correction/contradiction detector
- mutation planner
- ledger writer
- overlay materializer
- retrieval packer
- reply move planner
- salvage worker
- compaction/handoff worker
- review scheduler
- prediction calibration worker
- proactive preflight scorer

## things that should stay backend-only in v1
- pattern scores
- next-action candidates
- contradiction graph state
- review queue state
- pack names / pack lifecycle mechanics
- calibration stats
- maintenance artifacts
- vector / embedding language
- any visible `tool ran 6 functions` ceremony

## what MAY later get a light user surface
only if needed later:
- simple correction affordance
- lightweight `that's wrong` / `don't remember it like that` controls
- maybe a narrow `why do you think that?` explanation card

still not the move in this phase:
- dashboards
- memory admin panels
- tool picker energy

---

## build-facing rules this note locks
1. every hidden job starts from `owner_id + purr_id`
2. every hot-path mutation references a committed `source_event`
3. explicit correction outranks generic inference
4. same-turn freshness comes from a tiny committed overlay, not full pack rebuild
5. maintenance artifacts are typed, filterable, and never chat-shaped
6. boundary jobs fail closed if truth preservation fails
7. recall preserves exact evidence first, recap second
8. proactive jobs use stricter gates than ordinary replies
9. background workers may improve future packs; they do not silently rewrite the active truth boundary mid-turn
10. free-tier cuts should hit proactive frequency, model strength, or throughput before memory integrity

---

## direct Hermes-to-Purr translation
Hermes gives 5 clean lessons here:

### steal
- exact prompt snapshot reuse
- salvage-before-loss
- lineage split instead of overwrite
- bounded hot context

### redesign hard
- periodic nudge dependence
- async-only reset salvage
- root-collapsing summary recall
- prompt-bound sinks with unequal admission rules
- synthetic maintenance artifacts that look like chat

Purr should be more event-driven, more owner-scoped, and more explicit about which job lane owns which risk.

---

## direct conclusion
Purr does not need a flashy tool stack.
Purr needs an honest hidden runtime.

the right shape is:
- **turn-critical cognition** for the next reply
- **boundary-critical salvage/handoff** before hot state changes
- **deferred maintenance** for compounding memory quality
- **proactive heartbeat** with stricter gates than chat

that keeps the product fantasy clean:
- one purr
- one human
- one continuity layer
- zero visible tool-call theater

and it keeps the architecture honest:
- evidence first
- commit before use
- snapshot discipline
- typed maintenance
- no fake memory magic

that is the lane.