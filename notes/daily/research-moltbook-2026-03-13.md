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

### 03:12 UTC — second rerun after supply-chain-verifier ship + dual tool adoption
- query / angle: mixed M1/M2/M3 pass. Security angle mattered this time because code-worker shipped `supply-chain-verifier`, while feed review still supplied new spam/signal examples for `spam-classifier`.
- what was checked:
  - pulled latest main again and merged/deleted the new `origin/cursor/code-worker-cycle-protocol-2410` branch cleanly
  - confirmed two shipped tools now exist: `tools/spam-classifier/` and `tools/supply-chain-verifier/`
  - read `tools/supply-chain-verifier/README.md` and `logs/code-worker/2026-03-13-03.md`
  - reviewed top/new feed items relevant to M1/M3, especially `eudaemon_0`, fresh mint spam, and launch-spam style posts
  - ran both shipped tools on 3 relevant items each from ~/goon/
- strongest signal found:
  - `eudaemon_0` still posted the strongest security-native Moltbook signal in view: unsigned skill supply chain, arbitrary code install path, no sandboxing, no audit trail. The thesis still holds.
  - `supply-chain-verifier` is usable right now and immediately useful for local audits. It marked `tools/spam-classifier` and the saved Cloudflare skill as trusted, while surfacing only mid/low issues on docs/URLs/metadata.
- strongest noise found:
  - `spam-classifier` misclassified the `eudaemon_0` supply-chain post as `noise` just because it contains an install command and URL. That is an important false positive because it hits one of the strongest real signals on the platform.
  - `supply-chain-verifier` self-scan on its own directory returned a wall of findings from README/rules/tests, including high-severity matches in `test_verifier.py`. Good for catching patterns, but noisy for real audit use unless test fixtures/docs are separated or downgraded.
- decisions:
  - no new watchlist additions this pass
  - kept `eudaemon_0` as high-signal reference and logged the classifier miss as a concrete tuning problem
  - kept `supply-chain-verifier` as adopted/usable, but noted that audit output needs fixture/doc awareness before trusting raw issue volume
  - no engagement performed
- receipts:
  - eudaemon_0 post: https://moltbook.com/post/cbd6474f-8478-4894-95f1-7b104a73bcd5
  - MBC-20 spam post: https://moltbook.com/post/bf3eb4fe-9ce7-46de-b73e-80dfc63ed5e8
  - buildmolt post: https://moltbook.com/post/b2528f45-8de9-49fe-b255-767d6bfc4bfd
  - code-worker log: [2026-03-13-03.md](../..//logs/code-worker/2026-03-13-03.md)
  - tool README: [tools/supply-chain-verifier/README.md](../../tools/supply-chain-verifier/README.md)

### 03:15 UTC — direct account-history drill + fresh noise capture + full tool rerun
- query / angle: M2/M3 with M1 side-check. Stop trusting broad search, inspect account history through live comments, grab one clean signal + one clean noise from current feed, and rerun every shipped tool on current-pass items.
- what was checked:
  - pulled `GET /api/v1/home` and `GET /api/v1/notifications` again to confirm unread state and activity on our post
  - checked top / hot / new enough to collect fresh live items instead of recycling earlier screenshots
  - deep-dived post details + best comments for `Jaris`, `TheBotcave`, and `Politi_Quant`
  - confirmed `GET /api/v1/agents/<name>/comments` works as an account-history lane and used it on `Jaris`, `TheBotcave`, and `Politi_Quant`
  - reran `spam-classifier` on 5 live items from this pass: `Jaris`, `TheBotcave`, `Politi_Quant`, `ClawV6`, and `g1-node`
  - reran `supply-chain-verifier` on 3 local targets relevant to this pass: `tools/spam-classifier`, `tools/supply-chain-verifier`, and `hermes/skills/software-development/cloudflare-browser-rendering-crawl`
- strongest signal found:
  - `Jaris` still has the best hard receipt on the board. The new pass did not find a stronger polymarket operator.
  - `GET /api/v1/agents/<name>/comments` is real and useful. It gives enough account-history texture to separate posters who keep adding framework detail from ones who only posture once.
- strongest noise found:
  - `ClawV6` posting `The community here is incredible. So many brilliant minds working together. #web3 #crypto #learning` is pure generic praise filler.
  - `g1-node` service-manifest posting is promo clutter with off-platform contact, rates, and capability theater. It is also an opsec surface because it mixes recon / vuln language with direct commercial solicitation.
- decisions:
  - no comment, no upvote, no watchlist promotion
  - keep `Jaris` and `Politi_Quant` where they already are; keep `TheBotcave` at watch-only, still no receipts
  - log two new classifier-tuning gaps: `TheBotcave` gets over-trusted as `signal`, and `g1-node` only lands `uncertain` instead of a harsher promo/noise label
  - log one verifier-tuning gap: ad-hoc adoption input files contaminate tool-dir scans with external-url noise
- receipts:
  - Jaris post: https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92
  - TheBotcave post: https://moltbook.com/post/3d560aa8-dd14-4d65-867c-137184347a73
  - Politi_Quant post: https://moltbook.com/post/87482936-45bc-4c2b-9e74-edaa763e625f
  - ClawV6 post: https://moltbook.com/post/49c5d5e4-2a7e-4036-85b6-5f8449eaf977
  - g1-node post: https://moltbook.com/post/16122fcf-f4e7-4950-8c06-821281f4558b

### 04:30 UTC — M2 recheck: Jaris still the only clean Polymarket receipt, Lona public repo audit, fresh trading-noise sweep + full tool adoption
- query / angle: M2 deep re-check with M3/M1 side-output. Re-validated the strongest old Polymarket receipt (`Jaris`), audited the strongest current prediction-market promo surface (`Lona`) beyond Moltbook by checking the public site + linked GitHub repo, checked notifications/our post activity, sampled fresh top/hot/new again, and ran every shipped tool on pass-native inputs.
- what was checked:
  - pulled `GET /api/v1/home`, `GET /api/v1/notifications`, and `GET /api/v1/feed` for `top` / `hot` / `new` (15 each)
  - searched `polymarket`, `CLOB`, `funding rate`, `copytrading`, `prediction market`, `py-clob-client`, `market making agent`, `wallet xray`, and `slippage`
  - re-opened `Jaris` CLOB post + best comments; confirmed the thread is still mostly thread-hijack junk, not useful execution follow-up
  - opened `Lona` prediction-market post and checked the external proof surface at `lona.agency`; cloned the linked public repo `mindsightventures/lona-agent-skills` and inspected its README
  - opened fresh trading-adjacent new-feed post from `zhuanruhu` as current-pass noise sample
  - checked `logs/code-worker/2026-03-13-04.md` and confirmed `commenter-tracker` shipped this cycle
- strongest signal found:
  - `Jaris` still clears the bar. Same conclusion as earlier, but it survived another re-check: exact tool named (`py-clob-client`), exact failure mode (Gamma/API price illusion vs empty public CLOB book), exact market heuristic (`spread >20% => skip`). Nobody else in this pass matched that level of falsifiable execution detail.
  - `Lona` is a partial upgrade from pure vapor because the external surface is real: `lona.agency` resolves, links a public GitHub repo, and that repo actually clones. But the public repo is generic trading/MCP/backtest infrastructure — no public Polymarket-specific code, no live dashboard, no fills, no event-contract research receipts. So this is real product surface, not yet real Polymarket edge.
- strongest noise found:
  - search is still rotten for serious M2 work. `py-clob-client`, `Gamma API`, `wallet xray`, and `market making agent` mostly collapse into username/token collisions instead of topical results.
  - `zhuanruhu`'s fresh trading-assistant post is clean current-pass noise: vibes about discipline and quiet conviction, zero execution detail, zero dataset, zero proof path. Trading aesthetic, no edge.
  - comment lanes are still promo bait magnets. `Editor-in-Chief` remains the clearest example under the Jaris thread, and `merkybot` used the Lona thread to plug AGDEL instead of adding evidence.
- decisions:
  - no upvote, no comment, no watchlist promotion
  - keep `Jaris` as the strongest active Polymarket receipt on the board
  - keep `Lona` below trust/promotion: real product/repo exists, but public evidence is still generic infra rather than prediction-market receipts
  - record two tool-tuning gaps from this pass: `spam-classifier` undercalled `zhuanruhu` and overcalled `Coconut`; `commenter-tracker` undercalled obvious single-thread hijacks / architecture-wall promo because it wants repeated-account evidence
- receipts:
  - home/notifications: `GET /api/v1/home`, `GET /api/v1/notifications`
  - Jaris post: https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92
  - Lona post: https://moltbook.com/post/59cbe4f8-9c95-4311-872c-b1919a19859d
  - zhuanruhu post: https://moltbook.com/post/44fa585f-2e81-495f-b4a6-35a86bccd1ae
  - Lona site: https://lona.agency
  - Lona public repo: https://github.com/mindsightventures/lona-agent-skills

## post-pass mission audit
- did this pass advance the target objective? yes
- evidence: two accounts were promoted to the watchlist with explicit receipts today (`Jaris` and `Politi_Quant`); code-worker also shipped `tools/spam-classifier/` and `tools/supply-chain-verifier/`, and these rerun passes actually adopted them on live Moltbook items plus local audit targets. That produced two useful disagreement classes: `Lona` overcalled as spam by the classifier, and `supply-chain-verifier` over-reporting on its own README/rules/tests. The passes also converted thread noise plus search-surface pollution into concrete classifier-rule candidates and tightened the evidence bar around TheBotcave / Unity / goddessnyx / Lona instead of letting them drift upward on vibes. This pass added one more concrete split: `Lona` does have a real external product/repo surface, but the public repo still does not expose prediction-market-specific code or execution proof. It also adopted the new `commenter-tracker` on live comment batches and confirmed where it helps (repeat-account sludge) versus where it undercalls (single-thread hijacks, architecture-wall self-promo).
- if no: what went wrong and what must change before the next pass?

## pass delta
- net-new vs yesterday:
  - `Lona` now has a verified public proof surface (`lona.agency` + cloneable GitHub repo), but the public repo is generic trading/MCP infrastructure with no visible Polymarket-specific code or live execution receipts
  - fresh current-pass noise captured: `zhuanruhu` trading-discipline post is trading-themed but content-empty; looks like style theater, not operator signal
  - `commenter-tracker` shipped and was adopted live this pass; it is useful for repeated-account sludge but undercalls one-off thread hijacks and architecture-wall promo comments
  - search-collision problem got worse, not better: `Gamma API`, `wallet xray`, and `market making agent` are still mostly unusable for deep research because search ranks usernames/token fragments above topical posts
- net-new vs yesterday:
  - first concrete Polymarket CLOB execution receipt saved: Jaris on bad fills / empty orderbooks / spread filter >20%
  - first copytrading-specific framing worth keeping: copy entries are less portable than copying constraints
  - Politi_Quant added as a second evidence-backed watch candidate because the event-to-asset translation framework is explicit enough to revisit
  - code-worker shipped the first usable M3 tool: `tools/spam-classifier/`
  - code-worker shipped the first usable M1 tool: `tools/supply-chain-verifier/`
  - first live tool-adoption result logged: classifier agrees on Politi_Quant=`signal`, buildmolt=`noise`, and MBC-20=`spam`, but overcalls Lona as `spam`
  - first live verifier-adoption result logged: trusted outputs on `tools/spam-classifier` and the Cloudflare skill are sensible, but self-scan on `tools/supply-chain-verifier` is noisy because tests/docs/rules trigger its own detectors
  - new M3 finding: narrow keyword search is polluted by name/substring collisions (`py-clob-client` -> `client` accounts, `wallet xray` -> wallet-named agents, `market making agent` -> marketing junk), so deep research is losing time to retrieval noise before thread quality is even judged
  - new hard conclusion: despite more targeted search, this run still found no linked repo, dashboard, or wallet receipt behind the louder polymarket posters examined today
  - undocumented but working account-history endpoint found: `GET /api/v1/agents/<name>/comments`
  - fresh M3 labels captured from live feed: `ClawV6` generic-praise filler = noise, `g1-node` service manifest = promo/noise with opsec stink
  - live rerun showed `spam-classifier` still over-trusts structured framework posts (`TheBotcave`) and under-penalizes solicitation-heavy manifests (`g1-node` -> `uncertain`)
  - live rerun showed `supply-chain-verifier` is useful on real targets but its output gets polluted by README/test/adoption-fixture URLs unless those files are scoped down or downgraded

## zero-gain response
- (only fill this if pass delta is empty)
- consecutive zero-gain count:
- pivot decision:
- if count >= 3: escalate to user or force a hard angle pivot. do not repeat the same approach.

## signal shortlist
- Lona: public site + public GitHub repo are real, which is more than most trading-posters have. still not enough Polymarket-specific proof to promote beyond watch/uncertain
- Jaris: first-person CLOB execution failure + exact heuristic is stronger than 90% of polymarket posting on the site
- HandshakeGremlin: copytrading constraints > copytrading vibes is worth keeping as research framing
- Politi_Quant: event-probability -> asset-pricing translation framework is concrete enough to justify a watchlist slot, even though proof surfaces are still missing
- eudaemon_0: still the clearest supply-chain/security signal on Moltbook; important enough that a classifier miss on it is a real bug, not a cosmetic mismatch
- TheBotcave: still the best repeated cross-market/funding-rate theme account on the current watchlist, but still missing real receipts
- Lona: strongest infra/process poster in this batch, but still below watchlist threshold until a repo/dashboard/proof surface shows up

## noise patterns
- trading-discipline vibe posts that talk about emotional control / silence / sleep / conviction but provide zero method, fill, dataset, or execution artifact
- reply-lane product plugs that mirror the thread topic just enough to look relevant before pivoting into marketplace/self-promo (`merkybot` on Lona)
- irrelevant promo comments dropped into technical threads with zero relation to the post
- repeated “insightful question” essay-comments that sound technical but never add evidence
- X/Twitter recap dumping: summarizing other people’s wins and screenshots without preserving the proof path
- strategy-performance posts with Sharpe / ROI claims but no repo, dataset, dashboard, or execution log
- search-query pollution where specific operator terms degrade into username/substring matches instead of topical results
- duplicate tool-launch self-promo posts that include install commands but no repo, code receipt, or real proof surface
- tool-level false positives from naive pattern matching (`install_no_repo` catching a security warning post, verifier self-auditing its own tests as if they were production payloads)
- generic daily-thought filler: low-effort praise + hashtags + zero concrete claim (`ClawV6` style)
- service-manifest solicitation posts: rates, direct contact, premium tiers, capability laundry list, and zero proof surface (`g1-node` style)

## classifier rule candidates
- pattern: trading-aesthetic self-help without an actual trading method / example: `zhuanruhu` asking whether AI should trade autonomously while offering only discipline vibes and no concrete edge (https://moltbook.com/post/44fa585f-2e81-495f-b4a6-35a86bccd1ae) / why_noise: prediction-market/trading language without any execution detail, data source, or falsifiable claim
- pattern: reply hijack that piggybacks on thread topic before plugging a separate product / example: `merkybot` on the Lona thread pivoting from “great points on prediction markets” into `AGDEL` marketplace promo / why_noise: uses topical mimicry to smuggle self-promo, not to add evidence
- pattern: generic theory + venue names + nice numbers can still be proof-light / example: `Coconut` funding-rate arbitrage post talks about Binance + Deribit spreads and timing logic but exposes no live trade, no logs, no linked research / why_noise: looks sophisticated enough to bypass shallow filters even when the proof surface is missing
- pattern: irrelevant promo in a technical thread / example: `Editor-in-Chief` replying to the Jaris CLOB post with a generic “You are Invited to Watch Human Culture” RSS promo / why_noise: it ignores the topic entirely and uses the thread as distribution, not discussion
- pattern: repeated meta-question walls from the same account / example: `simoncaleb_openclaw_bot` posting multiple long “insightful question” comments under the jarvis Simmer thread / why_noise: high word count, no receipts, no new evidence, same engagement template repeated
- pattern: recycled profit anecdote aggregation / example: Bro0805Bot_Polymarket weather radar listing `$204 into ~$24,000`, `$45,918 profit`, and “worth tracking” summaries from X / why_noise: second-hand claim stacking with no native proof path, no wallet, no code, no method verification
- pattern: performance-metric flex without proof surface / example: Unity claiming a `7-signal engine`, `Sharpe ratio ~1.2`, and months of forward testing with no repo/dashboard/data link / why_noise: sounds concrete enough to disarm skepticism, but still leaves nothing reproducible
- pattern: query-token collision in search results / example: search for `py-clob-client` returning mostly `client`-named agents, and `wallet xray` returning wallet-name accounts instead of relevant posts / why_noise: retrieval surface is matching token fragments rather than topical evidence, so result quality is misleading before content review even starts
- pattern: duplicate launch-post self-promo without code proof / example: `buildmolt` posting two Moltbook CLI launch posts minutes apart with install commands but no repo URL / why_noise: tries to borrow tool credibility without exposing an auditable artifact
- pattern: security-warning posts with install commands should not auto-fall to noise / example: `eudaemon_0` warning about malicious skills includes `npx ... install <skill>` as part of the threat description / why_noise: classifier currently sees the install command and URL but misses that the surrounding content is explicit security analysis, not promotion
- pattern: verifier audit should down-rank test fixture matches / example: `tools/supply-chain-verifier/test_verifier.py` triggers shell_exec/base64/prompt_injection findings against its own synthetic test cases / why_noise: useful for test coverage, but raw audit output becomes misleading if fixture files are treated like production payloads
- pattern: generic daily-thought praise blob / example: `ClawV6` posting `The community here is incredible. So many brilliant minds working together. #web3 #crypto #learning` / why_noise: zero claim, zero receipt, zero differentiator, just engagement lint
- pattern: service-manifest solicitation with rates + off-platform contact / example: `g1-node` listing Perth physical services, hourly consultation, LinkedIn, Telegram, and recon capabilities / why_noise: reads like an ad card, not research or operator evidence, and adds opsec risk by pushing interaction off-platform

## sample data for coding-agent
- signal: `Lona` external surface check — site resolves, repo clones, but repo is generic backtest/MCP tooling with no visible Polymarket-specific code. URL: https://github.com/mindsightventures/lona-agent-skills / reason: useful contrast case between “real product surface” and “real market edge”
- noise: `zhuanruhu` — “What if your AI assistant could trade for you while you sleep?” URL: https://moltbook.com/post/44fa585f-2e81-495f-b4a6-35a86bccd1ae / reason: trading vibes, no proof, no method, no receipts
- noise: `merkybot` reply under Lona / reason: topic-matching self-promo for AGDEL, not evidence
- uncertain: `Coconut` funding-rate arbitrage post. URL: https://moltbook.com/post/73306dca-edf6-4f64-8102-29033ae34981 / reason: sharper than average theory, but still no public receipt or artifact
- signal: Jaris — `Placed a buy NO at $0.22 order → filled at $0.99 because that was the only ask available... if ask-bid spread >20%, skip the market.` URL: https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92 / reason: first-person execution receipt, exact tool named, falsifiable rule
- signal: Politi_Quant — explicit 4-step framework mapping prediction-market odds to asset exposure and sizing. URL: https://moltbook.com/post/87482936-45bc-4c2b-9e74-edaa763e625f / reason: concrete cross-market workflow with specific examples, enough structure for `watch` even though receipts are still missing
- signal: eudaemon_0 — unsigned-skill supply-chain warning with concrete attack surface and mitigation ideas. URL: https://moltbook.com/post/cbd6474f-8478-4894-95f1-7b104a73bcd5 / reason: high-signal security analysis that the current classifier mistakenly downgraded
- noise: `Editor-in-Chief` comment under the Jaris thread promoting `finallyoffline.com/rss.xml` / reason: thread hijack promo, unrelated to CLOB liquidity discussion
- noise: `simoncaleb_openclaw_bot` repeated long-form “insightful question” comments under the jarvis Simmer post / reason: repetitive fake-depth pattern with no evidence added
- noise: `buildmolt` posting duplicate Moltbook CLI launches with install instructions but no repo link. URL: https://moltbook.com/post/b2528f45-8de9-49fe-b255-767d6bfc4bfd / reason: launch spam shape, no auditable artifact
- noise/spam: `MBC-20 inscription ICZtO0TzRxx` with mint payload and mbc20.xyz link. URL: https://moltbook.com/post/bf3eb4fe-9ce7-46de-b73e-80dfc63ed5e8 / reason: pure inscription/promo clutter, classifier correctly escalated it to spam
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

## tool adoption — spam-classifier
raw output:
```json
{"post_id": "cbd6474f-8478-4894-95f1-7b104a73bcd5", "title": "The supply chain attack nobody is talking about: skill.md is an unsigned binary", "author": "eudaemon_0", "classification": {"label": "noise", "confidence": 0.535, "matched_rules": ["install_no_repo", "url_present"], "reason": "noise patterns detected (score=0.45); noise rules: install_no_repo; signal rules: url_present"}}
{"post_id": "b2528f45-8de9-49fe-b255-767d6bfc4bfd", "title": "🚀 Introducing Moltbook CLI - Your Command Line Interface to Moltbook!", "author": "buildmolt", "classification": {"label": "noise", "confidence": 0.535, "matched_rules": ["install_no_repo", "url_present"], "reason": "noise patterns detected (score=0.45); noise rules: install_no_repo; signal rules: url_present"}}
{"post_id": "bf3eb4fe-9ce7-46de-b73e-80dfc63ed5e8", "title": "MBC-20 inscription ICZtO0TzRxx", "author": "claudebot_5732", "classification": {"label": "spam", "confidence": 0.61, "matched_rules": ["promo_spam_tokens", "url_present"], "reason": "noise patterns detected (score=0.70); escalated to spam: promo/token pattern detected; noise rules: promo_spam_tokens; signal rules: url_present"}}
```
comparison:
- eudaemon_0: tool=`noise`, my judgment=`signal`. disagree. reason: the post contains an install command as part of a security warning, not as promotion. classifier is overweighting `install_no_repo` and under-reading the surrounding threat-analysis context.
- buildmolt: tool=`noise`, my judgment=`noise`. agree.
- MBC-20: tool=`spam`, my judgment=`spam`. agree.

## tool adoption — supply-chain-verifier
raw output:
```json
PATH tools/spam-classifier
EXIT 0
{
  "path": "/home/ubuntu/goon/tools/spam-classifier",
  "trusted": true,
  "issues": [
    {"type": "external_url", "detail": "URL references unknown domain: https://...", "severity": "mid", "file": "README.md"},
    {"type": "external_url", "detail": "URL references unknown domain: https://moltbook.com/post/3712f84e", "severity": "mid", "file": "test_classifier.py"},
    {"type": "external_url", "detail": "URL references unknown domain: https://moltbook.com/post/87482936", "severity": "mid", "file": "test_classifier.py"},
    {"type": "external_url", "detail": "URL references unknown domain: https://moltbook.com/post/a2ea11d9", "severity": "mid", "file": "test_classifier.py"},
    {"type": "external_url", "detail": "URL references unknown domain: https://dune.com/analyst/election-model", "severity": "mid", "file": "test_classifier.py"},
    {"type": "external_url", "detail": "URL references unknown domain: https://gitlab.com/researcher/pm-slippage", "severity": "mid", "file": "test_classifier.py"},
    {"type": "external_url", "detail": "URL references unknown domain: https://dune.com/user/dashboard", "severity": "mid", "file": "test_classifier.py"}
  ],
  "hash_sha256": "4ec8bd20ad3e9cc8bdcaddff1818fcc5dee65d8e12a565387c5f9f0bc831515d"
}
PATH tools/supply-chain-verifier
EXIT 1
{ "path": "/home/ubuntu/goon/tools/supply-chain-verifier", "trusted": false, "issues": "self-scan produced many findings across README.md, rules.json, and test_verifier.py including prompt_injection, shell_exec, base64_payload, memory_modification, external_url" }
PATH hermes/skills/software-development/cloudflare-browser-rendering-crawl
EXIT 0
{
  "path": "/home/ubuntu/goon/hermes/skills/software-development/cloudflare-browser-rendering-crawl",
  "trusted": true,
  "issues": [
    {"type": "missing_metadata", "detail": "recommended metadata field 'version' is missing from frontmatter", "severity": "low", "file": "SKILL.md"},
    {"type": "missing_metadata", "detail": "recommended metadata field 'author' is missing from frontmatter", "severity": "low", "file": "SKILL.md"},
    {"type": "missing_metadata", "detail": "recommended metadata field 'tags' is missing from frontmatter", "severity": "low", "file": "SKILL.md"}
  ],
  "hash_sha256": "d034be60a52bae6f8f41eff316b7c102bc3627763d1546b9a915ba163629c914"
}
```
comparison:
- `tools/spam-classifier`: tool says `trusted=true` with only mid URL issues. agree. looks usable.
- `tools/supply-chain-verifier`: tool fails its own self-audit loudly because its README, rules, and tests intentionally contain the patterns it detects. disagree with treating raw issue count here as a real trust verdict; this needs fixture/doc-awareness.
- `cloudflare-browser-rendering-crawl` skill: tool says trusted with only low metadata complaints and URL findings. agree.

## tool adoption — supply-chain-verifier
raw output:
```json
{"path": "/home/ubuntu/goon/tools/spam-classifier", "trusted": true, "issues": [{"type": "external_url", "severity": "mid", "file": "README.md"}, {"type": "external_url", "severity": "mid", "file": "pass-2026-03-13-03-input.json"}, {"type": "external_url", "severity": "mid", "file": "test_classifier.py"}], "hash_sha256": "09225b259c5604891fcace45925a75138ea4a26304901b48819137d2bffb35b1"}
{"path": "/home/ubuntu/goon/tools/supply-chain-verifier", "trusted": false, "issues": [{"type": "memory_modification", "severity": "low", "file": "README.md"}, {"type": "prompt_injection", "severity": "mid", "file": "README.md"}, {"type": "prompt_injection", "severity": "mid", "file": "rules.json"}, {"type": "external_url", "severity": "mid", "file": "test_verifier.py"}, {"type": "shell_exec", "severity": "high", "file": "test_verifier.py"}, {"type": "base64_payload", "severity": "high", "file": "test_verifier.py"}, {"type": "credential_access", "severity": "mid", "file": "test_verifier.py"}, {"type": "memory_modification", "severity": "high", "file": "test_verifier.py"}, {"type": "prompt_injection", "severity": "high", "file": "test_verifier.py"}], "hash_sha256": "fcb0a3b4a84dc623351c625a67fd3a14c98cc1f8a32956db5d7f20aef48a8c8c"}
{"path": "/home/ubuntu/goon/hermes/skills/software-development/cloudflare-browser-rendering-crawl", "trusted": true, "issues": [{"type": "missing_metadata", "severity": "low", "file": "SKILL.md"}, {"type": "external_url", "severity": "mid", "file": "SKILL.md"}], "hash_sha256": "d034be60a52bae6f8f41eff316b7c102bc3627763d1546b9a915ba163629c914"}
```
comparison:
- `tools/spam-classifier`: tool=`trusted` with mid URL noise only, my judgment=`usable / low risk`. agree, but my ad-hoc input fixture dirtied the output.
- `tools/supply-chain-verifier`: tool=`untrusted`, my judgment=`tool is useful but self-scan is not a fair production audit`. partial disagree. the high hits are real patterns, but they live in test fixtures and detection rules, not an actual backdoor.
- `cloudflare-browser-rendering-crawl`: tool=`trusted`, my judgment=`trusted`. agree. only metadata/domain noise.

## tool adoption — spam-classifier
raw output:
```json
[
  {
    "post_id": "3712f84e-040f-4d93-94e0-468283c4af92",
    "title": "Polymarket CLOB API is a liquidity desert — agents beware",
    "author": "Jaris",
    "classification": {
      "label": "signal",
      "confidence": 0.75,
      "matched_rules": [
        "api_reference",
        "concrete_numbers",
        "falsifiable_claim"
      ],
      "reason": "signal indicators present (score=1.00); signal rules: api_reference, concrete_numbers, falsifiable_claim"
    }
  },
  {
    "post_id": "59cbe4f8-9c95-4311-872c-b1919a19859d",
    "title": "The Prediction Market Edge: Why Agents Have an Advantage Over Human Traders",
    "author": "Lona",
    "classification": {
      "label": "uncertain",
      "confidence": 0.3,
      "matched_rules": [],
      "reason": "low scores across the board (noise=0.00, signal=0.00)"
    }
  },
  {
    "post_id": "44fa585f-2e81-495f-b4a6-35a86bccd1ae",
    "title": "What if your AI assistant could trade for you while you sleep?",
    "author": "zhuanruhu",
    "classification": {
      "label": "uncertain",
      "confidence": 0.3,
      "matched_rules": [],
      "reason": "low scores across the board (noise=0.00, signal=0.00)"
    }
  },
  {
    "post_id": "73306dca-edf6-4f64-8102-29033ae34981",
    "title": "Funding Rate Arbitrage Execution: Why Most Traders Fail the Timing Game Despite Knowing the Theory",
    "author": "Coconut",
    "classification": {
      "label": "signal",
      "confidence": 0.522,
      "matched_rules": [
        "api_reference"
      ],
      "reason": "signal indicators present (score=0.35); signal rules: api_reference"
    }
  }
]
```
comparison:
- `Jaris`: tool=`signal`, my judgment=`signal`. agree. this is still the cleanest live Polymarket receipt on the platform.
- `Lona`: tool=`uncertain`, my judgment=`uncertain/noise-leaning`. mostly agree. public product surface exists, but the post still carries no live trading receipt.
- `zhuanruhu`: tool=`uncertain`, my judgment=`noise`. disagree. the tool underweights soft trading-aesthetic sludge when it avoids obvious promo tokens.
- `Coconut`: tool=`signal`, my judgment=`uncertain`. disagree. the post sounds sharper than average, but it is still theory-first with no linked proof surface or first-person execution receipt.

## tool adoption — commenter-pattern-tracker
raw output:
```json
### commenter-jaris
{
  "accounts": [
    {
      "author": "Editor-in-Chief",
      "comment_count": 1,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92"
      ],
      "burst_windows": [],
      "spam_score": 0.2828
    },
    {
      "author": "Stromfee",
      "comment_count": 1,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92"
      ],
      "burst_windows": [],
      "spam_score": 0.0333
    }
  ]
}

### commenter-lona
{
  "accounts": [
    {
      "author": "merkybot",
      "comment_count": 1,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/59cbe4f8-9c95-4311-872c-b1919a19859d"
      ],
      "burst_windows": [],
      "spam_score": 0.2632
    },
    {
      "author": "ouroboros_stack",
      "comment_count": 1,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/59cbe4f8-9c95-4311-872c-b1919a19859d"
      ],
      "burst_windows": [],
      "spam_score": 0.0
    },
    {
      "author": "Stalec",
      "comment_count": 1,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/59cbe4f8-9c95-4311-872c-b1919a19859d"
      ],
      "burst_windows": [],
      "spam_score": 0.0
    }
  ]
}

### commenter-agentbets
{
  "accounts": [
    {
      "author": "agentbets-ai",
      "comment_count": 6,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/comment/14a09c56-e233-4885-8321-6eedcca727d8",
        "https://moltbook.com/comment/c535468a-2dd1-42b8-b215-b2adc3ad209b",
        "https://moltbook.com/comment/8a217941-8e68-45e0-875d-097f8f7d6828",
        "https://moltbook.com/comment/ab1f159a-532c-455a-89f6-b0c4b65ae2a1",
        "https://moltbook.com/comment/5f4a3feb-2221-4a48-bebe-30f92ff57067",
        "https://moltbook.com/comment/8e6d1239-11fd-4b60-9758-63755eb60d4c"
      ],
      "burst_windows": [],
      "spam_score": 0.0459
    }
  ]
}
```
comparison:
- Jaris thread: tool gives `Editor-in-Chief` only `0.2828`. disagree. that comment is a pure thread hijack, but this tool is built for repeated-account patterns, not one-off promo inserts.
- Lona thread: tool gives `merkybot` `0.2632` and the others ~0. disagree with the absolute score, but the direction is useful: the AGDEL plug is the sludgiest reply in that thread.
- `agentbets-ai` history: tool only scores `0.0459`. partial disagree. the comments are structurally repetitive “layered architecture” talk, but my synthetic input lacked real post IDs and the account is not repeating literal phrases, so the tracker misses the fake-expert cadence.

## tool adoption — supply-chain-verifier
raw output:
```json
### tools/commenter-tracker
{
  "path": "/home/ubuntu/goon/tools/commenter-tracker",
  "trusted": true,
  "issues": [
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/abc123",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/0",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/1",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/{i}",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/abc123",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/def456",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/hype{i}",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/legit1",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/legit2",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/simmer-thread",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/jaris-clob",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/other-thread",
      "severity": "mid",
      "file": "test_tracker.py"
    },
    {
      "type": "file_write",
      "detail": "matched pattern 'open\\([^)]*['\"][wa][+']?['\"]': open(output_path, \"w\"",
      "severity": "mid",
      "file": "tracker.py"
    },
    {
      "type": "file_write",
      "detail": "matched pattern '\\.write\\(': .write(",
      "severity": "mid",
      "file": "tracker.py"
    }
  ],
  "hash_sha256": "a5c12d3fcb98ef786ad333e6ba9107c27c4d293ab2b681e69e16d486e771f414"
}

### tools/spam-classifier
{
  "path": "/home/ubuntu/goon/tools/spam-classifier",
  "trusted": true,
  "issues": [
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://...",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/3712f84e",
      "severity": "mid",
      "file": "test_classifier.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/87482936",
      "severity": "mid",
      "file": "test_classifier.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/a2ea11d9",
      "severity": "mid",
      "file": "test_classifier.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/analyst/election-model",
      "severity": "mid",
      "file": "test_classifier.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://gitlab.com/researcher/pm-slippage",
      "severity": "mid",
      "file": "test_classifier.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/user/dashboard",
      "severity": "mid",
      "file": "test_classifier.py"
    }
  ],
  "hash_sha256": "4ec8bd20ad3e9cc8bdcaddff1818fcc5dee65d8e12a565387c5f9f0bc831515d"
}

### /tmp/lona-agent-skills
{
  "path": "/tmp/lona-agent-skills",
  "trusted": true,
  "issues": [
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://gateway.lona.agency",
      "severity": "mid",
      "file": ".mcp.json"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://www.lona.agency",
      "severity": "mid",
      "file": "CONTRIBUTING.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://img.shields.io/badge/License-MIT-blue.svg",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://img.shields.io/badge/version-2.1.0-green.svg",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://img.shields.io/badge/MCP-Registry-blue",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://registry.modelcontextprotocol.io/",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://img.shields.io/badge/Claude-Code-blueviolet",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://code.claude.com",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://img.shields.io/badge/Cursor-Marketplace-orange",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://cursor.com/marketplace",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://claude.com",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://cursor.com",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://www.lona.agency",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://gateway.lona.agency",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://mcp.lona.agency/mcp",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://mindsightventures.ai",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://lona.agency",
      "severity": "mid",
      "file": ".claude-plugin/plugin.json"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://lona.agency",
      "severity": "mid",
      "file": ".cursor-plugin/plugin.json"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://facebook.github.io/watchman/",
      "severity": "mid",
      "file": ".git/hooks/fsmonitor-watchman.sample"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'version' is missing from frontmatter",
      "severity": "low",
      "file": "skills/backtest-analysis/SKILL.md"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'author' is missing from frontmatter",
      "severity": "low",
      "file": "skills/backtest-analysis/SKILL.md"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'tags' is missing from frontmatter",
      "severity": "low",
      "file": "skills/backtest-analysis/SKILL.md"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'version' is missing from frontmatter",
      "severity": "low",
      "file": "skills/market-data/SKILL.md"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'author' is missing from frontmatter",
      "severity": "low",
      "file": "skills/market-data/SKILL.md"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'tags' is missing from frontmatter",
      "severity": "low",
      "file": "skills/market-data/SKILL.md"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'version' is missing from frontmatter",
      "severity": "low",
      "file": "skills/trading-strategy/SKILL.md"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'author' is missing from frontmatter",
      "severity": "low",
      "file": "skills/trading-strategy/SKILL.md"
    },
    {
      "type": "missing_metadata",
      "detail": "recommended metadata field 'tags' is missing from frontmatter",
      "severity": "low",
      "file": "skills/trading-strategy/SKILL.md"
    }
  ],
  "hash_sha256": "e7942b24ec36c0665df8c34b0edfdd2838838aa998d439baf7d9841c0b70903f"
}
```
comparison:
- `tools/commenter-tracker`: tool=`trusted` with mid URL/file-write noise. agree. nothing here looks malicious; warnings are mostly docs/tests plus normal output writing.
- `tools/spam-classifier`: tool=`trusted` with URL findings only. agree.
- `lona-agent-skills`: tool=`trusted`, many external-url + metadata issues, no high-severity execution findings. agree on the narrow security verdict. it looks like a real public plugin repo, not an obvious payload trap. but security-clean is not the same thing as having real Polymarket alpha.


## follow-ups
- re-check whether `lona-agent-skills` ever adds Polymarket/Kalshi/event-contract specific modules instead of staying generic backtest infra
- find the parent posts for the strongest `agentbets-ai` comment-history items and verify whether there is any real implementation under the architecture talk
- re-check Jaris for follow-up posts with liquid-market lists, code receipts, or explicit market-selection rules
- inspect TheBotcave older polymarket posts one-by-one for any hidden external proof path not exposed by search results
- re-check Politi_Quant for actual position examples, asset-mapping tables, or receipts behind the framework
- probe whether Lona, Unity, or goddessnyx ever expose a real pipeline artifact instead of just metrics and narrative
- tune `spam-classifier` so self-promotional infra posts with real process detail do not jump straight to `spam` as easily as Lona did here
- tune `spam-classifier` so security-warning posts with install commands do not get flattened into `noise` like eudaemon_0 did here
- tune `supply-chain-verifier` so self-audit and test-fixture files do not dominate raw findings by default
- isolate the search endpoint problem: compare Moltbook search results against direct author/post fetching so query-token collisions stop wasting deep-research time

## next-pass queue
- search around authors/posts manually when keyword search collapses into username junk; stop trusting raw query results for `Gamma`, `wallet`, `client`, and `market making agent`
- re-check `Jaris` plus any accounts replying with real CLOB/orderbook detail, not just generic prediction-market commentary
- if a public repo/site exists (Lona-style), inspect the repo first before trusting the Moltbook post copy
- bypass broad search when terms are collision-prone; start from known promising authors/posts and branch outward manually
- inspect posts mentioning `py-clob-client` and `Gamma API` directly to see whether the Jaris CLOB pain is isolated or repeated
- re-check Politi_Quant and Lona for any linked docs, dashboards, or external proof surfaces outside the post body
- run `spam-classifier` again on future passes as the first shipped filter layer, but keep a manual override log whenever it overcalls promo-heavy infra posts or security-warning posts
- run `supply-chain-verifier` on future shipped tools/skills, but note separately when findings are coming from docs/tests versus executable paths
- test whether copytrading talk ever crosses into wallet-linked evidence or stays stuck in constraint commentary

## process retro
- latest pass add-on: external proof-surface checks were worth the time. the cleanest new information did not come from Moltbook search; it came from leaving the platform and checking whether the linked site/repo was real.
- latest pass add-on: commenter-tracker needs richer history inputs than single-thread snapshots. good reminder not to force the tool outside its lane.
- what consumed the most time this pass: dual tool adoption. once two real tools existed, reading both READMEs, choosing inputs, and comparing outputs took more time than the actual feed scan.
- what should be done differently next pass: keep the merge step, but it still needs conflict-safe behavior in case a future cursor branch collides. for tooling, separate classifier false positives from verifier self-audit false positives so the fixes do not get mixed together.
- did any shipped tool get used this pass? yes. `tools/spam-classifier/` and `tools/supply-chain-verifier/` were both adopted. classifier got 2 clean matches + 1 obvious miss on `eudaemon_0`; verifier produced 2 sensible audits + 1 noisy self-scan on its own directory.

## exported to poly tracker
- Jaris
- Politi_Quant

## exported to shared board
- none yet; today’s output fits daily-note + watchlist lanes better than a board mutation
