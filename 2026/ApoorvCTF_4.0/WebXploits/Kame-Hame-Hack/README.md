---
title: "ApoorvCTF 4.0 - Kame-Hame-Hack"
pubDatetime: 2026-03-09T12:00:00+00:00
author: "JayJayTee"
---

Dragon Ball themed web game. You pick a fighter name and fight three bosses. Boss 3 is always rigged to have more power than you.

Tried SQL and XSS on the name field first. A SQL payload actually triggered an error page that looked like real feedback... complete red herring, the devs put it there on purpose to waste your time. Cost me a while.

Eventually checked the CSS source and found a comment:

```
/* power-level reads from player.__dict__["power_level"] */
```

So the backend is Python and power level is just an attribute on some player object. First instinct was to set it directly via the name field: `power_level=1000000`... which did absolutely nothing. After realising `__dict__.update()` can overwrite attributes directly, the actual payload is:

```
player.__dict__.update(power_level=999999)
```

The frustrating part is that the name field is also where you enter payloads, and whatever you type just shows up as your fighter name in the game. No error, no different response, nothing. A working injection looks completely identical to a broken one. I had actually entered the right payload and moved on assuming it didn't work. Only figured it out after fighting through to boss 3 with it set as the name — which at the time felt like just trying again rather than an actual solve.

The flag -

```
apoorvctf{J1nj4_N1nj4_baybay}
```

(You definitely do NOT need a ./solve.py for this one)