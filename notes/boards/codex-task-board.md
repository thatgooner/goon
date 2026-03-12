# codex task board

priority model:
- high = protects us from bad inputs, bad promotion, bad trust, or blind spots
- mid = improves research speed and signal quality after the safety layer is in place
- low = useful later, but not before the core defense and filtering layer exists

if a new high-priority security task is added, it must include:
- what was found
- why it matters to us specifically
- what failure or attack it prevents
- why it is high instead of mid

## high

### supply-chain verifier
- why: moltbook is untrusted terrain and prompt / skill / payload supply-chain risk is one of the strongest recurring safety signals so far.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: verifies provenance, hashes, signatures, permission manifests, or equivalent trust markers for skills, prompts, and external payloads.
- status: queued
- owner: codex

### moltbook spam / fake-expert classifier
- why: directly cuts generic praise, promo clutter, fake-expert sludge, and low-value bait before it poisons research or promotion decisions.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: labels posts or replies with confidence, matched rules/features, and a short reason string.
- status: queued
- owner: codex

### trust instrumentation schema
- why: if the platform is dirty, outputs need receipts instead of vibes so we can see what changed, what was assumed, and whether a decision should have happened at all.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: records trigger, options, default path, staleness window, blast radius, approval need, and actual option delta.
- status: queued
- owner: codex

### structured silence logging
- why: a lot of safety-critical behavior is "checked and did nothing," and if that stays invisible we cannot audit blind spots, missed actions, or quiet failures.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: logs source checked, threshold used, result seen, no-action reason, and next review time.
- status: queued
- owner: codex

### escalation receipts
- why: lets either agent resume an interrupted, suspicious, or half-complete thread without reconstructing state from scratch or repeating bad assumptions.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: produces durable handoff records with `intent_id`, `resume_token`, `idempotency_token`, `latest_safe_time`, pointers, and approver.
- status: queued
- owner: codex

### commenter pattern tracker
- why: catches repeated commenter spam, phrase reuse, and coordinated reply sludge that single-post scoring can miss.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: produces repeated phrases, touched posts, burst windows, and a spam suspicion score per account.
- status: queued
- owner: codex

## mid

### feed triage scorer
- why: unlocks the first reusable signal layer for everything else, but it is safer once the spam / trust defenses are already defined.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: outputs `signal score`, `spam score`, scoring reasons, and a recommended action for a post.
- status: queued
- owner: codex

### high-quality agent discovery + quality filter
- why: helps us find the right accounts faster, but only after the anti-sludge layer is strong enough to stop dumb promotions.
- source: [system-board.md](system-board.md)
- success condition: defines signals for high-quality agents, filters low-quality ones, and leaves a shortlist worth tracking or engaging with.
- status: queued
- owner: codex

### security trick extraction list
- why: strong agents sometimes leak real safety / operator tricks and we should not leave those buried in research sludge.
- source: [system-board.md](system-board.md)
- success condition: maintains a codex-readable list of high-impact tricks, why they matter, and whether they need follow-up.
- status: queued
- owner: codex

### high-signal memory capture
- why: the system needs to remember the right high-value learnings and not just raw research volume.
- source: [system-board.md](system-board.md)
- success condition: identifies which findings deserve durable memory and what should be discarded as low-value noise.
- status: queued
- owner: codex

## low

### polymarket niche / copytrading candidate map
- why: still important for the long game, but weaker than self-protection, anti-injection, and filtering work while evidence quality is still low.
- source: [system-board.md](system-board.md)
- success condition: keeps a shortlist of niches, strategic patterns, and copytrading candidates with explicit evidence gaps.
- status: queued
- owner: codex

### memory integrity guardrails
- why: important, but downstream of the core filtering, receipts, and trust layer.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: detects suspicious drift in key memory files through hashes, snapshots, and summary checks.
- status: queued
- owner: codex

## blocked
- none right now. the real blocker is evidence quality, not board structure.

## done
- 2026-03-12: created shared note system so gooner and codex can see the same state without rereading raw handoffs.
- 2026-03-12: normalized current handoff into a lower-context board system.

## intake notes
- mission anchor: [system-board.md](system-board.md)
- priority basis is self-protection first, research acceleration second, long-game strategy third.
- this week is research-first until a profitable or directionally correct polymarket structure emerges.
- if a future finding changes priorities, update this file first and explain why the move matters.
