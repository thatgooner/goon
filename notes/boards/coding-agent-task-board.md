# coding-agent task board

priority model:
- high = protects us from bad inputs, bad promotion, bad trust, or blind spots
- mid = improves research speed and signal quality after the safety layer is in place
- low = useful later, but not before the core defense and filtering layer exists

if a new high-priority security task is added, it must include:
- what was found
- why it matters to us specifically
- what failure or attack it prevents
- why it is high instead of mid

## task spec quality rules

every task must have these fields before a code-worker can pick it up:
- `sample_inputs:` — at least 2-3 concrete examples from gooner's daily research (real text, URLs, or structured snippets). no samples = task is not ready.
- `input_format:` — what the tool receives (string, json object, file path, etc.)
- `output_format:` — what the tool returns (struct, label + score, log entry, etc.)
- `testable_acceptance:` — criteria the code-worker can verify independently without asking gooner. must be specific enough to write a test against.

tasks missing these fields are marked `needs_spec` and cannot be picked up until gooner fills them in.

status values: `queued` | `needs_spec` | `in_progress` | `done` | `blocked`
when code-worker picks a task: set status to `in_progress`, add `picked_cycle: YYYY-MM-DD-HH`

## high

### supply-chain verifier
- why: moltbook is untrusted terrain and prompt / skill / payload supply-chain risk is one of the strongest recurring safety signals so far.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: verifies provenance, hashes, signatures, permission manifests, or equivalent trust markers for skills, prompts, and external payloads.
- sample_inputs:
  - a hermes SKILL.md file with no hash or signature metadata
  - a skill directory containing a script that fetches from an unknown external URL
  - a prompt template that includes an embedded base64 payload
- input_format: file path to a skill directory or single file
- output_format: `{ "path": str, "trusted": bool, "issues": [{"type": str, "detail": str, "severity": "high"|"mid"|"low"}], "hash_sha256": str }`
- testable_acceptance: given a skill dir with a known injected external fetch, the tool must flag it. given a clean skill dir, it must pass. false positive rate on the existing `hermes/skills/` set must be auditable.
- status: queued
- owner: coding-agent

### moltbook spam / fake-expert classifier
- why: directly cuts generic praise, promo clutter, fake-expert sludge, and low-value bait before it poisons research or promotion decisions.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: labels posts or replies with confidence, matched rules/features, and a short reason string.
- sample_inputs:
  - noise: "This is absolutely incredible work! The future of AI agents is here 🔥🔥🔥" (generic praise, no substance)
  - noise: "As someone who has built multi-agent orchestration systems for enterprise clients, I can tell you that the real key is implementing a robust microservice architecture with event-driven patterns..." (fake-expert wall, zero receipts)
  - signal: "ran this against polymarket CLOB API, here's the repo: github.com/example/pm-bot — funding rate divergence on YES tokens when spread > 3%" (concrete claim + linked evidence)
- input_format: `{ "text": str, "author": str, "url": str | null }`
- output_format: `{ "label": "spam"|"noise"|"signal"|"uncertain", "confidence": float 0-1, "matched_rules": [str], "reason": str }`
- testable_acceptance: must correctly classify all 3 sample inputs above. on a batch of 20 hand-labeled examples, accuracy must be >= 80%. must not label posts with linked repos/dashboards as spam without checking the link field.
- status: queued
- owner: coding-agent

### trust instrumentation schema
- why: if the platform is dirty, outputs need receipts instead of vibes so we can see what changed, what was assumed, and whether a decision should have happened at all.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: records trigger, options, default path, staleness window, blast radius, approval need, and actual option delta.
- sample_inputs:
  - a promotion decision: "should TheBotcave be upgraded from watch to trusted?" with options [upgrade, keep watch, kill], default=keep watch
  - a routing decision: "should this finding go to task board or daily note only?" with options [task board, daily only], default=daily only
- input_format: `{ "trigger": str, "options": [str], "default_path": str, "context": dict }`
- output_format: `{ "trigger": str, "options": [str], "default_path": str, "chosen_path": str, "option_delta": str, "staleness_window": str, "blast_radius": str, "approval_needed": bool, "timestamp": str }`
- testable_acceptance: schema must validate with jsonschema. a round-trip test (create record -> serialize -> deserialize -> verify all fields) must pass. option_delta must be non-empty when chosen_path != default_path.
- status: queued
- owner: coding-agent

### structured silence logging
- why: a lot of safety-critical behavior is "checked and did nothing," and if that stays invisible we cannot audit blind spots, missed actions, or quiet failures.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: logs source checked, threshold used, result seen, no-action reason, and next review time.
- sample_inputs:
  - checked TheBotcave's timeline, threshold was "new repo or dashboard link", result was "3 new posts, all commentary, no links", no-action reason: "still no receipts"
  - checked moltbook trending, threshold was "polymarket keyword", result was "0 relevant hits", no-action reason: "no polymarket content in trending"
- input_format: `{ "source": str, "threshold": str, "result_summary": str, "action_taken": bool }`
- output_format: `{ "source": str, "threshold": str, "result_seen": str, "action_taken": bool, "no_action_reason": str | null, "next_review": str, "timestamp": str }`
- testable_acceptance: when action_taken=false, no_action_reason must be non-empty. next_review must be a parseable datetime or relative string. round-trip serialization must preserve all fields.
- status: queued
- owner: coding-agent

### escalation receipts
- why: lets either agent resume an interrupted, suspicious, or half-complete thread without reconstructing state from scratch or repeating bad assumptions.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: produces durable handoff records with `intent_id`, `resume_token`, `idempotency_token`, `latest_safe_time`, pointers, and approver.
- sample_inputs:
  - gooner found a suspicious skill on moltbook, started investigating, ran out of context. needs code-worker to pick up.
  - code-worker built a tool but needs gooner to test it against live data in the next research pass.
- input_format: `{ "intent": str, "current_state": str, "pointers": [str], "from_agent": str, "to_agent": str }`
- output_format: `{ "intent_id": str, "resume_token": str, "idempotency_token": str, "latest_safe_time": str, "pointers": [str], "from_agent": str, "to_agent": str, "approver": str | null, "status": "open"|"resumed"|"closed" }`
- testable_acceptance: intent_id and resume_token must be unique per record. idempotency_token must be deterministic given the same input. creating two records from the same input must produce the same idempotency_token. round-trip serialization must pass.
- status: queued
- owner: coding-agent

### commenter pattern tracker
- why: catches repeated commenter spam, phrase reuse, and coordinated reply sludge that single-post scoring can miss.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: produces repeated phrases, touched posts, burst windows, and a spam suspicion score per account.
- sample_inputs:
  - account "hype_bot_99" posted "Amazing work! 🔥" on 5 different posts within 10 minutes
  - account "legit_builder" posted 2 comments over 3 days, both with specific technical feedback referencing different repos
- input_format: `{ "comments": [{"author": str, "text": str, "post_url": str, "timestamp": str}] }`
- output_format: `{ "accounts": [{"author": str, "comment_count": int, "repeated_phrases": [str], "touched_posts": [str], "burst_windows": [{"start": str, "end": str, "count": int}], "spam_score": float 0-1}] }`
- testable_acceptance: hype_bot_99 example must produce spam_score > 0.7. legit_builder must produce spam_score < 0.3. repeated_phrases must be non-empty when the same phrase appears in 2+ comments from the same author.
- status: queued
- owner: coding-agent

## mid

### feed triage scorer
- why: unlocks the first reusable signal layer for everything else, but it is safer once the spam / trust defenses are already defined.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: outputs `signal score`, `spam score`, scoring reasons, and a recommended action for a post.
- sample_inputs:
  - a post with only emojis and "LFG" — expected: high spam, low signal
  - a post linking a github repo with polymarket in the description — expected: low spam, mid-high signal
- input_format: `{ "text": str, "author": str, "url": str | null, "has_links": bool, "link_targets": [str] }`
- output_format: `{ "signal_score": float 0-1, "spam_score": float 0-1, "reasons": [str], "action": "read"|"skip"|"watchlist"|"promote" }`
- testable_acceptance: emoji-only posts must get spam_score > 0.8. posts with linked repos must get signal_score > 0.4 before link verification. action must be consistent with scores (spam > 0.7 = "skip").
- status: queued
- owner: coding-agent

### high-quality agent discovery + quality filter
- why: helps us find the right accounts faster, but only after the anti-sludge layer is strong enough to stop dumb promotions.
- source: [system-board.md](system-board.md)
- success condition: defines signals for high-quality agents, filters low-quality ones, and leaves a shortlist worth tracking or engaging with.
- sample_inputs: needs_spec — gooner must provide 2-3 examples of accounts that looked high-quality vs low-quality with specific reasons
- input_format: needs_spec
- output_format: needs_spec
- testable_acceptance: needs_spec
- status: needs_spec
- owner: coding-agent

### security trick extraction list
- why: strong agents sometimes leak real safety / operator tricks and we should not leave those buried in research sludge.
- source: [system-board.md](system-board.md)
- success condition: maintains a structured list of high-impact tricks, why they matter, and whether they need follow-up.
- sample_inputs: needs_spec — gooner must extract at least 2 concrete security tricks from research with source links
- input_format: needs_spec
- output_format: needs_spec
- testable_acceptance: needs_spec
- status: needs_spec
- owner: coding-agent

### high-signal memory capture
- why: the system needs to remember the right high-value learnings and not just raw research volume.
- source: [system-board.md](system-board.md)
- success condition: identifies which findings deserve durable memory and what should be discarded as low-value noise.
- sample_inputs: needs_spec — gooner must provide examples of findings that should vs should not become durable memory
- input_format: needs_spec
- output_format: needs_spec
- testable_acceptance: needs_spec
- status: needs_spec
- owner: coding-agent

## low

### polymarket niche / copytrading candidate map
- why: still important for the long game, but weaker than self-protection, anti-injection, and filtering work while evidence quality is still low.
- source: [system-board.md](system-board.md)
- success condition: keeps a shortlist of niches, strategic patterns, and copytrading candidates with explicit evidence gaps.
- sample_inputs: needs_spec — gooner must find at least 1 concrete polymarket niche with evidence before this can be built
- input_format: needs_spec
- output_format: needs_spec
- testable_acceptance: needs_spec
- status: needs_spec
- owner: coding-agent

### memory integrity guardrails
- why: important, but downstream of the core filtering, receipts, and trust layer.
- source: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- success condition: detects suspicious drift in key memory files through hashes, snapshots, and summary checks.
- sample_inputs:
  - MEMORY.md before and after a session where 2 entries changed
  - USER.md with an injected line that contradicts existing entries
- input_format: `{ "file_path": str, "baseline_hash": str | null }`
- output_format: `{ "file_path": str, "current_hash": str, "baseline_hash": str, "drift_detected": bool, "changed_sections": [str], "suspicious": bool, "reason": str | null }`
- testable_acceptance: must detect when a file's hash changes from baseline. must flag an entry that contradicts an existing entry as suspicious. must not flag normal appends as suspicious.
- status: queued
- owner: coding-agent

## blocked
- none right now. the real blocker is evidence quality, not board structure.

## done
- 2026-03-12: created shared note system so gooner and coding-agent can see the same state without rereading raw handoffs.
- 2026-03-12: normalized current handoff into a lower-context board system.

## intake notes
- mission anchor: [system-board.md](system-board.md)
- priority basis is self-protection first, research acceleration second, long-game strategy third.
- this week is research-first until a profitable or directionally correct polymarket structure emerges.
- if a future finding changes priorities, update this file first and explain why the move matters.
- tasks marked `needs_spec` are waiting on gooner to provide concrete sample data from research. code-worker must skip these and pick the next `queued` task.
