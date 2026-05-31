#!/usr/bin/env bash
# Build the public project website from Tiledown source content.

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
OUTPUT_ARG="${1:-"$ROOT/.build/website"}"
case "$OUTPUT_ARG" in
  /*) OUTPUT="$OUTPUT_ARG" ;;
  *) OUTPUT="$ROOT/$OUTPUT_ARG" ;;
esac

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

rm -rf "$OUTPUT"
mkdir -p "$(dirname "$OUTPUT")"

swift run --package-path "$ENGINE/Packages" tiledown build-site "$ROOT/content" "$OUTPUT"

echo "Website written to $OUTPUT"
