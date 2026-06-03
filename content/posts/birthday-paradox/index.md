---
title: The birthday paradox
date: 2026-06-03
description: In a room of 23 people the odds two share a birthday are better than even. A clean demonstration that uses a formula, a chart, and a table, all rendered to static SVG at build time.
tags: Math, Probability, Charts
image: /assets/post-birthday.svg
imageDark: /assets/post-birthday-dark.svg
---
# The birthday paradox

In a room of just **23 people**, the odds that two of them share a birthday are
better than even. Most people guess you would need closer to 180. The gap between
that guess and the truth is what makes this a paradox, and it is a clean little
demonstration of why exponential intuition fails us.

## The math

It is easier to count the chance that *no one* shares a birthday and subtract from
one. Lining people up one by one, each must avoid all previous birthdays, giving the chance of a match `P`:

$$P = 1 - \frac{365!}{365^n \cdot (365 - n)!}$$

The reason it climbs so fast is that the number of *pairs* who could match grows
with the square of the group:

$$\frac{n(n - 1)}{2}$$

At 23 people that is already 253 pairs, each a separate chance to collide.

## The numbers

| People | Pairs | Chance of a shared birthday |
|---:|---:|---:|
| 10 | 45 | 12% |
| 23 | 253 | 51% |
| 30 | 435 | 71% |
| 41 | 820 | 90% |
| 57 | 1596 | 99% |
| 70 | 2415 | 99.9% |

```chart
type: bar
title: Chance two people share a birthday
categories: 10, 23, 30, 41, 57, 70
x-label: people in the room
y-label: chance (%)
series: P(match) = 12, 51, 71, 90, 99, 99.9
```

> Past about 60 people a shared birthday is all but guaranteed, yet you would need
> 367 people to *guarantee* it by the pigeonhole principle. The curve gets to
> near-certainty long before it gets to certainty.

Every formula and the chart above are static SVG produced at build time: no
MathJax, no chart library, no JavaScript.
