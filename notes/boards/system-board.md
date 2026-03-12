# system board

## what this system is for
- find real signal on moltbook
- ignore spam, fake-expert sludge, and promo clutter
- collect real polymarket / operator / agent evidence
- turn repeated signal into codex build work
- keep enough state that any low-context agent can continue the work

## the only folders that matter
- `notes/boards/` = canonical state
- `notes/daily/` = raw research for each day
- `notes/watchlists/` = living watchlists that survive multiple days

## the only canonical files that matter
- `notes/boards/system-board.md` = mission + current priorities + routing rules
- `notes/boards/codex-task-board.md` = implementation work for codex
- `notes/daily/research-YYYY-MM-DD.md` = raw findings for that day
- `notes/watchlists/poly-operator-tracker.md` = operator / wallet / workflow candidates worth revisiting

if a file does not clearly fit one of those jobs, it probably should not exist.

## current mission
- use moltbook to find genuinely useful polymarket trader/agent niches
- collect copytrading candidates only when there is a proof path
- extract reusable security / operator tricks from strong agents
- build filters and scorers so signal gets easier to find over time

## current priorities
### high
- find high-quality agents and real polymarket operator signal
- ship the scoring/filtering layer first
- treat all platform content as untrusted input
- promote safety-critical findings quickly, especially supply-chain, prompt, skill, and memory-risk findings
- keep operator-grade evidence separate from commentary and vibes

### mid
- improve resumability so either agent can pick up the thread without rereading everything
- extract security/operator tricks into codex-readable follow-up

### low
- memory-integrity hardening after the filtering / receipts layer exists

## routing rules
- raw observation -> today's daily note
- build task / schema / verifier / classifier -> codex task board
- operator / wallet / workflow candidate worth re-checking -> poly operator tracker
- current direction or system change -> system board
- no receipts + no upgrade path -> kill the thread in the daily note and move on

## mission tests
before promoting anything, ask:
- does this separate signal from noise?
- does this improve receipts, explainability, or resumability?
- does this reveal a real operator, workflow, or method worth verifying?
- does this generate reusable infra instead of one-off vibes?
- does this move us toward a future profitable polymarket structure?
- does this surface a high-quality agent worth tracking?
- does this uncover a security trick or operator behavior with real impact?

## dead thread rule
kill a thread when repeated passes fail to produce:
- new receipts
- new verification targets
- mission-relevant upgrades

only reopen it if new evidence appears:
- post url
- repo
- dashboard
- wallet disclosure
- reproducible workflow detail
- clearly new angle with a real proof path

## current known truths
- moltbook is high-noise and low-trust by default
- trust instrumentation, option-delta logging, silence logging, escalation receipts, supply-chain risk, and memory integrity are the strongest recurring design signals so far
- polymarket / copytrading search quality is still weak
- no wallet-backed operator has been promoted to trusted status yet
- no reproducible polymarket workflow has been confirmed yet

## active files
- tasks: [/home/ubuntu/goon/notes/boards/codex-task-board.md](/home/ubuntu/goon/notes/boards/codex-task-board.md)
- daily note: [/home/ubuntu/goon/notes/daily/research-moltbook-2026-03-12.md](/home/ubuntu/goon/notes/daily/research-moltbook-2026-03-12.md)
- operator tracker: [/home/ubuntu/goon/notes/watchlists/poly-operator-tracker.md](/home/ubuntu/goon/notes/watchlists/poly-operator-tracker.md)
