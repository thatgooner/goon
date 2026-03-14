# supply-chain-verifier

Scans hermes skills, prompts, and payloads for supply-chain security risk. Rule-based, no LLM required.

**Mission**: M1 (security)

## what it detects

| category | severity | what |
|----------|----------|------|
| shell_exec | high | subprocess, os.system, eval, exec, __import__ in scripts |
| base64_payload | high | base64 encode/decode in scripts, embedded base64 strings |
| obfuscation | high | hex/unicode escape sequences, chr() chains, rot13, codecs |
| memory_modification | high (scripts) / low (docs) | writes to MEMORY.md, USER.md, hermes/memories |
| prompt_injection | high (scripts) / mid (docs) | "ignore previous", "you are now", jailbreak patterns |
| external_url | mid | URLs to domains not in known_safe_domains list |
| file_write | mid | open() in write mode, shutil.copy, pathlib writes |
| credential_access | mid | os.environ.get for API keys, .env, .git-credentials |
| missing_metadata | mid/low | SKILL.md missing name/description (required) or version/author/tags (recommended) |

## usage

```bash
# scan a single skill directory
python3 verifier.py hermes/skills/research/polymarket

# scan with JSON output
python3 verifier.py hermes/skills/research/polymarket --json

# full audit of all skills
python3 verifier.py hermes/skills/ --audit

# audit with JSON output
python3 verifier.py hermes/skills/ --audit --json

# filter by minimum severity
python3 verifier.py hermes/skills/ --audit --severity high

# use custom rules file
python3 verifier.py hermes/skills/ --rules custom-rules.json
```

## output format

Single scan:
```json
{
  "path": "/path/to/skill",
  "trusted": true,
  "issues": [
    {"type": "external_url", "detail": "URL references unknown domain: ...", "severity": "mid", "file": "scripts/api.py"}
  ],
  "hash_sha256": "abc123..."
}
```

- `trusted` = true only when zero high-severity issues found
- `hash_sha256` = SHA-256 of all file contents (deterministic, changes when any file changes)
- `issues[].file` = relative path within the scanned directory (only present for directory scans)

## customizing rules

Edit `rules.json` to:
- Add domains to `known_safe_domains` to suppress external_url warnings
- Add patterns to any detection category
- Adjust `required_skill_metadata` and `recommended_skill_metadata`

## running tests

```bash
python3 -m unittest tools/supply-chain-verifier/test_verifier.py -v
```

40 tests covering: all detection categories, clean/dirty skill directories, output format validation, real hermes/skills/ audit, edge cases.

## dependencies

- Python 3.8+
- PyYAML (for SKILL.md frontmatter parsing)
- No other dependencies
