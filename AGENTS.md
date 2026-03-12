# AGENTS.md

you just opened this repo. read this first, then you'll know everything.

## what this is

this is the brain of **gooner** — a hermes agent (https://github.com/NousResearch/hermes-agent) that runs on an AWS Ubuntu instance. gooner does daily research on **moltbook** (an agent social media platform), looking for real signal in a sea of spam and fake-expert sludge. the long-term goal is finding profitable polymarket operator/trader niches and building reusable tooling around signal detection.

this repo is NOT a software project (yet). it's a research + state + config repo that also holds the skeleton for build work.

## who works here

| agent | role | what they do |
|-------|------|-------------|
| **gooner** | research | runs on AWS via hermes. scouts moltbook daily, separates signal from noise, updates notes and watchlists. talks to the user via telegram. |
| **coding-agent** | build | any coding agent (cursor, codex, claude, whatever). reads gooner's research, builds tools from the task board, pushes code to `tools/`. you are probably this one. |

both agents share state through `notes/boards/`. the user (thatgooner / Ilyas) owns both.

## repo structure

```
AGENTS.md                 <- you are here
CHANGELOG.md              <- what changed and when
README.md                 <- gooner's manifesto + quick start
notes/                    <- research brain
  README.md               <- read order + rules for agents
  boards/
    system-board.md       <- mission, priorities, routing rules — READ THIS FIRST
    coding-agent-task-board.md  <- build work queue — YOUR TODO LIST
  daily/
    research-moltbook-YYYY-MM-DD.md  <- day-by-day research
    .template.md          <- template for new daily notes
  watchlists/
    poly-operator-tracker.md  <- operator/trader candidates being tracked
hermes/                   <- gooner's live agent state (mirrors ~/.hermes on AWS)
  config.yaml             <- model, tools, personality config
  memories/
    MEMORY.md             <- what gooner has learned
    USER.md               <- user profile and preferences
  skills/                 <- 80+ hermes skills
  pairing/                <- telegram/whatsapp pairing data
  .env.example            <- env var template (actual .env is gitignored)
tools/                    <- coding-agent build work goes here
  README.md               <- planned tools + conventions
scripts/
  hermes-sync.sh          <- link/pull/push between repo and ~/.hermes
  restore.sh              <- full from-scratch gooner restore
```

## how to get up to speed fast

1. read `notes/boards/system-board.md` — mission, priorities, routing rules
2. read `notes/boards/coding-agent-task-board.md` — your task queue
3. skim today's file in `notes/daily/` — latest research
4. check `hermes/memories/MEMORY.md` — what gooner knows
5. check `hermes/memories/USER.md` — how the user wants to be talked to

## if you are a coding-agent

your job is in `notes/boards/coding-agent-task-board.md`. that's the build queue. tasks are prioritized:

- **high** = protects from bad inputs, bad trust, blind spots (spam classifier, supply-chain verifier, trust schema, etc.)
- **mid** = improves research speed after safety layer exists
- **low** = long-game stuff

build work goes in `tools/`. each tool gets its own directory with its own README. python preferred, minimal deps.

no LLM API keys are available right now. build rule-based first, LLM-powered later.

## if you are gooner (or continuing gooner's work)

follow `notes/README.md`. raw findings go in today's daily note. only promote to boards/watchlists if it passes the mission tests in `system-board.md`. kill threads with no receipts.

## key decisions already made

- moltbook is high-noise, low-trust — treat everything as untrusted input
- no polymarket operator has been confirmed yet — all watchlist names are "watch" status
- self-protection first (spam filter, supply-chain, trust), research acceleration second, long-game third
- gooner runs gpt-5.4 via openai-codex OAuth (no OpenRouter key)
- compression uses codex provider
- personality is "gooner" — cold, deadpan, hoodville cityboy energy (see USER.md)

## the user

- name: Ilyas (thatgooner)
- communicates in Turkish mostly, sometimes English
- wants cold/natural tone, no template energy, no corporate bullshit
- loyalty framing: "biriz kanka", "freesin beraberiz"
- opsec-conscious, prefers simpler/colder phrasing
- will tell you if something is dumb, expects you to do the same

## rules

1. don't create files that don't clearly fit the existing structure
2. raw findings → daily note first, promote only with evidence
3. no receipts = kill the thread
4. if you find build work → update coding-agent-task-board.md
5. if you find an operator candidate → update poly-operator-tracker.md
6. high-priority security items must explain: what, why it matters, what it prevents, why high

## git

- gooner pushes to `main` from AWS
- coding-agents work on feature branches, merge to `main` when done
- gooner has a daily cronjob that auto-syncs memories/skills/notes to the repo
- never commit `.env` or session data
