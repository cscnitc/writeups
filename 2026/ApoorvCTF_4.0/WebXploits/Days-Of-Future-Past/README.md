---
title: "ApoorvCTF 4.0 - Days of Future Past"
pubDatetime: 2026-03-09T12:00:00+00:00
author: "JayJayTee"
---

Web app storing encrypted messages with a XOR stream cipher. You need to forge admin access and then break the encryption to get the flag.

Checking the HTML source gives you a few hints in comments - a `/backup/` path and `/static/js/app.js`. The JS has a hardcoded backup config path `/backup/config.json.bak` and a commented reference to an `X-API-Key` header. Fetching the bak file gives you the API key.

With that key you can hit `/api/v1/debug` which hands over a JWT secret derivation hint: "Company name (lowercase) concatenated with founding year". Company is CryptoVault, founded 2026, so the secret is `cryptovault2026`. You can verify this against the SHA-256 hash the endpoint also returns. Then forge an admin token:

```python
jwt.encode({"sub": "rad", "role": "admin", "exp": 9999999999}, "cryptovault2026", algorithm="HS256")
```

That gets you into `/api/v1/vault/messages` which returns 15 XOR-encrypted messages in hex. The debug endpoint also tells you they all use the same key stored in an HSM that can't be exported. That's the vulnerability — reusing the same XOR key across all 15 messages is the classic many-time pad mistake.

When you XOR two ciphertexts encrypted with the same key, the key drops out completely: `C1 XOR C2 = M1 XOR M2`. You're left with two plaintexts XORed together. With 15 messages that's over 100 pairs to work with.

The space trick makes this tractable - XORing a space (0x20) with any lowercase letter gives the uppercase version and vice versa. So if you XOR two ciphertexts and see a readable letter at some position, there's a good chance one message has a space there. That gives you a bunch of probable key bytes.

From there crib dragging does the rest. All 15 messages start with `apoorvctf{` which gives you 10 key bytes immediately. Each confirmed byte decrypts that position across all 15 messages, which reveals more plaintext, more cribs, more key bytes. Snowball from there.

The flag -

```
apoorvctf{3v3ry_5y573m_h45_4_w34kn355}
```

code [here](./solve.py)