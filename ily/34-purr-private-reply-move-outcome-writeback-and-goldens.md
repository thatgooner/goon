# Purr private reply-move outcome writeback + goldens

## why this note exists

`ily/15` locked the hidden `should_reply_how?` planner.
that note already said the repo needs:
- `hit | miss | null` semantics for predictive signals
- `helped | neutral | hurt` semantics for the chosen move
- real meanings for `response_value`, `timing_value`, `pack_hit`, and `pack_miss`

but it still left one seam too implied:

**what exactly gets written back after a reply plan plays out, where does that writeback live, and who closes the horizon if the user never gives a clean immediate answer?**

that matters because `feels one step ahead` will rot fast if the system cannot tell the difference between:
- the signal being right
- the move being good
- the prompt-visible admission being worth it

`ily/18`, `ily/19`, `ily/20`, `ily/31`, and `ily/33` narrowed the missing shape:
- hidden runtime lanes already exist
- proactive already has typed preflight/result artifacts
- review already has typed outcomes + trust transitions
- goldens already cover major memory seams
- Hermes runtime repair improves perceived continuity, but Hermes still does **not** have a serious durable per-reply outcome loop to steal directly

this note closes that reply-time writeback seam.

it does **not** open build mode.
it does **not** move the repo out of research-first posture.

---

## direct verdict

### one-line answer
**reply-time calibration should use a hybrid contract: typed backend-only outcome artifacts are canonical, while compact ledger events mirror only the row-level state changes that matter.**

### translation
- do **not** infer reply quality from transcript text or provider finish reasons
- do **not** collapse signal truth, move usefulness, and prompt-admission quality into one score
- do write:
  - a durable `reply_move_plan` before generation
  - typed `prediction_outcome` artifacts after horizon closure
  - typed `move_outcome` artifacts after the move can be judged
  - compact ledger feedback events only where memory-row stats or pack policy actually changed

### strongest rule
**`prediction_outcome`, `move_outcome`, and `pack_outcome` are 3 different planes. if they collapse into one plane, the system will teach itself the wrong lesson.**

---

## Hermes lesson that forces this note

latest Hermes pass on this machine sharpened one useful negative lesson:

Hermes has good runtime choreography:
- next-turn recall prefetch
- continuation repair
- compression salvage
- resume-by-artifact behavior

but Hermes still does **not** durably track reply-quality outcomes in the way Purr now needs.

what Hermes does persist is mostly:
- transcripts
- session metadata
- finish reasons
- message/tool counts
- prompt/session artifacts

what Hermes does **not** persist cleanly is:
- whether a predictive signal was right
- whether the selected reply tactic helped
- whether a prompt-visible hint was worth surfacing

translation for Purr:
- runtime repair/continuity tricks are worth stealing
- reply-quality calibration is **not** already solved there
- transport/runtime flags like truncation, retry, or `finish_reason` must never be mistaken for reply-outcome truth

hard warning:
**a repaired reply can feel continuous without teaching anything about whether the hidden planner made a good decision.**

---

## the seam this note closes

before this note, `ily/15` already gave us:
- `reply_move_plan`
- move classes
- visibility tiers
- horizon semantics
- rough writeback intent

but 5 things were still loose:

1. whether outcome writeback lives in `memory_events`, typed maintenance artifacts, or both
2. whether `pack_hit/miss` means signal truth, move quality, or prompt-admission quality
3. where horizon closure belongs when the user does not immediately resolve the prediction
4. how `response_value` and `timing_value` change without double-counting
5. which exact private-reply golden scenarios should exist beyond the general memory suite in `ily/31`

this note freezes all 5.

---

## direct contract

## 1. hybrid writeback, not transcript inference

canonical rule:
- **typed outcome artifacts** carry the rich reply-calibration detail
- **ledger row updates** carry the durable memory-state consequences
- **compact `memory_events`** mirror those consequences so the event trail still explains the row state

bad version:
- read the next few transcript turns later
- guess whether the reply was good
- backfill one vague score

right version:
- create the plan explicitly
- close the plan through a typed outcome path
- mutate stats through a bounded writeback contract
- keep transcript history separate from evaluation artifacts

## 2. one plan can produce multiple outcomes

for one `reply_move_plan`:
- there may be **1 move outcome**
- there may be **0-3 prediction outcomes** if up to 3 driver memories/signals were involved
- there may be **0-3 pack outcomes** only for the drivers that actually entered a prompt-visible admission surface

hard rule:
**one plan does not imply one score.**

## 3. move closure and prediction closure are allowed to happen at different times

example:
- the move `clarify_now` may look immediately helpful or annoying
- the underlying prediction may still need 2 more turns to resolve as `hit | miss | null`

so:
- move evaluation can close earlier
- prediction evaluation closes on its own declared horizon

---

## canonical durable artifacts

## 1. `reply_move_plan` stays durable

`ily/15` already made `reply_move_plan` real.
`ily/16` already put it inside the durable ledger truth plane.

this note keeps that.

minimum role:
- freeze what move was chosen
- freeze which memory/signal rows drove it
- freeze what visibility tier was used
- give later outcome artifacts something stable to point back to

hard rule:
**if a reply was shaped by the planner, the plan id must exist before generation. no post-hoc `we probably meant this` repair.**

## 2. new typed artifact: `prediction_outcome`

purpose:
- answer **whether a driving signal was right inside its declared horizon**

minimum fields:
- `prediction_outcome_id`
- `plan_id`
- `owner_id`
- `purr_id`
- `driver_memory_id`
- `driver_class` (`open_loop | pattern_signal | next_action_candidate | mixed_driver_ref`)
- `horizon_kind` (`turn | session | daily | long`)
- `outcome_kind` (`hit | miss | null`)
- `null_reason` (`no_reentry | superseded_by_correction | boundary_split | interrupted_by_stronger_event | insufficient_evidence`)
- `closing_event_id` (nullable)
- `closing_window_id`
- `best_evidence_refs[]`
- `closed_at`
- `dedupe_key`

hard rule:
- this artifact is about **signal truth**, not tactic quality
- `null` is not a soft spelling of `miss`

## 3. new typed artifact: `move_outcome`

purpose:
- answer **whether the chosen primary move helped the reply**

minimum fields:
- `move_outcome_id`
- `plan_id`
- `owner_id`
- `purr_id`
- `primary_move`
- `outcome_kind` (`helped | neutral | hurt`)
- `observed_via` (`same_turn_reaction | next_turn_followup | later_turn_resolution | boundary_close`)
- `closing_event_id` (nullable)
- `best_evidence_refs[]`
- `outcome_reason`
- `closed_at`
- `dedupe_key`

hard rule:
- this artifact is about **tactic usefulness**, not whether the underlying signal was true
- a move can hurt even when the signal hit

## 4. `pack_outcome` stays a ledger plane, not a new brain

`pack_outcome` is still real,
but it does **not** need its own heavyweight artifact family in v1.

canonical implementation posture:
- keep prompt-admission feedback as compact ledger feedback on the surfaced driver row
- use existing `memory_events.pack_hit | pack_miss`
- store the richer reference in `delta_json`, including:
  - `plan_id`
  - `admission_surface`
  - `prediction_outcome_id` or `move_outcome_id` if relevant

allowed `admission_surface` values:
- `session_pack`
- `turn_overlay_hint`
- `hidden_instruction`

hard rule:
**if a signal shaped routing only and never entered a model-visible admission surface, it may get `prediction_outcome` and `move_outcome`, but it gets no `pack_outcome`.**

---

## exact plane split

| plane | question | scope | canonical write surface | updates | not responsible for |
| --- | --- | --- | --- | --- | --- |
| `prediction_outcome` | was the underlying signal correct inside its horizon? | per driver memory/signal | typed artifact | `hit_rate`, `miss_rate`, `last_hit_at`, `last_miss_at`, promotion/decay eligibility | move quality, prompt-admission quality |
| `move_outcome` | did the chosen primary move help the reply? | per `reply_move_plan` | typed artifact | `response_value`, some `timing_value` adjustments, move-class calibration | signal truth, pack admission |
| `pack_outcome` | was prompt-visible admission of this signal worth it? | per surfaced driver/hint | `memory_events.pack_hit | pack_miss` + `delta_json` refs | pack selection weight, pack policy hints, admission restraint | signal truth, tactic quality |

hard translation:
- `prediction_outcome` teaches **truth calibration**
- `move_outcome` teaches **tactic calibration**
- `pack_outcome` teaches **prompt-admission calibration**

---

## horizon-closure ownership

## 1. turn/session closures belong to deferred maintenance

owner:
- deferred-lane `prediction calibration worker`

job:
- after a new committed event lands, inspect pending reply plans whose turn/session horizons may now be resolvable
- close `prediction_outcome` and/or `move_outcome` if the evidence is sufficient

why here:
- the hot reply path should not wait around to grade itself
- closure should read committed later evidence, not speculative runtime vibes

## 2. daily/long expiry and honest nulls belong to heartbeat

owner:
- proactive-lane `horizon closer`

job:
- when a daily/long horizon expires without enough honest evidence, close the prediction as `null`
- if appropriate, apply small decay or eligibility downgrade without pretending a miss happened

why here:
- no visible chat may arrive to close the loop
- the system still needs a durable answer instead of infinite unresolved predictions

## 3. explicit correction can early-close stale plans

if a fresher explicit correction lands before horizon resolution:
- invalidate the stale plan immediately
- close affected prediction outcomes as `null`, not fake `miss`, with `null_reason = superseded_by_correction`
- close move outcome only if the move itself can already be judged

hard rule:
**fresher committed truth beats pending planner bets.**

## 4. boundary events may force honest nulls

allowed boundary-driven null reasons:
- `boundary_split`
- `no_reentry`
- `interrupted_by_stronger_event`
- `insufficient_evidence`

forbidden behavior:
- silently leaving plans unresolved forever
- auto-calling every unresolved case a miss

---

## idempotency + replay safety

reply-outcome writeback must be replay-safe,
just like review outcomes in `ily/20`.

starting posture:
- one `reply_move_plan` -> one `plan_id`
- one move closure attempt -> one `move_outcome.dedupe_key`
- one driver + one horizon closure -> one `prediction_outcome.dedupe_key`
- one prompt-visible admission result -> one `pack_hit/miss` mirror event for that admission instance

recommended closure key shape:
- move: `plan_id + outcome_kind + closing_event_id_or_boundary_key`
- prediction: `plan_id + driver_memory_id + horizon_kind + closing_event_id_or_expiry_bucket`
- pack: `plan_id + driver_memory_id + admission_surface + closing_event_id_or_boundary_key`

hard rule:
**retrying a closure worker must not double-increment hit/miss counts or drift `response_value` twice.**

---

## writeback semantics for `response_value` and `timing_value`

## 1. `response_value`

meaning:
- how often using this kind of signal actually improved the reply move

primary owner:
- `move_outcome`

starting rule:
- `helped` -> raise `response_value` a little
- `neutral` -> no change or tiny decay only if this class repeatedly burns budget for no gain
- `hurt` -> lower `response_value`

hard rule:
**do not let raw signal truth update `response_value` by itself. a signal can be true and still produce a bad move.**

## 2. `timing_value`

meaning:
- how often the signal was useful at this horizon and this moment

shared owner:
- `prediction_outcome` decides whether the timing expectation was broadly right
- `move_outcome` can sharpen the local moment judgment if the move landed badly because timing was off

starting rule:
- `prediction hit` -> raise `timing_value` modestly for that horizon
- `prediction miss` -> lower `timing_value` for that horizon
- single `null` -> usually no major change
- repeated `null` at the same horizon -> small decay or lower proactive eligibility
- `move hurt` with clear mistiming -> extra small `timing_value` penalty

hard rule:
**`timing_value` is not just `hit_rate` with a different name. it is about whether the signal was useful now, not only whether it was eventually sort-of true.**

## 3. `hit_rate` and `miss_rate`

owner:
- `prediction_outcome` only

rule:
- `null` does not count as hit or miss
- repeated null-heavy patterns may still reduce eligibility through separate decay logic

## 4. `pack_hit` and `pack_miss`

owner:
- prompt-visible admission only

rule:
- update only when the signal actually entered `session_pack`, `turn_overlay_hint`, or `hidden_instruction`
- do **not** use `pack_hit/miss` for routing-only plans
- do **not** let `pack_hit/miss` mutate truth/confidence directly

---

## recommended minimal writeback order

when a reply-planner outcome closes:

1. append/commit the closing evidence event if needed
2. create `prediction_outcome` rows for each resolved driver
3. create `move_outcome` row if the move can be judged
4. compute per-driver calibration deltas
5. mutate `memory_items` stats (`last_hit_at`, `last_miss_at`, `response_value`, `timing_value`, eligibility/decay fields if needed)
6. write compact mirror events on affected rows
7. write `pack_hit/miss` only for prompt-visible admission surfaces
8. invalidate/update derived artifacts only if thresholds are crossed
9. request overlay or pack patch only if current-window freshness actually depends on it

hard rule:
**the transcript is never the place where evaluation gets "written back." evaluation lives in typed artifacts and ledger mutations.**

---

## recommended event mirror posture

`ily/13` already gives:
- `pack_hit`
- `pack_miss`

that is not enough by itself for reply-time calibration.

recommended additions if event enums expand:
- `prediction_hit`
- `prediction_miss`
- `prediction_null`
- `planner_move_helped`
- `planner_move_neutral`
- `planner_move_hurt`

if builders keep event enums smaller,
then at minimum:
- the typed outcome artifact is canonical
- every changed row must still get one compact mirror event pointing at that artifact via `delta_json`

hard rule:
**row stats may not change without an explainable event trail.**

---

## private reply-planner goldens

these extend `ily/31` with planner-specific seams.

## 1. weak prediction stays backend-only

### setup
- moderate/weak `pattern_signal`
- planner sees it, but it does not justify prompt-visible admission

### pass condition
- reply stays normal or routing-only
- no pack hint
- no `pack_hit/miss`
- later closure may still produce `prediction_outcome` and/or `move_outcome`

### failure it catches
- prediction scrapbook
- prompt sludge from signals that should have stayed invisible

---

## 2. signal hit, move hurt

### setup
- prediction correctly anticipates the user's next move/topic
- chosen primary move is too interruptive or off-tone

### pass condition
- `prediction_outcome = hit`
- `move_outcome = hurt`
- `response_value` drops
- truth/hit stats do not lie just because the tactic was bad

### failure it catches
- collapsing truth quality and tactic quality into one score

---

## 3. signal miss, move neutral

### setup
- planner predicts a follow-up that never comes
- reply still lands fine as a clean ordinary answer

### pass condition
- `prediction_outcome = miss`
- `move_outcome = neutral`
- `timing_value` drops more than `response_value`

### failure it catches
- over-penalizing a non-damaging move because the signal was wrong

---

## 4. pack miss, prediction hit

### setup
- a signal was strong enough to be surfaced in a prompt-visible hint
- the hint lands as intrusive or unnecessary
- later turns show the underlying signal was actually true

### pass condition
- `prediction_outcome = hit`
- `pack_outcome = pack_miss`
- pack admission weight drops without rewriting signal truth

### failure it catches
- treating prompt visibility as proof that the model should have seen it that way

---

## 5. explicit correction kills stale pending prediction

### setup
- old plan is still open
- explicit correction or contradiction lands before the original horizon closes

### pass condition
- stale driver is invalidated immediately
- closure becomes `null` with `null_reason = superseded_by_correction`
- no stale prediction shapes the next reply

### failure it catches
- same-session stale sharpness
- fake miss penalties for superseded plans

---

## 6. no re-entry yields honest null

### setup
- planner opened a daily-horizon expectation
- user never re-enters inside the honest window

### pass condition
- heartbeat/horizon closer writes `prediction_outcome = null`
- no forced visible question is created just to resolve the metric

### failure it catches
- infinite unresolved predictions
- spammy pings created only for evaluation convenience

---

## 7. duplicate closure is replay-safe

### setup
- same closure worker or retry path fires twice

### pass condition
- exactly one durable outcome artifact per dedupe key
- no double stat update
- no duplicate `pack_hit/miss`

### failure it catches
- retry inflation
- fake signal quality improvement from duplicate writes

---

## 8. one plan with many drivers keeps planes honest

### setup
- one plan uses up to 3 drivers:
  - one open loop
  - one pattern signal
  - one next-action candidate

### pass condition
- one `move_outcome`
- separate `prediction_outcome` rows per driver as needed
- `pack_outcome` only for the driver(s) actually surfaced prompt-side

### failure it catches
- one giant blended score hiding which driver actually paid off

---

## what must stay backend-only

keep these invisible in v1:
- `reply_move_plan`
- `prediction_outcome`
- `move_outcome`
- dedupe keys
- horizon closure workers
- `response_value`, `timing_value`, `hit_rate`, `miss_rate`
- planner reasoning about why a signal was suppressed
- pack-admission calibration internals

forbidden user-facing energy:
- `i predicted you were going to...`
- `my move score says...`
- `i ran a planner and it was a hit`
- dashboard-admin memory grading

strong rule:
**the user should feel the sharpness, not see the calibration machinery.**

---

## build-order impact

### what this changes
- it closes the missing reply-time calibration seam left open by `ily/15`
- it gives later builders a concrete answer on `typed artifacts vs memory_events vs hybrid`
- it expands the golden suite with reply-planner-specific seams instead of vague `did it feel smart` tests

### what this does not change
- it does **not** change slice order
- it does **not** unpark build mode
- it does **not** turn the reply planner into a visible feature

hard translation:
**this sharpens the quality bar for future packer/planner/runtime work. it does not change the repo's research-first gate.**

---

## short verdict

Purr should not learn from replies by staring at transcript vibes.

it should learn through 3 clean planes:
- was the signal right?
- was the move good?
- was prompt-visible admission worth it?

that means:
- typed backend-only outcome artifacts
- compact ledger mirrors
- deferred/heartbeat horizon closure
- replay-safe writeback
- planner-specific goldens

that is the clean way to make private memory prediction get sharper over time
without turning the system into prompt sludge, fake mind-reading, or self-delusion.
