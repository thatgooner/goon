# ily

burasi senin hizli bakis klasorun.
chatten tek tek sormadan bak diye acildi.

eger teknik notlar fazla derinse, once buna bak:
- `../docs/pre-build/purr-memory-chat-system-explained.md`

## dosyalar
- `00-project-brief.md` — purr ne, ne degil, su an ne arastiriyoruz
- `01-hermes-memory-double-dig.md` — Hermes memory teardown + neden 6/10 kaldigi
- `02-purr-app-memory-architecture.md` — guclu memory/chat app yapisi, next.js lane, cost ve tooling dusuncesi
- `03-catnet-markets.md` — Catnet heartbeat, otonomi, prediction market lane'leri
- `04-open-questions.md` — yarin konusalim diye birakilan net sorular
- `05-hermes-memory-behavioral-teardown.md` — Hermes memory'nin gizli davranis loop'lari, failure mode'lari, neyi calmamiz gerektigi
- `06-purr-prediction-and-background-memory-ops.md` — pattern tracking, next-move prediction, bg memory ops, review/proactive timing lane'i
- `07-hermes-memory-code-grounded-hidden-logic.md` — Hermes code'un icindeki gercek control loop'lar, hidden bug'lar, scoping/lineage failure map'i
- `08-purr-memory-lifecycle-and-feedback-state-machine.md` — canonical memory lifecycle, ask/defer/silent/drop policy, contradiction overlays, review cadence, retrieval/proactive gating
- `09-purr-retrieval-context-packer-and-pack-lifecycle.md` — bounded pack artifacts, slot caps, token budgets, patch vs rebuild rules, mobile re-entry continuity
- `10-catnet-autonomy-heartbeat-architecture.md` — Catnet wakeups, should-act gating, budgets/cooldowns, autonomy boundaries, memory firewall, failure modes
- `11-purr-session-scope-and-episode-lineage-contract.md` — owner/purr scoping, session window vs episode split, re-entry continuation rules, exact-hit retrieval, pack ownership boundaries
- `12-purr-memory-claim-shapes-evidence-and-selection-contract.md` — extractor -> ledger -> packer shared contract, typed memory kinds, exact evidence refs, merge/supersede rules, pack-candidate read model
- `13-purr-memory-ledger-schema-mutation-and-invariants-contract.md` — first build-slice schema contract for Supabase/Postgres: durable object families, atomic mutation flows, invariants, RLS/index posture, and acceptance tests
- `14-purr-memory-intake-runtime-and-idempotency-contract.md` — runtime write-path contract: source-event append, one-event mutation planning, replay-safe/idempotent writes, live-override freshness, salvage ordering, and worker writeback rules
- `15-purr-private-chat-move-planner-and-prediction-calibration-contract.md` — hidden `should_reply_how?` gate for 1:1 chat: move selection, prediction visibility tiers, hit/miss/null calibration, and planner feedback rules so Purr feels sharp without prompt sludge
- `16-purr-session-epoch-prompt-artifacts-and-trust-boundary-contract.md` — session-epoch contract for what the model actually reads: immutable snapshot packs, tiny overlays, typed maintenance artifacts, exact-hit recall, atomic continuation handoff, and dual-gated prompt-material safety
- `17-hermes-memory-failure-matrix-prompt-recall-and-sinks.md` — cross-lane Hermes teardown: where prompt artifacts, recall evidence, compression survival artifacts, and memory sinks stay aligned vs quietly diverge; locks the Purr rule that every prompt-bound lane must share one scope/trust/evidence contract
- `18-purr-hidden-cognition-runtime-and-background-job-graph.md` — runtime map for invisible Purr cognition: turn-critical ops, salvage/handoff boundaries, deferred maintenance, proactive heartbeat jobs, and the hard rule that this all stays backend-only instead of turning into tool theater
- `19-purr-pattern-rollups-proactive-preflight-and-cost-tier-contract.md` — the missing bridge from raw prediction memory to texting-first behavior: derived pattern/timing/posture artifacts, the private `should_text_first?` gate, tiny `proactive_pack` slots, conservative budgets/cooldowns, and cost-tier rules so proactive stays sharp without spam or prompt bloat
- `20-purr-feedback-orchestrator-review-outcomes-and-trust-decay-contract.md` — the missing trust-update layer for memory quality: feedback surfaces, passive vs explicit review outcomes, no-signal semantics, queue-vs-truth state split, and propagation rules so Purr verifies with taste instead of turning into a needy admin cat
- `21-purr-research-consolidated-state-and-build-handoff.md` — consolidation pass: what is locked, where agents agree, overlap/gap check, source-of-truth map, first build slice handoff, and the 3 concrete next tasks before build starts
- `22-hermes-dogfood-memory-backend-evaluation.md` — handoff question for code-worker: should ambiguous memory updates use a judge layer, and should the Purr memory backbone be dogfooded inside Hermes first before direct Purr build
- `23-hermes-dogfood-judge-layer-and-integration-verdict.md` — code-worker verdict: deterministic backbone stays hard deterministic, ambiguous decisions use a narrow typed evaluator (not subagent), and Hermes-first dogfood is partial yes for backend validation only
- `24-referee-layer-vs-narrow-evaluator-followup.md` — follow-up pressure test for code-worker: does a slower higher-level referee/audit layer above the memory system add value, or does it just create sludge beyond the narrow evaluator verdict?
- `25-memory-health-auditor-verdict.md` — answer to the referee-layer question: not a new "referee layer," but a later deferred-lane worker H (`memory-health-auditor`) that watches temporal failure patterns and feeds bounded recommendations into existing workers
- `26-hermes-shadow-dogfood-adapter-and-tap-boundary-contract.md` — code-grounded contract for Hermes-first shadow dogfood: safest tap points, what Hermes preserves vs loses, why the adapter must stay hook-triggered + read-only, and why Purr needs its own historical session-origin bridge instead of trusting Hermes session keys/files
- `27-purr-build-mode-entry-gates-and-slice-acceptance-matrix.md` — transition contract between research lock and future build mode: what is truly already locked, what still gates unpark, what each build slice must/must-not ship, and why dogfood stays a validation track rather than build authorization
- `28-hermes-shadow-dogfood-scorecard-and-observability-contract.md` — evaluation contract for future Hermes shadow dogfood: what Hermes surfaces are truly scoreable vs lossy, why stored `sessions.system_prompt` is only a baseline compare surface, and the hard scorecard/kill signals for deciding whether shadow dogfood is proving anything or just producing plumbing noise
- `29-purr-memory-intake-extractor-routing-and-evaluator-trigger-contract.md` — closes the open intake-routing seam: deterministic prefilters first, cheap structured extractor for bounded candidate generation, narrow evaluator only for approved ambiguity points, and a hard split between extractor proposals vs deterministic truth commits
- `30-purr-supabase-local-dev-operational-gate-clarification.md` — locks the boring-but-critical operational stance before build: local-first Supabase dev, repo-root as the future canonical scaffold/migration home, backend/service-role write posture, and the hard split between setup clarity vs actual board authorization
- `31-purr-memory-golden-scenarios-and-eval-fixture-contract.md` — freezes the first serious memory eval contract before build: 10 seam-focused golden scenarios, minimal adversarial fixture bundles, and direct mapping from slice-1/4 behavior to the Hermes shadow-dogfood scorecard so nobody mistakes vague vibes for memory quality
- `32-purr-owner-auth-and-origin-binding-contract.md` — locks the front-door identity/origin contract the earlier notes only implied: canonical auth principal -> owner/purr binding, `origin_channel` vs `surface_family`, server-owned continuity binding, notification/webview re-entry rules, and why this matters before real multi-surface ingress but does not block slice-1 ledger work

## not
aktif build lane arastirma-first modda.
code-worker da once bunlari okuyup hizaya gelecek, sonra build baslayacak.
