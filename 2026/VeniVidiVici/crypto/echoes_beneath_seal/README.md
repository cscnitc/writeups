---
title: "Veni Vidi Vici CTF 2026 - Echoes Beneath the Seal"
pubDatetime: 2026-01-18T17:57:00+05:30
author: "astroanax"
---

Another HP theme chall. The files we got were a readme with the story and an intercepts.txt containing what looked like a RSA encrypted messages with a custom alphabet and an encrypted memo.

The intercepts file started with a header showing a rune set which was a 63 character alphabet, followed by an encrypted memo that looked like a flag format with curly braces. Then came a hundred json objects each containing n, e, and c values for RSA.

I tried the Hastad attack on the e = 5 group since we had exactly 5 ciphertexts. Using CRT to combine them and then taking the 5th root gave us a plaintext. But the result was a fake flag telling us not to submit it. The word cesrap immediately stood out because it is parsec spelled backwards(parsec was the flag format for this CTF).
I also checked the e = 3 entries and found the same fake flag. Both entries 77 and 90 had the exact same ciphertext value but different moduli. Taking the cube root directly worked and gave the same cesrap fake flag.

I was stuck here, but Shaheen got it. He said it was just a vignere on the memo, and yeah that worked.

 The curly braces in both the memo and key were not in the rune set so I filtered those out and only operated on the alphabetic characters. Running the decryption on the memo gave us parsec followed by the real flag content.

flag: `parsec{d0_n0t_f0rg3t_y0ur_c0nst_ch4rs}`

code [here](./solve.py)
