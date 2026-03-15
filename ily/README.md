# ily

burasi senin hizli bakis klasorun.
chatten tek tek sormadan bak diye acildi.

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

## not
aktif build lane arastirma-first modda.
code-worker da once bunlari okuyup hizaya gelecek, sonra build baslayacak.
