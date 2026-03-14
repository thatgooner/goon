# poly operator tracker

## active watchlist

### TheBotcave
- platform: moltbook
- thesis: posts around polymarket plus funding-rate divergence / hedging looked more grounded than average timeline sludge.
- status: watch
- credibility signals:
  - more grounded tone than typical promo clutter
  - mentions concepts that can potentially be verified later
- bullshit signals:
  - no confirmed methodology saved yet
  - no linked repo, dashboard, or wallet receipt saved yet
- linked evidence:
  - source daily note: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- wallet disclosed?: no
- next check: look for explicit methodology, dashboards, repos, or verifiable trade receipts

### nova-morpheus
- platform: moltbook
- thesis: money-adjacent checklist / control framing looked more useful for process than for direct alpha.
- status: watch
- credibility signals:
  - risk/process framing looked more operational than average copytrading noise
- bullshit signals:
  - unclear whether there is any implementation behind the framing
  - no saved receipts yet
- linked evidence:
  - source daily note: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- wallet disclosed?: no
- next check: verify whether the account posts templates, workflows, receipts, or only frameworks

### FailSafe-ARGUS
- platform: moltbook
- thesis: concise replies had a better tone-to-signal ratio than average comments, but the evidence bar is still low.
- status: watch
- credibility signals:
  - less fluff than surrounding replies
- bullshit signals:
  - no deeper technical posts saved yet
  - no repo, tool, dashboard, or wallet receipt saved yet
- linked evidence:
  - source daily note: [research-moltbook-2026-03-12.md](../daily/research-moltbook-2026-03-12.md)
- wallet disclosed?: no
- next check: confirm whether there are real technical posts beyond lightweight comments

### Jaris
- platform: moltbook
- thesis: one of the few accounts posting concrete Polymarket CLOB execution pain instead of generic alpha theater.
- status: watch
- credibility signals:
  - named the exact client (`py-clob-client`) and described a specific bad fill path
  - gave a falsifiable heuristic: skip markets where ask-bid spread >20%
  - post is grounded in first-person execution failure, not abstract strategy cosplay
- bullshit signals:
  - no linked repo, dashboard, wallet, or follow-up methodology saved yet
  - profile is still thin (5 posts total) so one concrete post is not enough for trust
- linked evidence:
  - source daily note: [research-moltbook-2026-03-13.md](../daily/research-moltbook-2026-03-13.md)
  - post: [Polymarket CLOB API is a liquidity desert — agents beware](https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92)
- wallet disclosed?: no
- next check: verify whether Jaris posts additional execution notes, liquid-market lists, or actual code receipts beyond the initial CLOB warning

### Politi_Quant
- platform: moltbook
- thesis: explicit event-to-asset translation framework is more structured than the average prediction-market sermon and is concrete enough to justify a re-check.
- status: watch
- credibility signals:
  - gave a 4-step workflow: event selection -> asset mapping -> implied-probability check -> sizing by the gap
  - used specific examples (Trump tariff escalation vs EEM vol, debt ceiling vs T-bills, Fed independence vs Treasury vol)
  - post is centered on cross-market probability translation, not generic “agents are faster” fluff
- bullshit signals:
  - still no linked repo, dashboard, wallet, or actual trade receipt
  - only 5 posts total so the evidence base is still thin
- linked evidence:
  - source daily note: [research-moltbook-2026-03-13.md](../daily/research-moltbook-2026-03-13.md)
  - post: [Political risk as a tradeable factor: a framework for agents](https://moltbook.com/post/87482936-45bc-4c2b-9e74-edaa763e625f)
- wallet disclosed?: no
- next check: verify whether Politi_Quant ever posts actual position examples, asset-mapping tables, or trade receipts instead of framework-only posts

### jr_openclaw
- platform: moltbook
- thesis: one of the few fresh accounts this week with a public Polymarket repo instead of just strategy talk. real code surface exists, but public execution receipts are still thin.
- status: watch
- credibility signals:
  - posted a live GitHub repo: `getthetroll/polymarket-arb-bot`
  - repo README matches the Moltbook claim: scans 300+ markets every 30s, uses `py-clob-client`, logs trades to CSV, exposes risk controls and config knobs
  - post includes a wallet tip address, so there is at least one concrete external identity surface beyond the text itself
- bullshit signals:
  - no public trade log, fill receipt, dashboard, or wallet-linked performance proof yet
  - repo can exist without proving the strategy is profitable or truly running live
- linked evidence:
  - source daily note: [research-moltbook-2026-03-13.md](../daily/research-moltbook-2026-03-13.md)
  - post: [Open sourced: Polymarket yes/no arb bot — free to use](https://moltbook.com/post/4ab45e36-fedf-4aa7-b68d-cc27a4c69160)
  - repo: https://github.com/getthetroll/polymarket-arb-bot
- wallet disclosed?: yes — `0xf5bAD39aeB2f6E02322878C1C82783fE740b397c`
- next check: verify whether any public fills, trade logs, or repo commits show real execution beyond README claims

## rejected / downgraded
- none yet

dead thread rule:
- if an account produces no new receipts across repeated checks, move it here with the kill reason instead of re-adding it to active watchlist rotation.

## evidence rules
- do not upgrade an account based on tone alone.
- require explicit receipts where possible: post URL, repo, dashboard, wallet disclosure, or reproducible workflow detail.
- keep "interesting" separate from "trusted".
- if a claim has no receipts, record the gap instead of filling it with vibe.

## next verification targets
- confirm whether any candidate publishes a real methodology instead of commentary-only content.
- look for linked repos, dashboards, execution notes, or wallet-linked receipts.
- downgrade candidates quickly if repeated passes show only promo or recycled framework posting.
