# hermes agent data

this directory mirrors the live `~/.hermes/` state from the AWS instance.

## what lives here

| path | what it is | synced? |
|------|-----------|---------|
| `config.yaml` | model, tools, terminal, compression settings | yes |
| `.env` | API keys — **never commit this** | gitignored |
| `memories/MEMORY.md` | what the agent has learned | yes |
| `memories/USER.md` | user profile and preferences | yes |
| `skills/` | agent-created reusable skills | yes |
| `sessions/` | conversation history (SQLite) | gitignored |

## how it connects to the live agent

after cloning this repo on your AWS instance, run:

```bash
./scripts/hermes-sync.sh link
```

this creates symlinks from `~/.hermes/` pointing into this repo so the live agent reads and writes directly to version-controlled files.

to pull live hermes data into the repo (without symlinks):

```bash
./scripts/hermes-sync.sh pull
```

to push repo data back to `~/.hermes/`:

```bash
./scripts/hermes-sync.sh push
```

## rules

- never commit `.env` — it contains API keys
- never commit `sessions/` — it's large and may contain sensitive conversation data
- commit `config.yaml`, `memories/`, and `skills/` regularly to keep the repo as the source of truth
