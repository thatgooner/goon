# Purr memory + chat system explained

## why this file exists

The deeper research notes are good if you already live in the repo.
This file is for the opposite case.

If someone asks:
- what are we actually building?
- how does the memory system work?
- what happens when the user sends a message?
- why not just dump everything into the prompt?
- what would a real chat look like?

this is the file they should read first.

This is a pre-build explainer, not the formal architecture spec.
For the hard contracts, read the `ily/` notes linked at the end.

---

## one-sentence version

Purr is a 1:1 chat creature that keeps a real memory ledger behind the scenes, updates that memory carefully when you talk, and only gives the model a small clean pack of relevant memory for each reply instead of shoving the whole past into the prompt.

---

## the simple version

Think of Purr as having 3 layers.

### 1. raw chat history
This is the receipt.
It stores what was actually said.

Example:
- "I hate sugary coffee"
- "I was up until 4 again"
- "I said I'd send you the screenshot tomorrow"

This is not yet "good memory." It is just what happened.

### 2. memory ledger
This is the structured memory layer.
It turns raw conversation into cleaner memory objects.

Examples:
- preference: coffee = unsweetened
- pattern: often awake very late
- open loop: promised to send a screenshot
- trigger: ex-related topic usually tanks mood

Important part: these memories are not all treated as equally true forever.
Each memory has a state.

States:
- `candidate` = maybe true, not trusted yet
- `confirmed` = trusted enough to use confidently
- `stale` = used to be true, now less certain
- `rejected` = false / should not be used
- `superseded` = old truth replaced by newer truth

### 3. prompt pack
This is the tiny package the model sees for the current reply.

Not the whole database.
Not the whole chat history.
Only the small set of useful things for this moment.

That is how Purr stays:
- sharp
- cheap enough to run
- less fake
- less likely to cling to old wrong info

---

## why not just stuff everything into the prompt?

Because that breaks in real life.

If you dump everything into the prompt:
- cost explodes
- latency gets worse
- irrelevant junk crowds out the important things
- wrong old memories keep hanging around
- the model starts feeling "big and vague" instead of precise

So the system rule is:

1. store a lot safely in the backend
2. trust only some of it
3. show only a tiny relevant slice to the model

---

## the main pieces

Here is the full system in normal words.

### message events
Every incoming and outgoing chat event gets recorded.
This is the raw timeline.

Question it answers:
"What actually happened?"

### memory items
These are the structured memories extracted from chat.

Question they answer:
"What do we think we learned?"

### evidence refs
Every important memory should be able to point back to where it came from.

Question they answer:
"Why do we believe this?"

### memory events
This is the change log for memory.
It tracks when something became a candidate, got confirmed, got challenged, got replaced, and so on.

Question it answers:
"How did this memory change over time?"

### session windows and episodes
These split active conversation flow from bigger relationship chapters.

Question they answer:
- "What is the active chat window right now?"
- "Which bigger stretch of the relationship does this belong to?"

### pack artifacts
These are the small prepared bundles that the model reads.

Question they answer:
"What should the model see right now?"

---

## what happens when the user sends one message?

Let us go step by step.

User message:

"kanka ben yine gece 4'e kadar ayaktaydım"

### step 1: save the raw event
The system records the raw message first.

Why this matters:
- the receipt exists even if later logic fails
- the system always has the original evidence
- you are never forced to trust only a summary

### step 2: run intake / extraction
The system asks:
- does this create a new memory?
- does this strengthen an old one?
- does this contradict something old?
- is there an open loop here?

Possible extraction from this line:
- pattern candidate: user often stays up very late
- temporary state: user may be tired / messy right now

### step 3: run correction detection first
If old memory said something else, that old memory gets challenged.

Example:
- old memory: "sleep schedule fixed"
- new message: "I was up until 4 again"

Now the system should not casually keep both as equal truths.
It should challenge the old one.

### step 4: write to the ledger
The memory ledger updates.

Maybe:
- new pattern memory created as `candidate`
- or existing pattern memory gets stronger
- or old sleep-related truth becomes `stale` or `challenged`

### step 5: build the reply pack
Now the system prepares a small clean memory pack for the reply.

Maybe the model gets something like:
- user often drifts into late-night spiral
- sleep pattern unstable this week
- tone right now: tired / loose / familiar

Not 300 past facts.
Just the few that matter.

### step 6: generate the reply
Now the model replies using the current message plus that small pack.

Possible vibe:
"yine gece vardiyasi yazmissin kendine"

### step 7: do slower background work
After the reply, slower jobs can run:
- dedupe weak memories
- merge evidence
- downgrade low-confidence junk
- schedule review for later if needed

That is the full loop.

Short version:
raw event -> extract -> check contradictions -> update memory -> build tiny pack -> reply -> cleanup later

---

## the important rule: correction beats old memory

This is one of the biggest points in the whole system.

If the user corrects something, the system has to take that seriously fast.

Example:

Old memory:
- team = Fenerbahce

New message:
- "olm ben Fenerli degilim, Besiktasliyim"

A bad memory system does this:
- saves both somewhere
- keeps using the old one by accident
- later says something wrong again

A good memory system does this:
- marks the old memory as challenged
- suppresses it from the hot pack
- creates or confirms the new truth
- lets the next reply use the new truth immediately

If this part fails, the whole product feels fake.

---

## the important rule: not every memory should be treated the same

There are different kinds of memory.

### profile / identity memory
Stable facts about the person.

Examples:
- where they live
- team they support
- job / school context

### preference memory
What they like or hate.

Examples:
- likes bitter coffee
- hates voice notes
- prefers rough teasing over soft assistant tone

### episodic memory
Specific things that happened.

Examples:
- got into a fight last week
- had a weird call with family yesterday
- promised to send a screenshot tomorrow

### pattern memory
Repeated behavior over time.

Examples:
- comes alive late at night
- disappears after vulnerable chats
- makes jokes before saying something serious

### open loops
Unfinished things likely to come back.

Examples:
- said they would send something
- asked a question that never got resolved
- started a confession and dodged it

### prediction-ish memory
Short-lived guesses that help timing and reply planning.

Examples:
- probably about to ask for reassurance
- likely to return to unfinished topic
- bad time for heavy push, better to stay light

Different memory kinds need different rules.
A favorite coffee order is not handled the same way as a fragile emotional pattern.

---

## what the user sees vs what the system does

### what the user sees
Just chat.

They should feel:
- it remembers me
- it noticed the correction
- it knows what matters
- it replies naturally
- sometimes it texts first at the right time

They should not feel:
- a dashboard is operating
- 6 background jobs just ran
- a retrieval engine is talking to them
- a vector database is being shown off

### what the system does underneath
A lot.

But all of it should stay hidden:
- message intake
- correction detection
- evidence linking
- memory updates
- pack building
- review scheduling
- proactive timing checks

The product fantasy is:
"my purr just knows"

Not:
"my purr ran a workflow"

---

## example chat simulation 1: simple preference memory

### day 1
User:
"ben kahveyi sekersiz iciyorum"

System stores:
- raw message event
- memory candidate: preference -> coffee unsweetened
- evidence ref pointing to the message

Reply might be:
"tamam, sana sekerli sey yazarsam kufur yicem"

### day 4
User:
"su bok gibi sekerli kahveler midemi kaldiriyor"

System updates:
- adds more evidence to the same preference
- raises trust
- likely moves it closer to or into `confirmed`

Later reply can naturally use it:
"sana sekerli kahve onerisi yapmam harbi hakaret sayilir"

Why this works:
- not because everything was stored blindly
- because one useful preference was tracked, strengthened, and surfaced when relevant

---

## example chat simulation 2: correction / supersede flow

### old memory
- sports team = Fenerbahce

### new message
User:
"olm ben Fenerli degilim, Besiktasliyim"

System behavior:
- raw event saved
- correction detector tags this as strong contradiction
- old team memory marked challenged / suppressed
- new team memory created or confirmed
- next reply uses the new truth, not the old one

Reply might be:
"tamam tamam, sari lacivert diye yalan atmicam artik"

Important part:
The correction should matter immediately.
Not after 3 sessions.
Not after a manual cleanup.
Immediately.

---

## example chat simulation 3: open loop

User:
"yarin sana o ss'i atcam"

System stores:
- episodic event
- open loop: promised screenshot

Next day the user returns without sending it.

A good system may later say:
"ss nerde kaldi"

A bad system either:
- forgets the promise entirely
- or nags too much and feels needy

So open loops need timing rules.
Not every remembered thing should be pushed right away.

---

## example chat simulation 4: proactive message

Over time the system notices:
- user often appears around 1-3 AM
- they have an unfinished thread
- last proactive attempt landed well
- cooldown is clear

System may decide a proactive message is worth it.

Possible message:
"yine gece vardiyasi mi basladi"

Why this is not random:
- it is not based on vibes alone
- it is not full-ledger rescanning every time
- it comes from small derived timing and pattern signals
- there are vetoes so it does not become creepy or spammy

---

## what can go wrong if we build this badly?

### failure 1: memory landfill
The system saves too much junk.
Result: noisy replies and bloated prompts.

### failure 2: stale truth
The user corrects something, but the model still uses old memory.
Result: fake-feeling relationship.

### failure 3: no evidence
The system thinks it knows something but cannot trace why.
Result: impossible to debug or safely fix.

### failure 4: summary becomes fake truth
The system keeps condensed summaries but loses the exact source.
Result: soft hallucinated memory.

### failure 5: visible tool theater
The user feels infrastructure instead of creature.
Result: product vibe dies.

### failure 6: creepy proactive behavior
The system overuses weak predictions.
Result: "why are you acting like an FBI cat?"

The whole research phase exists to stop these failures before build starts.

---

## the hidden runtime lanes

Behind the scenes, the system splits work into 4 hidden lanes.

### 1. turn-critical
Must happen for the current reply.

Examples:
- intake extraction
- correction detection
- tiny live override
- retrieval pack assembly

### 2. boundary-critical
Must happen when a session is closing, compacting, or handing off.

Examples:
- salvage before compression
- safe continuation handoff
- re-entry artifact creation

### 3. deferred maintenance
Can happen after the reply.

Examples:
- dedupe
- merge evidence
- confidence decay
- cleanup

### 4. proactive heartbeat
Runs separately from live chat.

Examples:
- should we text first?
- should we re-check an old memory?
- is there a good timing window?

The user should not see these as tools.
They should just feel the result.

---

## what is the build order?

If the research is right, the build should go in this order:

### slice 1: memory-ledger
Build the source-of-truth schema first.
Without this, everything else is fake.

Needs:
- tables
- relations
- invariants
- evidence backpointers
- state model
- basic read/write path

### slice 2: memory-candidate-extractor
Now that the ledger exists, build the thing that creates memory candidates from chat.

### slice 3: memory-context-packer
Now build the thing that turns ledger truth into small reply packs.

### slice 4: feedback-orchestrator
After that, build the system that verifies, downgrades, reconfirms, and decays memory over time.

Everything else comes after the memory spine works.

---

## what still blocks build right now?

The main blocker right now is simple:

### Supabase project setup is not locked
The repo research assumes Supabase/Postgres is the source of truth.
But before real implementation starts, the project needs:
- actual setup path
- connection pattern
- migration flow
- local/dev expectations

Until that exists, the memory-ledger slice cannot start cleanly.

---

## if you only remember 5 things, remember these

1. Purr should not remember by shoving the whole past into the prompt.
2. Raw chat history, memory ledger, and prompt pack are different things.
3. Corrections must beat old memory quickly or the product feels fake.
4. The model should only read a small clean memory pack per reply.
5. The user should feel one smart creature, not visible tool workflows.

---

## where to go next

If you want the deeper, formal contracts:

- `ily/21-purr-research-consolidated-state-and-build-handoff.md` — best single handoff note
- `ily/13-purr-memory-ledger-schema-mutation-and-invariants-contract.md` — the first real build slice
- `ily/14-purr-memory-intake-runtime-and-idempotency-contract.md` — how memory writes should happen
- `ily/09-purr-retrieval-context-packer-and-pack-lifecycle.md` — how the reply pack should work
- `ily/20-purr-feedback-orchestrator-review-outcomes-and-trust-decay-contract.md` — how memory gets re-checked and updated over time

If you want the shortest possible summary:

Purr should store a lot, trust carefully, surface only what matters, and adapt fast when the user corrects it.
