# Hermes memory code-grounded hidden logic map

## why this pass exists
surface teardown was not enough.
we needed to look at the actual Hermes code and stop guessing.

this pass is grounded in the live Hermes repo on this machine:
- `~/.hermes/hermes-agent/tools/memory_tool.py`
- `~/.hermes/hermes-agent/run_agent.py`
- `~/.hermes/hermes-agent/hermes_state.py`
- `~/.hermes/hermes-agent/tools/session_search_tool.py`
- `~/.hermes/hermes-agent/agent/context_compressor.py`

the goal was simple:
find the hidden behavior loops that make Hermes feel better than a dumb assistant,
and find the hidden failure modes we absolutely should not copy into Purr.

---

## the strong part is more specific than `Hermes has memory`
Hermes is good because it is opinionated about **when memory is allowed to affect the model**.
not just where memory is stored.

that hidden discipline is the real asset.

---

## 1. Hermes runs a deliberate `live write / frozen read` split
code proof:
- `tools/memory_tool.py:91-95`
- `tools/memory_tool.py:106-121`
- `tools/memory_tool.py:281-292`

what it does:
- memory loads from disk once
- Hermes captures a frozen `_system_prompt_snapshot`
- tool calls mutate live memory entries and save them to disk immediately
- but the system prompt keeps using the frozen snapshot for the rest of the session

why this is strong:
- prefix/prompt caching stays stable
- behavior does not drift every time a memory write happens
- persistence can happen immediately without paying prompt-rebuild tax every turn

why this is dangerous for Purr:
- same-session corrections can feel fake if the reply still reasons from the old snapshot
- `i know you` product fantasy dies faster than a normal assistant does

Purr consequence:
- keep the frozen session pack idea
- do **not** keep frozen truth
- canonical truth must stay live in the ledger
- direct corrections need a small turn-level override lane

---

## 2. Hermes stores the exact prompt snapshot and reuses it across resumed sessions
code proof:
- `run_agent.py:3380-3419`

what it does:
- first turn builds the full system prompt once
- later turns in the same continuing session load the stored prompt back from SQLite instead of rebuilding from disk

why this is strong:
- prompt prefix remains stable across gateway/CLI continuation
- the agent does not re-inject changed memory files and accidentally blow cache reuse
- the active prompt becomes a session artifact, not a live view of files

why this matters for Purr:
- this is one of the cleanest Hermes ideas to steal
- Purr should persist the exact hot pack / session pack for a conversation window
- re-entry should reuse that pack until a deliberate rebuild event happens

---

## 3. Hermes has a real pre-compression salvage step
code proof:
- `run_agent.py:2627-2768`
- `run_agent.py:2776-2806`

what it does:
- before context compression, Hermes injects a hidden `save anything worth remembering` turn
- exposes only the memory tool
- lets the model write memories before context gets summarized or dropped
- then strips the flush artifacts from history

why this is strong:
- memory salvage is operationalized, not left to hope
- valuable facts can get promoted before compression flattens the session
- it protects against `the model knew it, but never wrote it down`

what to steal for Purr:
- salvage before compression
- salvage before long-idle cutoff
- salvage before archive/handoff
- salvage before proactive timing jobs build on stale context

hard note:
this should become a background/service behavior in Purr, not visible chat ceremony.

---

## 4. Hermes compression protects message structure, not just semantics
code proof:
- `agent/context_compressor.py:158-216`
- `agent/context_compressor.py:218-310`

what it does:
- avoids splitting tool-call/result groups at compression boundaries
- removes orphaned tool results
- inserts stub tool results if an assistant tool call survives but its result got dropped

why this is strong:
- long-context systems do not only fail semantically
- they fail structurally
- Hermes explicitly guards against malformed tool history after compression

Purr consequence:
- any hidden cognition, archive, or background-tool lane needs the same integrity mindset
- summaries are not enough
- evidence chains and causal structure matter too

---

## 5. Hermes keeps lineage when it compresses, but the lineage model is split-brain
code proof:
- `run_agent.py:2810-2829`
- `hermes_state.py:342-403`

what it does:
- compression ends the old session
- creates a new child session with `parent_session_id`
- also auto-numbers titles like `foo #2`

what is genuinely good:
- the raw session history is not overwritten
- parent-child lineage survives compression
- you can keep an audit trail instead of pretending summaries are the only truth

what is weak:
- user-facing continuation often relies on title suffixes, not just real graph traversal
- title lineage is convenience UX, not a serious memory graph

Purr consequence:
- use real episode/session lineage in the data model
- do not let title tricks stand in for relationship history
- public/product naming can be cute, but backend lineage must be explicit

---

## 6. Hermes recall is cheaper than prompt stuffing, but the code shows 2 sharp cracks
code proof:
- `tools/session_search_tool.py:205-271`
- `hermes_state.py:587-680`

what Hermes does right:
- FTS5 search first
- summarize only matched sessions
- keep long-tail history out of the hot prompt

that philosophy is still good.

but the actual implementation exposes 2 important breaks:

### crack A — recall is not truly user-scoped
`search_messages()` filters by source/platform, not by a per-user memory boundary.
for a local agent this is tolerable.
for Purr it is unacceptable.

Purr consequence:
- every retrieval path must filter by `owner_id` and `purr_id` first
- cross-user bleed is a product-killer, not a footnote

### crack B — child-session hits can get resolved to the root parent and lose the actual matched detail
`session_search_tool.py` resolves matched child sessions back to the root parent before summarizing.
that is neat for delegation UX.
but for compression lineage it can mean:
- the match happened in a child continuation
- summarization loads the root parent session instead
- the recap may miss the actual matched content

Purr consequence:
- retrieval contract must unify current session, recent episodes, and long-term memory without flattening away the exact evidence segment that mattered

---

## 7. one hidden Hermes bug is especially useful for us: the memory nudge loop is basically dead
code proof:
- `run_agent.py:3303-3312`
- `run_agent.py:3336-3347`
- `run_agent.py:2858-2860`

what the code says:
- Hermes intends to nudge the model after enough turns to consider saving memory
- the counter is supposed to reset only when memory is actually used

what the code actually does:
- `_turns_since_memory` gets reset at the start of every turn
- then incremented once
- so for normal intervals, it never accumulates enough to fire

why this matters:
- one of Hermes' supposed `behavior loops` is weaker in reality than it looks from the surface
- this is exactly why code-grounded teardown matters

Purr consequence:
- do not rely on cute nudges inside the live chat loop as the main persistence mechanism
- memory extraction has to be event-driven and service-side
- if capture matters, make it operational, inspectable, and measurable

---

## 8. Hermes memory mutation is too flat for Purr-grade truth
code proof:
- `tools/memory_tool.py:154-279`

what it does:
- `add`
- `replace` by substring match
- `remove` by substring match
- flat delimiter-separated text entries

why it works for Hermes:
- tiny state
- low cognitive overhead
- easy for the model to operate

why it fails for Purr:
- ambiguous matches become normal as memory grows
- contradiction handling becomes text surgery
- there is no first-class provenance
- there is no confidence model
- there is no supersedes/conflicts graph
- there is no review lifecycle

Purr consequence:
- memory rows need ids and typed fields
- contradiction must be a state transition, not a wording fight
- evidence refs must be first-class

---

## 9. Hermes sanitizes memory writes, but not the whole memory ingestion surface
code proof:
- `tools/memory_tool.py:160-163`
- `tools/memory_tool.py:204-207`
- `tools/memory_tool.py:106-121`

what it does well:
- scans tool-mediated memory writes for prompt-injection / exfil style patterns

what it does not do:
- scan existing memory files when loading them from disk into the prompt snapshot

why this matters:
- tool writes are not the only way persistent prompt material appears
- manual edits or external writes can bypass the write-time scanner and still get injected later

Purr consequence:
- sanitize on ingest
- sanitize on promotion into hot-pack material
- sanitize network-derived/social-derived summaries too
- treat `future prompt material` as a security boundary every time, not just at write time

---

## 10. Hermes writes are atomic, but concurrency is still weak
what Hermes gets right:
- temp file + atomic rename prevents torn writes

what still breaks conceptually:
- there is no real merge/lock/provenance model for concurrent writers
- two stale writers can still clobber each other logically

Purr consequence:
- use row-level or event-level mutation in the ledger
- do not let memory consistency depend on flat-file last-writer-wins behavior

---

## the real steal / reject list is now sharper

## steal directly
- frozen session/hot-pack snapshot discipline
- stored prompt snapshot reuse across session continuation
- pre-compression salvage pass
- transcript/history separated from hot memory
- structural integrity guards during compression
- cheap recall via search -> summarize instead of raw transcript stuffing
- security mindset around anything that will later be re-injected

## reject directly
- flat MEMORY.md / USER.md as the product memory model
- substring mutation as the main update path
- same-session stale truth with no live override lane
- unscoped recall
- title-based pseudo-lineage standing in for real episode lineage
- chat-loop nudges as the main memory capture strategy

## redesign for Purr
- owner-scoped structured ledger
- stable session pack + live correction override
- unified retrieval contract across current/recent/long horizons
- evidence-backed contradiction handling
- event-driven extraction/salvage/review jobs
- strict review/decay for predictive memory

---

## direct build-order implication
this pass does **not** move us into flashy build mode.
it sharpens what the first invisible memory spine must handle.

if we start building after research lock, the first slices should still be:
1. structured ledger
2. retrieval/context packer
3. contradiction + review loop
4. salvage/consolidation/background timing jobs

but now the bar is clearer.
those slices must explicitly solve:
- same-session correction freshness
- per-user retrieval isolation
- real lineage
- evidence-safe recall
- prompt-pack stability without truth drift

---

## short verdict
Hermes is better than it first looks because the good part is not `it has memory files`.
it is that Hermes treats memory as a **controlled behavior pipeline**.

but the code also shows where that pipeline stops being enough:
- stale same-session truth
- flat mutation
- weak scoping
- pseudo-lineage shortcuts
- best-effort capture
- one dead nudge loop

for Purr the move is not `copy Hermes harder`.
it is:
- steal the discipline
- reject the flatness
- make truth structured
- make recall owner-scoped
- make corrections live
- keep all of that invisible inside the product surface

that is the lane.