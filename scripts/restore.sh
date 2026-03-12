#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="$HOME/.hermes"

echo "=== gooner restore script ==="
echo "this will rebuild gooner from the repo on a fresh machine."
echo ""

# ── step 1: install hermes-agent ──
if command -v hermes &>/dev/null; then
    echo "[1/6] hermes already installed: $(which hermes)"
else
    echo "[1/6] installing hermes-agent..."
    curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v hermes &>/dev/null; then
        echo "error: hermes not found after install. check PATH."
        echo "try: source ~/.bashrc"
        exit 1
    fi
    echo "  installed: $(which hermes)"
fi

# ── step 2: link repo data into ~/.hermes ──
echo "[2/6] linking repo data into ~/.hermes..."
"$REPO_ROOT/scripts/hermes-sync.sh" link

# ── step 3: set up .env ──
if [ -f "$REPO_ROOT/hermes/.env" ]; then
    echo "[3/6] .env already exists"
else
    echo "[3/6] creating .env from template..."
    cp "$REPO_ROOT/hermes/.env.example" "$REPO_ROOT/hermes/.env"
    echo "  IMPORTANT: edit hermes/.env and fill in your API keys"
    echo "  at minimum you need: OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN"
fi

# ── step 4: restore pairing data ──
echo "[4/6] restoring pairing data..."
PAIRING_DIR="$HERMES_HOME/pairing"
mkdir -p "$PAIRING_DIR"

if [ -d "$REPO_ROOT/hermes/pairing" ]; then
    cp -r "$REPO_ROOT/hermes/pairing/"* "$PAIRING_DIR/" 2>/dev/null || true
    echo "  pairing data restored"
else
    echo "  no pairing data in repo — you'll need to re-pair telegram"
    echo "  run: hermes gateway setup"
fi

# ── step 5: restore git config ──
echo "[5/6] setting git config..."
git config --global user.name "thatgooner"
git config --global user.email "ceekmf@gmail.com"
echo "  git user: thatgooner <ceekmf@gmail.com>"

# ── step 6: verify ──
echo "[6/6] verifying..."
echo ""

checks_passed=0
checks_total=5

if command -v hermes &>/dev/null; then
    echo "  ✓ hermes binary found"
    ((checks_passed++))
else
    echo "  ✗ hermes binary not found"
fi

if [ -f "$HERMES_HOME/config.yaml" ]; then
    echo "  ✓ config.yaml linked"
    ((checks_passed++))
else
    echo "  ✗ config.yaml missing"
fi

if [ -f "$HERMES_HOME/memories/MEMORY.md" ]; then
    echo "  ✓ MEMORY.md linked"
    ((checks_passed++))
else
    echo "  ✗ MEMORY.md missing"
fi

if [ -f "$HERMES_HOME/memories/USER.md" ]; then
    echo "  ✓ USER.md linked"
    ((checks_passed++))
else
    echo "  ✗ USER.md missing"
fi

if [ -d "$HERMES_HOME/skills" ] && [ "$(ls -A "$HERMES_HOME/skills" 2>/dev/null)" ]; then
    skill_count=$(find "$HERMES_HOME/skills" -name "SKILL.md" | wc -l)
    echo "  ✓ skills linked ($skill_count skills)"
    ((checks_passed++))
else
    echo "  ✗ skills missing"
fi

echo ""
echo "=== $checks_passed/$checks_total checks passed ==="
echo ""

if [ ! -f "$REPO_ROOT/hermes/.env" ] || [ ! -s "$REPO_ROOT/hermes/.env" ]; then
    echo "NEXT STEPS:"
    echo "  1. edit hermes/.env and add your API keys"
    echo "  2. run: hermes gateway setup    (to re-pair telegram)"
    echo "  3. run: hermes                  (to start gooner)"
else
    echo "NEXT STEPS:"
    echo "  1. run: hermes gateway setup    (if telegram pairing expired)"
    echo "  2. run: hermes                  (to start gooner)"
fi
