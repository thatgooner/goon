# hermes memory review

purpose: inspect Hermes memory management hard before we copy anything into purr.

## tldr

Hermes memory is good because it is layered, cheap, durable, and disciplined.
It is not enough for purr as-is because it is tiny, mostly flat text, and built for one agent/user environment rather than a product with rich per-user memory.

best reusable idea:
- small always-on memory + full session history + on-demand recall

worst thing to copy blindly:
- treating memory as a few flat note files with no lifecycle state, confidence, or per-user structure

---

## what Hermes actually has

Hermes is not one memory system. It has layers.

### layer 1 — curated always-on memory
files:
- `~/.hermes/memories/MEMORY.md`
- `~/.hermes/memories/USER.md`

used for:
- user preferences
- environment facts
- project conventions
- short durable notes

important traits:
- bounded by char limit
- human-readable
- injected into the system prompt at session start
- mutated during the session, but prompt stays frozen until next session / compression rebuild

why this is good:
- low token cost
- stable behavior
- easy to audit
- hard to bloat if the limits stay strict

### layer 2 — full transcript memory
file/backend:
- `~/.hermes/state.db`

used for:
- session history
- full messages
- search later

important traits:
- SQLite + WAL
- FTS5 full-text search
- session metadata and lineage

why this is good:
- durable
- local and simple
- much cheaper than trying to keep everything in prompt memory

### layer 3 — session_search recall
used for:
- finding old conversations on demand
- summarizing old sessions only when needed

important traits:
- lexical search first
- then cheap summarization
- keeps long-tail memory out of the hot prompt

why this is good:
- cost-aware
- lets the agent recall old context without dragging huge history into every turn

### layer 4 — skills as procedural memory
Hermes separates facts from procedures.

memory = what is true / important
skills = how to do something

why this is good:
- stops the core memory from becoming a junk drawer
- keeps reusable workflows in a separate lane

---

## where Hermes is especially strong

### 1. frozen snapshot pattern
Hermes loads memory once and keeps the prompt stable for the session.

why it matters:
- prompt caching stays valid
- behavior does not drift every time memory changes
- writes can still happen immediately without exploding costs

for purr:
- this is one of the best things to steal
- purr should also have a hot memory pack that is stable for a session/window, not rebuilt on every little event

### 2. bounded memory discipline
Hermes forces memory to stay small.

why it matters:
- keeps quality high
- forces consolidation
- prevents “save everything forever in prompt” brainrot

for purr:
- same principle should survive
- but the hot pack should be generated from a bigger structured store, not be the whole store itself

### 3. persistent-memory safety scanning
Hermes scans memory content for prompt injection / exfil patterns because memory gets re-injected later.

why it matters:
- persistent memory is an attack surface
- especially if any memory can be derived from untrusted content

for purr:
- absolutely reuse this mindset
- if purr ever stores user-generated or network-derived memory summaries, sanitize them before they become prompt material

### 4. proactive memory capture
Hermes does not just hope the model remembers to save memory.
It has:
- memory nudges after enough turns
- memory flush before compression
- session end / reset flush behavior

why it matters:
- memory capture is operationalized
- the model gets a final chance to preserve what matters before context disappears

for purr:
- same principle, but likely event-driven and server-side
- important memory extraction should not depend only on the live chat loop

### 5. transcript store separate from hot memory
This is probably the cleanest Hermes move.

why it matters:
- transcripts are the raw mine
- hot memory is the refined metal
- search/summarize bridges the two

for purr:
- same exact philosophy should hold
- raw chat should live in durable storage
- only selected memory items or compact retrieval packs should hit the LLM prompt

### 6. stored prompt snapshot reuse across continued sessions
Hermes does not just freeze the prompt in RAM.
It stores the full assembled system prompt in SQLite and reuses that exact prompt on later session continuation instead of rebuilding from disk.

why it matters:
- prevents cache breakage across gateway/CLI continuation
- avoids re-injecting memory changes the model already wrote itself
- makes the active prompt a session artifact, not a live view of files

for purr:
- we should likely persist the exact session hot pack / prompt pack per conversation window
- continuation should reload that pack unless a deliberate rebuild event happens

### 7. compression with lineage, not overwrite
When Hermes compresses, it ends the old session, creates a new child session, and links them with `parent_session_id`.

why it matters:
- transcript audit trail stays intact
- search still has access to the pre-compression raw session
- the active conversation gets smaller without pretending old detail never existed

for purr:
- relationship history should also keep lineage/episode structure
- summaries should never become the only surviving truth

### 8. structural integrity guards during compression
Hermes does not only summarize semantics.
It also protects tool-call structure:
- avoids splitting tool-call/result groups at boundaries
- removes orphan tool results
- inserts stub tool results if needed so the API still accepts the compressed history

why it matters:
- long-context systems break in ugly ways if compression corrupts message structure
- this is hidden infra quality, but it is real quality

for purr:
- any background cognition / hidden tool lane needs the same integrity mindset
- summary or archive jobs must not break causal/evidence structure

---

## where Hermes is weak for purr

### 1. flat free-text memory entries
Hermes memory entries are basically note blocks.
Good for an assistant. weak for a richer memory product.

missing fields purr needs:
- memory id
- owner id
- purr id
- kind
- state
- confidence
- salience
- created_at
- last_confirmed_at
- evidence refs
- supersedes/conflicts_with
- review schedule

### 2. tiny scope
Hermes has very small memory caps.
Good for assistant continuity.
Not enough for:
- long-running relationship memory
- episodic memory
- emotional patterns
- social memory / catnet memory
- corrections over time

### 3. weak per-user product isolation by default
Hermes is basically one environment, one agent state, one memory area.
Fine for local agent use.
Not enough for a product where every human has a separate purr.

### 4. lexical recall only at search layer
FTS5 is useful but lexical.
Semantic memory needs more.

for purr:
- vector should support fuzzy/semantic recall
- but vector should not replace structured memory state

### 5. no explicit lifecycle
Hermes memory is mostly add/replace/remove.
Purr needs real lifecycle states:
- candidate
- confirmed
- rejected
- stale

without this, “i remember everything” becomes “i accumulate noise forever.”

### 6. same-session memory goes stale on purpose
Hermes chooses prompt stability over same-session freshness.
That is a rational assistant tradeoff.
For purr, it becomes a product risk.

failure pattern:
- user corrects something now
- memory write succeeds
- active prompt still reasons from the old snapshot

for purr:
- session pack can stay mostly frozen
- but we need a live turn-level override lane for direct corrections / contradictions / high-value new facts

### 7. memory mutation is substring-based text editing
Hermes updates memory by matching short text substrings inside flat entries.

why this breaks for purr:
- ambiguous matches are common as memory grows
- contradictions become text-management problems instead of state transitions
- there is no first-class provenance / evidence / supersedes graph

### 8. recall is lexical first, summary second
Hermes recall is good enough for agent continuity, but not enough for product-grade relational memory.

limits:
- FTS5 is lexical
- `session_search` skips the current session
- returned memory is a summarized recap, not canonical structured truth

for purr:
- recall should unify current session, recent episodes, and long-term memory under one retrieval contract
- semantic help should exist, but structured filtering has to lead

### 9. compression summaries can become lossy stand-ins
Hermes compression is careful, but summaries are still summaries.
If the summary model fails, middle turns may even be dropped.

for purr:
- summaries can be navigation aids
- they must not become the main truth source for relationship memory
- canonical truth needs ledger rows + evidence refs back to raw history

---

## what purr should steal from Hermes

steal these almost directly:
- layered memory model
- frozen hot-memory snapshot pattern
- bounded hot context
- durable transcript store
- proactive memory flush / capture moments
- memory security scanning
- separation of factual memory from procedural logic

---

## what purr should not steal directly

do NOT copy as-is:
- flat MEMORY.md / USER.md as the main product memory
- substring-based edits as the main mutation model
- lexical search as the only recall lane
- one global memory namespace
- no confidence / no review / no staleness model

---

## purr-grade version of the same architecture

### hot layer
small prompt pack for current interaction:
- core tone + relationship facts
- active preferences
- unresolved loops
- a tiny number of relevant episodes

### ledger layer
Supabase source of truth:
- structured memory items
- feedback events
- review checks
- session/message references

### recall layer
retrieval service:
- filter by owner/purr
- rank by relevance + recency + confidence + salience + unresolved status
- vector only where semantic help is real

### raw layer
messages/sessions:
- durable transcript store
- source for later extraction and audit

---

## direct conclusion

Hermes already teaches the main lesson:
never confuse raw history with usable memory.

for purr the move is not “build a bigger MEMORY.md.”
it is:
- keep Hermes’ layering discipline
- move the real store to structured per-user data
- generate compact memory packs on demand
- make correction and verification first-class

that is the lane.
