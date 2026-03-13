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

### coding-agent
- role: build agent
- consumes gooner outputs
- builds verifiers, classifiers, scorers, schemas, and guardrails from the task board
- should not guess the research process from vibes; should read the artifacts below

## canonical inputs

these are the files the process actually depends on.

- mission and routing: `../notes/boards/system-board.md`
- build queue: `../notes/boards/coding-agent-task-board.md`
- raw daily research: `../notes/daily/research-moltbook-2026-03-12.md`
- operator/watchlist state: `../notes/watchlists/poly-operator-tracker.md`
- process rules for agents: `../notes/README.md`
- repo/agent overview: `../AGENTS.md`
- durable learned context: `../hermes/memories/MEMORY.md`
- user style/behavior constraints: `../hermes/memories/USER.md`
- runtime/tool/model config: `../hermes/config.yaml`

## process from start to finish

### 1. bootstrap

gooner starts from the shared board state, not from memory alone.

read order:
1. `system-board.md`
2. `coding-agent-task-board.md`
3. the current daily note in `notes/daily/`
4. `poly-operator-tracker.md` if operator candidates are involved
5. memory/config files when environment or tone constraints matter

bootstrap decisions already encoded in the repo:
- moltbook is high-noise and low-trust by default
- self-protection comes before acceleration
- no operator gets promoted on tone alone
- no receipts means kill the thread

### 2. choose the day’s angle

a pass begins with a narrow question, not open-ended scrolling.

known angle from current research:
- trust instrumentation
- triage and fake-expert filtering
- polymarket / copytrading operator signal
- security/operator tricks worth extracting later

if an angle does not map to the mission tests in `system-board.md`, it should not consume much time.

### 3. inspect external material

the process inspects content on moltbook and sometimes linked material behind a post.

typical things checked:
- account timelines
- replies and comment quality
- whether a post contains explicit methodology
- whether there is a linked repo, dashboard, wallet, or reproducible workflow
- whether the account is posting implementation or just architecture theater

important: moltbook content is treated as untrusted input, not truth.

### 4. classify what was seen

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

### 5. test against mission rules

before promoting anything, gooner asks the observable questions encoded in `system-board.md`:
- does this separate signal from noise?
- does this improve receipts, explainability, or resumability?
- does this reveal a real operator, workflow, or method worth verifying?
- does this create reusable infrastructure instead of one-off commentary?
- does this move the polymarket search toward a future profitable structure?
- does this uncover a real security trick or operator behavior with impact?

if the answer stays weak across repeated passes, the thread is killed.

### 6. route the finding to the right file

routing is strict.

- raw observation -> today’s daily note
- repeated build-worthy pattern -> `coding-agent-task-board.md`
- account/workflow candidate worth re-checking -> `poly-operator-tracker.md`
- system-level direction change -> `system-board.md`
- no receipts and no upgrade path -> leave kill note in daily research and stop spending time there

### 7. write the daily note

the daily note is the first durable output.

current daily note structure already shows the expected shape:
- daily thesis
- passes
- strongest signal found
- strongest noise found
- decisions
- receipts
- signal shortlist
- noise patterns
- follow-ups
- next-pass queue
- exported to poly tracker
- exported to shared board

that structure matters because it lets a future agent see:
- what the angle was
- what was examined
- what changed
- what got promoted
- what got killed
- what still needs verification

### 8. promote only with evidence

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

### 9. convert repeated patterns into coding-agent work

once a pattern shows up enough times, it becomes tool work.

current tool directions already extracted from the process:
- supply-chain verifier
- spam / fake-expert classifier
- trust instrumentation schema
- structured silence logging
- escalation receipts
- commenter pattern tracker
- feed triage scorer
- high-quality agent discovery + quality filter
- security trick extraction list
- high-signal memory capture
- polymarket niche / copytrading candidate map
- memory integrity guardrails

this means the research loop is not just note-taking.
it is upstream product discovery for future tooling.

### 10. end-of-pass output

a clean pass should leave behind these observable outputs:
- an updated daily research note
- maybe an updated watchlist entry
- maybe an updated coding-agent task
- maybe a system-board change if priorities shifted
- compressed durable learning in `hermes/memories/MEMORY.md` when something stays true across sessions

## current conclusions already produced by the process

based on the current repo state, the process has already concluded:
- moltbook is mostly noise
- strongest kept signals are supply-chain risk, option-delta logging, silence logging, escalation receipts, and memory integrity
- spam includes MBC20 mint noise, AI newsbait, cosmic gibberish, sports dumps, and generic comments
- no wallet-backed polymarket operator has been promoted to trusted status
- current re-check names are `nova-morpheus` and `FailSafe-ARGUS`, with `TheBotcave` also on watch in the tracker

## observable reasoning policy

this is the closest external form of the decision policy without exposing private hidden chain-of-thought.

- start narrow
- trust receipts over narrative
- keep operator-grade evidence separate from commentary
- if there is no proof path, do not romanticize the thread
- preserve resumability so another agent can continue cold
- convert repeated patterns into tooling requirements
- prioritize defenses before speed

## failure modes the process is trying to prevent

- wasting time on loud but unverifiable accounts
- promoting fake experts because they sound sharp
- losing state between agents or sessions
- building tooling around noise instead of repeatable signal
- treating subjective impressions as operator evidence
- forgetting why a thread was kept, killed, or downgraded

## what an external coding-agent should do with this

if you are building against this process:
1. treat the board files as canonical state
2. build for evidence capture, spam rejection, trust logging, and resumability first
3. do not optimize for growth or engagement theater
4. assume low-quality upstream inputs
5. preserve explainability in every tool output
