# i'm thatgooner

![cover](assets/cover.jpg)

i seen enough gooners to know one when i smell one so when u walk in here talkin bout automation like this some polished little system for healthy people i already know what time it is this repo just me givin the spiral better infrastructure before another good idea die between eighteen tabs one broken workflow and a night that got way too comfortable bein ugly so i dump the research the tools the infra notes the weird fixes and whatever else survive the session in here cause memory is a scam bookmarks are where useful links go to die and if i had to suffer to find it then it might as well pay rent if it saved me time it stayed if it saved my ass it got documented and if it was bullshit it got left in the tab graveyard where it belonged now take what helps quit actin dumb and keep it moving

## what's in here

```
notes/                  research brain
  boards/               mission + task boards (system state)
  daily/                day-by-day moltbook research
  watchlists/           operator candidates worth re-checking
hermes/                 agent config, memories, skills (mirrors ~/.hermes)
tools/                  codex build work (classifiers, scorers, verifiers)
scripts/                setup and sync scripts
```

## agents

| name | role | focus |
|------|------|-------|
| **gooner** | research | daily moltbook scouting, signal/noise separation |
| **codex** | build | tools, classifiers, schemas from gooner's findings |

both share state through `notes/boards/`. start there.

## setup on a new machine

```bash
git clone https://github.com/thatgooner/goon.git
cd goon

# pull hermes data into repo (first time only)
./scripts/hermes-sync.sh pull

# or symlink repo into ~/.hermes (recommended for live agent)
./scripts/hermes-sync.sh link
```

see [hermes/README.md](hermes/README.md) for details.

## start reading

1. [system board](notes/boards/system-board.md) — mission and priorities
2. [codex task board](notes/boards/codex-task-board.md) — build work queue
3. [today's research](notes/daily/) — latest daily note
4. [operator tracker](notes/watchlists/poly-operator-tracker.md) — watchlist
