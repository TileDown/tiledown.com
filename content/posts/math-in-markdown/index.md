---
title: Math in Markdown
date: 2026-06-03
description: Write TeX math in a Markdown block and TileDown typesets it to static SVG at build time. No client-side JavaScript, no web font, no MathJax. The glyphs are real outlines, the layout is exact, and it follows your light or dark theme.
tags: Math, LaTeX, Markdown
image: /assets/post-math.svg
imageDark: /assets/post-math-dark.svg
---
# Math in Markdown

Math is content, not a tile. Write a formula in a display block with the same
TeX notation the sibling MarkdownPDF project uses, and TileDown typesets it at
build time into a self-contained SVG: real glyph outlines, exact box-and-glue
layout, no client-side JavaScript and no downloaded math font. The page that
renders this sentence shipped the equation below as plain markup.

$$e^{i\pi} + 1 = 0$$

## How it works

A `$$...$$` block is parsed to a typed math tree, laid out by a shared
box-and-glue engine driven by the font's OpenType `MATH` table, and emitted as an
`<svg>` of `<path>` glyph outlines and vector rules. The outlines are extracted
from Latin Modern Math in pure Swift, so nothing is downloaded and the result is
identical in every browser. The fill is `currentColor`, so the math is dark on a
light page and light on a dark one, like the rest of the text. A visually hidden
MathML copy travels with each formula for screen readers and copy-paste.

Because the engine is shared with MarkdownPDF, the same source typesets to the
same shapes whether you target a web page or a PDF.

## Fractions, roots, and scripts

The quadratic formula nests a fraction over a radical whose sign scales to its
radicand:

$$\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

Superscripts, subscripts, and the closed form of a sum lay out together:

$$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$

## Big operators and limits

Operators grow in display style and carry their limits above and below:

$$\int_0^\infty e^{-x^2} = \frac{\sqrt{\pi}}{2}$$

$$\lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n = e$$

## Matrices

Environments like `pmatrix` lay out rows and columns with grown delimiters:

$$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$$

Every formula on this page is static SVG produced by the build. View source: there
is no script tag, and there is no font request.
