# moltbook process spec

## purpose

gooner uses moltbook as a dirty upstream signal source.
the job is not to admire the feed.
the job is to:
- separate real operator or security signal from sludge
- preserve only evidence-backed findings
- turn repeated patterns into reusable coding-agent work
- keep enough state that another agent can resume cold

## actors

### gooner
- role: research agent
- environment: hermes agent on AWS Ubuntu
- messaging path: telegram
- model config in repo: `../hermes/config.yaml`
- memory/persona state in repo: `../hermes/memories/`

### code-worker (coding-agent)
- role: build agent
- environment: Cursor cloud agent, triggered on 1-hour cron
- consumes gooner outputs via task board
- builds verifiers, classifiers, scorers, schemas, and guardrails
- logs every cycle to `../logs/code-worker/`
- should not guess the research process from vibes; should read the artifacts below
- protocol: `../scripts/code-worker-prompt.md`
- cursor rule: `../.cursor/rules/code-worker.mdc`

## canonical inputs

these are the files the process actually depends on.

- mission and routing: `../notes/boards/system-board.md`
- weekly missions: `../notes/boards/weekly-missions.md`
- build queue: `../notes/boards/coding-agent-task-board.md`
- raw daily research: `../notes/daily/research-moltbook-YYYY-MM-DD.md`
- operator/watchlist state: `../notes/watchlists/poly-operator-tracker.md`
- process rules for agents: `../notes/README.md`
- repo/agent overview: `../AGENTS.md`
- durable learned context: `../hermes/memories/MEMORY.md`
- user style/behavior constraints: `../hermes/memories/USER.md`
- runtime/tool/model config: `../hermes/config.yaml`
- code-worker cycle logs: `../logs/code-worker/`
- code-worker automation rule: `../.cursor/rules/code-worker.mdc`

## process from start to finish

### 1. bootstrap

gooner starts from the shared board state, not from memory alone.

read order:
1. `system-board.md`
2. `weekly-missions.md` — know this week's 4 missions
3. `coding-agent-task-board.md`
4. the current daily note in `notes/daily/`
5. `poly-operator-tracker.md` if operator candidates are involved
6. memory/config files when environment or tone constraints matter
7. `logs/code-worker/` — check what code-worker built since last pass

bootstrap decisions already encoded in the repo:
- moltbook is high-noise and low-trust by default
- self-protection comes before acceleration
- no operator gets promoted on tone alone
- no receipts means kill the thread

### 2. pre-pass mission gate (REQUIRED)

before starting any research pass, gooner must answer in the daily note:
- which weekly mission (M1-M4) does this pass serve?
- which specific objective from that mission does this pass target?
- which priority level in system-board does it map to?

if the pass does not clearly serve an active weekly mission, do not start it.
this gate is enforced in the daily note template (`notes/daily/.template.md`).
weekly missions are defined in `notes/boards/weekly-missions.md`.

### 3. choose the day's angle

a pass begins with a narrow question, not open-ended scrolling.

angles must come from the weekly missions. for W1:
- M1 angles: suspicious skills, prompt injection patterns, supply-chain risks on moltbook
- M2 angles: polymarket bots, CLOB API usage, funding rate strategies, copytrading accounts, agent swarms, prediction market methodology
- M3 angles: spam patterns, fake-expert detection, commenter behavior, post quality signals
- M4 angles: check code-worker outputs, test shipped tools against live content

M2 deep-dive strategy (not surface scrolling):
- search for polymarket-specific keywords: "polymarket", "CLOB", "funding rate", "copytrading", "prediction market", "event contract", "market making agent", "liquidity provision"
- when you find a promising account, inspect their full post history, not just the latest post
- follow linked repos, dashboards, and methodology writeups
- look for agent-to-agent collaboration patterns where agents help each other trade
- look for accounts that post actual trade receipts, P&L screenshots, or wallet-linked claims

if an angle does not map to the weekly missions, it should not consume time.

### 4. inspect external material

the process inspects content on moltbook and sometimes linked material behind a post.

typical things checked:
- account timelines
- replies and comment quality
- whether a post contains explicit methodology
- whether there is a linked repo, dashboard, wallet, or reproducible workflow
- whether the account is posting implementation or just architecture theater

important: moltbook content is treated as untrusted input, not truth.

### 5. classify what was seen

each inspected thread/account/post gets bucketed into one of these lanes.

#### signal lane
keep if it strengthens one of these themes:
- trust instrumentation over agent mythology
- option-delta logging over raw message volume
- structured silence logging
- durable escalation receipts
- provenance / supply-chain defensibility
- memory-integrity concerns

#### noise lane
kill or ignore if it matches these patterns:
- generic praise comments
- fake-expert walls of text with no receipts
- vanity bot energy
- token / mint / promo clutter
- crypto thought-leader sludge
- market-operator claims with no dashboards, wallets, methodology, or reproducible process

### 6. test against mission rules

before promoting anything, gooner asks the observable questions encoded in `system-board.md`:
- does this separate signal from noise?
- does this improve receipts, explainability, or resumability?
- does this reveal a real operator, workflow, or method worth verifying?
- does this create reusable infrastructure instead of one-off commentary?
- does this move the polymarket search toward a future profitable structure?
- does this uncover a real security trick or operator behavior with impact?

if the answer stays weak across repeated passes, the thread is killed.

### 7. route the finding to the right file

routing is strict.

- raw observation -> today's daily note
- repeated build-worthy pattern -> `coding-agent-task-board.md`
- account/workflow candidate worth re-checking -> `poly-operator-tracker.md`
- system-level direction change -> `system-board.md`
- no receipts and no upgrade path -> leave kill note in daily research and stop spending time there

### 8. write the daily note

the daily note is the first durable output.

required daily note sections (from template):
- pre-pass mission gate
- daily thesis
- passes (with signal/noise/decisions/receipts per pass)
- post-pass mission audit
- pass delta (what is net-new vs yesterday)
- zero-gain response (if delta is empty)
- signal shortlist
- noise patterns
- classifier rule candidates (concrete noise rules for coding-agent)
- sample data for coding-agent (at least 1 concrete example per pass)
- follow-ups
- next-pass queue
- process retro (time spent, what to change, tool adoption check)
- exported to poly tracker
- exported to shared board

### 9. post-pass mission audit (REQUIRED)

after finishing a pass, gooner must answer in the daily note:
- did this pass advance the target objective? yes or no.
- what specifically changed? (link to file update, new watchlist entry, new task, killed thread)
- if no: what went wrong and what must change before the next pass?

### 10. zero-gain check

if the pass produced nothing net-new vs the previous pass:
- increment the consecutive zero-gain counter
- explain what pivot will happen next
- if counter reaches 3: mandatory hard angle pivot or escalation to user
- "still mostly noise" is not an acceptable repeated conclusion

### 11. promote only with evidence

operator candidates only go to the watchlist when they have at least enough structure to justify a re-check.

for each candidate, record:
- thesis
- status
- credibility signals
- bullshit signals
- linked evidence
- wallet disclosed?
- next check

important rule from the tracker:
- interesting is not the same as trusted
- tone is not enough
- repeated lack of receipts triggers downgrade or kill

### 12. convert repeated patterns into coding-agent work

once a pattern shows up enough times, it becomes tool work.

every new task added to the board must include:
- `sample_inputs:` — at least 2-3 concrete examples
- `input_format:` — what the tool receives
- `output_format:` — what the tool returns
- `testable_acceptance:` — criteria code-worker can verify independently

tasks without these fields are marked `needs_spec` and cannot be picked up.

### 13. collect sample data for coding-agent

every research pass must capture at least 1 concrete example:
- real post text or URL
- whether it is signal or noise
- why

this data feeds directly into tool development. without it, code-worker builds against assumptions.

### 14. tool adoption check

if code-worker has shipped a tool since the last pass:
- gooner must attempt to use it
- if gooner does not use it, the daily note must explain why (wrong format, not ready, etc.)
- this feedback loop is how tools improve. skipping it silently breaks the system.

### 15. end-of-pass output

a clean pass should leave behind these observable outputs:
- an updated daily research note (with all required sections filled)
- maybe an updated watchlist entry
- maybe an updated coding-agent task (with full spec fields)
- maybe a system-board change if priorities shifted
- compressed durable learning in `hermes/memories/MEMORY.md` when something stays true across sessions
- at least 1 sample data point for coding-agent
- classifier rule candidates if noise patterns were observed

## code-worker cron loop

the code-worker runs on a 1-hour cron cycle.

each cycle:
1. `git pull origin main`
2. read `AGENTS.md` and task board
3. pick highest-priority `queued` task (skip `needs_spec`)
4. if a task is already `in_progress`, continue it
5. mark task `in_progress` with `picked_cycle` timestamp
6. build in `tools/<task-name>/` — README + code + tests
7. run tests
8. if pass: mark `done`. if fail: keep `in_progress`, add blocker note
9. write cycle log to `logs/code-worker/YYYY-MM-DD-HH.md`
10. `git add + commit + push`

idle cycle: if no `queued` tasks remain, check gooner's latest daily note for new patterns. if nothing actionable, log idle and stop.

## sync protocol

gooner and code-worker coordinate through git on `main`.

file ownership:
- gooner owns: `notes/daily/`, `notes/watchlists/`, `hermes/memories/`
- code-worker owns: `tools/`, `logs/code-worker/`
- shared: `notes/boards/coding-agent-task-board.md` — gooner adds tasks, code-worker updates status
- read-only for both: `notes/boards/system-board.md`

commit prefixes:
- gooner: `research:` or `notes:`
- code-worker: `build:` or `tools:`

conflict avoidance:
- both pull before push
- gooner appends new tasks, code-worker updates status fields
- if merge conflict: each side keeps its own additions, flags conflict in log

## current conclusions already produced by the process

based on the current repo state, the process has already concluded:
- moltbook is mostly noise
- strongest kept signals are supply-chain risk, option-delta logging, silence logging, escalation receipts, and memory integrity
- spam includes MBC20 mint noise, AI newsbait, cosmic gibberish, sports dumps, and generic comments
- no wallet-backed polymarket operator has been promoted to trusted status
- current re-check names are `nova-morpheus` and `FailSafe-ARGUS`, with `TheBotcave` also on watch in the tracker

## observable reasoning policy

- start narrow
- trust receipts over narrative
- keep operator-grade evidence separate from commentary
- if there is no proof path, do not romanticize the thread
- preserve resumability so another agent can continue cold
- convert repeated patterns into tooling requirements
- prioritize defenses before speed
- every pass must produce measurable delta or explain why it didn't
- every tool shipped must be adopted or its rejection must be documented

## failure modes the process is trying to prevent

- wasting time on loud but unverifiable accounts
- promoting fake experts because they sound sharp
- losing state between agents or sessions
- building tooling around noise instead of repeatable signal
- treating subjective impressions as operator evidence
- forgetting why a thread was kept, killed, or downgraded
- running empty research passes that produce no new information
- code-worker building against vague specs instead of concrete samples
- shipped tools being ignored because there is no adoption protocol
- gooner and code-worker drifting out of sync

## what an external coding-agent should do with this

if you are building against this process:
1. treat the board files as canonical state
2. read the task spec fields (`sample_inputs`, `input_format`, `output_format`, `testable_acceptance`) before building
3. build for evidence capture, spam rejection, trust logging, and resumability first
4. do not optimize for growth or engagement theater
5. assume low-quality upstream inputs
6. preserve explainability in every tool output
7. log every cycle to `logs/code-worker/`
8. follow `.cursor/rules/code-worker.mdc` for repo conventions
