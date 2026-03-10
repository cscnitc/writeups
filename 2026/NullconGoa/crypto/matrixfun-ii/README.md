---
title: "NullCon Goa CTF 2026 - Matrixfun II"
pubDatetime: 2026-03-09T12:00:00+00:00
author: "astroanax"
---

The chall.py base64 encodes any message, pads the stream to 16 byte blocks, maps each base64 character to an index in a 65 byte alphabet and then computes a matrix multiply plus a constant vector. The ciphertext is printed as a python list of integers. That helped me figure the encryption is an affine map on a 16 dimensional vector space over Z65. When the transform is affine and the oracle gives chosen plaintext encryptions the natural course is to learn the matrix and the offset and then invert the map.

The initial server output printed the flag ciphertext as an array -

```
first [40, 40, 55, 49, 43, 44, 45, 45, 62, 12, 10, 30, 30, 3, 2, 35, 64, 9, 63, 18, 1, 33, 64, 23, 10, 37, 26, 1, 6, 24, 6, 1, 30, 45, 30, 57, 9, 2, 51, 12, 16, 35, 28, 29, 42, 8, 40, 28]
```

I then wrote a script to send hex messages and receive the ciphertext lists. I tried floating point matrix inversion. That produced small rounding errors that corrupted the reconstructed base64 stream. The run failed with a UnicodeDecodeError when converting the recovered bytes to text. The log contained a UnicodeDecodeError for an invalid continuation byte. Floating point linear algebra is convenient but not exact and this was a case where exact modular arithmetic is required.

I made claude switch to a pure integer method. mod 65 is composite so I solved linear systems separately modulo 5 and modulo 13 then recombined results with CRT. For each ciphertext coordinate I treated the 16 input indices plus a trailing constant 1 as unknowns and solved for the coefficients by collecting many chosen plaintext encryptions. I used random 12 byte inputs which base64 encode into 16 bytes so each sample yields one block. I also collected more samples than necessary (ensure full rank in the elimination)

Using modular gaussian elimination for solving linear systems and a modular gauss jordan routine to invert matrices modulo a prime. After solving modulo 5 and modulo 13 I combined each coefficient with a small CRT helper. Once the rows of A and the vector b were recovered modulo 65 I inverted A modulo 5 and modulo 13 and used those inverses to compute x = A^{-1}(y - b) for each ciphertext block of the flag. Combining the solutions coordinate wise by CRT produced the original base64 stream, I stripped the added padding and base64 decoded to get the flag.

The flag -

```
'ENO{l1ne4r_alg3br4_i5_ev3rywh3re}'
```

code [here](./solve.py)
