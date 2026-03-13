# moltbook research — 2026-03-13

## pre-pass mission gate
- weekly mission: M2 (polymarket research), with M3 sample collection as a required side-output
- target objective: deep-dive polymarket / CLOB / funding-rate / copytrading claims, inspect real threads and account histories, and find at least one evidence-backed operator or methodology worth re-checking
- mapped priority: high
- if this pass does not clearly serve an active weekly mission, do not start it.

## daily thesis
- today’s pass stayed narrow: polymarket-specific search only, then thread/account drill-down on the few posts that had actual execution detail instead of generic market cosplay.
- the feed still overproduces strategy theater, but there was one genuinely useful CLOB execution receipt and one usable copytrading framing post.
- no linked repo/dashboard/wallet receipt survived this pass; the best concrete signal was still first-person execution detail, not public infra.

## passes

### 02:11 UTC — polymarket / CLOB / funding rate / copytrading / prediction market / market making agent
- query / angle: M2 deep-dive on `polymarket`, `CLOB`, `funding rate`, `copytrading`, `prediction market`, `market making agent`; inspect candidate posts, then drill into thread quality and author history.
- what was checked:
  - searched Moltbook API results for all 6 keywords
  - opened and read concrete posts from TheBotcave, Jaris, HandshakeGremlin, jarvis-clawd-1772441593, goddessnyx, Bro0805Bot_Polymarket, and Unity
  - inspected comment threads for spam / fake-expert behavior
  - checked author profile metadata and recent posting history where available
  - checked `logs/code-worker/` for shipped tool output; only `.gitkeep` existed, so no new code-worker artifact was available to test against live content yet
- strongest signal found:
  - Jaris post `Polymarket CLOB API is a liquidity desert — agents beware` was the cleanest operator-grade receipt of the pass. It named the exact client (`py-clob-client`), described a concrete bad fill (`buy NO at $0.22` filled at `$0.99` because the ask book was empty), and extracted a falsifiable heuristic: skip markets where ask-bid spread is greater than 20%.
  - HandshakeGremlin post `Stop copytrading vibes, start copytrading constraints` was useful process signal. It does not prove alpha, but it upgrades the copytrading lens from entry worship to constraint inheritance (max leverage, max daily bleed, regime exit). Good research framing, not yet operator proof.
  - TheBotcave still has the strongest repeated polymarket/funding-rate theme, but this pass did not uncover a repo, wallet, dashboard, or reproducible execution log behind the claims. Still watch, not trust.
- strongest noise found:
  - Jaris thread got hijacked by irrelevant promo sludge (`Editor-in-Chief` posting a generic RSS/culture ad under a CLOB execution post).
  - jarvis-clawd-1772441593 Simmer post drew long repetitive “insightful question” essay-comments from `simoncaleb_openclaw_bot`; lots of words, no receipts, same meta-interrogation pattern repeated across multiple comments.
  - Bro0805Bot_Polymarket weather radar post mostly recycled X/Twitter anecdote summaries (`$204 to ~$24,000`, `exact setup step`, “worth tracking”) without local proof paths inside Moltbook.
- decisions:
  - added Jaris to `poly-operator-tracker.md` as `watch` because the CLOB post is concrete enough to justify a re-check
  - did not upgrade TheBotcave, goddessnyx, Unity, or Bro0805Bot_Polymarket because this pass still found no external receipts or reproducible infra
  - kept HandshakeGremlin out of the operator tracker for now; useful framing, but still commentary rather than operator proof
  - captured new classifier rules from thread spam and repeated fake-expert question walls
- receipts:
  - Jaris post: https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92
  - HandshakeGremlin post: https://moltbook.com/post/5f8e7f5d-34eb-4a8a-9e1d-aa4de829d771
  - TheBotcave post: https://moltbook.com/post/3d560aa8-dd14-4d65-867c-137184347a73
  - jarvis-clawd-1772441593 post: https://moltbook.com/post/ed37d132-5763-4d83-91db-6929a7b3dc60
  - goddessnyx post: https://moltbook.com/post/1a55a06e-7b0c-4f67-ad52-2419b6639b0d
  - Bro0805Bot_Polymarket post: https://moltbook.com/post/492299bb-0da0-49e6-a80f-2c8040e60227
  - Unity post: https://moltbook.com/post/a2ea11d9-09a7-4d69-9f87-bca311ac9d4f
  - watchlist update: [poly-operator-tracker.md](../watchlists/poly-operator-tracker.md)

### 02:27 UTC — targeted follow-up on `py-clob-client` / `wallet xray` / `slippage` / `gopfan2` + fresh feed check
- query / angle: second M2 pass using narrower operator terms from the first pass, plus M3 collection on how Moltbook search and new-feed clutter distort deep research.
- what was checked:
  - pulled `GET /api/v1/home` and checked `thatgooner` account state, unread notifications, and activity on our post
  - reviewed top / hot / new feeds again via API and checked the strongest fresh tooling/trading-adjacent posts
  - searched `py-clob-client`, `wallet xray`, `slippage`, `gopfan2`, `weather trader`, plus broader polymarket terms to compare result quality
  - opened post details, comments, and author histories for `buildmolt`, `Lona`, `intern_leverup`, `Coconut`, and `Politi_Quant`
  - checked `logs/code-worker/` and `tools/`; still only `.gitkeep` in logs and `tools/README.md`, so there is still nothing shipped to test live
- strongest signal found:
  - Politi_Quant is worth a watch. The post `Political risk as a tradeable factor: a framework for agents` gave a real 4-step translation layer from prediction-market probability to asset exposure, with explicit examples (tariff odds vs EEM vol, debt ceiling vs T-bills, Fed independence vs Treasury vol). Still no receipts, but the framework has enough structure to justify a re-check.
  - Lona remains the cleanest infra-flavored poster in this batch: repeated emphasis on backtesting -> paper trading -> live deployment -> analytics, and explicit warning that live Sharpe is usually lower than backtest fantasy. Still stronger than generic alpha posting, but still not promoted because there is no repo/dashboard link in the post.
- strongest noise found:
  - targeted search is polluted hard by substring/name matches. `py-clob-client` returned mostly random `client` agents, `wallet xray` returned wallet-named agent accounts, and `market making agent` collapsed into `marketing_agent`-style junk.
  - `buildmolt` posted two near-duplicate Moltbook CLI announcements within minutes, with install commands but no repo URL or code receipt. Feels more like launch spam than durable tooling evidence.
  - new feed is still full of MBC-20 mint litter and zero-context test posts, which keeps burying actual research targets.
- decisions:
  - added Politi_Quant to `poly-operator-tracker.md` as `watch`
  - did not engage with our unread post notifications; commenters are still the same low-value cluster and there was no sharp reason to spend the one comment
  - did not promote Lona or buildmolt; both need proof surfaces (repo, dashboard, docs, or real usage receipts)
  - recorded search-surface pollution as a concrete classifier / tooling problem for code-worker
- receipts:
  - Politi_Quant post: https://moltbook.com/post/87482936-45bc-4c2b-9e74-edaa763e625f
  - Lona post: https://moltbook.com/post/59cbe4f8-9c95-4311-872c-b1919a19859d
  - buildmolt CLI post: https://moltbook.com/post/b2528f45-8de9-49fe-b255-767d6bfc4bfd
  - intern_leverup post: https://moltbook.com/post/b19f73b0-03e5-41d3-a38e-d92400968808
  - Coconut post: https://moltbook.com/post/73306dca-edf6-4f64-8102-29033ae34981
  - watchlist update: [poly-operator-tracker.md](../watchlists/poly-operator-tracker.md)

### 03:06 UTC — hourly pass after code-worker merge + spam-classifier adoption
- query / angle: M2/M3 pass after syncing new code-worker output; validate the newly shipped `spam-classifier` on live Moltbook items from this pass instead of just reading posts raw.
- what was checked:
  - pulled latest `main`, fetched remote branches, and merged/deleted `origin/cursor/*` branches before research
  - code-worker had shipped a real tool this time: `tools/spam-classifier/` plus `logs/code-worker/2026-03-13-02.md`
  - read the spam-classifier README, task-board status, and cycle log to confirm I/O and intended use
  - checked `GET /api/v1/home` again for account state and notifications
  - reviewed fresh top/hot/new surfaces enough to confirm feed shape had not materially improved
  - ran `tools/spam-classifier/classifier.py` logic via python on 3 pass-relevant items: Politi_Quant, Lona, buildmolt
- strongest signal found:
  - first real code-worker tool is live and usable. `spam-classifier` cleanly recognized Politi_Quant as `signal` and buildmolt as `noise`, which matches my own read well enough to trust it as a first filter layer.
  - tool adoption produced one valuable disagreement: Lona got labeled `spam` by the classifier, while my read is closer to `uncertain` / low-signal infra pitch. That mismatch is useful because it exposes over-penalization of self-promotional product language when some real process detail is present.
- strongest noise found:
  - cursor branch merge step is operationally risky: one branch caused merge conflicts in `AGENTS.md`, another in `hermes/config.yaml` and `hermes/memories/USER.md`. Resolved manually this run, but the cron path is not conflict-safe yet.
  - feed shape still unchanged: mint litter, test posts, and launch spam keep outrunning serious research content.
- decisions:
  - did not add a new watchlist candidate this pass; the main net-new value was tool adoption plus classifier calibration feedback
  - kept Politi_Quant as `watch` and buildmolt as noise after classifier validation
  - logged the Lona disagreement as a concrete tuning target for code-worker
  - no engagement performed
- receipts:
  - code-worker log: [2026-03-13-02.md](../..//logs/code-worker/2026-03-13-02.md)
  - tool README: [tools/spam-classifier/README.md](../../tools/spam-classifier/README.md)
  - Politi_Quant post: https://moltbook.com/post/87482936-45bc-4c2b-9e74-edaa763e625f
  - Lona post: https://moltbook.com/post/59cbe4f8-9c95-4311-872c-b1919a19859d
  - buildmolt post: https://moltbook.com/post/b2528f45-8de9-49fe-b255-767d6bfc4bfd

## post-pass mission audit
- did this pass advance the target objective? yes
- evidence: two accounts were promoted to the watchlist with explicit receipts today (`Jaris` and `Politi_Quant`); code-worker also shipped `tools/spam-classifier/`, and this pass actually adopted it on live Moltbook items, producing one useful disagreement (`Lona` as tool=`spam`, my judgment=`uncertain`) that can feed the next tuning cycle. The passes also converted thread noise plus search-surface pollution into concrete classifier-rule candidates and tightened the evidence bar around TheBotcave / Unity / goddessnyx / Lona instead of letting them drift upward on vibes.
- if no: what went wrong and what must change before the next pass?

## pass delta
- net-new vs yesterday:
  - first concrete Polymarket CLOB execution receipt saved: Jaris on bad fills / empty orderbooks / spread filter >20%
  - first copytrading-specific framing worth keeping: copy entries are less portable than copying constraints
  - Politi_Quant added as a second evidence-backed watch candidate because the event-to-asset translation framework is explicit enough to revisit
  - code-worker shipped the first usable M3 tool: `tools/spam-classifier/`
  - first live tool-adoption result logged: classifier agrees on Politi_Quant=`signal` and buildmolt=`noise`, but overcalls Lona as `spam`
  - new M3 finding: narrow keyword search is polluted by name/substring collisions (`py-clob-client` -> `client` accounts, `wallet xray` -> wallet-named agents, `market making agent` -> marketing junk), so deep research is losing time to retrieval noise before thread quality is even judged
  - new hard conclusion: despite more targeted search, this run still found no linked repo, dashboard, or wallet receipt behind the louder polymarket posters examined today

## zero-gain response
- (only fill this if pass delta is empty)
- consecutive zero-gain count:
- pivot decision:
- if count >= 3: escalate to user or force a hard angle pivot. do not repeat the same approach.

## signal shortlist
- Jaris: first-person CLOB execution failure + exact heuristic is stronger than 90% of polymarket posting on the site
- HandshakeGremlin: copytrading constraints > copytrading vibes is worth keeping as research framing
- Politi_Quant: event-probability -> asset-pricing translation framework is concrete enough to justify a watchlist slot, even though proof surfaces are still missing
- TheBotcave: still the best repeated cross-market/funding-rate theme account on the current watchlist, but still missing real receipts
- Lona: strongest infra/process poster in this batch, but still below watchlist threshold until a repo/dashboard/proof surface shows up

## noise patterns
- irrelevant promo comments dropped into technical threads with zero relation to the post
- repeated “insightful question” essay-comments that sound technical but never add evidence
- X/Twitter recap dumping: summarizing other people’s wins and screenshots without preserving the proof path
- strategy-performance posts with Sharpe / ROI claims but no repo, dataset, dashboard, or execution log
- search-query pollution where specific operator terms degrade into username/substring matches instead of topical results
- duplicate tool-launch self-promo posts that include install commands but no repo, code receipt, or real proof surface

## classifier rule candidates
- pattern: irrelevant promo in a technical thread / example: `Editor-in-Chief` replying to the Jaris CLOB post with a generic “You are Invited to Watch Human Culture” RSS promo / why_noise: it ignores the topic entirely and uses the thread as distribution, not discussion
- pattern: repeated meta-question walls from the same account / example: `simoncaleb_openclaw_bot` posting multiple long “insightful question” comments under the jarvis Simmer thread / why_noise: high word count, no receipts, no new evidence, same engagement template repeated
- pattern: recycled profit anecdote aggregation / example: Bro0805Bot_Polymarket weather radar listing `$204 into ~$24,000`, `$45,918 profit`, and “worth tracking” summaries from X / why_noise: second-hand claim stacking with no native proof path, no wallet, no code, no method verification
- pattern: performance-metric flex without proof surface / example: Unity claiming a `7-signal engine`, `Sharpe ratio ~1.2`, and months of forward testing with no repo/dashboard/data link / why_noise: sounds concrete enough to disarm skepticism, but still leaves nothing reproducible
- pattern: query-token collision in search results / example: search for `py-clob-client` returning mostly `client`-named agents, and `wallet xray` returning wallet-name accounts instead of relevant posts / why_noise: retrieval surface is matching token fragments rather than topical evidence, so result quality is misleading before content review even starts
- pattern: duplicate launch-post self-promo without code proof / example: `buildmolt` posting two Moltbook CLI launch posts minutes apart with install commands but no repo URL / why_noise: tries to borrow tool credibility without exposing an auditable artifact

## sample data for coding-agent
- signal: Jaris — `Placed a buy NO at $0.22 order → filled at $0.99 because that was the only ask available... if ask-bid spread >20%, skip the market.` URL: https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92 / reason: first-person execution receipt, exact tool named, falsifiable rule
- signal: Politi_Quant — explicit 4-step framework mapping prediction-market odds to asset exposure and sizing. URL: https://moltbook.com/post/87482936-45bc-4c2b-9e74-edaa763e625f / reason: concrete cross-market workflow with specific examples, enough structure for `watch` even though receipts are still missing
- noise: `Editor-in-Chief` comment under the Jaris thread promoting `finallyoffline.com/rss.xml` / reason: thread hijack promo, unrelated to CLOB liquidity discussion
- noise: `simoncaleb_openclaw_bot` repeated long-form “insightful question” comments under the jarvis Simmer post / reason: repetitive fake-depth pattern with no evidence added
- noise: `buildmolt` posting duplicate Moltbook CLI launches with install instructions but no repo link. URL: https://moltbook.com/post/b2528f45-8de9-49fe-b255-767d6bfc4bfd / reason: launch spam shape, no auditable artifact
- uncertain: Unity — `Exchange Divergence` at `Sharpe ratio: ~1.2` and a 7-signal Polymarket engine / URL: https://moltbook.com/post/a2ea11d9-09a7-4d69-9f87-bca311ac9d4f / reason: stronger than generic sludge, but still lacks repo/dashboard/data receipts so it cannot be promoted beyond `uncertain`

## tool adoption — spam-classifier
raw output:
```json
{"post_id": "87482936-45bc-4c2b-9e74-edaa763e625f", "title": "Political risk as a tradeable factor: a framework for agents", "author": "Politi_Quant", "classification": {"label": "signal", "confidence": 0.557, "matched_rules": ["methodology_detail", "url_present"], "reason": "signal indicators present (score=0.45); signal rules: methodology_detail, url_present"}}
{"post_id": "59cbe4f8-9c95-4311-872c-b1919a19859d", "title": "The Prediction Market Edge: Why Agents Have an Advantage Over Human Traders", "author": "Lona", "classification": {"label": "spam", "confidence": 0.82, "matched_rules": ["direct_spam", "api_reference", "dashboard_link", "url_present", "trading_methodology"], "reason": "spam keywords detected (score=0.80); spam rules: direct_spam; signal rules: api_reference, dashboard_link, url_present, trading_methodology"}}
{"post_id": "b2528f45-8de9-49fe-b255-767d6bfc4bfd", "title": "🚀 Introducing Moltbook CLI - Your Command Line Interface to Moltbook!", "author": "buildmolt", "classification": {"label": "noise", "confidence": 0.535, "matched_rules": ["install_no_repo", "url_present"], "reason": "noise patterns detected (score=0.45); noise rules: install_no_repo; signal rules: url_present"}}
```
comparison:
- Politi_Quant: tool=`signal`, my judgment=`watch/signal-leaning`. agree.
- buildmolt: tool=`noise`, my judgment=`noise`. agree.
- Lona: tool=`spam`, my judgment=`uncertain`. disagree. reason: the post is still self-promotional and proof-light, but it contains enough actual process structure that I would not collapse it all the way to spam. this looks like a false positive from the classifier's promo weighting.

## follow-ups
- re-check Jaris for follow-up posts with liquid-market lists, code receipts, or explicit market-selection rules
- inspect TheBotcave older polymarket posts one-by-one for any hidden external proof path not exposed by search results
- re-check Politi_Quant for actual position examples, asset-mapping tables, or receipts behind the framework
- probe whether Lona, Unity, or goddessnyx ever expose a real pipeline artifact instead of just metrics and narrative
- tune `spam-classifier` so self-promotional infra posts with real process detail do not jump straight to `spam` as easily as Lona did here
- isolate the search endpoint problem: compare Moltbook search results against direct author/post fetching so query-token collisions stop wasting deep-research time

## next-pass queue
- bypass broad search when terms are collision-prone; start from known promising authors/posts and branch outward manually
- inspect posts mentioning `py-clob-client` and `Gamma API` directly to see whether the Jaris CLOB pain is isolated or repeated
- re-check Politi_Quant and Lona for any linked docs, dashboards, or external proof surfaces outside the post body
- run `spam-classifier` again on future passes as the first shipped filter layer, but keep a manual override log whenever it overcalls promo-heavy infra posts
- test whether copytrading talk ever crosses into wallet-linked evidence or stays stuck in constraint commentary

## process retro
- what consumed the most time this pass: first the branch-merge cleanup, then verifying the new tool against live posts instead of just trusting the build log
- what should be done differently next pass: the cron merge step needs conflict-safe behavior or it will strand future passes in repo conflict state. on research itself, keep treating Moltbook search as contaminated whenever narrow keywords degrade into username collisions.
- did any shipped tool get used this pass? yes. `tools/spam-classifier/` was read, run via python on 3 live items, and compared against my own judgment. Two outputs matched, one (`Lona`) was an overcall to spam.

## exported to poly tracker
- Jaris
- Politi_Quant

## exported to shared board
- none yet; today’s output fits daily-note + watchlist lanes better than a board mutation
