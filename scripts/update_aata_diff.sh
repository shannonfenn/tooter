#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM_DIR="$ROOT_DIR/.cache/aata-upstream"
OUT_DIR="$ROOT_DIR/references/aata/diffs"

mkdir -p "$ROOT_DIR/.cache" "$OUT_DIR"

if [[ ! -d "$UPSTREAM_DIR/.git" ]]; then
  git clone --filter=blob:none --no-checkout https://github.com/twjudson/aata.git "$UPSTREAM_DIR"
fi

git -C "$UPSTREAM_DIR" fetch --tags --force

git -C "$UPSTREAM_DIR" log --oneline --reverse Annual-Edition-2021..Annual-Edition-2025 -- src \
  > "$OUT_DIR/2021-to-2025-commits.txt"

git -C "$UPSTREAM_DIR" diff --name-status Annual-Edition-2021..Annual-Edition-2025 -- src \
  > "$OUT_DIR/2021-to-2025-changed-files.txt"

git -C "$UPSTREAM_DIR" diff --stat Annual-Edition-2021..Annual-Edition-2025 -- src \
  > "$OUT_DIR/2021-to-2025-stat.txt"

git -C "$UPSTREAM_DIR" diff Annual-Edition-2021..Annual-Edition-2025 -- src \
  > "$OUT_DIR/2021-to-2025-source.diff"

echo "AATA diff reports updated in $OUT_DIR"

