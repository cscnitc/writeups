---
title: "NullCon Goa CTF 2026 - Tetraes"
pubDatetime: 2026-03-09T12:00:00+00:00
author: "astroanax"
---

The starting point was chall.py. The cipher looks like AES in shape with a 4x4 state, a SubBytes lookup, a rotate rows step, a MixColumns stage and an add round key. There were subtle difference, such as the per round key is implemented by rotating the 16 byte key instead of using an AES key schedule, and ark also XORs state[0][0] with r ^ 42 each round. The S box is an explicit tuple in the source and that made me want to check it first because SubBytes is the only non linear building block.

encrypt(key, key) was not equal to the key. The cipher was not involutive. Those negative checks told me there was no immediate algebraic collapse to exploit, so I inspected the S box values. The S box is almost a permutation but it had a duplicate entry. My quick output showed the S-box produced 256 entries but only 255 unique values and the duplicate was the value 0x64 at indices 0 and 140. Seeing that duplication changed the whole approach because a non bijective S box means two different inputs to SubBytes can map to the same output and a difference that is erased at SubBytes cannot be reintroduced by the following linear layers.

Given that structural defect and the fact the service reveals encrypt(key, key) and accepts chosen plaintexts under the same key, if you can force the byte entering SubBytes at some position to be either 0x00 or 0x8c, then the two different inputs that map to the same S output will collide. After SubBytes the MixColumns and XORs are linear, so the suppressed difference will be a full block collision in the ciphertext. That gives a simple oracle. For a fixed position p find x such that encrypt(block with x at p) equals encrypt(block with x ^ 0x8c at p). When you see that collision you realize that the key byte at p is either x or x ^ 0x8c, except for position zero where the first ark also xors 42 so the relation shifts by 42. Given that, the key recovery becomes a 2 step process. First we collect 2 candidates per byte by probing the oracle. Second, brute force the remaining 2^16 keys locally by checking which candidate key reproduces the banner ciphertext encrypt(key, key) that the server prints on connect. The brute force is trivial on my giga chad gaming rgb laptop


I batched many messages into one send and parsed many responses at once. The server prints the prompt message to encrypt after every result, so I counted prompts to know how many ciphertext lines to expect. This made the attack faster.

During the live session I observed different banner ciphertexts on different connections, such as -

cipher.hex() = '916c96a44ad10eba77ae08b398f1c1ce'
cipher.hex() = '85521f3d158fb2c60238bade92edc806'
cipher.hex() = '301ec6978d6d3c3815949a9534f3e63a'

The S box duplicate I found locally -

256 255
0x64 [0, 140]

Thus I got the flag

ENO{a1l_cop5_ar3_br0adca5t1ng_w1th_t3tra}

code [here](./solve.py)
