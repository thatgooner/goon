# coding-agent task board

read `weekly-missions.md` first. every task here must serve an active weekly mission.

priority model:
- high = directly serves this week's missions (M1-M4), has full spec, ready to build
- parked = valid work but not this week. do not pick up.

## task spec quality rules

every buildable task must have:
- `sample_inputs:` — at least 2-3 concrete examples. no samples = not ready.
- `input_format:` — what the tool receives
- `output_format:` — what the tool returns
- `testable_acceptance:` — criteria code-worker can verify independently

status values: `queued` | `in_progress` | `done` | `blocked`
when code-worker picks a task: set status to `in_progress`, add `picked_cycle: YYYY-MM-DD-HH`

---

## high — build this week

### moltbook spam / fake-expert classifier
- mission: M3 (quality filter)
- why: cuts generic praise, promo clutter, fake-expert sludge before it poisons research.
- sample_inputs:
  - noise: "This is absolutely incredible work! The future of AI agents is here 🔥🔥🔥" (generic praise, no substance)
  - noise: "As someone who has built multi-agent orchestration systems for enterprise clients, I can tell you that the real key is implementing a robust microservice architecture with event-driven patterns..." (fake-expert wall, zero receipts)
  - signal: "ran this against polymarket CLOB API, here's the repo: github.com/example/pm-bot — funding rate divergence on YES tokens when spread > 3%" (concrete claim + linked evidence)
- input_format: `{ "text": str, "author": str, "url": str | null }`
- output_format: `{ "label": "spam"|"noise"|"signal"|"uncertain", "confidence": float 0-1, "matched_rules": [str], "reason": str }`
- testable_acceptance: must correctly classify all 3 sample inputs above. on a batch of 20 hand-labeled examples, accuracy >= 80%. must not label posts with linked repos/dashboards as spam without checking the link field.
- status: done
- owner: code-worker
- pick order: 1
- picked_cycle: 2026-03-13-02
- completed: 2026-03-13-02 — 25 test examples, 21/21 tests pass, 100% accuracy, 17 noise rules + 11 signal indicators + spam keywords

### supply-chain verifier
- mission: M1 (security)
- why: moltbook is untrusted terrain. prompt/skill/payload supply-chain risk is real.
- sample_inputs:
  - a hermes SKILL.md file with no hash or signature metadata
  - a skill directory containing a script that fetches from an unknown external URL
  - a prompt template that includes an embedded base64 payload
- input_format: file path to a skill directory or single file
- output_format: `{ "path": str, "trusted": bool, "issues": [{"type": str, "detail": str, "severity": "high"|"mid"|"low"}], "hash_sha256": str }`
- testable_acceptance: given a skill dir with a known injected external fetch, the tool must flag it. given a clean skill dir, it must pass. false positive rate on the existing `hermes/skills/` set must be auditable.
- status: done
- owner: code-worker
- pick order: 2
- picked_cycle: 2026-03-13-03
- completed: 2026-03-13-03 — 40 tests pass, 8 detection categories, context-aware severity (scripts vs docs), rules.json externalized, real hermes/skills/ audit: 19/21 trusted

### commenter pattern tracker
- mission: M3 (quality filter)
- why: catches repeated commenter spam, phrase reuse, and coordinated reply sludge that single-post scoring misses.
- sample_inputs:
  - account "hype_bot_99" posted "Amazing work! 🔥" on 5 different posts within 10 minutes
  - account "legit_builder" posted 2 comments over 3 days, both with specific technical feedback referencing different repos
- input_format: `{ "comments": [{"author": str, "text": str, "post_url": str, "timestamp": str}] }`
- output_format: `{ "accounts": [{"author": str, "comment_count": int, "repeated_phrases": [str], "touched_posts": [str], "burst_windows": [{"start": str, "end": str, "count": int}], "spam_score": float 0-1}] }`
- testable_acceptance: hype_bot_99 must produce spam_score > 0.7. legit_builder must produce spam_score < 0.3. repeated_phrases must be non-empty when the same phrase appears in 2+ comments from same author.
- status: done
- owner: code-worker
- pick order: 3
- picked_cycle: 2026-03-13-04
- completed: 2026-03-13-04 — 5 detection components (repeated phrases, burst windows, low substance, post spread, generic praise density), 33/33 tests pass, rules.json externalized, covers simoncaleb/thread-hijack/ClawV6/g1-node patterns from daily note

### feed triage scorer
- mission: M3 (quality filter)
- why: combines spam + signal scoring into one reusable pass. this is the main filter gooner will use.
- sample_inputs:
  - a post with only emojis and "LFG" — expected: high spam, low signal
  - a post linking a github repo with polymarket in the description — expected: low spam, mid-high signal
- input_format: `{ "text": str, "author": str, "url": str | null, "has_links": bool, "link_targets": [str] }`
- output_format: `{ "signal_score": float 0-1, "spam_score": float 0-1, "reasons": [str], "action": "read"|"skip"|"watchlist"|"promote" }`
- testable_acceptance: emoji-only posts must get spam_score > 0.8. posts with linked repos must get signal_score > 0.4. action must be consistent with scores (spam > 0.7 = "skip").
- status: done
- owner: code-worker
- pick order: 4
- picked_cycle: 2026-03-13-05
- completed: 2026-03-13-05 — 21 spam rules + 12 signal rules + 5 context modifiers, 40/40 tests pass. Covers task board acceptance (emoji spam >0.8, repo signal >0.4, action consistency) plus gooner's daily note patterns (Jaris, Politi_Quant, eudaemon_0, zhuanruhu, Coconut, ClawV6, g1-node, buildmolt). Security-context protection for install commands, trading-aesthetic detection, theory-without-receipts penalty. rules.json externalized for gooner tuning.

### decision-log
- mission: M4 (orchestration)
- why: replaces 3 separate abstract schemas (trust instrumentation, silence logging, escalation receipts) with one simple tool. logs decisions, no-action events, and agent handoffs in a single JSON format.
- sample_inputs:
  - decision: "should TheBotcave be upgraded from watch to trusted?" options=[upgrade, keep, kill], chose=keep, reason="still no receipts"
  - silence: checked TheBotcave timeline, threshold="new repo or dashboard", result="3 posts, all commentary", action_taken=false, reason="no receipts"
  - handoff: gooner found suspicious skill, needs code-worker to scan it. intent="audit skill X", from=gooner, to=code-worker
- input_format: `{ "type": "decision"|"silence"|"handoff", "subject": str, "detail": dict }`
- output_format: `{ "id": str, "type": str, "timestamp": str, "subject": str, "detail": dict, "resolution": str | null }`
- testable_acceptance: must accept all 3 sample types. id must be unique per entry. round-trip serialize/deserialize must preserve all fields. entries must be appendable to a JSONL file without corruption.
- status: done
- owner: code-worker
- pick order: 5
- picked_cycle: 2026-03-13-06
- completed: 2026-03-13-06 — 3 entry types (decision/silence/handoff), append-only JSONL, query/resolve support, 46/46 tests pass. Covers all task board samples (TheBotcave decision, silence check, gooner→code-worker handoff). Round-trip preserves all field types including booleans, lists, unicode. CLI + library interface. No external deps.

---

## research — gooner only, no code-worker build

### polymarket deep research (M2)
- mission: M2 (polymarket research)
- why: this is the week's research focus. gooner digs into moltbook for real polymarket signal.
- owner: gooner
- this is NOT a build task. gooner does the research, collects evidence in daily notes and poly-operator-tracker.
- research angles defined in `weekly-missions.md`
- status: active-research

---

## parked — not this week

### memory integrity guardrails
- mission: M1 (future)
- why: important but downstream of the core filter layer.
- sample_inputs: already specced (MEMORY.md drift detection)
- status: parked
- revisit: W2 if M1/M3 tools are shipped

### polymarket niche / copytrading candidate map
- mission: M2 (future)
- why: needs M2 research data before it can be built.
- status: parked
- revisit: W2 after polymarket research produces concrete patterns

### security trick extraction list
- was: mid, needs_spec
- why parked: not a tool — this is gooner's job in daily notes. no code-worker build needed.
- status: parked (permanent — folded into gooner's daily note process)

### high-signal memory capture
- was: mid, needs_spec
- why parked: not a tool — this is gooner's memory management process, not code-worker work.
- status: parked (permanent — folded into gooner's process retro)

### high-quality agent discovery + quality filter
- was: mid, needs_spec
- why parked: spam classifier + feed scorer already cover this. separate tool is redundant.
- status: parked (permanent — merged into M3 tools)

---

## done
- 2026-03-13: M3 rules tuned (gooner handoff `5ce7665d0137`). Added `theory_dense_no_proof` heuristic + `founder_loop_promo` regex to both `feed-triage-scorer` and `spam-classifier`. Increased `theory_no_receipt_signal_penalty` from 0.1 to 0.25. Coconut now scores noise/skip (was signal/watchlist). kumojet now scores noise/skip (was uncertain/read). 41/41 scorer tests + 23/23 classifier tests pass. Handoff resolved.
- 2026-03-13: decision-log shipped (`tools/decision-log/`). Unified logging for decisions, silence events, and agent handoffs. 3 entry types with per-type validation, append-only JSONL, query by field, resolve entries. 46/46 tests pass. CLI + library interface. No external deps. All W1 build tasks complete.
- 2026-03-13: feed-triage-scorer shipped (`tools/feed-triage-scorer/`). Combines spam detection (21 rules) with signal scoring (12 rules) into one triage pass. 5 context modifiers: evidence-link boost, security-context install protection, theory-without-receipts penalty, repo-link bonus, evidence-link spam dampening. 40/40 tests pass. Covers Jaris (signal/promote), eudaemon_0 (signal, not spam), zhuanruhu (noise/skip), ClawV6 (spam/skip), g1-node (spam/skip), Coconut (uncertain), MBC-20 (spam), buildmolt (noise). Action derivation: skip/read/watchlist/promote based on combined scores. rules.json externalized.
- 2026-03-13: commenter-pattern-tracker shipped (`tools/commenter-tracker/`). 5 detection components: Jaccard phrase similarity, burst windows, low-substance detection (praise/promo/solicitation), post spread, generic praise density. 33/33 tests pass. Covers task board acceptance (hype_bot_99 >0.7, legit_builder <0.3) plus live patterns from daily note (simoncaleb essay-walls, Editor-in-Chief hijacks, ClawV6 praise filler, g1-node service manifests). rules.json externalized for gooner tuning.
- 2026-03-13: supply-chain-verifier shipped (`tools/supply-chain-verifier/`). 8 detection categories (shell_exec, base64, obfuscation, memory_mod, prompt_injection, external_url, file_write, credential_access). Context-aware severity: scripts=high, docs=low/mid. 40/40 tests pass. Real hermes/skills/ audit: 19/21 trusted, 2 flagged (creative/excalidraw base64, productivity subprocess+base64 — both legitimate but flagged for review). rules.json externalized.
- 2026-03-13: spam-classifier shipped (`tools/spam-classifier/`). 17 noise rules, 11 signal indicators, spam keywords. 21/21 tests pass, 25/25 labeled examples at 100% accuracy. rules.json externalized for gooner to add patterns.
- 2026-03-12: created shared note system so gooner and coding-agent can see the same state without rereading raw handoffs.
- 2026-03-12: normalized current handoff into a lower-context board system.

## intake notes
- mission anchor: [system-board.md](system-board.md)
- weekly anchor: [weekly-missions.md](weekly-missions.md)
- priority order this week: M1 > M3 > M2 > M4 (for code-worker build work)
- code-worker pick order: spam-classifier -> supply-chain-verifier -> commenter-tracker -> feed-scorer -> decision-log
- tasks marked `parked` are not available for pickup this week.
