---
title: Service Contracts Are Next
date: 2026-05-27
description: The service-form internals are tested, but the CLI still needs configuration loading.
tags: Services, Contracts, Roadmap
image: /assets/post-services.svg
---
# Service Contracts Are Next

The engine already has service contracts and service-form rendering tests. A
service-form tile can bind to a typed operation contract, render browser-safe
HTML, and avoid leaking server credentials.

The CLI does not yet load service bindings from `tiledown.yml`, so this public
site does not render a live service form. That is intentional: the missing work
is configuration and deployment plumbing, not a hidden demo path.
