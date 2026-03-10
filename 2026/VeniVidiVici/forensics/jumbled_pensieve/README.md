---
title: "Veni Vidi Vici CTF 2026 - Jumbled Pensieve"
pubDatetime: 2026-01-20T01:11:00+05:30
author: "astroanax"
---

The description talked about the Department of Mysteries going dark and memories being fractured by a [Confundus Charm](https://harrypotter.fandom.com/wiki/Confundus_Charm). It mentioned 30 corrupted relics. The challenge was that some fragments need to be reassembled using an exclusive potion.

There were 23 pngs named scan_result, and 7 dat files. 

Running file gave pngs as 400x200 pixel images. The dat files were just binary data.

Looking at the first bytes of these dats, I saw the IHDR chunk identifier that belongs to pngs. The challenge description mentioned that beginnings lie out of order and identities are masked, which now made perfect sense. The shard files were pngs but their headers had been deliberately zeroed.

I figured the scan_result pngs were decoys, while the corrupted shards were what actually belonged to the Hunt.

The next thing came to mind was that I needed to XOR these 7 images.


My script using PIL gave me the flag.

So the final flag was VVV{Unshuffl3_Th3_M4g1c_Byt3s}. 

code [here](./solve.py)
