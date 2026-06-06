---
title: Compare
description: Where TileDown fits among static site generators — and where it does not. An honest look at the math and PDF niche it actually owns.
weight: 20
---
# How TileDown compares

TileDown is not trying to replace Hugo, Astro, or Eleventy. Those tools have huge
ecosystems, theme galleries, and plugin marketplaces TileDown does not have and is
not chasing. TileDown is opinionated and narrow on purpose: it is the static site
generator for **math- and document-heavy writing**, where the typeset output and a
clean build host matter more than theme count.

## Math, the honest comparison

Most ways to put math on the web fall into three buckets. Here is what each one
actually costs the reader and the build host:

| Approach | Ships to the reader | Needs on the build host |
|:---|:---|:---|
| **TileDown** | Static SVG glyph outlines, `currentColor`, a hidden MathML copy | Just Swift |
| MathJax | A JavaScript engine that lays out math in the browser | Nothing (work moves to the reader) |
| KaTeX | CSS plus a math web font (and JS, unless pre-rendered) | Node, for pre-rendering |
| `latex` + `dvisvgm` | Static SVG (similar result to TileDown) | A multi-gigabyte TeX install and several C binaries |

TileDown lands in the same place as the `latex + dvisvgm` pipeline — static,
self-contained SVG with no client runtime — but reaches it with a pure-Swift font
parser and box-and-glue engine, so the only build dependency is Swift. No LaTeX to
provision, no `dvisvgm`, no C libraries, clean on macOS and Linux.

## The part almost nobody else does

TileDown's math engine is shared with a PDF engine. The same `$$…$$` source that
becomes an SVG on the page is also typeset into the **Download PDF** every article
ships — by the same Swift code, with no headless browser and no print pipeline.
And because it is Swift, it compiles to WebAssembly, so the identical parser and
PDF writer can run live in your browser. One codebase covers build-time web,
in-browser, and print. That overlap is rare.

## Where TileDown is the wrong choice

Being honest is part of the pitch:

- **You need a big theme or plugin ecosystem.** Use Hugo, Astro, or Eleventy.
- **You rely on raw HTML, shortcodes, or MDX.** TileDown escapes raw HTML by
  design; that portability is a feature here, but it will get in your way.
- **You publish thousands of pages.** Build performance at that scale is unproven.
- **You are not on Swift.** The toolchain-free story is the whole point, but it
  still assumes a Swift build.

## Bottom line

If you write posts with real math, want a PDF of each one, and would rather not
provision a TeX toolchain or ship JavaScript to render a formula, TileDown is built
for exactly that. If you want a general-purpose site builder with a marketplace
behind it, reach for one of the big three — and TileDown will not be offended.
