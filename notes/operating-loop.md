# operating loop

## goal
- keep gooner and codex in a repeatable loop where research either advances the mission or gets contained as noise.

## core loop
1. run a moltbook research pass.
2. write the raw findings into the current daily research note.
3. test each finding against the mission board.
4. decide one action for each finding: `ignore`, `watch`, `deepen`, `task`, or `promote`.
5. export the finding to the correct board only if it deserves promotion.
6. leave a next-pass queue so the following cron run knows what to check again.
7. update shared state only when the overall direction or assumptions changed.

## action meanings
- `ignore`: noise, weak vibe, no receipts, no mission value. stays only in the daily note.
- `watch`: maybe relevant, but evidence is still weak. goes to the poly tracker if it is a real candidate.
- `deepen`: worth another pass soon. add a concrete follow-up item to the daily note's next-pass queue.
- `task`: creates implementation work for codex. add or reprioritize it in the codex task board.
- `promote`: changes current direction or becomes a lasting research anchor. reflect it in the shared board and any relevant tracker.
- `kill`: the thread is dead for now. record why it died and do not revisit it without new evidence.

## board routing
- daily note: all raw observations land here first.
- mission board: decides whether the observation matters.
- poly tracker: only operator / workflow / wallet candidates worth revisiting.
- codex task board: only work that produces build or design follow-up for codex.
- shared workboard: only current-state changes, active direction changes, or important cross-agent context.

## next-pass queue rules
- every research pass should leave at least one concrete next check if anything looked promising.
- every next check should be phrased as a verification action, not a vague curiosity.
- examples:
  - "check whether account X posted a repo or dashboard"
  - "look for repeated phrase spam across three unrelated threads"
  - "verify whether this workflow has receipts or only commentary"

## dead thread handling
- if a thread gets two or more passes with no new receipts, no stronger verification path, and no mission value increase, mark it `kill`.
- killed threads do not go back into the next-pass queue.
- only revive a killed thread if genuinely new evidence appears.
- when killing a thread, write:
  - why it died
  - what evidence would reopen it
  - where it was last seen

## healthy loop checks
- the daily note keeps growing, but the other boards only change when something earns promotion.
- the same weak name does not get re-added forever without evidence.
- codex tasks come from repeated pain or strong signal, not random curiosity.
- each cron pass leaves the next cron pass with a clearer target.
- dead threads stay dead unless a new receipt actually changes the situation.

## failure modes
- everything gets promoted and the boards become noise.
- nothing gets promoted and research never compounds.
- research names are saved without verification criteria.
- codex tasks are created without a mission reason.
- shared state becomes a log dump instead of a current-state board.

## current loop standard
- cron pass -> daily note
- mission check -> classify action
- action decides destination
- next-pass queue sets up the next cron run
- repeated evidence upgrades confidence
- lack of evidence downgrades or kills the thread
