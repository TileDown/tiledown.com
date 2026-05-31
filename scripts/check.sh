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

run_browser_checks() {
  if "$PYTHON" - <<'PY' >/dev/null 2>&1
import playwright.sync_api
PY
  then
    BASE_URL="http://localhost:$PORT" "$PYTHON" "$ROOT/test_site.py"
  elif command -v uv >/dev/null 2>&1; then
    BASE_URL="http://localhost:$PORT" uv run --with playwright "$PYTHON" "$ROOT/test_site.py"
  else
    echo "Python Playwright is not installed. Install it for $PYTHON, or install uv for the ephemeral Playwright runner." >&2
    exit 1
  fi
}

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

run_browser_checks
