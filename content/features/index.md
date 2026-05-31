---
title: Feature Tour
description: A live tour of the TileDown features this site can exercise today.
weight: 10
image: /assets/feature-tour.svg
imageDark: /assets/feature-tour-dark.svg
---
# Feature Tour

This page is intentionally built from ordinary TileDown Markdown. It exists to
exercise the user-facing features that already work in the CLI.

## Markdown source

TileDown parses CommonMark through Swift Markdown, then renders through TileKit.
Raw HTML is escaped by design, so source stays portable and editor-friendly.

> The Markdown file remains the canonical source. The engine derives rendered
> HTML, shared CSS, browser JavaScript, JSON, and feeds from that source.

Inline code like `swift run tiledown fmt --check source.md` uses the same theme as
code blocks:

```sh
cd Packages
swift run tiledown build-site ../Website/content ../.build/website
swift run tiledown json ../Website/content/index.md ../.build/home.json
```

## Tables, links, and images

| Capability | Example on this site |
|:---|:---|
| Pages | [](page:docs) resolves from a `page:` reference |
| Posts | [](post:browser-visible-tiles) resolves from a `post:` reference |
| Tags | [](tag:Tiles) resolves from a `tag:` reference |
| Socials | [GitHub](social:github) resolves from `tiledown.yml` |
| Redirects | [Design notes](link:design) goes through `/out/design/` |

![TileDown mark](/assets/tiledown-mark.svg)

## Typed tiles

The callout tile is static: it emits HTML and CSS but no browser runtime.

:::tile callout
title: Static tile
body: A callout tile demonstrates typed properties rendered into themed HTML.
:::

The counter tile is local: it emits JavaScript, but it does not need a server.

:::tile counter
label: Press to test JavaScript
:::

## Site generation

The site build turns `index.md` files into routes. The top-level folders become
navigation sections, dated posts feed the updates list and RSS, and post tags
generate tag filter pages.

The build also copies assets verbatim, writes one shared `styles.css`, creates
redirect shim pages for configured outbound links, and excludes `draft: true`
pages from the published output.

## Theme-aware page images

Pages can pair `image` with `imageDark` in front matter. Built-in layouts use the
pair for hero images and post-card thumbnails, switching with the same dark-mode
rules as the site theme. The homepage image on this site uses that path.

## Tag AND filtering

Generated tag pages are static URLs. Start with the [Markdown tag](/tags/markdown/)
and select Swift to narrow the listing to [Markdown AND Swift](/tags/markdown/swift/).
Selected tags stay visible in the tag bar, and clicking one removes it from the
current filter.
