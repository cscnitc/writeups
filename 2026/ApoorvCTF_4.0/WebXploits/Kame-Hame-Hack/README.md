---
title: "ApoorvCTF 4.0 - Kame-Hame-Hack"
pubDatetime: 2026-03-12T12:00:00+00:00
author: "JayJayTee"
---

A Dragon Ball-themed web game where you enter a fighter name and battle three bosses. Bosses 1 and 2 are always beatable; boss 3 is rigged — the boss power always exceeds yours. Category was Web Exploitation.

## Recon

SQL and XSS injections on the fighter name field were tried first. A SQL payload triggered an error page that looked like feedback — it seemed like a red herring planted by the devs to waste time.

Inspecting the CSS source files revealed a comment:

```css
/* power-level reads from player.__dict__["power_level"] */
```

This exposed that the backend was Python (specifically, Jinja2, after inspection of cookie storage and the HTML source file) and that power level was stored as an attribute on a player object — meaning it could be overwritten via `__dict__`.

## Exploitation

Setting the power level directly via the name field had no effect:

```
power_level=1000000  ...doesn't work
```

The working payload uses `__dict__.update()` to overwrite the attribute directly:

```
player.__dict__.update(power_level=999999)
```

The tricky part: the fighter name field doubles as the payload input. Whatever you type becomes your displayed fighter name, including injections. There is no error, no confirmation, nothing visually different — a working injection looks identical to a failed one. The correct payload had been entered and discarded multiple times for this reason. It only became clear after fighting through to boss 3 with the payload active as the name.

The flag -

```
apoorvctf{J1nj4_N1nj4_baybay}
```