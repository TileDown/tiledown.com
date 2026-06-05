# tiledown.com

The public TileDown website. Markdown + tile content in `content/`, built by the
`tiledown` CLI from the sibling `tile-down` engine, deployed to GitHub Pages.

## Release / versioning

- `versionName` in `content/tiledown.yml` is the **single source of truth** for the
  site version. Bump it on every release; it renders as `.td-brand-subtitle`.
- The Playwright suites derive the expected version from `tiledown.yml` at runtime
  (`_site_version()` in `test_site.py` / `test_live_site.py`). Do **not** hardcode a
  version string in a test again — that turned a one-line bump into a silent CI
  failure once already.
- The site version is intentionally **decoupled** from the `tile-down` engine
  version. They can differ.

## Before you push

- Run `scripts/check.sh`. It builds the site and runs `test_site.py` (26 browser
  checks) against a local server — the **same gate CI runs in its Build job**. A
  green local run is a faithful preview of CI.
- The Playwright suites encode the site's invariants (math SVG, embeds, theme
  toggle, tiles, RSS, version). Treat changing a tested value as editing a contract,
  not a string: grep the tests before changing rendered content.

## Deploy

- `main` is the deploy branch. Pushing to `main` triggers the Pages workflow:
  Build (with the `check.sh` gate) → Deploy → Live Playwright check
  (`test_live_site.py` against `https://tiledown.com`). A failed Build means Deploy
  never runs, so a broken gate fails safe.
- Workflow concurrency group is `pages` with `cancel-in-progress: false`: a failed
  run is harmless and the next push supersedes it.
