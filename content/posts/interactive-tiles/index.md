---
title: Interactive Tiles
date: 2026-06-01
description: Typed tiles can render scoped browser behavior while the rest of the page remains static.
tags: Tiles, Browser, JavaScript
image: /assets/post-interactive.svg
imageDark: /assets/post-interactive-dark.svg
---
# Interactive Tiles

TileDown pages are static files, but a typed tile can emit the browser behavior
it owns. That keeps interactivity explicit and local to the content that needs it.

The counter below is rendered by the generator and runs entirely in the browser.
It is not a framework dependency and it does not require build-time JavaScript.

:::tile counter
label: Count this tile
:::

## Why the boundary matters

- The engine and CLI stay Swift.
- The generated page can still contain visitor-side JavaScript where a tile needs it.
- Browser behavior can be tested with Playwright against the generated output.

:::tile callout
title: Browser-tested output
body: The website check clicks this kind of tile in Chromium, so generated behavior is verified where visitors will use it.
:::
