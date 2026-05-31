---
title: Markdown as Canonical Source
date: 2026-05-31
description: TileDown keeps Markdown on disk as the source of truth while deriving typed output.
tags: Markdown, Source, Swift
image: /assets/post-markdown.svg
imageDark: /assets/post-markdown-dark.svg
---
# Markdown as Canonical Source

TileDown treats Markdown as the author-owned format. The parser reads front
matter, CommonMark blocks, and typed tile directives into a structured model.

The formatter can then rewrite a document to one canonical profile:

```sh
swift run tiledown fmt --check source.md
swift run tiledown fmt --write source.md
```

That keeps the source stable enough for reviews and future visual editing while
still being a plain text format.
