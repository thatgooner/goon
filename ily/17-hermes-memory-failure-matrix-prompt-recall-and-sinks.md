# Hermes memory failure matrix: prompt artifacts, recall evidence, and sink parity

## why this note exists
`05`, `07`, and `16` already got us past the surface read.
what was still worth locking was the **cross-lane failure map**:
not just what Hermes remembers,
but where its memory system quietly splits into different truth lanes with different rules.

latest code pass across:
- `vendor/hermes-agent/run_agent.py`
- `vendor/hermes-agent/agent/context_compressor.py`
- `vendor/hermes-agent/tools/memory_tool.py`
- `vendor/hermes-agent/hermes_state.py`
- `vendor/hermes-agent/tools/session_search_tool.py`
- `vendor/hermes-agent/agent/prompt_builder.py`
- `vendor/hermes-agent/gateway/session.py`
- `vendor/hermes-agent/gateway/run.py`

made one thing very obvious:

**Hermes is strong when it treats prompt state like a frozen artifact.**
**Hermes gets risky when prompt-bound material, recall evidence, and maintenance artifacts follow different trust/scope rules.**

Purr cannot inherit that split by accident.

---

## direct thesis
Hermes is not one memory system.
it is at least 4 overlapping lanes:

1. **snapshotted prompt material**
2. **live mutable memory sinks**
3. **recall/search outputs**
4. **synthetic survival artifacts created during compression/handoff**

those lanes are only partially aligned.
that partial alignment is good enough for an agent.
it is not good enough for `memory is the product`.

for Purr, the move is not `copy Hermes memory harder`.
it is:

- preserve the artifact discipline
- make all prompt-bound lanes obey one admission policy
- make recall evidence survive root/child/session boundaries
- make maintenance artifacts typed instead of chat-shaped
- make scope identity start from `owner_id + purr_id`, not platform/session convenience

---

## the matrix

| lane | Hermes good move | Hermes hidden failure | Purr rule |
| --- | --- | --- | --- |
| prompt snapshot | exact cached system prompt reused across continuation | only the cached system prompt is truly snapshotted; other prompt-bound inputs are not | snapshot every prompt-visible plane intentionally |
| live memory sink | cheap bounded memory with frozen-read/live-write split | writes and reads do not share the same trust gate; same-session freshness is intentionally stale | committed live overrides + shared admission policy |
| recall/search | FTS5 raw hit layer exists underneath | public tool returns summary-only recall and can lose exact child evidence | exact-hit evidence first, recap second |
| compression/handoff | pre-loss flush and lineage split are real strengths | summaries, stub tool results, and synthetic handoff artifacts can blur into transcript truth | typed maintenance plane only, never fake chat |
| identity scope | session lineage exists | session keys and resume/search flows are only partly user-scoped | every durable object and lookup starts from owner/purr scope |

---

## 1. prompt artifact lane: where Hermes is strongest

### what Hermes gets right
Hermes treats the active system prompt as a real session artifact.

in `run_agent.py`, the assembled prompt is:
- built once for a fresh session
- written into SQLite as `sessions.system_prompt`
- reused on later continuation instead of being rebuilt from current disk state

that is a real win.
it protects:
- cache stability
- behavioral continuity
- resistance to accidental mid-session drift

this is one of the best ideas in the whole stack.
Purr should keep this.

### hidden split inside the same lane
the problem is that **not all prompt-bound material is treated equally**.

Hermes has at least 3 prompt-visible sublanes:

1. `cached system prompt`
2. `ephemeral system prompt` and `prefill_messages` injected only at API-call time
3. later-turn Honcho recall injected into the active user message

so the system prompt is frozen,
but some other model-visible inputs are **not** frozen the same way.

that means prompt continuity is only partially artifactized.

a practical translation:
- Hermes preserves the main spine
- but side-channel prompt material can still drift by turn, provider path, or config state

### Purr consequence
Purr should define explicit prompt planes and snapshot policy for each:
- immutable `session_snapshot`
- tiny `turn_overlay`
- explicit `evidence_recall_bundle`
- hidden `planner_artifact`
- never smuggle extra recall or maintenance text in through a fake user turn

this note does not replace `16`.
it explains **why `16` is mandatory**.

---

## 2. live memory sink: frozen read, live write, uneven trust

### what Hermes gets right
`tools/memory_tool.py` has a clean split:
- `load_from_disk()` captures a frozen snapshot for system prompt use
- writes mutate live memory files immediately
- prompt reads keep using the frozen snapshot until invalidation/compression/new session

this is a strong assistant pattern.
cheap, stable, understandable.

### hidden failure 1 — same-session writes are intentionally stale
Hermes knows this is a tradeoff.
mid-session memory writes do not affect the active prompt.

that is acceptable for an agent.
for Purr,
it becomes dangerous if a direct correction lands and the next reply still reasons from old truth.

### hidden failure 2 — write-time scan, weak load-time gate
Hermes scans new memory content on `add` and `replace`.
that is good.

but `load_from_disk()` then reads `MEMORY.md` and `USER.md` straight back into the prompt snapshot without the same load-time quarantine layer that context files get.

so the trust rule is:
- stricter on tool-mediated write
- weaker on later prompt re-entry

that is the wrong boundary.

### hidden failure 3 — sink parity is inconsistent
context files in `prompt_builder.py` get load-time prompt-injection scanning.
local memory files use a different write-time scanner.
Honcho recall is assembled into prompt-visible text without the same obvious quarantine model.

same class of risk,
different policies.

### Purr consequence
Purr needs one admission pipeline for **all future prompt material**:
- source classification
- provenance requirement
- trust scan on write
- trust scan again on promotion to pack
- explicit authority label
- visibility lane check

if it can touch the model,
it belongs to the same trust boundary.

---

## 3. recall lane: the raw evidence exists, but the user-facing tool blurs it

### what Hermes gets right
under the hood, Hermes actually has a better recall primitive than its public `session_search` shape suggests.

`hermes_state.py::search_messages()` gives:
- FTS5 hits
- ranked snippets
- a little surrounding context
- session metadata

that is the right direction.
there is a real evidence-bearing layer under the hood.

### hidden failure 1 — summary wrapper eats the proof
`tools/session_search_tool.py` does this:
1. FTS5 search
2. dedup by session
3. resolve child session to root parent
4. load transcript
5. truncate around rough query terms
6. summarize with an LLM

so the user-facing result is usually **summary prose**, not exact evidence.

that is a huge difference.
recall becomes:
- useful for continuity
- weak for proof
- vulnerable to scope drift

### hidden failure 2 — child hit can collapse into root recap
if the actual matched message lived in a child session,
Hermes can resolve that hit back to the root parent and summarize the parent transcript instead.

that means the exact hit may be the thing that disappears.

for Purr this is not a cosmetic issue.
it breaks:
- contradiction handling
- exact recall
- auditability
- `why do you think this` answers

### hidden failure 3 — current-session exclusion is only partly lineage-aware
Hermes tries to exclude the current session from recall.
good instinct.

but the exclusion logic is not a full lineage-family exclusion rule.
so depending on where the current leaf sits,
recall can bounce back stale ancestor material as if it were a separate old memory.

### hidden failure 4 — the search contract is looser than it looks
`search_messages()` advertises phrase/boolean/prefix-style support,
but its sanitizer strips some operator syntax.
`session_search` then truncates around the first raw query term it sees.

that means the ranking hit,
the truncation window,
and the summary scope can all drift apart.

### Purr consequence
Purr recall contract should be:

1. exact evidence refs first
2. quoted excerpt second
3. hit window / episode / lineage ids third
4. only then optional recap

and current-lineage exclusion should happen at the lineage family level,
not just the local leaf id.

---

## 4. compression and survival lane: strong salvage, weak artifact hygiene

### what Hermes gets right
Hermes does two very important things before and during compression:

#### A. pre-loss salvage is explicit
`run_agent.py::flush_memories()` gives the model one last pass to save useful memory before context is destroyed.
that is smart.
Purr should steal the instinct, even if not the exact implementation.

#### B. lineage split beats in-place rewrite
compression does not just mutate history blindly.
it creates a new continuation session with parent linkage.
that is much better than pretending the old session never existed.

### hidden failure 1 — summary failure can still mean middle-turn loss
`context_compressor.py` is honest about it:
if summary generation fails,
Hermes may drop middle turns without summary.

that is acceptable only if you treat the compressed transcript as disposable working memory.
Purr cannot.

### hidden failure 2 — message content is truncated before summarization
very long messages are head/tail clipped before the summary model sees them.
so even the best summary has already lost some source detail.

### hidden failure 3 — structural survival can create fake evidence shapes
Hermes protects tool-call/result integrity by removing orphan tool results and inserting stub tool-result placeholders where needed.
that is useful for API validity.

but those placeholders are not the real historical result.
that means Hermes preserves:
- message shape well
- truth provenance less well

### hidden failure 4 — synthetic artifacts can become chat-shaped
compaction summary material is inserted as a normal assistant/user-shaped conversation turn because that keeps the transcript API-valid.

again: good runtime hack,
bad memory-product hygiene.

### Purr consequence
Purr should preserve the **operation**, not the disguise.

meaning:
- salvage runs yes
- extractive checkpoints yes
- summary artifacts yes
- lineage bridge artifacts yes
- tool integrity helpers yes

but all of them must be:
- typed
- auditable
- filterable
- non-conversational unless they were actually spoken

no fake user turns.
no fake Purr turns.
no summary pretending to be evidence.

---

## 5. scope lane: Hermes lineage exists, but product identity is too soft

### what Hermes gets right
Hermes does have:
- session ids
- parent session ids
- title continuation helpers
- source metadata

that is better than nothing.

### hidden failure 1 — gateway DM scope can collapse users together
`gateway/session.py::build_session_key()` makes non-WhatsApp DMs share one session key per platform if there is no thread id.

that is a practical gateway shortcut.
for a product,
it is insane.

### hidden failure 2 — `/resume` and listing are not truly user-scoped
Hermes comments say `this user/platform`,
but the listing and title resolution path are effectively platform-scoped,
not strict per-user scoped.

### hidden failure 3 — search is not owner-first
session recall paths rely on session/source behavior,
not on a hard `owner_id` boundary that is present on every durable lookup.

### Purr consequence
Purr must never let convenience session keys become memory identity.

hard rule:
- every durable object
- every retrieval path
- every prompt-pack lookup
- every resume alias
- every review/proactive job

must begin with:
- `owner_id`
- `purr_id`

then apply window/episode/epoch/lineage logic inside that boundary.

---

## the steal / reject split

## steal almost directly
- exact prompt snapshot reuse across continuation
- bounded hot context discipline
- pre-loss memory salvage before compaction/reset
- lineage split instead of in-place overwrite
- raw transcript store separated from prompt memory
- structural integrity checks around tool-call compression

## reject or redesign hard
- summary-only recall as the main recall surface
- child-hit -> root-only recap collapse
- fake chat-shaped maintenance artifacts
- dropping middle turns when summary fails
- write-time-only trust gates for prompt-bound material
- platform/session convenience scoping as a stand-in for product identity
- flat substring mutation as a durable truth model

---

## the clean Purr translation
this pass makes the earlier Purr notes feel less optional and more like direct antidotes.

### `11` was right
we need strict owner/purr scope + lineage semantics because Hermes scope is too soft.

### `12` was right
we need exact evidence refs because Hermes recall and compaction can get summary-heavy.

### `14` was right
we need a committed live-override lane because Hermes frozen-read/live-write split goes stale on purpose.

### `16` was right
we need typed artifact planes because Hermes runtime survival helpers blur into transcript truth.

so the updated thesis is:

**Purr is not “Hermes memory but bigger.”**
**Purr is Hermes artifact discipline, plus much stricter scope/evidence/trust boundaries.**

---

## direct build-facing rules this note locks
before anybody ships the memory spine, these rules should hold:

1. **exact-hit recall survives compression and lineage splits**
2. **no prompt-bound sink bypasses the same trust/admission policy**
3. **maintenance artifacts are typed, never disguised as normal speech**
4. **same-turn corrections can affect the next reply without full pack rebuild**
5. **summary failure cannot delete unsalvaged truth**
6. **resume/search/append all resolve to the same active owner-scoped leaf**
7. **owner/purr scope is stronger than platform/session convenience**

---

## direct conclusion
the deepest Hermes lesson from this pass is not just `freeze the prompt`.
it is:

**when memory touches the model through more than one lane, every lane becomes part of the product truth boundary.**

Hermes handles some of those lanes well.
it leaves others only partially aligned.

for Purr,
partial alignment is not enough.

if memory is the product,
then:
- prompt artifacts
- recall evidence
- maintenance outputs
- resume pointers
- live overrides
- remote/mirrored sinks

all need one honest contract.

that is the standard now.
