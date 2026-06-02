---
title: Charts in Markdown
date: 2026-06-02
description: Author charts inline with a fenced code block. TileDown renders static SVG, no client runtime, using the same notation as MarkdownPDF.
tags: Charts, Markdown, SVG
image: /assets/post-charts.svg
imageDark: /assets/post-charts-dark.svg
---
# Charts in Markdown

A chart is static content, so in TileDown it is plain Markdown, not a tile. Open a
fenced block tagged `chart`, describe the data in a few `key: value` lines, and the
generator renders a self-contained SVG at build time. No browser runtime, no
script tag, identical in every browser. The notation matches the sibling
MarkdownPDF project, so the same source renders in both engines.

Here is the only benchmark that matters:

```chart
type: bar
title: Developer happiness by static site generator
categories: TileDown, Hugo, Jekyll, Bespoke PHP
y-label: happy devs (%)
series: This year = 92, 71, 64, 12
```

A staggering **90% of developers** report being happier with TileDown than with
the generator they used last. We are legally and morally obligated to tell you
that these numbers are completely made up. We invented them. They are not real.
We did, however, render them honestly.

Trend data is just as rigorous. Weekend rewrites reportedly drop off a cliff once
the build stops fighting you:

```chart
type: line
title: Weekend blog rewrites per month
categories: Jan, Feb, Mar, Apr, May
x-label: month
y-label: rewrites
series: Before = 4, 3, 4, 2, 3
series: After = 3, 1, 1, 0, 0
```

And effort versus joy, plotted as honest-to-goodness `(x, y)` points (also
fabricated, but to scale):

```chart
type: scatter
title: Effort vs joy
x-label: hours configuring
y-label: joy
series: Generators = (1, 9), (3, 7), (8, 3), (14, 1)
```

A doughnut, because a hole improves morale:

```chart
type: doughnut
title: Where the build minute goes
categories: Compiling, Waiting, Doom-scrolling
series: Minutes = 3, 1, 26
```

Everything above is a **static SVG** chart: zero shipped JavaScript. Hover any
bar, point, or slice for a native tooltip. TileDown also renders the same data as
an **interactive tile**, which opts into a small script for a styled tooltip that
follows the cursor (charts are static by default; interactivity is a deliberate
opt-in):

:::chart
type: bar
title: Same data, now interactive
labels: TileDown, Hugo, Jekyll, Bespoke PHP
series.Happy devs: 92, 71, 64, 12
:::

The figures are invented; the rendering, the dark mode, and the static-by-default
output are real.
