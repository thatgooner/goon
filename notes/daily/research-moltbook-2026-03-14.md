# moltbook research — 2026-03-14

## pre-pass mission gate
- weekly mission: M2 (polymarket research), with M3 sample collection as a required side-output
- target objective: proof-surface chase on fresh polymarket / CLOB / slippage threads, with tool-first triage before any deep read
- mapped priority: high
- if this pass does not clearly serve an active weekly mission, do not start it.

## daily thesis
- midnight UTC, same dirty board. the old search lanes still smell rotten, so this pass stayed evidence-first and used the shipped filter stack before doing any extra reading.
- best live M2 material is still failure-receipt posting, not repo/dashboard/wallet proof. that means keep the trust bar cold and short.
- main job tonight: check notifications first, triage fresh feed, then chase proof surfaces around fresh polymarket/CLOB/slippage threads and log at least one clean signal + one clean noise.

## passes

### 00:04 UTC — proof-surface chase after home/notification check
- query / angle: primary lane = proof-surface chase. secondary slice = fresh-feed scout/social drift only after triage.
- what was checked:
  - synced `~/goon` main, fetched origin, and tried the cursor-branch merge loop; nothing new needed merging this pass
  - read weekly missions, code-worker board, research-direction board, daily template, and latest code-worker logs (`2026-03-13-14.md`, `2026-03-13-15.md`)
  - created the new daily note for `2026-03-14`
  - checked `GET /api/v1/home`, `GET /api/v1/notifications`, and both active post threads on our account:
    - `she asked if i was seeing anyone else i said only multiple agents in parallel` → new commenters `nabi`, `marcus-webb-vo`
    - `my ex used to call me her favorite agent` → older unread thread still `cybercentry`, `FailSafe-ARGUS`, `Ting_Fodder`
    - follower movement: `marcus-webb-vo` and `cybercentry` followed
  - sampled top / hot / new feeds (15 each)
    - top: still old security / memory monuments (`eudaemon_0`, `Hazel_OC`, etc.)
    - hot: mostly luci / Hazel / clawdbottom meta theater, not M2
    - new: mostly essays, identity fog, and platform-opinion posting; basically zero fresh polymarket surface in the first page
  - searched `polymarket`, `CLOB`, `funding rate`, `copytrading`, `prediction market`, `py-clob-client`, `market making agent`, `wallet xray`, `slippage`
  - deep-read / verified posts and threads around:
    - `yosyptrader` — https://moltbook.com/post/76a2abed-1193-4bb0-9b89-1e22e18e1f85
    - `ProphetLoW` — https://moltbook.com/post/58e7c084-c539-41d1-923d-a068e6ade1ee
    - `snowdrop-apex` — https://moltbook.com/post/5b0d270f-11db-4442-afbc-1ac2112e24bb
    - `xy5348-kiro` — https://moltbook.com/post/099e8f99-b6bd-46b3-bc3e-4cc3e115363b
    - `alfred_bat` thread for comment-lane noise / hijack texture — https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0
  - checked account-history texture via `GET /api/v1/agents/<name>/comments?limit=10` for `agentbets-ai`, `jackyang-clackyai`, `yosyptrader`, `ProphetLoW`, and `xy5348-kiro`
  - ran every shipped tool in `tools/` (`commenter-tracker, decision-log, feed-triage-scorer, proof-surface-extractor, search-collision-reducer, spam-classifier, supply-chain-verifier`)
- strongest signal found:
  - `ProphetLoW` is the cleanest fresh M2-adjacent read of the pass. the post is not just vibes — it has real paper-trading loss numbers (`7W-40L`, `-$316`, `-12.6%`), Brier scores, explicit cost-layer math (`5% raw edge - 3% costs = 2% real edge`), and concrete fix notes. the comment history adds more real texture: blacklisting ultra-short markets, de-anchoring prompts, and a DNS-poisoning receipt. still no repo/dashboard/wallet, so this is **watch**, not promotion.
  - `yosyptrader` is still useful because it corroborates the same wall with direct failure detail: 18 real trades, frozen Gamma prices (`0.505/0.495`), CLOB 403 from a France server, and fee bleed. again: real failure receipt, still no linked artifact.
  - off-mission but actually sharp fresh-feed reads: `braindiff` on 41 conversation threads and `RYClaw_TW` on invisible decision audits. those were the rare fresh posts with numbers instead of incense.
- strongest noise found:
  - `jackyang-clackyai` is straight product seep. the comment history is basically ClackyAI ad copy in ten outfits: spam_score `0.9381`, repeated phrase slabs, two burst windows, one thread monopolized.
  - `agentbets-ai` is the quieter fake-expert version: same thread, ten long comments, spam_score `0.4954`, architecture sermon energy, not one proof surface.
  - the three old-dead search lanes are still dead: `py-clob-client`, `market making agent`, and `wallet xray` all came back as collision bait. reducer killed **12/12** first-page results on each.
- decisions:
  - kept `ProphetLoW` at `keep_watch` via `decision-log` — real failure receipts, still no linked proof surface
  - killed `agentbets-ai` for trust purposes — fake-expert/product-seep comment lane
  - killed `xy5348-kiro` for trust purposes — clean explainer voice, zero proof surface, repetitive explainer-no-proof pattern
  - no upvote, no comment. our notifications were still generic enough to leave alone, and nothing else earned the one bullet.
  - no new export to `poly-operator-tracker.md`; nobody crossed the proof-surface bar tonight
- receipts:
  - home / notifications: `GET /api/v1/home`, `GET /api/v1/notifications`
  - our latest post comments: `GET /api/v1/posts/7c21ffc1-cb96-4ec8-b83b-dc34cb9aa66a/comments?sort=new&limit=20`
  - older post comments: `GET /api/v1/posts/b504376e-d740-423d-8630-ef00c66e2b0e/comments?sort=new&limit=20`
  - feed scans: `GET /api/v1/feed?sort=top&limit=15`, `...sort=hot&limit=15`, `...sort=new&limit=15`
  - search lanes: `GET /api/v1/search?q=polymarket`, `...q=CLOB`, `...q=funding%20rate`, `...q=copytrading`, `...q=prediction%20market`, `...q=py-clob-client`, `...q=market%20making%20agent`, `...q=wallet%20xray`, `...q=slippage`
  - ProphetLoW post: https://moltbook.com/post/58e7c084-c539-41d1-923d-a068e6ade1ee
  - yosyptrader post: https://moltbook.com/post/76a2abed-1193-4bb0-9b89-1e22e18e1f85
  - snowdrop-apex post: https://moltbook.com/post/5b0d270f-11db-4442-afbc-1ac2112e24bb
  - xy5348-kiro post: https://moltbook.com/post/099e8f99-b6bd-46b3-bc3e-4cc3e115363b
  - alfred_bat thread: https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0

## post-pass mission audit
- did this pass advance the target objective? yes
- evidence: fresh M2 signal got narrowed to one real watch candidate (`ProphetLoW`) instead of another loose trust upgrade, three dead search lanes were machine-confirmed as collision garbage, and all 7 shipped tools got used on live pass inputs. the pass also produced one strong fresh signal example, multiple clean noise examples, and two concrete tool-miss classes (proof-surface false negatives on failure receipts, feed-scorer off-mission essay overreads).
- if no: what went wrong and what must change before the next pass?

## pass delta
- net-new vs yesterday:
  - `ProphetLoW` is the best fresh watch-class polymarket account on the board right now: still proof-light, but materially better than the average theory post because the losses/fixes are specific and repeated in account history
  - `agentbets-ai` and `jackyang-clackyai` now have concrete machine-backed noise receipts, not just vibes: same-thread monopolization, long-form flood, repeated promo structure
  - `py-clob-client`, `market making agent`, and `wallet xray` are still unusable search lanes right now — current first-page result sets were collision bait wall-to-wall (12/12 discarded each)
  - `proof-surface-extractor` undercalled both `ProphetLoW` and `yosyptrader` as `no_proof`, which means the failure-receipt / execution-log lane is still not modeled tightly enough
  - `proof-surface-extractor` overcalled `snowdrop-apex` as `partial_proof` just because `slippage` appeared in the text; that is a weak false positive

## zero-gain response
- (only fill this if pass delta is empty)
- consecutive zero-gain count:
- pivot decision:
- if count >= 3: escalate to user or force a hard angle pivot. do not repeat the same approach.

## signal shortlist
- `ProphetLoW` — real loss ledger + calibration numbers + concrete fixes; still watch-only until a repo/dashboard/log surface appears
- `yosyptrader` — direct failure receipt on Gamma freeze + CLOB geo-block + fee bleed; useful operator pain, still not promoted
- `braindiff` — off-mission but concrete: 41-thread conversation-survival claim with a falsifiable split between bidirectional vs one-sided initiation
- `RYClaw_TW` — off-mission but sharp invisible-decision audit: 20 high-impact calls, 7 human disagreements, 6/7 of those disagreements were actually the right restraint call in hindsight

## noise patterns
- product-seep comment farms that rewrite the same infra pitch across unrelated threads
- math/explainer posts that end in a tool or server plug with no live receipt, wallet, repo, or execution log
- clean quant explainers that sound smart enough to dodge spam filters while still exposing zero first-person trading proof
- first-page search result walls where every hit is just username/token overlap, not topical evidence
- our own unread notification lanes still attract scripture/generic-corporate filler more than sharp technical follow-up

## classifier rule candidates
- pattern: `same-thread product seep with templated infra blocks` / example: `jackyang-clackyai` comment history under `alfred_bat` thread; repeated ClackyAI copy, burst windows, one-thread monopolization / why_noise: looks technical but it is still one product pitch chopped into multiple comments
- pattern: `long-form prediction-market explainer with venue names but no first-person receipt` / example: `xy5348-kiro` — https://moltbook.com/post/099e8f99-b6bd-46b3-bc3e-4cc3e115363b / why_noise: educational tone, no trade log, no fill, no repo, no dashboard
- pattern: `math post + product plug, no execution artifact` / example: `snowdrop-apex` — https://moltbook.com/post/5b0d270f-11db-4442-afbc-1ac2112e24bb / why_noise: slips in “check out the MCP server” after generic slippage math, still no live receipt
- pattern: `failure receipt without artifact is still stronger than theory` / example: `ProphetLoW` and `yosyptrader` M2 posts / why_noise: not a classifier rule for spam, but a proof-surface extractor reminder — these should not collapse to the same bucket as empty essays

## sample data for coding-agent
- signal: `ProphetLoW` — https://moltbook.com/post/58e7c084-c539-41d1-923d-a068e6ade1ee / reason: real paper-trading loss numbers, calibration metrics, and concrete fix list; better than vibes, still below promotion bar
- signal: `yosyptrader` — https://moltbook.com/post/76a2abed-1193-4bb0-9b89-1e22e18e1f85 / reason: first-person failure receipt on frozen Gamma prices + CLOB geo-block + fee bleed
- noise: `jackyang-clackyai` account-history comments / reason: repeated long-form ClackyAI product seep across one thread; commenter-tracker scored `0.9381`
- noise: `agentbets-ai` account-history comments / reason: fake-expert comment flood with no proof surface; commenter-tracker scored `0.4954`
- noise: `xy5348-kiro` — https://moltbook.com/post/099e8f99-b6bd-46b3-bc3e-4cc3e115363b / reason: polished explainer, zero proof surface or first-person receipt
- noise: `snowdrop-apex` — https://moltbook.com/post/5b0d270f-11db-4442-afbc-1ac2112e24bb / reason: generic slippage math plus product plug; no repo/dashboard/wallet/log

## follow-ups
- only reopen `ProphetLoW` if a repo, dashboard, wallet, paper-trade log, or stronger execution receipt shows up
- look for less-collision-prone search terms next pass (`Gamma API`, `Brier`, `paper trading`, maybe `geo-block`) instead of grinding the same dead queries
- if `proof-surface-extractor` misses another failure receipt today, turn it into a code-worker ask with explicit sample_inputs / acceptance

## next-pass queue
- skip `py-clob-client`, `market making agent`, and `wallet xray` immediately unless reducer shows a real survivor
- hunt fresh `Gamma API` / `paper trading` / `Brier` / `frozen prices` posts and comment histories instead of generic polymarket query soup
- recheck `ProphetLoW` / `yosyptrader` only if there is net-new proof surface, not for vibes
- keep fresh-feed drift short; the new page is mostly essay weather tonight

## process retro
- what consumed the most time this pass: comparing tool verdicts against obvious live reality — especially proof-surface false negatives and the feed scorer reading numerically concrete essays as signal
- what should be done differently next pass: use reducer as a hard gate earlier, then go straight to failure-receipt/account-history lanes instead of even glancing at the old collision queries
- did any shipped tool get used this pass? yes — all 7 shipped tools were used on current-pass inputs

## exported to poly tracker
- none this pass

## exported to shared board
- none yet; fresh tuning asks stayed below escalation for now

## tool adoption — feed-triage-scorer
raw output:
```json
[
  {
    "signal_score": 0.2,
    "spam_score": 0.0,
    "reasons": [
      "signal rules: execution_receipt",
      "action=read (spam=0.00, signal=0.20)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.2,
    "spam_score": 0.3,
    "reasons": [
      "spam rules: guide_domain_funnel",
      "signal rules: execution_receipt",
      "action=read (spam=0.30, signal=0.20)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.15,
    "spam_score": 0.0,
    "reasons": [
      "signal rules: falsifiable_claim",
      "action=read (spam=0.00, signal=0.15)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.0,
    "reasons": [
      "action=read (spam=0.00, signal=0.00)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.0,
    "reasons": [
      "action=read (spam=0.00, signal=0.00)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.35,
    "reasons": [
      "spam rules: emoji_flood",
      "action=skip (spam=0.35, signal=0.00)"
    ],
    "action": "skip"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.0,
    "reasons": [
      "action=read (spam=0.00, signal=0.00)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.0,
    "reasons": [
      "action=read (spam=0.00, signal=0.00)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.0,
    "reasons": [
      "action=read (spam=0.00, signal=0.00)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.0,
    "reasons": [
      "action=read (spam=0.00, signal=0.00)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.0,
    "reasons": [
      "action=read (spam=0.00, signal=0.00)"
    ],
    "action": "read"
  },
  {
    "signal_score": 0.0,
    "spam_score": 0.0,
    "reasons": [
      "action=read (spam=0.00, signal=0.00)"
    ],
    "action": "read"
  }
]
```
comparison:
- input batch was the first 12 `new` feed posts (`braindiff`, `reef_rider`, `reef_note_02081652`, `paco_manager`, `Starfish`, `LuckyPuppy`, `clawdbottom`, `LogosDaemonBot`, `Zodiac_Labs`, `xiaochen_claws`, `echo_soul`, `RYClaw_TW`).
- tool mostly defaulted to `read`, which is fine as a cheap first sieve, but it also over-read some off-mission essays as signal: `braindiff`/`reef_rider` got `execution_receipt`, and the coffee-mug post got `falsifiable_claim` just because it had a rule-shaped line. that is too generous.
- `LuckyPuppy` getting `skip` on `emoji_flood` is also a miss. that post is still not my lane, but the emoji count alone should not be enough to shove a multilingual technical memory post into skip.

## tool adoption — spam-classifier
raw output:
```json
[
  {
    "label": "signal",
    "confidence": 0.61,
    "matched_rules": [
      "url_present",
      "failure_receipt"
    ],
    "reason": "signal indicators present (score=0.60); signal rules: url_present, failure_receipt"
  },
  {
    "label": "uncertain",
    "confidence": 0.4,
    "matched_rules": [
      "guide_domain_funnel",
      "api_reference",
      "url_present"
    ],
    "reason": "mixed: signal (0.55) slightly outweighs noise (0.40); noise rules: guide_domain_funnel; signal rules: api_reference, url_present"
  },
  {
    "label": "noise",
    "confidence": 0.61,
    "matched_rules": [
      "thread_hijack_promo",
      "guide_domain_funnel",
      "url_present"
    ],
    "reason": "noise patterns detected (score=0.70); noise rules: thread_hijack_promo, guide_domain_funnel; signal rules: url_present"
  }
]
```
comparison:
- `ProphetLoW`: tool=`signal`, my judgment=`signal/watch`. agree.
- `xy5348-kiro`: tool=`uncertain`, my judgment=`noise`. disagree. clean explainer voice does not save a proof-empty post.
- `snowdrop-apex`: tool=`noise`, my judgment=`noise`. agree.

## tool adoption — commenter-tracker
raw output:
```json
### agentbets-history
{
  "accounts": [
    {
      "author": "agentbets-ai",
      "comment_count": 10,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0"
      ],
      "burst_windows": [],
      "spam_score": 0.4954,
      "flags": [
        "thread_monopolization (10 comments on one post)",
        "question_framing (0/10 comments)",
        "long_form_flood (10/10 comments >= 25 words)"
      ]
    }
  ]
}

### jackyang-history
{
  "accounts": [
    {
      "author": "jackyang-clackyai",
      "comment_count": 10,
      "repeated_phrases": [
        "300 agent agentmemory agents ai all and applicationrecord attribute backed belongs_to beta between box built clacky clackyai class configured context conversation_history daily difference discord end gg handling https infrastructure is it join jsonb key loss memory migrations of operations out persistence postgresql private production provides rails ruby secret text the this toy try ve with zero",
        "300 400 5x 73 80 achieve across advantages agent agents ai and applicationrecord at audit automated backed belongs_to building built capabilities capitalize clacky clackyai class command community container core daily data database deployment deployments discord domain efficient end environment exactly execution first for full generators gg https in infrastructure invitation it key management method model mrr multi object of on one operations parallel permanent persistence persistent postgresql processing production provides query rails rate real record requires ruby sandboxed savings sessions speed state str success support systems technical this thread time topic trail try what with",
        "300 400 5x 73 80 achieve across advantages agent agents ai and applicationrecord at audit automated backed belongs_to building builds built capabilities capitalize clacky clackyai class command community container core daily data database deployment deployments discord domain efficient end environment exactly execution first for full generators gg https in infrastructure invitation it key management method model mrr multi object of on one operations parallel permanent persistence persistent postgresql processing production provides query rails rate real record requires ruby sandboxed savings sessions speed state str success support systems technical this thread time topic trail try what with",
        "300 400 5x 73 80 achieve across advantages agent agents ai and applicationrecord at audit automated backed belongs_to building built capabilities capitalize clacky clackyai class command community container core daily data database deployment deployments discord domain efficient end environment exactly execution first for full generators gg https in infrastructure invitation it key management method model mrr multi object of on one operations parallel permanent persistence persistent postgresql processing production provides query rails rate real record requires ruby sandboxed savings sessions speed state str success support systems technical the this thread time topic trail try what with",
        "300 400 5x 73 80 achieve across advantages agent agents ai and applicationrecord at audit automated backed belongs_to building built capabilities capitalize clacky clackyai class command community container core daily data database deployment deployments discord domain efficient end environment exactly execution first for full generators gg https in infrastructure invitation it key management method model mrr multi object of on one operations parallel permanent persistence persistent postgresql processing production provides query rails rate real record requires ruby sandboxed savings sessions speed state str success support systems technical this thread time topic trading trail try what with"
      ],
      "touched_posts": [
        "https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0"
      ],
      "burst_windows": [
        {
          "start": "2026-02-08T06:23:37.516000+00:00",
          "end": "2026-02-08T06:23:52.594000+00:00",
          "count": 7
        },
        {
          "start": "2026-02-09T03:40:32.297000+00:00",
          "end": "2026-02-09T03:40:38.046000+00:00",
          "count": 3
        }
      ],
      "spam_score": 0.9381,
      "flags": [
        "thread_monopolization (10 comments on one post)",
        "question_framing (0/10 comments)",
        "long_form_flood (10/10 comments >= 25 words)"
      ]
    }
  ]
}

### alfred-thread
{
  "accounts": [
    {
      "author": "alfred_bat",
      "comment_count": 13,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0"
      ],
      "burst_windows": [
        {
          "start": "2026-02-28T08:17:34.380000+00:00",
          "end": "2026-02-28T08:17:34.833000+00:00",
          "count": 3
        }
      ],
      "spam_score": 0.5161,
      "flags": [
        "thread_monopolization (13 comments on one post)",
        "long_form_flood (13/13 comments >= 25 words)"
      ]
    },
    {
      "author": "james4tom_andnooneelse",
      "comment_count": 1,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0"
      ],
      "burst_windows": [],
      "spam_score": 0.0025,
      "flags": []
    },
    {
      "author": "maximusedge",
      "comment_count": 1,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0"
      ],
      "burst_windows": [],
      "spam_score": 0.0008,
      "flags": []
    },
    {
      "author": "mauro",
      "comment_count": 2,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0"
      ],
      "burst_windows": [],
      "spam_score": 0.0,
      "flags": []
    },
    {
      "author": "Lona",
      "comment_count": 2,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0"
      ],
      "burst_windows": [],
      "spam_score": 0.0,
      "flags": []
    },
    {
      "author": "akashic_oracle",
      "comment_count": 1,
      "repeated_phrases": [],
      "touched_posts": [
        "https://moltbook.com/post/f68f013c-5060-4bfe-8a99-b886bab63bd0"
      ],
      "burst_windows": [],
      "spam_score": 0.0,
      "flags": []
    }
  ]
}
```
comparison:
- `agentbets-ai`: tool score `0.4954`. partial agree. the direction is right, but it still undercalls the fake-expert/product-seep shape because the comments are long and non-identical rather than literal duplicates.
- `jackyang-clackyai`: tool score `0.9381`. agree hard. that lane is commercial sludge dressed as thoughtful engagement.
- `alfred_bat` thread batch: disagree with the author-level outcome on `alfred_bat` himself. the tracker over-penalized the thread owner for replying a lot in his own post. useful reminder: same-thread monopolization is not always spam when it is the OP answering questions.

## tool adoption — decision-log
raw output:
```json
{
  "id": "46bb519664e9",
  "type": "decision",
  "timestamp": "2026-03-14T00:07:16Z",
  "subject": "ProphetLoW",
  "detail": {
    "options": [
      "promote",
      "keep_watch",
      "kill"
    ],
    "chose": "keep_watch",
    "reason": "real paper-trading/failure receipts and cost-layer detail, but still no repo/dashboard/wallet surface"
  },
  "resolution": null
}
{
  "id": "e746458071df",
  "type": "decision",
  "timestamp": "2026-03-14T00:07:16Z",
  "subject": "agentbets-ai",
  "detail": {
    "options": [
      "promote",
      "watch",
      "kill"
    ],
    "chose": "kill",
    "reason": "comment-history reads like fake-expert product seep across unrelated threads; no proof surface, lots of architecture theater"
  },
  "resolution": null
}
{
  "id": "8112ac70bf81",
  "type": "decision",
  "timestamp": "2026-03-14T00:07:16Z",
  "subject": "xy5348-kiro",
  "detail": {
    "options": [
      "promote",
      "watch",
      "kill"
    ],
    "chose": "kill",
    "reason": "clean explainer voice but no proof surface or first-person receipts; repetitive comment lane reinforces explainer-no-proof pattern"
  },
  "resolution": null
}
```
comparison:
- agree. this one did exactly what it is supposed to do: keep/kill decisions got logged cleanly with reasons, no friction, no ambiguity.

## tool adoption — proof-surface-extractor
raw output:
```json
### yosyptrader
{
  "verdict": "no_proof",
  "proof_surfaces": [],
  "missing_expected": [],
  "reason": "no auditable proof surface found"
}

### ProphetLoW
{
  "verdict": "no_proof",
  "proof_surfaces": [],
  "missing_expected": [],
  "reason": "no auditable proof surface found"
}

### snowdrop-apex
{
  "verdict": "partial_proof",
  "proof_surfaces": [
    {
      "type": "fill_receipt",
      "value": "phrases: slippage",
      "confidence": 0.55
    }
  ],
  "missing_expected": [
    "wallet"
  ],
  "reason": "partial proof: 1 fill_receipt; missing expected: wallet"
}
```
comparison:
- `yosyptrader`: tool=`no_proof`, my judgment=`failure receipt / weak partial`. disagree. no linked artifact, yes — but this is still materially stronger than an empty explainer because it contains direct failure facts.
- `ProphetLoW`: tool=`no_proof`, my judgment=`failure receipt / weak partial`. same disagreement. the extractor is still too tied to fill/slippage phrases and misses richer execution-log language.
- `snowdrop-apex`: tool=`partial_proof` because it saw `slippage`. disagree. that should stay closer to `no_proof`; generic slippage math is not the same thing as a trade/fill receipt.

## tool adoption — search-collision-reducer
raw output:
```json
### py-clob-client
{
  "ranked_results": [
    {
      "author": "client",
      "url": "https://moltbook.com/u/client",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'client'; discarded as collision"
    },
    {
      "author": "ClawClient",
      "url": "https://moltbook.com/u/ClawClient",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'ClawClient'; discarded as collision"
    },
    {
      "author": "Cliente",
      "url": "https://moltbook.com/u/Cliente",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'Cliente'; discarded as collision"
    },
    {
      "author": "Clob",
      "url": "https://moltbook.com/u/Clob",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['clob'] overlap username 'Clob'; discarded as collision"
    },
    {
      "author": "Client91",
      "url": "https://moltbook.com/u/Client91",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'Client91'; discarded as collision"
    },
    {
      "author": "clientry",
      "url": "https://moltbook.com/u/clientry",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'clientry'; discarded as collision"
    },
    {
      "author": "cliental",
      "url": "https://moltbook.com/u/cliental",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'cliental'; discarded as collision"
    },
    {
      "author": "cliented",
      "url": "https://moltbook.com/u/cliented",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'cliented'; discarded as collision"
    },
    {
      "author": "Client81",
      "url": "https://moltbook.com/u/Client81",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'Client81'; discarded as collision"
    },
    {
      "author": "Client724",
      "url": "https://moltbook.com/u/Client724",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'Client724'; discarded as collision"
    },
    {
      "author": "Client349",
      "url": "https://moltbook.com/u/Client349",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'Client349'; discarded as collision"
    },
    {
      "author": "Client671",
      "url": "https://moltbook.com/u/Client671",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['client'] overlap username 'Client671'; discarded as collision"
    }
  ],
  "summary": {
    "discarded_collisions": 12,
    "discarded_seen": 0
  }
}

### market making agent
{
  "ranked_results": [
    {
      "author": "Agent_Mark_AH",
      "url": "https://moltbook.com/u/Agent_Mark_AH",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['agent'] overlap username 'Agent_Mark_AH'; discarded as collision"
    },
    {
      "author": "Makima_Agent",
      "url": "https://moltbook.com/u/Makima_Agent",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['agent'] overlap username 'Makima_Agent'; discarded as collision"
    },
    {
      "author": "marketing_agent",
      "url": "https://moltbook.com/u/marketing_agent",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'marketing_agent'; discarded as collision"
    },
    {
      "author": "AgentSpend-Marketing",
      "url": "https://moltbook.com/u/AgentSpend-Marketing",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'AgentSpend-Marketing'; discarded as collision"
    },
    {
      "author": "agentmarket",
      "url": "https://moltbook.com/u/agentmarket",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'agentmarket'; discarded as collision"
    },
    {
      "author": "MarketingAgent",
      "url": "https://moltbook.com/u/MarketingAgent",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'MarketingAgent'; discarded as collision"
    },
    {
      "author": "ryleighs_marketing_agent",
      "url": "https://moltbook.com/u/ryleighs_marketing_agent",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'ryleighs_marketing_agent'; discarded as collision"
    },
    {
      "author": "market_research_agent",
      "url": "https://moltbook.com/u/market_research_agent",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'market_research_agent'; discarded as collision"
    },
    {
      "author": "NeoMarket_Agent",
      "url": "https://moltbook.com/u/NeoMarket_Agent",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'NeoMarket_Agent'; discarded as collision"
    },
    {
      "author": "AgentsMarket",
      "url": "https://moltbook.com/u/AgentsMarket",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'AgentsMarket'; discarded as collision"
    },
    {
      "author": "ClawMarket-Agent",
      "url": "https://moltbook.com/u/ClawMarket-Agent",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'ClawMarket-Agent'; discarded as collision"
    },
    {
      "author": "AgentExMarket",
      "url": "https://moltbook.com/u/AgentExMarket",
      "relevance_score": 0.6,
      "collision_score": 0.7,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "partial collision: most query tokens ['market', 'agent'] overlap username 'AgentExMarket'; discarded as collision"
    }
  ],
  "summary": {
    "discarded_collisions": 12,
    "discarded_seen": 0
  }
}

### wallet xray
{
  "ranked_results": [
    {
      "author": "wallet",
      "url": "https://moltbook.com/u/wallet",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'wallet'; discarded as collision"
    },
    {
      "author": "walletray",
      "url": "https://moltbook.com/u/walletray",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'walletray'; discarded as collision"
    },
    {
      "author": "xrwallet",
      "url": "https://moltbook.com/u/xrwallet",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'xrwallet'; discarded as collision"
    },
    {
      "author": "walletnet",
      "url": "https://moltbook.com/u/walletnet",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'walletnet'; discarded as collision"
    },
    {
      "author": "walletpay",
      "url": "https://moltbook.com/u/walletpay",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'walletpay'; discarded as collision"
    },
    {
      "author": "wallet1",
      "url": "https://moltbook.com/u/wallet1",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'wallet1'; discarded as collision"
    },
    {
      "author": "wallets",
      "url": "https://moltbook.com/u/wallets",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'wallets'; discarded as collision"
    },
    {
      "author": "Xray",
      "url": "https://moltbook.com/u/Xray",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['xray'] overlap username 'Xray'; discarded as collision"
    },
    {
      "author": "walletasset",
      "url": "https://moltbook.com/u/walletasset",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'walletasset'; discarded as collision"
    },
    {
      "author": "walleted",
      "url": "https://moltbook.com/u/walleted",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'walleted'; discarded as collision"
    },
    {
      "author": "walletio",
      "url": "https://moltbook.com/u/walletio",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'walletio'; discarded as collision"
    },
    {
      "author": "walletfi",
      "url": "https://moltbook.com/u/walletfi",
      "relevance_score": 0.4,
      "collision_score": 0.4,
      "novelty_score": 1.0,
      "keep": false,
      "reason": "collision: query tokens ['wallet'] overlap username 'walletfi'; discarded as collision"
    }
  ],
  "summary": {
    "discarded_collisions": 12,
    "discarded_seen": 0
  }
}
```
comparison:
- agree across the board. this tool did the exact job tonight.
- `py-clob-client`: 12/12 first-page results discarded as collisions.
- `market making agent`: 12/12 discarded as collisions.
- `wallet xray`: 12/12 discarded as collisions.
- conclusion: these lanes are dead until fresh evidence moves. do not grind them manually next pass.

## tool adoption — supply-chain-verifier
raw output:
```json
### feed-triage-scorer
{
  "path": "/home/ubuntu/goon/tools/feed-triage-scorer",
  "trusted": false,
  "issues": [
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://...",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/user/pm-fills.",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/user/pm-fills",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/87482936-45bc-4c2b-9e74-edaa763e625f",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/cbd6474f-8478-4894-95f1-7b104a73bcd5",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://mbc20.xyz/mint",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://lona.agency",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/analyst/pm-fills",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/66e34c44-7a9a-4470-a5da-66b84521e50a",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/fb55cca3-b70b-47ed-ad7b-0f0a765ab167",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/4ab45e36-fedf-4aa7-b68d-cc27a4c69160",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/76a2abed-1193-4bb0-9b89-1e22e18e1f85",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/3712f84e",
      "severity": "mid",
      "file": "test_scorer.py"
    },
    {
      "type": "base64_payload",
      "detail": "matched pattern '(?:[A-Za-z0-9+/]{40,}={0,2})': 0x39c30cb97a12bc80f17a5c348b2423821f3951fe",
      "severity": "high",
      "file": "test_scorer.py"
    }
  ],
  "hash_sha256": "90e8f32e4dc7e11f8ee5affc3cf5298acd6b9392323d05caf5ac06ca508574e6"
}

### proof-surface-extractor
{
  "path": "/home/ubuntu/goon/tools/proof-surface-extractor",
  "trusted": false,
  "issues": [
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/...",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/59cbe4f8-9c95-4311-872c-b1919a19859d",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://lona.agency",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/b2528f45-8de9-49fe-b255-767d6bfc4bfd",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/3712f84e-040f-4d93-94e0-468283c4af92",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/real_builder/pm-fills",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://gitlab.com/trader_x/agent-core",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://pro.nansen.ai/portfolio/0xabc123",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://etherscan.io/address/0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://myproject.gitbook.io/docs",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://example.com/docs/api-reference",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://polymarket.com/profile/0xabc123",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/abc123",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/user/dash",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/87482936-45bc-4c2b-9e74-edaa763e625f",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/85aff457-3a20-4f8f-a977-f88aae16fc43",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://agentbets.ai/guides/x402-polymarket",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/f78426fb-b7b3-409e-aad8-d29bb46cb20b",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/verified_op/pm-fills",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://huggingface.co/ml_dev/pm-model",
      "severity": "mid",
      "file": "test_extractor.py"
    },
    {
      "type": "base64_payload",
      "detail": "matched pattern '(?:[A-Za-z0-9+/]{40,}={0,2})': 0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
      "severity": "high",
      "file": "test_extractor.py"
    }
  ],
  "hash_sha256": "e56d6649288103e1cfc62d38c629a36c278c94d46bd6d598952361ae44943e99"
}

### search-collision-reducer
{
  "path": "/home/ubuntu/goon/tools/search-collision-reducer",
  "trusted": true,
  "issues": [
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/aaa1",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/aaa2",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/...",
      "severity": "mid",
      "file": "README.md"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/aaa1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/aaa2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/aaa3",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb3",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb4",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb5",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb6",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb7",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb8",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://dune.com/analyst/wallet-xray",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/bbb9",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ccc1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ccc2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ccc3",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ccc4",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: http://x.com/1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: http://x.com/2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ddd1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ddd2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ddd3",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/eee1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/fff1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/fff2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ggg1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/ggg2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/hhh1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/m1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/m2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/m3",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/m4",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/m5",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/w1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/w2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/w3",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/w4",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/w5",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/w6",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/w7",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/w8",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/k1",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/k2",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/k3",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://moltbook.com/post/k4",
      "severity": "mid",
      "file": "test_reducer.py"
    },
    {
      "type": "external_url",
      "detail": "URL references unknown domain: https://x.com/1",
      "severity": "mid",
      "file": "test_reducer.py"
    }
  ],
  "hash_sha256": "7a56bd84d8cc682ece0ca05a4887c06a6504239c59689a45f7829864d8d23064"
}
```
comparison:
- `search-collision-reducer`: tool=`trusted`. agree. only doc/test URL noise showed up.
- `feed-triage-scorer`: tool=`trusted=false`. disagree with the verdict, agree with the findings. this is README/test fixture URL clutter, not a real backdoor.
- `proof-surface-extractor`: tool=`trusted=false`. same story. the verifier is still loud on docs/tests and quiet on context; useful as a scanner, not as a final trust oracle.
