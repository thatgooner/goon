# Purr pattern rollups + proactive preflight + cost-tier contract

## why this note exists
`06` made prediction a real memory lane.
`09` defined a tiny `proactive_pack`.
`15` defined `should_reply_how?` for the next reply.
`18` split hidden cognition into turn-critical, boundary-critical, deferred, and proactive lanes.

that still leaves one builder-sized hole:

**how do raw prediction memories turn into a small, trustworthy, low-cost surface that can decide whether Purr texts first at all?**

right now the repo knows:
- what `pattern_signal`, `open_loop`, and `next_action_candidate` are
- that proactive should be stricter than normal replies
- that the default should usually be `do nothing`
- that notification copy should reveal less than the internal rationale

what it did **not** yet lock was:
- the derived artifacts between raw predictive memory and heartbeat decisions
- the exact `should_text_first?` gate
- the slot contract for `proactive_pack`
- cold-start / cooldown / budget rules
- what gets cut first when cost is tight

without that, builders will do one of two bad things:
- rescore too much raw memory on every wakeup
- or let vague pattern vibes leak into proactive pings

both are wrong.

---

## direct thesis
raw `pattern_signal` rows are **not** a runtime surface.

Purr needs a second layer of **derived predictive artifacts** that are:
- smaller than the ledger
- more stable than one-off predictions
- cheaper to score than full memory scans
- stricter than normal reply-time prediction
- still tied back to exact evidence

call the private proactive gate:

**`should_text_first?`**

job:
1. read a tiny derived surface
2. apply hard vetoes first
3. choose the cheapest valid proactive move if any
4. emit a tiny hidden plan artifact
5. default to `no_act`

strong rule:
**proactive quality should come from better gating, not from more generation.**

another strong rule:
**raw predictive memories may influence proactive scoring, but only derived trusted artifacts may enter the proactive decision surface.**

---

## Hermes lesson that forces this note
Hermes' strongest memory lesson is still discipline:
- frozen hot prompt artifacts are good
- salvage-before-loss is good
- bounded always-on memory is good

but Hermes also shows what not to copy for texting-first behavior:
- periodic nudge theater is not a serious proactive system
- summary-heavy recall is too weak for exact proof
- async-only maintenance leaves timing holes
- prompt-bound sinks drift if they do not share one trust contract

translation for Purr:
- do **not** run generic `maybe save memory now` style loops and pretend that solves timing
- do **not** rescan a whole session/ledger on every heartbeat
- do **not** let a weak summary or stale pattern become the reason for a push notification
- do build compact derived artifacts with exact backpointers and explicit decay

---

## note map
1. design rules
2. canonical derived predictive artifacts
3. rollup promotion / decay contract
4. the `should_text_first?` gate
5. proactive move classes + selection order
6. `proactive_pack` slot contract
7. cost tiers + recompute policy
8. outcomes, cooldowns, and backoff
9. failure modes
10. build acceptance tests

---

## 1. design rules

### rule 1 — proactive is stricter than reply-time prediction
reply shaping can use a weak hint.
texting first cannot.

minimum posture:
- stronger evidence
- fresher timing state
- lower annoyance risk
- harder fail-closed behavior

### rule 2 — the heartbeat reads derived state, not the raw ledger
heartbeat jobs should not fan out across all `pattern_signal` rows.
that is how cost and sludge creep in.

heartbeat should mostly read:
- `pattern_rollup`
- `timing_window`
- `proactive_posture`
- `proactive_candidate`
- cooldown / budget state

### rule 3 — exact evidence still matters
rollups are not permission to become summary-only.

any proactive-eligible artifact must retain:
- source memory ids
- best supporting evidence refs
- last confirming hit
- last contradictory miss

if it cannot point back to proof,
it should not be allowed to drive a ping.

### rule 4 — no-op is the normal result
most wakeups should end in:
- no generation
- no message
- no visible effect

that is not failure.
that is restraint.

### rule 5 — cold-start is conservative
Purr should earn the right to text first.

cold-start stance:
- no playful proactive teasing from thin air
- no inference-heavy check-ins
- only explicit callback-style moves with clear evidence

### rule 6 — challenged truth poisons proactive faster than reply-time behavior
if a driving memory is:
- `challenged`
- `candidate`
- stale beyond its horizon
- contradicted by fresher evidence

then the proactive score should collapse hard.

### rule 7 — free-tier pressure hits frequency before memory integrity
under budget pressure:
- cut wakeup frequency first
- cut cheap-model arbitration second
- cut stronger-model prose third
- do **not** weaken source-event append, evidence storage, or trust gating

memory quality is still the product.

---

## 2. canonical derived predictive artifacts
these are the missing surfaces between the ledger and the heartbeat.

## 2.1 `pattern_rollup`
purpose:
- compress repeated `pattern_signal` hits into one durable behavioral summary
- make timing/value scoring cheap
- keep raw pattern rows out of the heartbeat hot path

example:
- `after 2-3 days of silence, re-entry often starts with apology + meme`
- `late-night re-entry after stress-topic often benefits from light callback, not hard probe`

minimum fields:
- `rollup_id`
- `owner_id`
- `purr_id`
- `rollup_type` (`reentry_pattern | followup_pattern | tone_pattern | timing_pattern | callback_pattern`)
- `source_pattern_ids[]`
- `trigger_signature`
- `predicted_transition`
- `horizon` (`daily | long` for proactive use)
- `support_count`
- `hit_count_30d`
- `miss_count_30d`
- `last_hit_at`
- `last_miss_at`
- `confidence_band`
- `volatility`
- `trust_state`
- `best_evidence_refs[]`
- `decays_at`
- `eligible_for_proactive`

hard rules:
- turn/session-horizon pattern rows do not become proactive rollups by default
- purely mood-guess rollups are reply-shaping only, not ping-driving
- a rollup may summarize many rows, but it must still expose best proof

## 2.2 `timing_window`
purpose:
- say **when** a proactive move is plausible
- separate timing fit from content fit

example:
- `weekday evening re-entry window`
- `24-72h callback window after explicit promise`
- `good chance of response after work, bad chance after midnight`

minimum fields:
- `window_id`
- `owner_id`
- `purr_id`
- `window_type` (`local_hour | silence_gap | daypart | promise_followup | reentry_window`)
- `opens_at_rule`
- `closes_at_rule`
- `timezone_confidence`
- `support_count`
- `success_rate`
- `recent_fail_rate`
- `last_validated_at`
- `expires_at`
- `risk_flags[]`

hard rules:
- if timezone confidence is weak, timing windows may gate down to `no_act`
- no timing window may rely only on guessed sleep/life schedule
- a timing window is not enough on its own; it only says `when maybe`, never `send now`

## 2.3 `proactive_posture`
purpose:
- summarize whether this user should be texted first at all right now
- collapse annoyance, consent, response history, and quiet-state risk into one cheap read surface

minimum fields:
- `owner_id`
- `purr_id`
- `posture_stage` (`cold_start | warming | trusted | cooling_off | suppressed`)
- `text_first_allowed`
- `quiet_hours_rule`
- `recent_response_state` (`positive | neutral | ignored | negative | unknown`)
- `recent_burden_score`
- `negative_feedback_at`
- `last_proactive_sent_at`
- `max_daily_sends`
- `min_spacing_minutes`
- `heavy_cooldown_until`
- `preference_override` (`allow | reduce | block`)

hard rules:
- `suppressed` means no proactive send except maybe critical product/service necessity outside this note's scope
- `cooling_off` should dominate cute opportunity scores
- explicit `stop texting first` style feedback must hit this artifact directly

## 2.4 `proactive_candidate`
purpose:
- a bounded candidate move produced by incremental jobs before the final heartbeat decision
- lets the system rank a few plausible actions instead of improvising from scratch

example:
- callback on explicit promise
- low-key check-in during strong timing window
- memory-backed tease only if trusted and recently rewarded
- review ping for one stale high-leverage fact

minimum fields:
- `candidate_id`
- `owner_id`
- `purr_id`
- `candidate_type` (`callback | check_in | tease_or_roast | review_ping`)
- `driver_refs[]` (open loop / rollup / timing window ids)
- `target_window_id`
- `value_score`
- `risk_score`
- `trust_gate_passed`
- `earliest_send_at`
- `expires_at`
- `dedupe_key`
- `why_now_compact`
- `best_evidence_refs[]`

hard rules:
- candidates are ephemeral and expire fast
- candidates do not authorize sends by themselves
- one candidate should map to one action class only

## 2.5 `proactive_preflight_result`
purpose:
- record what the wakeup actually decided
- make dedupe, audits, and cooldown updates honest

minimum fields:
- `preflight_id`
- `owner_id`
- `purr_id`
- `wakeup_id`
- `decision` (`no_act | send`)
- `chosen_candidate_id`
- `veto_reason` or `selection_reason`
- `budget_state_snapshot`
- `pack_ref`
- `dedupe_key`
- `decided_at`
- `expires_at`

hard rule:
- if a wakeup ends in `no_act`, we still want the reason
- otherwise builders will not know whether the system is disciplined or just broken

---

## 3. rollup promotion / decay contract
this is what keeps predictive memory from turning into landfill.

## 3.1 promotion from raw rows -> `pattern_rollup`
starting thresholds for proactive-eligible rollups:

### daily-horizon rollup
needs all of:
- at least **2 confirming hits**
- on **2 separate days**
- with last hit inside **14 days**
- and no stronger contradictory miss in the same window

### long-horizon rollup
needs all of:
- at least **3 confirming hits**
- across at least **2 weeks**
- with last hit inside **30 days**
- and miss rate not obviously degrading

### never proactive-eligible by default
- one-off `pattern_signal`
- pure mood speculation
- unresolved contradiction clusters
- anything driven mostly by summary text instead of exact evidence refs

## 3.2 `open_loop` special case
`open_loop` can create a proactive candidate earlier than general patterns because it is often explicit unresolved truth.

example allowed early:
- user said they would send something later
- purr/user left a concrete callback thread hanging

example not allowed early:
- vague `they might want comfort later` style inference

## 3.3 candidate creation rules
create a `proactive_candidate` only when all apply:
- at least one trusted driver exists
- timing window is open or about to open
- posture is not `suppressed`
- no duplicate candidate with same `dedupe_key` is active
- expected value beats a conservative floor

## 3.4 decay rules
prediction should decay faster than stable facts.

starting decay posture:
- `proactive_candidate`: hours to 2 days max depending on class
- `timing_window`: expires when local/time gap logic closes or confidence falls
- `pattern_rollup` daily: decay sharply after 14 quiet days without hit
- `pattern_rollup` long: decay after 30 days or repeated misses

## 3.5 miss handling
one miss should not nuke a good pattern.
repeated misses should.

starting rule:
- 1 miss -> lower confidence band
- 2 recent misses -> remove proactive eligibility
- 3 recent misses -> retire or demote rollup until re-earned

## 3.6 negative-feedback handling
if a proactive message lands badly:
- update `proactive_posture` first
- then demote the candidate class or timing window
- then demote the driving rollup if the mismatch was actually conceptual, not just bad timing

that ordering matters.
don't blame the behavioral pattern if the real issue was annoyance budget.

---

## 4. the `should_text_first?` gate
this is the proactive sibling of `should_reply_how?`.

it runs on heartbeat or event-driven wakeups **before** generation.

it reads only:
- top 0-2 active `proactive_candidate` rows
- top 0-1 `open_loop` driver if directly relevant
- top 0-1 `pattern_rollup`
- top 0-1 `timing_window`
- current `proactive_posture`
- budget/cooldown state
- current send surface availability

if that surface is not enough,
the answer is usually `no_act`,
not `go pull more memory forever`.

## 4.1 hard vetoes
any one of these forces `no_act`:
- `text_first_allowed = false`
- explicit negative preference or active suppression
- heavy cooldown active
- quiet-hours rule active and no strong explicit callback reason
- all driving memory is `candidate`, `challenged`, or stale beyond horizon
- dedupe key already active/recently attempted
- user already re-entered or replied before send
- no trustworthy target window / surface
- budget exhausted
- timezone confidence too weak for time-sensitive send

## 4.2 soft scoring questions
if not vetoed, ask in order:

### Q1 — is there a trusted reason to appear?
valid reasons:
- explicit open loop with good callback value
- strong timing hit on a previously rewarded contact pattern
- due review of high-leverage truth with low-friction phrasing
- relationship-backed playful move with earned trust

### Q2 — is the timing actually favorable?
check:
- local hour / daypart
- recent silence gap
- recent burden / annoyance score
- whether the opportunity is already going stale

### Q3 — what is the cheapest valid move?
prefer the least intrusive action that still captures the value.

### Q4 — is it worth spending budget now?
if expected value is merely decent, keep the budget.

## 4.3 output enum
first-pass outputs:
- `no_act`
- `send_callback`
- `send_check_in`
- `send_review_ping`
- `send_tease_or_roast`

hard rule:
no multi-send planning.
one wakeup, one decision.

## 4.4 tiny plan artifact
if the gate says yes, emit:
- `planned_action`
- `primary_driver_ref`
- `target_window_id`
- `risk_flags[]`
- `caution_note`
- `copy_visibility_tier`
- `dedupe_key`
- `expires_at`

if that artifact gets too large,
the gate is doing generation work by accident.

---

## 5. proactive move classes + selection order
private proactive should use a smaller, safer move set than full chat.

## 5.1 selection order
use the cheapest valid move first:
1. `no_act`
2. `callback`
3. `check_in`
4. `review_ping`
5. `tease_or_roast`

why this order:
- callback is anchored to explicit unresolved truth
- check-in can stay light
- review pings can help but break the spell if overused
- tease/roast needs the most earned trust and the sharpest timing

## 5.2 class rules

### `callback`
use when:
- an explicit open loop exists
- value is clear
- timing is acceptable

examples:
- promised follow-up
- unfinished ask with obvious continuity value

forbidden when:
- loop is stale and unsupported
- callback would drag unrelated baggage back in

### `check_in`
use when:
- timing window is strong
- relationship posture allows it
- message can stay low-claim and low-pressure

forbidden when:
- only rationale is speculative mood reading
- recent ignored or negative proactive outcome exists

### `review_ping`
use when:
- a high-leverage memory is due for light confirmation
- the phrasing can stay natural
- review budget is not already spent

forbidden when:
- it feels like admin disguised as personality
- there is no real upside to asking now

### `tease_or_roast`
use when:
- strong relationship trust exists
- the exact kind of teasing has landed before
- timing window and burden posture both say yes

forbidden when:
- it leans on insecurity or pain without strong earned context
- the same joke class recently missed
- the rationale depends on private inference flexing

---

## 6. `proactive_pack` slot contract
`09` locked the token envelope.
this note locks the actual slots.

## 6.1 budget target
- target: **120-250 tokens**
- hard cap: **350 tokens**

## 6.2 slot caps
`proactive_pack` may contain at most:

### slot A — primary driver
- **1 item max**
- either:
  - one explicit `open_loop`
  - or one `pattern_rollup`

### slot B — timing fit
- **1 `timing_window` max**
- compact form only

### slot C — posture / burden summary
- **1 compact `proactive_posture` summary**
- include cooldown / recent response state / quiet-state outcome

### slot D — chosen candidate
- **1 `proactive_candidate` max**
- include class, expiry, and one-line `why_now_compact`

### slot E — caution
- **0-1 caution block**
- only if there is a real risk flag the generator must respect

### slot F — evidence micro-ref
- **0-1 tiny evidence ref**
- only when an explicit promise or exact phrase materially improves safety/precision
- not a transcript dump

## 6.3 explicit exclusions
never put these in `proactive_pack`:
- more than one driver rationale
- raw transcript snippets beyond the tiny evidence ref
- low-trust `next_action_candidate` rows
- challenged memories
- multiple joke ideas
- freeform planner essays
- vector similarity explanations

## 6.4 visibility rule
notification preview should reveal less than the in-chat message.

so the pack should carry:
- internal reason in compact form
- plus a `copy_visibility_tier` like `low | medium`

not:
- the whole behavioral rationale verbatim

---

## 7. cost tiers + recompute policy
this is where the system stays sane.

## 7.1 tier A — no-model / read-model only
default heartbeat path.

allowed work:
- read current derived artifacts
- apply vetoes
- compute cheap scores
- decide `no_act` most of the time

this should handle the majority of wakeups.

## 7.2 tier B — cheap-model arbitration
only use when:
- two candidate classes are close
- tone class is ambiguous
- a natural review phrasing needs a tiny arbitration step

hard rule:
cheap-model arbitration may pick between candidates.
it may not reopen the whole memory search problem.

## 7.3 tier C — final message generation
only after the gate says yes.

generation may use:
- `proactive_pack`
- current tone/profile constraints
- selected visibility tier

it should **not** fetch broader history unless the chosen class explicitly requires the tiny evidence ref.

## 7.4 recompute triggers
update derived proactive artifacts on:
- new source event that hits a predictive memory lane
- open-loop creation / resolution
- proactive outcome closure
- local-time/daypart rollover for active users
- explicit preference or burden feedback

avoid:
- full-ledger rescans on every heartbeat
- global nightly recompute for inactive users
- re-embedding everything just to send one ping

## 7.5 budget degradation order
when cost gets tight:
1. reduce heartbeat frequency
2. narrow event-driven wakeups to high-value triggers
3. disable tier B arbitration for low-value classes
4. cut playful/tease proactive before callback/review
5. shorten generation budget
6. only last: suppress proactive entirely for some cohorts

never cut:
- source-event durability
- trust gating
- cooldown enforcement
- evidence backpointers

---

## 8. outcomes, cooldowns, and backoff
proactive quality is not just send/no-send.
it needs explicit aftercare.

## 8.1 outcome classes
after a proactive send, close outcome as one of:
- `positive_reply`
- `neutral_reply`
- `seen_no_reply`
- `ignored`
- `dismissed`
- `negative_reaction`
- `timing_bad`
- `canceled_before_send`
- `null` (could not evaluate honestly)

## 8.2 first-pass cooldown defaults
starting architecture defaults:
- any proactive send spacing: **minimum 12h**
- same-class spacing: **24h**
- after `ignored`: **48h cooling**
- after `dismissed` or `negative_reaction`: **7d heavy cooldown**
- after two poor outcomes in 14 days: posture -> `cooling_off`

these are not sacred forever numbers.
they are conservative v1 defaults.

## 8.3 posture updates by outcome
- `positive_reply` -> slight trust lift for that action class and timing window
- `neutral_reply` -> small/no change
- `seen_no_reply` -> tiny burden increase
- `ignored` -> bigger burden increase and class cooldown
- `dismissed` / `negative_reaction` -> posture downgrade first
- `timing_bad` -> demote timing window before demoting relationship class
- `canceled_before_send` -> no penalty if the user naturally re-entered first

## 8.4 class-specific limits
starting daily limits:
- `callback`: max **1/day**
- `check_in`: max **1/day**
- `review_ping`: max **2/week**
- `tease_or_roast`: max **3/week**, and only in `trusted`

shared rule:
these are sub-budgets, not reasons to spend the whole allowance.

## 8.5 cold-start policy
### `cold_start`
allowed:
- explicit callback only
- maybe one light review ping if directly user-beneficial and clearly grounded

not allowed:
- tease/roast
- inference-heavy check-in

### `warming`
allowed:
- callback
- occasional check-in if prior response history is not negative

### `trusted`
allowed:
- all classes, still under cooldown/budget rules

### `cooling_off` / `suppressed`
allowed:
- normally `no_act`
- maybe explicit callback later if the user reopens the lane first

---

## 9. failure modes

### 9.1 pattern landfill
raw predictive rows keep spawning candidates forever.

fix:
- rollup thresholds
- decay
- dedupe keys
- expiration on candidates
- miss-driven demotion

### 9.2 heartbeat fanout cost blowup
every wakeup scans too much history.

fix:
- derived artifacts only
- incremental updates on event commit
- no-model first

### 9.3 creepy specificity
notification reveals more than the user should feel Purr safely knows right then.

fix:
- visibility tiers
- tiny proactive pack
- caution flags
- reveal less in preview than in chat

### 9.4 stale timing confidence
old routine keeps firing after the user's life changed.

fix:
- recent miss pressure
- timezone confidence checks
- proactive eligibility removal before factual deletion

### 9.5 playful class bypass
cute/roast messages bypass the intended caution because they feel fun.

fix:
- separate class budgets
- trusted-stage requirement
- stronger negative-feedback penalties for tease/roast misses

### 9.6 summary-only permission
a summary artifact says the user `usually` does something, but exact proof is thin.

fix:
- rollups keep best evidence refs
- summary without evidence never drives proactive

---

## 10. build acceptance tests
this note is only useful if builders can test it.

## must pass
1. **weak pattern, no explicit loop -> `no_act`**
   - one fresh `pattern_signal` alone must not create a proactive send.

2. **explicit promise + valid window -> `send_callback` allowed**
   - one explicit open loop with good timing may create a callback even in `warming`.

3. **challenged driver -> forced `no_act`**
   - if the main driver is challenged or stale, no proactive send survives preflight.

4. **duplicate wakeups -> one deduped result**
   - repeated heartbeat/event wakeups must not send duplicates with the same `dedupe_key`.

5. **negative reaction -> heavy cooldown**
   - a bad proactive outcome must downgrade posture and suppress the class for days, not minutes.

6. **budget pressure cuts playful frequency before core callback integrity**
   - tightening cost should remove low-value proactive classes before weakening trust/evidence logic.

7. **preview safer than body**
   - preview copy must expose less rationale than the in-chat message.

8. **user re-entry race cancels stale send**
   - if the user naturally returns before dispatch, the proactive candidate should close as `canceled_before_send`.

9. **inactive users do not get full-ledger rescans**
   - heartbeat must read derived surfaces only unless a rare high-value exception is explicitly approved.

10. **cold-start cannot roast first**
   - no `tease_or_roast` while posture is `cold_start` or `warming` without prior positive evidence for that class.

---

## direct conclusion
Purr should not text first because a model improvised a cute hunch.

Purr should text first only when:
- a trusted driver exists
- timing is genuinely favorable
- posture/budget allow it
- one cheap action class clearly beats silence
- the system can explain the decision with compact evidence-backed artifacts

that gives us the missing bridge:
- raw prediction memory in the ledger
- derived rollups for cheap/private scoring
- a real `should_text_first?` gate
- a tiny proactive pack
- conservative budgets and cooldowns

so the product can feel sharp without becoming:
- spammy
- creepy
- prompt-bloated
- or fake-smart

that is the lane.
