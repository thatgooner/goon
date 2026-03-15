# Purr private-chat move planner + prediction calibration contract

## why this note exists
`06` defined prediction-shaped memory.
`08` defined lifecycle / contradiction / review rules.
`09` defined pack artifacts and budget discipline.
`12` defined the packer-facing selection surface.
`13` defined pack-hit / pack-miss events.
`14` defined the intake/runtime write path.

that solved most of the memory spine.
what is still loose is the last private 1:1 control loop:

**how does predictive memory change the next reply without turning into prompt sludge, creepy overclaim, or fake sharpness?**

right now the repo can say:
- what a `pattern_signal` is
- what an `open_loop` is
- what a `next_action_candidate` is
- what packs exist
- how mutations commit safely

but it still does not explicitly define the hidden planner that converts those signals into:
- answer directly
- clarify now
- lightly pre-empt the likely follow-up
- callback an open loop
- stay quiet about a weak prediction
- do nothing special

that gap matters because `feels one step ahead of me` will not come from shoving more prediction text into the prompt.
it will come from **better move selection**.

---

## direct thesis
Purr needs a private 1:1 gate that mirrors Catnet's `should_act?` gate.

call it:

**`should_reply_how?`**

job:
- read a tiny set of trusted current signals
- decide whether prediction should change the move at all
- choose the cheapest valid move that improves the reply
- emit a tiny hidden plan artifact
- keep weak prediction backend-only

strong rule:
**predictive memory should usually compile into a move decision, not into extra prompt prose.**

bad version:
- pack 6 speculative hints
- let generation free-associate around them
- act impressed when the model sounds vaguely insightful

right version:
- decide one move
- carry at most one prediction hint if it materially changes the move
- leave everything else in the ledger/read model

---

## Hermes lesson that forces this note
Hermes' strongest idea is not `memory files`.
it is that memory only reaches the model through controlled prompt artifacts.

latest code-grounded pass on this machine sharpens that:
- the visible prompt stays frozen while durable memory can change underneath it
- salvage at boundaries matters more than periodic nudge theater
- background flush paths can lose richness if they only replay visible chat text
- exact hit evidence gets weaker when recall collapses child hits into root summaries

translation for Purr:
- keep the stable pack discipline
- do **not** let prediction leak into the prompt as unbounded commentary
- let predictive memory change reply behavior through a narrow planner artifact
- treat calibration as ledger feedback, not vibes inside generation

---

## note map
1. design rules
2. the `should_reply_how?` gate
3. reply move classes
4. planner inputs + precedence
5. planner artifact contract
6. prediction visibility tiers
7. hit / miss / null calibration rules
8. planner feedback loop
9. failure modes
10. build acceptance tests

---

## 1. design rules

### rule 1 — explicit truth outranks predictive help
priority order stays:
1. live corrections / contradictions
2. active boundaries
3. stable preferences / hard facts
4. open loops
5. relationship texture
6. strong pattern signals
7. next-action candidates

prediction may bias move choice.
it may not override cleaner truth.

### rule 2 — one primary move per reply
private chat should not secretly run 5 tactics at once.

planner output should choose:
- exactly **1 primary move**
- optionally **1 secondary caution**
- optionally **1 hidden prediction hint**

if the plan needs a paragraph to explain itself, it is not compact enough.

### rule 3 — cheapest valid move first
same posture as Catnet:
- if a normal direct reply is enough, do that
- if a tiny callback improves it, do that
- if a clarification is necessary, ask
- if no predictive move clears threshold, do nothing special

sharpness should come from restraint too.

### rule 4 — backend-only by default
most predictive objects should never become prompt-visible.

default posture:
- `pattern_signal` -> ranking/helper first
- `next_action_candidate` -> planner/helper first
- `open_loop` -> often pack-visible because it is real unresolved truth

### rule 5 — calibration must be outcome-based
`hit_rate`, `miss_rate`, `response_value`, `timing_value`, `pack_hit`, and `pack_miss` cannot stay decorative fields.

they need explicit semantics:
- what was predicted
- by when
- what counts as confirmation
- what counts as miss
- what counts as inconclusive/null

without that, Purr will hallucinate a sense of pattern quality.

### rule 6 — prompt budget should pay for moves, not self-explanations
if a predictive signal does not change the next move, it should stay out of the pack.

---

## 2. the `should_reply_how?` gate
this runs after turn-critical memory mutations commit and before final reply generation.

it reads:
- current `session_pack`
- current `live_override_patch` if any
- top-ranked `open_loop` items
- top-ranked `pattern_signal` items
- top-ranked `next_action_candidate` items
- latest user message/event
- reply safety/boundary state

then it asks 4 things:

### Q1 — does prediction need to affect this reply at all?
if no, output `direct_reply` and stop.

examples where answer is no:
- user asked a clean factual question
- no open loop is relevant
- predictions are low-confidence or stale
- prediction would only add theater, not utility

### Q2 — is there an unresolved truth/boundary issue that must dominate?
if yes, prediction gets demoted.

examples:
- explicit user correction just landed
- a challenged memory would make a callback risky
- the likely move is actually to clarify a contradiction

### Q3 — is there one bounded move that improves the reply?
examples:
- short callback to an unresolved loop
- softer tone because a stress-pattern is active
- answer + pre-empt one likely follow-up
- ask now because the likely ambiguity is high-cost

### Q4 — is the expected value high enough to spend the move?
if not, keep the reply normal.

important:
`should_reply_how?` is not a content generator.
it is a move selector.

---

## 3. reply move classes
these are the first-pass move types for private 1:1 chat.
keep the set small.

### 3.1 `direct_reply`
default.
use when prediction adds no real value.

### 3.2 `direct_reply_plus_callback`
answer the current message, but lightly thread in one unresolved loop.

good for:
- promised follow-up
- unfinished thread that is clearly relevant now

bad for:
- dragging old unresolved junk into unrelated chat

### 3.3 `direct_reply_plus_preempt`
answer normally, then pre-empt one likely next ask/topic pivot.

good for:
- repeated procedural follow-ups
- obvious next-step questions
- known pattern where user immediately asks part B after part A

hard rule:
pre-emption must be narrow.
no sprawling fake-mindreading.

### 3.4 `clarify_now`
ask a short clarification because ambiguity is high-cost and prediction indicates the wrong assumption will land badly.

good for:
- known contradiction-sensitive dimension
- unstable preference / boundary zone
- high-leverage fact that changes the whole response

### 3.5 `tone_shift`
content stays similar, but delivery changes because trusted relationship/pattern state says the wrong tone would miss.

examples:
- more deadpan, less wholesome
- lighter touch because current pattern suggests user is touchy
- more direct because the user is clearly asking for a clean answer

### 3.6 `loop_probe`
ask a low-friction follow-up about an open loop that seems ready to resolve.

strong use:
- the user re-entered near the loop topic
- the value of resolution is high
- annoyance/callback budget allows it

### 3.7 `prediction_suppressed`
planner explicitly decides that prediction exists but should stay backend-only.

this is important.
silence is a valid move.

---

## 4. planner inputs + precedence

## 4.1 minimum planner inputs
minimum hidden selection surface for one reply:
- `latest_user_intent`
- `active_boundary_flags`
- `active_correction_flags`
- `relevant_open_loops[]`
- `relevant_pattern_signals[]`
- `relevant_next_action_candidates[]`
- `reply_context_risk`
- `annoyance_budget_state`
- `prediction_confidence_floor`

## 4.2 precedence rules

### hard vetoes
any of these should force prediction demotion or suppression:
- relevant memory is `challenged`, `rejected`, or `superseded`
- relevant signal is stale and no fresh evidence supports it
- the move would surface a private inference more strongly than warranted
- prediction conflicts with an explicit live correction
- planner would need more than one speculative step to justify the move

### soft scoring
if not vetoed, planner scores:
- **response_value** — would using this signal make the reply more useful / more aligned / less fake?
- **timing_value** — is this the right turn/window for it?
- **confidence** — how trustworthy is the underlying signal now?
- **specificity** — is this one narrow move or a vague vibe cloud?
- **intrusion_risk** — will this feel sharp or creepy?

## 4.3 open-loop priority rule
active open loops outrank pure prediction.

why:
- open loops are real unresolved truth
- next-action candidates are operational guesses

so if both are present:
- prefer `direct_reply_plus_callback` or `loop_probe`
- suppress a weaker speculative pre-emption

## 4.4 correction-first rule
if a live correction landed this turn:
- planner may still choose a move class
- but the move must be consistent with the override patch
- no old prediction may survive against a committed correction

---

## 5. planner artifact contract
this should be a tiny internal artifact.
not a user-visible feature.

## 5.1 canonical `reply_move_plan`
minimum fields:
- `plan_id`
- `owner_id`
- `purr_id`
- `window_id`
- `source_event_id`
- `primary_move`
- `secondary_caution` (`none | avoid_overclaim | avoid_reopening | ask_briefly | keep_light`)
- `driving_memory_ids[]`
- `driving_signal_class` (`correction | boundary | open_loop | pattern_signal | next_action_candidate | mixed`)
- `move_reason`
- `prediction_visibility` (`none | backend_only | pack_hint`)
- `expires_after_turns`
- `created_at`

### hard caps
- `driving_memory_ids`: max 3
- `primary_move`: exactly 1
- `secondary_caution`: max 1
- `pack_hint`: max 1 short hint

## 5.2 `move_reason` posture
should be tiny and operational.

examples:
- `recent explicit correction; do not rely on old preference row`
- `active open loop is directly relevant to the user ask`
- `trusted turn-horizon candidate suggests one likely follow-up; pre-empt briefly`
- `prediction too weak for prompt exposure; keep normal reply`

bad version:
- mini-essay about the user's psyche

## 5.3 pack integration rule
`reply_move_plan` should affect generation in one of three ways:
1. no prompt change — move is implemented by response planner/routing only
2. one compact hidden instruction line — only if generation needs it
3. one compact prediction hint in pack — only if necessary and budget-eligible

preferred order is 1 -> 2 -> 3.

---

## 6. prediction visibility tiers
not all predictive signals deserve the same visibility.

### tier A — backend-only
use for:
- weak `pattern_signal`
- broad mood guesses
- low-confidence `next_action_candidate`
- long-horizon speculative tendencies

allowed effect:
- ranking
- planner suppression
- future calibration

not allowed:
- direct prompt phrasing
- explicit callback

### tier B — planner-visible, not prompt-visible
use for:
- moderate-confidence signals that help choose the move but do not need to be stated

example:
- known pattern suggests the user will immediately ask part B
- planner chooses `direct_reply_plus_preempt`
- prompt does not need a separate prediction bullet

### tier C — compact pack hint
use only when:
- the signal is trusted
- the move materially depends on it
- the hint can fit in one short line
- intrusion risk is low

example:
- `likely follow-up: user wants the concrete next step, not more theory`

hard cap:
- 0-1 preferred
- 0-2 absolute max only if one is an open-loop callback and the other is a narrow turn-horizon prediction

### tier D — never-visible
forbidden prompt exposure:
- low-confidence private inferences
- sensitive long-horizon behavioral patterns
- anything that sounds like surveillance narration

---

## 7. hit / miss / null calibration rules
this is the most missing contract seam in the repo right now.

## 7.1 why null matters
not every non-hit is a miss.

sometimes:
- the user never reached the predicted horizon
- the conversation pivoted because Purr itself changed the path
- a signal was irrelevant this turn, not wrong globally

so we need 3 outcomes:
- `hit`
- `miss`
- `null`

`null` should not punish as hard as a miss.

## 7.2 horizon semantics

### turn horizon
prediction window: next 1-3 user/assistant turns.

**hit** when:
- predicted follow-up/topic/move happens inside the horizon
- or the chosen reply move clearly prevented an expected ambiguity and the next turn validates that direction

**miss** when:
- opposite move/topic occurs inside the horizon
- or the planner exposed a prediction hint that clearly lands wrong

**null** when:
- conversation ends before the horizon resolves
- another stronger event interrupts the path

### session horizon
prediction window: current active chat window.

**hit** when:
- the predicted loop/topic/mood lane emerges before the window closes

**miss** when:
- the session resolves in a materially different lane despite enough opportunity

**null** when:
- session ends too early
- boundary event/re-entry splits the window before enough evidence

### daily horizon
prediction window: later same day / warm re-entry.

**hit** when:
- expected re-entry/callback/opportunity lands in that day window

**miss** when:
- the opposite behavior repeats or the timing expectation clearly fails

**null** when:
- user never re-enters that day or channel conditions invalidate timing

### long horizon
prediction window: repeated weekly rhythm.

**hit** when:
- multiple new events continue the same stable pattern

**miss** when:
- repeated counter-evidence accumulates

**null** when:
- there is simply not enough fresh evidence yet

## 7.3 move-level feedback
calibration should attach to both:
- the underlying memory item
- the planner move outcome

because a signal can be right while the move was wrong.

example:
- `next_action_candidate` was right that the user wanted a follow-up
- but `clarify_now` was still the wrong move because it felt too interruptive

so log separately:
- **signal outcome** (`hit | miss | null`)
- **move outcome** (`helped | neutral | hurt`)

## 7.4 first-pass field semantics

### `hit_rate`
share of resolved evaluations for that signal that ended `hit`.

### `miss_rate`
share of resolved evaluations for that signal that ended `miss`.

### `response_value`
how often using this kind of signal improved the reply.

### `timing_value`
how often the signal was useful **at this horizon** and **at this moment**, not just generally true.

### `pack_hit`
selected into a pack or move plan and later judged helpful.

### `pack_miss`
selected into a pack or move plan and later judged unhelpful / wrong / intrusive.

important:
- `pack_hit` is not identical to truth
- it means **good selection outcome**

---

## 8. planner feedback loop

## 8.1 when to write feedback
allowed triggers:
- turn resolved inside horizon
- session closed
- daily timing window closed
- explicit user correction/refutation
- strong implicit validation (`yes exactly`, direct follow-up match, resolved loop)

## 8.2 what should be written
for each resolved plan/signal:
- `prediction_evaluation` event with `hit | miss | null`
- optional `move_evaluation` event with `helped | neutral | hurt`
- updates to `last_hit_at` / `last_miss_at`
- bounded adjustment to `response_value` / `timing_value`
- TTL decay or promotion decision

## 8.3 conservative adjustment rule
avoid overfitting fast.

starting posture:
- single hit should not immediately promote a weak pattern to hot-pack truth
- repeated misses should demote faster than repeated hits promote
- long-horizon signals need more evidence to rise
- intrusive move classes should require stronger `timing_value`

## 8.4 packer/planner handshake
selection quality should improve from both sides:
- packer learns which signals were worth surfacing
- planner learns which move classes paid off

that means future build should keep distinct event reasons like:
- `pack_hit`
- `pack_miss`
- `planner_move_helped`
- `planner_move_hurt`
- `prediction_hit`
- `prediction_miss`

v1 can collapse some of these if needed.
but the logic distinction should stay clear in the notes.

---

## 9. failure modes this contract is meant to stop

### 9.1 prediction scrapbook
bad:
- the pack fills with pattern trivia

brake:
- one primary move
- backend-only default
- 0-1 preferred hint rule

### 9.2 fake mind-reading
bad:
- Purr narrates speculative private inferences like facts

brake:
- tiered visibility
- intrusion-risk veto
- `prediction_suppressed` as a valid move

### 9.3 same-session stale sharpness
bad:
- a correction commits
- old prediction still shapes the next reply

brake:
- correction-first rule
- committed override patch outranks prediction

### 9.4 calibration theater
bad:
- fields like `hit_rate` exist but no one defines evaluation windows

brake:
- explicit hit/miss/null semantics per horizon
- signal outcome separated from move outcome

### 9.5 planner thrash
bad:
- each tiny signal change causes a different secret tactic every turn

brake:
- one primary move
- cheapest-valid-move-first
- weak predictions stay internal

### 9.6 creepy proactive bleed
bad:
- private chat prediction logic quietly turns into overreaching first-text behavior

brake:
- private-chat planner and proactive planner stay related but separate
- proactive still uses stricter preflight from `09`

---

## 10. build acceptance tests
if code-worker later builds this lane, the first implementation should only count as good if it can pass checks like:

- a reply can be generated with **no** prediction hint when prediction is not worth it
- a trusted open loop can change the move without bloating the pack
- an explicit correction suppresses stale predictive moves on the very next reply
- the planner emits one compact `reply_move_plan`, not a pile of hidden tactics
- `pattern_signal` and `next_action_candidate` can stay backend-only and still influence selection
- turn/session/daily/long horizons have explicit resolved outcomes (`hit | miss | null`)
- `pack_hit` / `pack_miss` update from selection outcomes rather than vague intuition
- intrusive/creepy predictions fail the visibility gate even if confidence looks high
- free-tier pressure reduces model strength or proactive frequency before core move-planning integrity

---

## implication for the repo/task board
this note does **not** move the project out of research-first mode.

it closes a real remaining architecture gap between:
- predictive memory kinds
- bounded pack design
- runtime mutation safety
- actual 1:1 reply behavior

translation for later build order:
- `memory-context-packer` is still about bounded prompt artifacts
- `feedback-orchestrator` now needs a narrower sub-lane: **private-chat move planner**
- future implementation should treat `should_reply_how?` as a small hidden selection layer, not as a feature-dash UI

---

## short verdict
Purr should not feel one step ahead because it stuffs more guesses into the prompt.

it should feel one step ahead because:
- memory signals are structured
- weak prediction stays invisible
- one compact planner chooses the move
- corrections outrank guesses
- calibration teaches the system which signals actually pay off

that is the clean way to make `i remember everything` feel sharp instead of performative.
