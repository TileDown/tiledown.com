#!/usr/bin/env bash
# Build the public project website, serve it locally, and run browser checks.

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
PYTHON="${PYTHON:-python3}"
PORT="${WEBSITE_PORT:-8092}"
WORK=$(mktemp -d "${TMPDIR:-/tmp}/tiledown-website.XXXXXX")
OUT="$WORK/site"
pids=()

cleanup() {
  for pid in "${pids[@]:-}"; do kill "$pid" 2>/dev/null || true; done
  for pid in "${pids[@]:-}"; do wait "$pid" 2>/dev/null || true; done
  rm -rf "$WORK"
}
trap cleanup EXIT

"$ROOT/scripts/build.sh" "$OUT"

test -f "$OUT/index.html"
test -f "$OUT/features/index.html"
test -f "$OUT/docs/index.html"
test -f "$OUT/posts/index.html"
test -f "$OUT/tags/index.html"
test -f "$OUT/feed.xml"
test -f "$OUT/CNAME"
grep -q "tiledown.com" "$OUT/CNAME"
grep -q "<rss" "$OUT/feed.xml"

if lsof -ti "tcp:$PORT" >/dev/null 2>&1; then
  echo "Port $PORT is already in use. Free it or set WEBSITE_PORT." >&2
  exit 1
fi

( cd "$OUT" && exec python3 -m http.server "$PORT" >/dev/null 2>&1 ) & pids+=($!)

for _ in $(seq 1 50); do
  if curl -sf -o /dev/null "http://localhost:$PORT/"; then break; fi
  sleep 0.1
done

BASE_URL="http://localhost:$PORT" "$PYTHON" "$ROOT/test_site.py"
