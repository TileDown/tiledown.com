---
title: Docs
description: Current commands, architecture, and status for Tiledown.
weight: 20
image: /assets/docs-preview.svg
---
# Docs

Tiledown is a Swift package under `Packages/`. The engine is `TileKit`; the CLI is
`tiledown`.

## Build this website

From the repo root:

```sh
scripts/build-website.sh
scripts/check-website.sh
```

The first command writes the generated site to `.build/website`. The second
command builds it, serves it locally, and runs Playwright checks against the
generated pages.

## CLI surface

```sh
cd Packages
swift run tiledown version
swift run tiledown build source.md template.html out.html
swift run tiledown build-site ../Website/content ../.build/website
swift run tiledown json ../Website/content/index.md ../.build/home.json
swift run tiledown fmt --check ../Website/content/index.md
```

## Current status

| Area | Status |
|:---|:---|
| Markdown parsing | CommonMark plus a constrained profile |
| Built-in layouts | top navigation and left sidebar |
| Themes | standard and system themes with light/dark support |
| Posts | dated posts, latest posts, RSS, tags, draft exclusion |
| Tiles | callout, counter, and service-form internals |
| Service forms | tested in the engine, waiting on CLI config loading |
| Live publishing | GitHub Pages workflow builds this site from source |
| Platforms | macOS and Linux build and test gates |

## Architecture

The design documents are part of the repository:

- [Design snapshot](link:design)
- [Open issues](link:issues)
- [Repository](link:repo)

The package is split into small targets: core product metadata, source parsing,
tile parsing, Markdown rendering, output rendering, site generation, service
contracts, service-form rendering, and the facade used by the CLI.
