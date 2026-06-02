---
title: Interactive Charts
date: 2026-06-03
description: When a chart needs richer hover behavior, TileDown renders it as an interactive tile that ships a small script for a styled, cursor-following tooltip.
tags: Charts, Interactive, JavaScript
image: /assets/post-interactive-charts.svg
imageDark: /assets/post-interactive-charts-dark.svg
---
# Interactive Charts

[Charts in Markdown](post:charts-in-markdown) are static SVG with zero shipped
JavaScript, which is the right default. But sometimes you want a richer hover: a
styled tooltip that follows the cursor and reads on touch and keyboard. TileDown
offers the same chart as an **interactive tile**, which opts into a small
page-local script. Static by default; interactivity is a deliberate choice.

Hover the bars below (or focus them with the keyboard):

:::chart
type: bar
title: Developer happiness, now interactive
labels: TileDown, Hugo, Jekyll, Bespoke PHP
series.Happy devs: 92, 71, 64, 12
:::

The data is the same fabricated benchmark from the static article; the difference
is the cursor-following tooltip. The script is scoped to interactive charts: a
page with only static fences ships none.

Same opt-in, with two series:

:::chart
type: line
title: Weekend rewrites, interactive
labels: Jan, Feb, Mar, Apr, May
series.Before: 4, 3, 4, 2, 3
series.After: 3, 1, 1, 0, 0
:::

This is the tile half of TileDown's split: static SVG is a Markdown capability;
the interactive chart is a tile, because interactivity is what a tile is for.
