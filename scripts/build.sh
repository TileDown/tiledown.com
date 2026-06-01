#!/usr/bin/env bash
# Build the public project website from TileDown source content.

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
OUTPUT_ARG="${1:-"$ROOT/.build/website"}"
case "$OUTPUT_ARG" in
  /*) OUTPUT="$OUTPUT_ARG" ;;
  *) OUTPUT="$ROOT/$OUTPUT_ARG" ;;
esac
CONTENT="$ROOT/content"

if [ -n "${TILEDOWN_REPO:-}" ]; then
  ENGINE="$TILEDOWN_REPO"
elif [ -d "$ROOT/tile-down/Packages" ]; then
  ENGINE="$ROOT/tile-down"
elif [ -d "$ROOT/../tile-down/Packages" ]; then
  ENGINE="$ROOT/../tile-down"
else
  echo "Set TILEDOWN_REPO to a checkout of TileDown/tile-down." >&2
  exit 1
fi

if [ -n "${TILEDOWN_BASE_URL:-}" ]; then
  WORK=$(mktemp -d "${TMPDIR:-/tmp}/tiledown-site-content.XXXXXX")
  trap 'rm -rf "$WORK"' EXIT
  CONTENT="$WORK/content"
  cp -R "$ROOT/content" "$CONTENT"
  CONFIG="$CONTENT/tiledown.yml"
  if grep -q '^baseURL:' "$CONFIG"; then
    awk -v baseURL="baseURL: $TILEDOWN_BASE_URL" '
      /^baseURL:/ { print baseURL; next }
      { print }
    ' "$CONFIG" > "$CONFIG.tmp"
    mv "$CONFIG.tmp" "$CONFIG"
  else
    printf '\nbaseURL: %s\n' "$TILEDOWN_BASE_URL" >> "$CONFIG"
  fi
fi

rm -rf "$OUTPUT"
mkdir -p "$(dirname "$OUTPUT")"

swift run --package-path "$ENGINE/Packages" tiledown build-site "$CONTENT" "$OUTPUT"

echo "Website written to $OUTPUT"
