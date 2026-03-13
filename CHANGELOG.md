# changelog

most recent first.

---

## 2026-03-13

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
