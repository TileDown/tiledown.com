---
title: Docs
description: Current commands, architecture, and status for TileDown.
weight: 20
image: /assets/docs-preview.svg
imageDark: /assets/docs-preview-dark.svg
---
# Docs

TileDown is a Swift package under `Packages/`. The engine is `TileKit`; the CLI is
`tiledown`.

## Build this website

From the repo root:

```sh
scripts/build.sh
scripts/check.sh
```

The first command writes the generated site to `.build/website`. The second
command builds it, serves it locally, and runs Playwright checks against the
generated pages.

## CLI surface

```sh
tiledown help
tiledown version
tiledown build source.md template.html out.html
tiledown build-site content/ dist/
tiledown serve --port 8765 content/
tiledown doctor --publish content/
tiledown json content/index.md .build/home.json
tiledown fmt --check content/index.md
```

## Current status

| Area | Status |
|:---|:---|
| Markdown parsing | CommonMark plus a constrained profile |
| Built-in layouts | top navigation and left sidebar |
| Themes | standard and system themes with light/dark support |
| Posts | dated posts, latest posts, RSS, tags, draft exclusion |
| Source code | build-time syntax highlighting, including Markdown source disclosure |
| Tiles | callout, counter, and service-form internals |
| CLI diagnostics | help, serve, and doctor checks for content directories |
| Service forms | local service contracts are implemented; deployed proxy hosting is future work |
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
