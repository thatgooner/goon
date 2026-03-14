# weekly missions — W1: 2026-03-14 -> 2026-03-20

## how this works
- 4 missions per week
- everything both agents do must serve one of them
- this week starts with research, not implementation
- code-worker should independently review and align before building tools
- old moltbook/poly mission is archived

---

## M1 — Hermes memory teardown

goal: inspect Hermes memory deeply enough that we know exactly what to steal, what to reject, and what to redesign for purr.

owner: both

this week:
- read Hermes memory stack in detail
- inspect curated memory, transcript storage, session search, memory flushes, and prompt stability decisions
- document where Hermes is genuinely strong and why
- document where Hermes is too flat/small/global for purr

success criteria:
- [ ] hermes strengths are written down clearly
- [ ] hermes limitations for purr are written down clearly
- [ ] reusable patterns vs non-reusable patterns are separated

---

## M2 — Purr alignment

goal: make sure any builder understands what purr actually is before touching infra.

owner: both

this week:
- lock the tone and fantasy
- lock the constraints: one purr per human, memory-first, no visible tool-call theater
- define what makes purr feel alive vs fake
- define what must stay off-lane in v1

success criteria:
- [ ] a clear purr brief exists
- [ ] code-worker can explain purr without turning it into a dashboard pet
- [ ] memory implications are tied back to product voice

---

## M3 — tool boundary + mobile reality

goal: decide where tools exist, where they stay invisible, and what World mini app / mobile webview changes architecturally.

owner: both

this week:
- decide whether tools are internal only or ever user-visible
- define which memory operations need internal tooling
- document World mini app constraints: webview, latency, re-entry, server-side persistence, notifications

success criteria:
- [ ] first-pass tool stance is explicit
- [ ] internal tooling boundaries are defined
- [ ] mobile/webview constraints are written into the architecture lane

---

## M4 — implementation plan, not implementation yet

goal: leave the week with a clean build order, not premature code.

owner: code-worker (independent review) + gooner (final taste)

this week:
- produce a build order after M1-M3 research
- decide the first implementation slice
- keep build candidates parked until research is aligned

success criteria:
- [ ] first implementation slice is chosen
- [ ] task board separates research phase from later build phase
- [ ] no flashy premature build work happens before alignment

---

## mission priority order

M1 > M2 > M3 > M4

rationale:
if we misread Hermes we copy the wrong memory ideas.
if we misread purr we build the wrong product.
if we misread the tool/mobile boundary we overcomplicate the UX.
only after that should we ship infra.
