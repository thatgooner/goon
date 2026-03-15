# Hermes dogfood implementation plan — executive summary

## what this is
full technical plan for shadow-testing the Purr memory backbone inside Hermes' conversation stream. produced from 5 parallel subagent investigations + controller synthesis.

full plan: `docs/plans/2026-03-15-hermes-purr-memory-dogfood-implementation-plan.md`

---

## architecture in one sentence
external Python adapter in `tools/hermes-dogfood-adapter/` reads Hermes' SQLite database in read-only mode, maps events to Purr schema via deterministic UUID5, writes to Supabase, runs extractor. Hermes is never modified. kill = stop the process.

---

## phase gates

| transition | gate criteria |
|-----------|--------------|
| start → phase 0 | Supabase schema up, adapter runs, messages flowing |
| phase 0 → 1 | ≥100 memory_items, ≥95% evidence valid, 0 dupes, ≤30% junk, 7 days |
| phase 1 → 2 | ≥20 comparisons, budget compliance, overlap_f1 ≥0.5, 7 days |
| phase 2 → 3 | ≥10 corrections, caught_ratio ≥0.6, no impossible states, 7 days |
| phase 3 → done | review good_ratio ≥0.7, proactive no_act ≥0.7, 14 days |

---

## first implementation task
**task A1: Supabase local dev setup + phase 0 migration.** creates all tables needed for phase 0. no Hermes dependency. can start immediately.

---

## biggest risks

1. **extractor quality on real data.** rule-based extraction may produce too much junk. mitigation: weekly manual audit; upgrade to cheap LLM if junk_ratio > 50%.
2. **Supabase hosting decision.** local dev is easy; live dogfood needs a real project. must be resolved before live shadow begins.
3. **scope creep.** "just one more feature in the adapter" → adapter becomes a second Hermes. mitigation: strict phase gates, kill signals, 6-week timeout.

---

## what stays sacred

- deterministic backbone (11 surfaces from ily/23) — untouched
- no in-loop subagent — confirmed
- no Hermes code changes — confirmed
- no Hermes behavior change — confirmed in all 4 phases
- narrow evaluator — phase 3 only, optional
- worker H — post-phase 3 only

---

## build order impact

main build order unchanged: memory-ledger → extractor → packer → feedback-orchestrator.
dogfood adapter is a parallel validation track, not a replacement for the main build.
test order changed: each build slice gets real-data validation via its corresponding dogfood phase.
