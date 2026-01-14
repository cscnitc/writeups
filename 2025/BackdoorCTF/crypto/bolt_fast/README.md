---
title: "BackdoorCTF 2025 - bolt fast"
pubDatetime: 2026-01-14T03:33:00+05:30
author: "astroanax"
---
I chose this as one of the easiest because the author intentionally used a tiny 16-bit value inside the RSA key generation which makes factoring trivial with a small search.
I thought this one could be doable coz `dp_smart`was a 16 bit prime, so that pointed towards something there. Maybe we could factor it?

`chall.py` gives us `N`, `e`, and `c`. I was stuck what do this for a few minutes, tried seeing if the "you can't even use weiner's attack now hahaha" comment had any gotchas, but then realized that since `e` is `inverse(dp_smart, p-1)`, $p = \frac{e * dp - 1}{t+1}$ and thus we can brute force all dp values, check `t` for each of them.
If `p` divides `N`, we have factorized it and then can find the $\phi$ and then decrypt `c`.

flag: `flag{w31n3r_d1dn7_73ll_y0u_70_b3_6r33dy}`

code [here](./solve.py)
