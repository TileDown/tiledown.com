---
title: Publishing Pipeline
date: 2026-06-01
description: The public website is built from source content on Linux and deployed as static files.
tags: Publishing, Linux, CI
image: /assets/post-publishing.svg
imageDark: /assets/post-publishing-dark.svg
---
# Publishing Pipeline

This site is the product demo and the deployment proof. A GitHub Pages workflow
checks out the TileDown engine, builds the content with the Swift CLI, runs the
browser test suite, and uploads the static artifact.

The same source can also be built locally:

```sh
scripts/check.sh
```

## What ships

| Output | Generated from |
|:---|:---|
| HTML pages | Markdown folders and front matter |
| CSS | The built-in site theme |
| JavaScript | Only client behavior emitted by typed tiles |
| RSS | Published posts |
| Redirect shims | Named external links |

:::tile callout
title: Linux path
body: The website workflow validates the generated output on Linux before publishing it to GitHub Pages.
:::
