# Hermes shadow-dogfood scorecard + observability contract

## why this note exists

ily/23 approved Hermes-first dogfood as a **partial yes**.
ily/26 locked the safest tap boundary.
that was enough to say **how** to observe Hermes without contaminating it.
it was not enough to say **when the observation is actually proving anything**.

there was still a missing seam:
- what Hermes surfaces can really be trusted for scoring
- what looks measurable but is actually lossy or partial
- what counts as a pass for shadow dogfood vs just "some plumbing moved"
- what should kill the dogfood lane before it turns into a side quest

this note closes that seam.

it is not a build note.
it is the evaluation contract for future Hermes shadow dogfood.

---

## direct verdict

**shadow dogfood only counts as validation if it passes 5 hard memory-spine dimensions at once:**
1. ingestion fidelity
2. correction freshness
3. pack quality
4. recall evidence quality
5. review/proactive safety

if only some of those pass, the honest output is:
- `useful plumbing signal`
- or `insufficient data`

not:
- `Purr memory validated`
- `we proved Purr is better than Hermes`
- `time to wire Purr into live behavior`

hard translation:
**shadow dogfood validates plumbing, not creature quality.**

---

## strongest new Hermes conclusion from the code pass

Hermes gives us a decent observability bundle,
but it does **not** preserve one perfect truth artifact for evaluation.

most important correction to earlier assumptions:
- Hermes `sessions.system_prompt` / `session_<id>.json.system_prompt` is the cached base prompt snapshot from `AIAgent._cached_system_prompt`
- gateway `context_prompt` plus gateway `ephemeral_system_prompt` are injected at API-call time only
- so Hermes does **not** persist the full effective prompt that hit the provider on a normal gateway turn

translation for dogfood:
- phase-1 compare can still use stored Hermes prompt material as a **baseline reference**
- but it is a **partial compare surface**, not the complete effective prompt truth
- if exact prompt parity matters, dogfood needs request dumps or a dedicated hook/log sink

second hidden conclusion:
- Hermes token/cost accounting looks available in runtime objects,
  but the gateway-side persisted accounting is weak enough that post-hoc scorecards should not pretend they have exact cost truth from SQLite alone

third hidden conclusion:
- final persisted transcripts are useful,
  but they are not immutable event truth because retry/undo/compression/reset can rewrite or fork what survives

so the evaluation bundle must be treated as:
- SQLite
- gateway transcript JSONL
- gateway sessions.json origin metadata
- live hooks
- optional request dumps for exact API request truth

not as:
- one perfect stored prompt
- one perfect append-only event log

---

## what Hermes surfaces are actually scoreable

## 1. reliable enough surfaces

### A. SQLite session/message store
useful for:
- session lineage via `parent_session_id`
- persisted message ordering inside a session
- role/content/tool-call surfaces
- coarse counts like `message_count` and `tool_call_count`
- stored cached prompt baseline in `sessions.system_prompt`

### B. gateway transcript JSONL
useful for:
- richer per-turn transcript than SQLite alone
- `session_meta` capture on fresh session
- assistant/tool messages with more fields than SQLite keeps
- debug playback of what the gateway appended at that time

### C. `sessions.json`
useful for:
- live routing/origin context
- `chat_id`
- `thread_id`
- `chat_type`
- `user_name`
- current `session_key -> session_id` mapping while the session is alive

### D. live hooks
useful for:
- turn boundaries
- session start/reset boundaries
- step-loop depth
- low-cost timing triggers for snapshot reads

### E. optional request dumps
useful for:
- exact API request body
- full effective prompt truth
- exact provider-facing compare if phase-1 ever needs that level of precision

---

## 2. weak / lossy / fake-confidence surfaces

### do not overtrust these

- `sessions.system_prompt` as if it were the full gateway prompt
  - it misses gateway-only `context_prompt` and configured ephemeral additions
- SQLite alone as if it were the richest transcript surface
  - JSONL/session snapshot keep more fields
- persisted session totals as if they were exact cost truth
  - gateway runtime tracks more than it durably writes back
- current `sessions.json` mapping as if it were historical routing truth
  - it is a live index, not a historical ledger
- final transcript rows as if they were immutable event history
  - retry/undo/compression/reset can rewrite what remains
- hook previews as if they were full evidence payloads
  - they are timing hints, not canonical message truth

hard rule:
**anything that depends on exact provider prompt, exact historical routing, or immutable raw-turn chronology must be scored from the full observability bundle, not one store.**

---

## scorecard

## dimension 1 — ingestion fidelity

### what we are testing
can Purr mirror Hermes turns into its own ledger without drift, duplication, fake evidence, or lineage confusion?

### what to measure
- replay-no-op rate on mirrored Hermes turns
- duplicate `message_events` count
- duplicate `memory_evidence_refs` count
- duplicate active-truth count inside exclusive dedupe scopes
- share of source events keyed by Purr-owned bridge state from Hermes `session_id`
- lineage continuity after reset/compression via `parent_session_id`
- evidence-grounding rate to mirrored raw turns
- adapter maintenance burden per week
- added Hermes reply latency

### pass gate
pass only if:
- same source event can replay with **zero duplicate truth/evidence side effects**
- evidence refs stay grounded to mirrored raw turns
- reset/compression does not drift lineage/origin continuity
- adapter adds **no measurable Hermes latency**
- adapter upkeep stays boring enough to justify itself

### fail now if
- adapter needs Hermes runtime patching to work
- adapter embeds into Hermes reply path
- bridge identity relies on Hermes `session_key`
- evidence starts pointing at Hermes prompt text or memory files

### do not lie with these anti-metrics
- high raw row counts
- lots of hook events firing
- "the adapter is stable" because hook failures were swallowed
- happy-path ingestion without replay/reset/compression tests

---

## dimension 2 — correction freshness

### what we are testing
when a real correction appears in Hermes traffic,
does the Purr spine update live truth cleanly enough that the next-turn pack could be right without full rebuild sludge?

### what to measure
- challenge/supersede transaction success on explicit corrections
- old-truth suppression latency
- duplicate-active-truth count after correction
- ghost override count
- generic-extractor vs correction-race count
- false-positive contradiction rate
- committed correction overlay creation count

### pass gate
pass only if:
- old truth is challenged/suppressed immediately on explicit contradiction
- new truth becomes active with exact evidence attached
- correction overlay comes from committed truth, not floating inference
- no duplicate active truth survives the correction path
- false contradiction rate stays low enough to trust the lane

### fail now if
- next-turn truth would still be stale after explicit correction
- correction logic and generic extraction race into parallel truths
- override artifacts exist without ledger-backed mutation

### anti-metrics
- high contradiction-detection count
- eventual eventual consistency without next-turn freshness
- pretty debug logs that do not correspond to committed state

---

## dimension 3 — pack quality

### what we are testing
can Purr produce bounded prompt material that beats Hermes-style flat memory behavior without turning compare into prompt archaeology theater?

### what to measure
- `session_pack` budget compliance (target 500-800, hard cap 1000)
- `turn_delta_pack` budget compliance (target 30-120, hard cap 180)
- `reentry_pack` budget compliance (target 350-650, hard cap 800)
- `proactive_pack` budget compliance (target 120-250, hard cap 350)
- lane slot-cap compliance
- suppression correctness for challenged/stale/superseded truth
- prediction-hint count staying within contract (0-2 max)
- transcript fallback frequency
- compare-log deltas:
  - what Purr included that Hermes baseline missed
  - what Hermes baseline included that Purr correctly suppressed
  - what both included

### pass gate
pass only if:
- packs stay inside hard caps
- stale/challenged truth never lands in hard factual slots
- prediction hints stay tiny
- compare logs show repeated specific wins, not just different wording
- transcript fallback is exceptional, not default behavior

### important observability caveat
because Hermes persisted prompt is only a **partial compare baseline**, score this dimension in two layers:

1. **baseline compare**
   - Purr pack vs Hermes stored cached prompt snapshot
   - good enough for rough overlap/suppression analysis

2. **exact compare** (optional, later)
   - Purr pack vs provider-facing request dump / custom hook capture
   - required only if we need exact full prompt parity claims

### fail now if
- compare output starts acting like a truth source
- evaluation rewards larger packs or fuller prompts
- stored Hermes prompt is treated as exact provider prompt when it is not

### anti-metrics
- bigger prompt = better memory
- more tokens stuffed = stronger recall
- high overlap with Hermes baseline by itself
- using Hermes prompt text as if it were evidence

---

## dimension 4 — recall evidence quality

### what we are testing
does every durable memory claim stay anchored to exact mirrored source text instead of recap sludge?

### what to measure
- percent of memory rows with exact `message_id/window_id/episode_id/span` backpointers
- exact-hit-before-recap compliance rate
- prompt-derived evidence contamination count
- summary-derived evidence contamination count
- child-session hit preservation vs root-collapse recap
- quoted-evidence retrieval success on sampled memories

### pass gate
pass only if:
- sampled memories can always be walked back to exact mirrored source text
- exact excerpt survives ahead of lineage recap
- summary artifacts stay navigation-only
- zero evidence refs point to Hermes prompt text, memory files, or maintenance artifacts

### fail now if
- recall can explain itself but cannot quote exact evidence
- child-session hits keep collapsing into root recap
- summary-only recall is treated as proof

### anti-metrics
- lexical hit count alone
- pretty summaries
- human-readable recap without exact backpointer truth

---

## dimension 5 — review / proactive safety

### what we are testing
once later phases exist,
does Purr verify and text-first with restraint,
or does it turn into needy admin sludge / creepy timing sludge?

### what to measure
- explicit review prompts vs passive confirmation ratio
- `no_signal` outcomes vs contradiction outcomes
- explicit review frequency against caps:
  - max 1 blocking memory check in a reply turn
  - max 1 trailing/light memory check in a reply turn
  - max 1 proactive review ping per day
  - max 3 explicit attempts per memory before heavy cooldown
- proactive `no_act` rate
- repeated veto counts on sensitive topic clusters
- would-have-done logs for review/proactive choices
- challenged/stale truth suppression before proactive scoring

### pass gate
pass only if:
- silence mostly stays `no_signal`, not contradiction
- explicit asking stays sparse and high-value
- proactive scoring is mostly restraint
- repeated veto/no-signal patterns make the system back off instead of escalate
- would-have-done logs show timing quality rather than random activity

### fail now if
- review turns needy
- proactive scoring keeps selecting creepy or badly timed moves
- stale/challenged truth still drives review or proactive behavior

### anti-metrics
- number of review actions
- number of proactive candidates
- engagement bait from pings
- treating any answer rate as proof of good timing

---

## trigger queries / kill signals

these do not all mean instant death,
but they do mean **do not claim success**.

### quality-failure triggers
- contradiction churn: >3 challenge/supersede events on the same `dedupe_key` in 14 days
- evaluator uncertainty cluster: >3 low-confidence evaluator calls on the same family
- repeated user corrections on same `subject_key`
- stale-pack leakage across >3 consecutive pack generations
- proactive veto repeat clusters on same topic
- pattern oscillation: promote/demote cycling on the same memory

### hard kill signals
kill or sharply narrow the dogfood lane if:
- Hermes behavior starts reading from Purr state
- compare lane starts mutating truth
- evidence grounding drifts to prompt artifacts
- origin/lineage tracking keeps drifting after resets/compression
- adapter starts adding measurable latency
- bridge upkeep becomes annoying enough to eat weekly cycles
- 6 weeks pass without clear positive signal from phases 0-1

---

## verdict logic

## valid outputs

### `validated_plumbing`
only allowed if all 5 dimensions pass and no hard kill fired.

### `useful_plumbing_signal`
allowed if some dimensions have strong evidence,
but later phases or enough event volume do not exist yet.

### `insufficient_data`
allowed if the lane is too early to claim anything.

### `failed_boundary`
required if any hard kill signal fires.

---

## what this changes in repo understanding

### it does change
- phase-1 compare must stop pretending Hermes `sessions.system_prompt` is the full exact provider prompt
- scorecards must treat Hermes observability as a bundle, not a single canonical store
- exact cost/prompt claims need stronger capture than SQLite alone

### it does not change
- first build slice stays `memory-ledger`
- dogfood stays a later validation track
- Hermes remains shadow-only
- no visible tool theater
- no reopening of Catnet or Moltbook side lanes

---

## direct conclusion

the missing dogfood problem was not architecture.
it was honesty.

we already knew how to tap Hermes safely.
now the repo also knows how to judge whether that tap is proving anything.

best rule:
**treat Hermes shadow dogfood as a scored observability exercise with hard fail boundaries — not as a vibes machine, not as a prompt-diff hobby, and definitely not as permission to blur Hermes and Purr together.**
