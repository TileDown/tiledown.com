---
title: Slug Overrides and References
date: 2026-05-28
description: A source folder can publish at a different slug while references still resolve.
tags: Routing, References, Markdown
image: /assets/post-routing.svg
imageDark: /assets/post-routing-dark.svg
slug: posts/reference-routing
---
# Slug Overrides and References

This post lives in `posts/custom-source-url/`, but its front matter publishes it
at `/posts/reference-routing/`.

The same build resolves internal references. For example, this link points to the
feature tour through a `page:` reference: [](page:features).

External links can also go through generated redirect shims, such as
[the design notes](link:design).
