---
title: "ApoorvCTF 4.0 - Days Of Future Past"
pubDatetime: 2026-03-12T12:00:00+00:00
author: "JayJayTee"
---

A web application called CryptoVault stored encrypted messages using a XOR stream cipher. The attack chain combined JWT forgery for admin access followed by a many-time pad attack to recover the flag. Category was Cryptography / Web Exploitation.

## Step 1: Reconnaissance

The HTML source leaked useful hints in comments:

```
/api/v1/health        → debug/health endpoint
/backup/              → backup directory hint
/static/js/app.js     → frontend JS with full API map
```

The JS file contained a hardcoded backup config path and a commented-out hint about an `X-API-Key` header:

```js
// backupConfig: '/backup/config.json.bak'
```

## Step 2: JWT Secret Recovery & Forgery

Fetching `/backup/config.json.bak` revealed the API key. The `/api/v1/debug` endpoint (authenticated with the key) returned:

```json
"secret_derivation_hint": "Company name (lowercase) concatenated with founding year"
```

Company **CryptoVault**, founded **2026** → secret: `cryptovault2026`. Verified by the SHA-256 hash returned by the debug endpoint.

Forged admin JWT:

```python
jwt.encode(
    {"sub": "rad", "role": "admin", "exp": 9999999999},
    "cryptovault2026",
    algorithm="HS256"
)
```

## Step 3: Vault Access

The forged token unlocked `/api/v1/vault/messages`, returning 15 XOR-encrypted messages in hex. The debug endpoint confirmed a XOR stream cipher with a key in an HSM — meaning the key cannot be exported directly.

## Step 4: Many-Time Pad Attack

All 15 messages were encrypted with the **same key**. This is the classic many-time pad weakness:

```
C1 XOR C2 = (M1 XOR K) XOR (M2 XOR K) = M1 XOR M2
```

The key cancels entirely, leaving two plaintexts XORed together.

**The Space Trick** — XORing a space (0x20) with any lowercase letter produces the corresponding uppercase letter, and vice versa. With 15 messages and 105+ pairwise combinations, likely space positions fall out quickly.

**Crib Dragging** — sliding a known plaintext fragment (e.g. `apoorvctf{`) across ciphertext XOR pairs. All 15 messages shared the same flag-format prefix, giving 10 key bytes immediately. Each confirmed byte decrypts that position across every message, creating a snowball: more plaintext → more cribs → more key bytes.

The flag -

```
apoorvctf{3v3ry_5y573m_h45_4_w34kn355}
```
