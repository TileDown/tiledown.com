---
title: Browser-Visible Tiles
date: 2026-05-30
description: Some TileDown behavior only proves itself inside a browser.
tags: Tiles, Browser, Testing
image: /assets/post-tiles.svg
imageDark: /assets/post-tiles-dark.svg
---
# Browser-Visible Tiles

Swift unit tests cover the parser, model, renderer, and output contracts. They do
not fully prove generated browser behavior.

The project now has a Playwright gate that builds a fixture site, serves it
locally, and checks behavior in Chromium: image loading, tables, theme switching,
draft exclusion, feeds, and local tile JavaScript.

:::tile callout
title: Browser gate
body: The same fixture runs locally and in the Linux CI job.
:::
