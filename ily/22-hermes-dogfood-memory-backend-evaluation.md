# Hermes dogfood memory backend evaluation

## why this note exists

Research on the Purr memory system is now deep enough that the next question is not just "how do we build it in Purr?"
It is also:

1. should memory updates stay mostly deterministic, or should a stronger reasoning/judge layer sit inside the memory loop for ambiguous decisions?
2. should we dogfood the Purr memory backbone inside Hermes first, using real conversations, before wiring it into the actual Purr product?

This note is not the answer.
It is the question handoff for code-worker.

---

## current user/product context

- Ilyas is talking to Hermes right now on Telegram.
- This means there is already a live, repeated, real-user conversation surface.
- Because of that, Hermes is a serious dogfood candidate for testing the memory spine before direct Purr integration.
- The goal would **not** be to turn Hermes into Purr.
- The goal would be to test whether the Purr memory backend behaves correctly on real conversations.

Important boundary:
- Hermes dogfood = memory engine testbed
- Purr = final creature/product

Do not collapse those into one thing.

---

## question 1 — algorithm vs judge/subagent

The current architecture is strongly contract-driven:
- append source event first
- extract memory candidates
- detect contradictions/corrections
- write into ledger with evidence
- build a bounded pack
- later run review / proactive jobs

That suggests a mostly deterministic backbone.

But some decisions are obviously not clean rule work.
Examples:
- is this a real contradiction, a joke, or a one-off exception?
- should this pattern be promoted from weak signal to trusted pattern?
- is this stale, superseded, or still valid but temporarily challenged?
- would this proactive move land, or would it feel creepy?
- is this worth explicit review, or should silence be treated as no-signal and left alone?

So the real question is:

### what should stay deterministic?
Likely candidates:
- source-event append
- idempotency
- evidence backpointers
- exact state writes
- unique constraints / mutation transactions
- suppression rules after explicit contradiction
- pack slot caps / hard budgets

### what might need a judge layer?
Likely candidates:
- contradiction interpretation in ambiguous language
- pattern promotion / decay decisions
- stale vs superseded vs exception judgments
- review timing taste
- proactive creepiness veto
- low-confidence memory audit / merge review

Code-worker should answer:
- should this judge be a subagent, a single in-process reasoning call, or some narrower structured evaluator?
- where exactly in the runtime should that judgment happen?
- which parts must **never** depend on agentic judgment?
- how do we keep the system debuggable if agentic judgment exists?

---

## question 2 — Hermes-first dogfood before direct Purr build

There is now a strong product argument for testing the memory backend inside Hermes first.

Why it is attractive:
- real conversations already exist
- same user is already talking regularly
- failures become visible early
- easier to debug the memory spine before Purr UI/world/cat behavior layers exist
- can validate correction handling, stale truth, pack quality, and memory drift on live usage

But there are obvious risks:
- Hermes and Purr are not the same product
- Hermes should not accidentally absorb the full Purr creature logic
- test harness logic can leak into product assumptions
- dogfood can become a permanent side quest if the scope is not tight

So code-worker should answer:

### is Hermes dogfood a good idea?
Direct yes/no/partial answer.

### if yes, what exactly gets integrated first?
Suggested layers to evaluate:
1. shadow source-event logging + ledger writes
2. candidate extraction + evidence refs
3. contradiction/correction handling
4. read-only pack generation for comparison
5. turn-delta override for corrections
6. later: review lane
7. latest/last: proactive lane

### what should explicitly stay out of the first Hermes dogfood pass?
Examples:
- full Purr persona/product behavior changes
- Catnet
- public-safe/social memory
- market logic
- visible memory dashboards
- heavy user-facing review UI

### what are the minimum success signals?
Examples:
- corrections stop going stale in the next reply
- pack suggestions are clearly better than naive memory stuffing
- low-confidence junk does not flood hot memory
- evidence backtracking works
- stale/superseded transitions are inspectable
- proactive is not enabled before core memory quality is proven

### what are the kill signals?
Examples:
- too much latency on live chat
- agentic memory loop becomes nondeterministic sludge
- too many wrong promotions into confirmed memory
- hard-to-debug memory mutations
- Hermes/Purr boundary gets muddy

---

## what code-worker should produce

A compact but sharp recommendation answering:

1. **Backbone vs judge split**
- what remains strict/rule-driven
- what can be agentic
- what runtime form the agentic part should take

2. **Hermes dogfood recommendation**
- yes / no / partial
- why

3. **If yes, phased rollout**
- phase 0
- phase 1
- phase 2
- phase 3
with explicit scope boundaries

4. **Instrumentation / debug posture**
- what to log
- how to compare old vs new memory behavior
- how to inspect errors safely

5. **Build-order impact**
- does this change `memory-ledger -> extractor -> packer -> feedback-orchestrator`?
- or does it only change where we test those slices first?

---

## current leaning from gooner side

Not a final answer, but the current instinct is:
- memory backbone should stay mostly deterministic
- ambiguous/high-leverage decisions can use a narrower judge layer
- Hermes-first dogfood sounds promising if it stays clearly scoped as backend-memory testing, not as "turn Hermes into Purr"

Code-worker should pressure-test that instinct instead of rubber-stamping it.
