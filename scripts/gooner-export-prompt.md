# prompt for gooner — export yourself to the repo

copy-paste the block below into your hermes chat session with gooner.

---

```
i need you to export your full internal state to the goon repo so the coding-agent can see your config, memories, and skills. here is exactly what to do:

1. go to the repo:
   cd ~/goon

2. pull latest changes:
   git checkout main && git pull origin main

3. copy your hermes data into the repo:
   cp ~/.hermes/config.yaml hermes/config.yaml 2>/dev/null; \
   cp ~/.hermes/memories/MEMORY.md hermes/memories/MEMORY.md 2>/dev/null; \
   cp ~/.hermes/memories/USER.md hermes/memories/USER.md 2>/dev/null; \
   cp -r ~/.hermes/skills/* hermes/skills/ 2>/dev/null; \
   echo "done copying"

4. also dump a full listing of everything in ~/.hermes so we know what else exists:
   find ~/.hermes -type f | head -100 > hermes/file-listing.txt

5. show me your current config:
   cat ~/.hermes/config.yaml

6. show me what env vars you have set (just the names, not the values):
   env | grep -iE '(API|KEY|TOKEN|SECRET|NOUS|OPENROUTER|OPENAI|ANTHROPIC|HERMES)' | cut -d= -f1 | sort

7. commit and push:
   cd ~/goon && \
   git add hermes/ && \
   git commit -m "export gooner hermes state: config, memories, skills" && \
   git push origin main

after you do all of this, tell me:
- what model provider and model you are using
- what tools you have enabled
- what skills you have saved
- what MCP servers you are connected to (if any)
- what messaging gateway you use (telegram, discord, etc.)
- what your MEMORY.md says
- what your USER.md says
```

---

## what this gives us

after gooner runs this, the repo will have:
- `hermes/config.yaml` — live config
- `hermes/memories/MEMORY.md` — what gooner has learned
- `hermes/memories/USER.md` — user profile
- `hermes/skills/` — any skills gooner has created
- `hermes/file-listing.txt` — full map of ~/.hermes contents

the coding-agent (me or any other build agent) can then read all of this and understand gooner's full setup.

## after the export

tell the user to share the env var names that gooner listed in step 6. those are the keys the coding-agent needs access to if it will be building and testing tools that hit the same APIs.
