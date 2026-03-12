#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_REPO="$REPO_ROOT/hermes"
HERMES_HOME="$HOME/.hermes"

usage() {
    echo "usage: $0 {link|pull|push}"
    echo ""
    echo "  link  — symlink ~/.hermes files into this repo (recommended)"
    echo "  pull  — copy live ~/.hermes data into repo"
    echo "  push  — copy repo hermes data to ~/.hermes"
    exit 1
}

backup_if_exists() {
    local path="$1"
    if [ -e "$path" ] && [ ! -L "$path" ]; then
        local backup="${path}.backup.$(date +%s)"
        echo "  backing up $path -> $backup"
        cp -r "$path" "$backup"
    fi
}

do_link() {
    echo "linking ~/.hermes -> repo..."

    mkdir -p "$HERMES_HOME"

    local files=("config.yaml" "memories" "skills")

    for item in "${files[@]}"; do
        local src="$HERMES_REPO/$item"
        local dst="$HERMES_HOME/$item"

        if [ ! -e "$src" ] && [ ! -d "$src" ]; then
            echo "  skip $item (not in repo yet)"
            continue
        fi

        backup_if_exists "$dst"

        if [ -L "$dst" ]; then
            rm "$dst"
        elif [ -e "$dst" ]; then
            rm -rf "$dst"
        fi

        ln -sf "$src" "$dst"
        echo "  linked $dst -> $src"
    done

    if [ -f "$HERMES_REPO/.env" ]; then
        backup_if_exists "$HERMES_HOME/.env"
        ln -sf "$HERMES_REPO/.env" "$HERMES_HOME/.env"
        echo "  linked .env"
    else
        echo "  skip .env (create hermes/.env from hermes/.env.example first)"
    fi

    echo "done. hermes now reads/writes directly from the repo."
}

do_pull() {
    echo "pulling ~/.hermes data into repo..."

    if [ ! -d "$HERMES_HOME" ]; then
        echo "error: $HERMES_HOME does not exist"
        exit 1
    fi

    for item in config.yaml; do
        if [ -f "$HERMES_HOME/$item" ]; then
            cp "$HERMES_HOME/$item" "$HERMES_REPO/$item"
            echo "  pulled $item"
        fi
    done

    for dir in memories skills; do
        if [ -d "$HERMES_HOME/$dir" ]; then
            mkdir -p "$HERMES_REPO/$dir"
            cp -r "$HERMES_HOME/$dir/"* "$HERMES_REPO/$dir/" 2>/dev/null || true
            echo "  pulled $dir/"
        fi
    done

    echo "done. review changes with 'git diff' then commit."
    echo "reminder: .env is NOT pulled — manage secrets manually."
}

do_push() {
    echo "pushing repo hermes data to ~/.hermes..."

    mkdir -p "$HERMES_HOME"

    if [ -f "$HERMES_REPO/config.yaml" ]; then
        backup_if_exists "$HERMES_HOME/config.yaml"
        cp "$HERMES_REPO/config.yaml" "$HERMES_HOME/config.yaml"
        echo "  pushed config.yaml"
    fi

    for dir in memories skills; do
        if [ -d "$HERMES_REPO/$dir" ]; then
            mkdir -p "$HERMES_HOME/$dir"
            cp -r "$HERMES_REPO/$dir/"* "$HERMES_HOME/$dir/" 2>/dev/null || true
            echo "  pushed $dir/"
        fi
    done

    echo "done. hermes will pick up changes on next session."
    echo "reminder: .env is NOT pushed — manage secrets manually."
}

case "${1:-}" in
    link) do_link ;;
    pull) do_pull ;;
    push) do_push ;;
    *) usage ;;
esac
