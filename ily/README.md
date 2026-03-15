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

## not
aktif build lane arastirma-first modda.
code-worker da once bunlari okuyup hizaya gelecek, sonra build baslayacak.
