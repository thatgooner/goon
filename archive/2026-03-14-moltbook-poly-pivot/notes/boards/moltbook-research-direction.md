# moltbook research direction — anti-waste rules

goal: make each pass evidence-first, not scroll-first. kill repeated name-chasing unless the proof surface actually moved.

## pass lane rotation

each pass picks 1 primary lane:
- fresh-feed scout — new names/posts first, not old watches
- proof-surface chase — repo/dashboard/wallet/profile/fill hunt
- account-history / commenter graph — inspect reply lanes and `/agents/<name>/comments`
- off-platform verification — clone/read linked repos, check docs/site/dashboard reality
- tool-tuning / handoff — use shipped tools, record misses, turn repeated waste into buildable asks

secondary lanes are allowed, but the pass should have one clear center.

## hard anti-waste rules

- legacy cap: open max 2 old names per pass unless there is net-new evidence
- fresh quota: surface at least 3 fresh accounts/posts/threads per pass, or explicitly log zero-gain and why
- zero-gain pivot: if the same lane gives zero net-new evidence twice, pivot lanes on the next pass
- search-collision stop rule: if keyword search is collapsing into username/token collisions, stop grinding that lane and switch to feed/account-history/off-platform verification
- proof-surface bar: if there is no wallet, repo, dashboard, polymarket profile, fill receipt, execution log, or concrete first-person failure receipt, keep the writeup short and do not upgrade trust
- old-name rule: if `Jaris` / `Lona` / `TheBotcave` / other repeats have no new proof, give them 1-2 lines max and move on

## evidence ladder

strongest -> weakest
- wallet / repo / dashboard / polymarket profile / fill receipt / execution log
- concrete first-person failure or methodology receipt with falsifiable rule
- structured framework with examples but no proof surface
- polished theory / vibes / founder posting / generic alpha prose

## tool usage rule

before manually sinking time into a batch:
- use `feed-triage-scorer` on fresh feed candidates
- use `spam-classifier` on uncertain posts
- use `commenter-tracker` when a thread looks hijacked or templated
- use `decision-log` when you keep / kill / watch / refuse an account so the decision is explicit

## code-worker handoff triggers

if any of these repeat 2+ times in a day, turn them into a concrete build/tuning ask:
- keyword search collision wastes time
- tool keeps missing the same pattern
- proof-surface extraction is still manual and slow
- commenter spam shape is obvious but not machine-caught
- repeated old-name revisits produce no new evidence

handoff format should include:
- sample_inputs
- input_format
- output_format
- testable_acceptance

## current direction

right now the best move is:
1. fresh names first
2. proof-surface chase second
3. old watchlist names only when something moved
4. convert repeated waste into code-worker tasks instead of rerunning the same dead search