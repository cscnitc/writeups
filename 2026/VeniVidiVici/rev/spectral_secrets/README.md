---
title: "Veni Vidi Vici CTF 2026 - Spectral Secrets"
pubDatetime: 2026-03-09T15:42:00+05:30
author: "astroanax"
---

This was a really fun hardware security challenge involving a custom 16-bit RISC CPU simulator with a Spectre-style vulnerability. The challenge presented a CPU with protected memory at addresses 0 through 7 containing the secret flag, and our goal was to extract those 8 bytes using a cache timing side-channel attack.

Looking at the chall files, I saw a complete cpu implementation in python with custom instructions, cache, and memory protection. The readme mentioned that the cache is exactly half the size of ram, which seemed important. The challenge author also said to take a closer look at the ldbi instruction and that something was off about the protections.

The ldbi instruction here does an indirect load. It reads a 2 byte pointer from a memory address, then a byte from that pointer address. The cache gets populated when reading the byte at the pointer address, but this happens before the permission check. The cache write is at lines 267-273, while the permission check that raises an exception is at lines 280-291. This is the classic [Spectre vulnerability](https://spectreattack.com/spectre.pdf) pattern where speculative execution leaves traces in the cache even when the access should have been denied.

If i trigger ldbi on a protected address, it will read the secret bytes as a pointer value, and then try to dereference that and cache the result before failing the permission check. Even though the instruction fails, the cache state has been modified based on the secret value. By probing which addresses got cached, we can infer the secret 

For the first byte at address 7, I can control what gets read alongside it by writing to address 8. When ldbi reads from address 7 in the unaligned case, it actually reads bytes from addresses 7 and 8 to form a 2 byte pointer. If I write 0x00 to address 8, then the pointer becomes secret[7] * 256. The cpu will then try to read from that and cache it. The cache is mapped with a 1 bit tag, so for any address, there is only one other address that maps to the same cache but with a different tag. If we prime the cache with the evicting address, and then trigger the ldbi, then probe the address again, we can measure the timing, which informs us of the eviction. If the evicting address is slow to access, it means it was evicted, which means our guess for the secret was correct and that address got cached by ldbi.

I wrote a python script that systematically probes all 256 values for each byte. For each guess, we calculate the corresponding pointer address, and does the process mentioned above.

Running the initial version of my exploit, I kept getting all 0s. After the organizers released a fix, I ran the exploit again and successfully got all 8 bytes. The pattern was to leak byte 7 first with the lower byte set to 0x00, then use that leaked byte as the known lower byte when leaking byte 6, and so on backwards through the secret.

The final flag bytes were 0x67, 0xF6, 0x97, 0x5E, 0xC4, 0x58, 0xBA, 0x5C, giving us the flag.

flag: `parsec{h4rdw4r3_in53cur1ty_0x67F6975EC458BA5C}`

code [here](./solve.py)
