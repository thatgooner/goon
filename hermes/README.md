# hermes agent data

this directory is gooner's brain. everything here mirrors the live `~/.hermes/` on the AWS instance.

if this repo is intact, gooner is never lost. clone + restore = gooner is back.

## what lives here

| path | what it is | in repo? |
|------|-----------|----------|
| `config.yaml` | model, tools, personality, all settings | yes |
| `.env` | API keys | **gitignored** — recreate from `.env.example` |
| `memories/MEMORY.md` | what gooner has learned | yes |
| `memories/USER.md` | user profile and preferences | yes |
| `skills/` | 80+ agent skills | yes |
| `pairing/` | telegram/whatsapp pairing state | yes |
| `sessions/` | conversation history | gitignored (large, sensitive) |

## restore gooner from scratch

if the AWS instance dies, or you want gooner on a new machine:

```bash
git clone https://github.com/thatgooner/goon.git
cd goon
./scripts/restore.sh
```

this will:
1. install hermes-agent (if not installed)
2. symlink config, memories, skills, pairing from repo into `~/.hermes/`
3. create `.env` from template (you fill in keys)
4. set git config
5. verify everything

then:
```bash
# fill in your API keys
nano hermes/.env

# re-pair telegram if needed
hermes gateway setup

# start gooner
hermes
```

## daily sync

if gooner is running with symlinks (`hermes-sync.sh link`), all changes to memories, skills, and config are automatically in the repo. just commit:

```bash
cd ~/goon
git add hermes/
git commit -m "sync gooner state"
git push
```

## manual sync (without symlinks)

```bash
./scripts/hermes-sync.sh pull    # copy ~/.hermes -> repo
./scripts/hermes-sync.sh push    # copy repo -> ~/.hermes
```

## rules

- never commit `.env`
- commit config, memories, skills, and pairing regularly
- if gooner learns something important, commit immediately
- if you change config in the repo, run `hermes-sync.sh push` or re-link
