---
title: Linux-First Builds
date: 2026-05-29
description: The engine targets macOS and Linux, so generated browser behavior is checked on Linux too.
tags: Linux, CI, Swift
image: /assets/post-linux.svg
imageDark: /assets/post-linux-dark.svg
---
# Linux-First Builds

TileKit targets macOS and Linux. The Linux path matters because the generator is
an engine and CLI, not just a local macOS tool.

The repository runs Swift build and tests in a Linux container. The browser gate
also runs on Linux, so generated-site behavior is checked where the public Pages
build is produced.

Local Linux runs can use Docker, Colima, Lima, or a native Linux machine.
