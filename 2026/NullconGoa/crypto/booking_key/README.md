---
title: "NullCon Goa CTF 2026 - Booking Key"
pubDatetime: 2026-03-09T10:00:00+00:00
author: "astroanax"
---


Reading the chall script, the code walks a pointer through the book until it finds the char to encode and records how many forward steps were required. It then moves on to the next plaintext char. I misread a small detail, that after finding a match the code advanced the pointer once and started the next search from the following char. I wrote a decoder that expected counts to be distances from the next position rather than from the matched position.

When I tried that decoder against a sample ciphertext I got plausible strings but nothing reliable. The candidate set was large and different copies of the book produced different outputs. Tried thinking of a bunch of approaches, but they all didnt feel right.
I noticed my error, the encryption stops when book[current] matches the target character and it appends the count. It does not increment current after the match, meaning the next char search begins from the matched position. 


After fixing the decryption logic, The script loads the canonical book, extracts the ciphertext, brute forces starting positions, filters by charset, and tries the candidates until one is accepted. 

Running the decoder on with the canonical book gave a small number of plausible results which included the intended password.

The decryptor tries every start index and yields candidate plaintexts. The helper script accepts a pasted cipher array and prints candidates. The automated script wraps the decryptor and performs the interaction sequence needed to submit candidates until acceptance.

flag: ENO{y0u_f1nd_m4ny_th1ng5_in_w0nd3r1and}

code [here](./solve.py)
