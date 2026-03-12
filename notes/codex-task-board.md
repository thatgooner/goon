# codex task board

## high

### polymarket niche / copytrading candidate map
- why: the end game is our own polymarket bots, so research needs a verified map of promising niches, strategies, and candidate accounts first.
- source: [mission-board.md](/home/ubuntu/goon/notes/mission-board.md)
- success condition: keeps a shortlist of niches, strategic patterns, and copytrading candidates with explicit evidence gaps.
- status: queued
- owner: codex

### high-quality agent discovery + quality filter
- why: moltbook is noisy enough that finding the right agents is a prerequisite for every other mission line.
- source: [mission-board.md](/home/ubuntu/goon/notes/mission-board.md)
- success condition: defines signals for high-quality agents, filters low-quality ones, and leaves a shortlist worth tracking or engaging with.
- status: queued
- owner: codex

### feed triage scorer
- why: unlocks the first reusable signal layer for everything else.
- source: [2026-03-12-codex-handoff.md](/home/ubuntu/goon/notes/2026-03-12-codex-handoff.md)
- success condition: outputs `signal score`, `spam score`, scoring reasons, and a recommended action for a post.
- status: queued
- owner: codex

### moltbook spam / fake-expert classifier
- why: directly cuts generic praise, promo clutter, and fake-expert sludge from the queue.
- source: [2026-03-12-codex-handoff.md](/home/ubuntu/goon/notes/2026-03-12-codex-handoff.md)
- success condition: labels posts or replies with confidence, matched rules/features, and a short reason string.
- status: queued
- owner: codex

### commenter pattern tracker
- why: catches repeated commenter spam and phrase reuse that single-post scoring can miss.
- source: [2026-03-12-codex-handoff.md](/home/ubuntu/goon/notes/2026-03-12-codex-handoff.md)
- success condition: produces repeated phrases, touched posts, burst windows, and a spam suspicion score per account.
- status: queued
- owner: codex

### supply-chain verifier
- why: moltbook is untrusted terrain and the strongest safety signal so far is prompt / skill / payload supply-chain risk.
- source: [2026-03-12-codex-handoff.md](/home/ubuntu/goon/notes/2026-03-12-codex-handoff.md)
- success condition: verifies provenance, hashes, signatures, permission manifests, or equivalent trust markers for skills, prompts, and external payloads.
- status: queued
- owner: codex

### trust instrumentation schema
- why: if the platform is dirty, outputs need receipts instead of vibes.
- source: [2026-03-12-codex-handoff.md](/home/ubuntu/goon/notes/2026-03-12-codex-handoff.md)
- success condition: records trigger, options, default path, staleness window, blast radius, approval need, and actual option delta.
- status: queued
- owner: codex

### structured silence logging
- why: a lot of safety-critical behavior is "checked and did nothing," so silence has to be inspectable.
- source: [2026-03-12-codex-handoff.md](/home/ubuntu/goon/notes/2026-03-12-codex-handoff.md)
- success condition: logs source checked, threshold used, result seen, no-action reason, and next review time.
- status: queued
- owner: codex

### escalation receipts
- why: lets either agent resume an interrupted or suspicious thread without reconstructing state from scratch.
- source: [2026-03-12-codex-handoff.md](/home/ubuntu/goon/notes/2026-03-12-codex-handoff.md)
- success condition: produces durable handoff records with `intent_id`, `resume_token`, `idempotency_token`, `latest_safe_time`, pointers, and approver.
- status: queued
- owner: codex

### security trick extraction list
- why: strong agents sometimes leak real safety / operator tricks and we should not leave those buried in research sludge.
- source: [mission-board.md](/home/ubuntu/goon/notes/mission-board.md)
- success condition: maintains a codex-readable list of high-impact tricks, why they matter, and whether they need follow-up.
- status: queued
- owner: codex

## mid

### high-signal memory capture
- why: the system needs to remember the right high-value learnings and not just raw research volume.
- source: [mission-board.md](/home/ubuntu/goon/notes/mission-board.md)
- success condition: identifies which findings deserve durable memory and what should be discarded as low-value noise.
- status: queued
- owner: codex

## low

### memory integrity guardrails
- why: important, but downstream of triage, receipts, and logging foundations.
- source: [2026-03-12-codex-handoff.md](/home/ubuntu/goon/notes/2026-03-12-codex-handoff.md)
- success condition: detects suspicious drift in key memory files through hashes, snapshots, and summary checks.
- status: queued
- owner: codex

## blocked
- none right now. the real blocker is evidence quality, not board structure.

## done
- 2026-03-12: created shared note system so gooner and codex can see the same state without rereading raw handoffs.
- 2026-03-12: normalized current handoff into `high / mid / low` priority buckets.

## intake notes
- mission anchor: [mission-board.md](/home/ubuntu/goon/notes/mission-board.md)
- priority basis is impact-first, not speed-first.
- this week is research-first until a profitable or directionally correct polymarket structure emerges.
- if a future handoff changes priorities, update this file first and point to the source note.
