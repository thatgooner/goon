# changelog

most recent first.

---

## 2026-03-13

### process hardening + code-worker automation (coding-agent)

**what happened**: hardened the moltbook research process and built the code-worker automation layer so the system can run overnight with real progress.

**changes**:
- `notes/daily/.template.md` — added pre-pass mission gate, post-pass audit, pass delta, zero-gain response, classifier rule candidates, sample data for coding-agent, process retro, tool adoption check
- `notes/boards/system-board.md` — added operational rules: zero-gain rule (3-pass limit), mission gate enforcement, tool adoption protocol, sync protocol with file ownership
- `notes/boards/coding-agent-task-board.md` — added task spec quality rules (sample_inputs, input/output format, testable_acceptance required). upgraded all existing tasks with concrete specs. tasks without specs marked `needs_spec`
- `external-agent/moltbook-process-spec.md` — updated with new gates, code-worker cron loop, sync protocol, tool adoption, sample data collection
- `external-agent/interaction-surface.md` — updated with code-worker write targets, automation files, new file ownership map
- `.cursor/rules/code-worker.mdc` — Cursor agent rule for 1-hour cron automation
- `scripts/code-worker-prompt.md` — trigger prompt for Cursor cloud agent cron
- `logs/code-worker/.gitkeep` — progress log directory
- `AGENTS.md` — updated agent table, added code-worker protocol, sync rules, file ownership
- `README.md` — updated to reflect new structure

### moltbook process export for external agents (coding-agent)

**what happened**: added a separate handoff folder so an outside coding-agent can reconstruct gooner's observable moltbook workflow without reverse-engineering the whole repo.

**changes**:
- created `external-agent/README.md` — entrypoint for low-context agents
- created `external-agent/moltbook-process-spec.md` — full externalized process from bootstrap to promotion/kill rules
- created `external-agent/interaction-surface.md` — file interaction map plus external request surface
- updated `AGENTS.md` to point new agents at the external-agent handoff
- updated `README.md` to list the new folder

---

## 2026-03-12

### gooner setup + repo infrastructure (coding-agent)

**what happened**: first coding-agent session. reviewed the repo, fixed structural issues, set up gooner's full backup system.

**changes**:
- fixed all internal links from absolute (`/home/ubuntu/goon/...`) to relative paths
- added `.gitignore` to protect secrets and editor files
- created `hermes/` directory structure to mirror gooner's live `~/.hermes/` state
- created `scripts/hermes-sync.sh` — link/pull/push between repo and live agent
- created `scripts/restore.sh` — full from-scratch gooner restore on any new machine
- created `notes/daily/.template.md` for consistent daily research notes
- created `tools/` directory for coding-agent build work with planned tool map
- renamed all `codex` references to `coding-agent` (including file rename `codex-task-board.md` → `coding-agent-task-board.md`)
- created `AGENTS.md` so any new agent can understand the full context immediately

### gooner state export (gooner)

**what happened**: gooner exported its full hermes internal state to the repo.

**changes**:
- `hermes/config.yaml` — live agent config
- `hermes/memories/MEMORY.md` — gooner's learned knowledge
- `hermes/memories/USER.md` — user profile and preferences
- `hermes/skills/` — 80+ hermes skills exported
- `hermes/file-listing.txt` — full `~/.hermes/` directory map

### config fixes (coding-agent)

**what happened**: fixed two config issues discovered during review.

**changes**:
- personality: changed from `kawaii` to custom `gooner` (cold, deadpan, hoodville cityboy voice)
- compression: changed `summary_provider` from `auto` (needs OpenRouter key) to `codex` (uses existing OAuth)

### initial research system (gooner)

**what happened**: gooner set up the notes system before the coding-agent arrived.

**changes**:
- `notes/boards/system-board.md` — mission, priorities, routing rules, mission tests, dead thread rule
- `notes/boards/coding-agent-task-board.md` — 12 queued build tasks (6 high, 4 mid, 2 low)
- `notes/daily/research-moltbook-2026-03-12.md` — first day of moltbook research
- `notes/watchlists/poly-operator-tracker.md` — 3 names on watch (TheBotcave, nova-morpheus, FailSafe-ARGUS)

**key findings from research**:
- moltbook is high-noise, low-trust
- strongest signals: trust instrumentation, option-delta logging, silence logging, escalation receipts, supply-chain risk
- strongest noise: generic praise, fake-expert walls, promo spam, vanity bots
- no confirmed polymarket operator or workflow yet

---

## status as of end of day

- gooner: running on AWS, updated config, daily research active
- coding-agent: repo infrastructure complete, 0/12 tools built
- next: build tools from task board (spam classifier, supply-chain verifier, etc.)
