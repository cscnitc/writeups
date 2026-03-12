---
title: "ApoorvCTF 4.0 - Project Mirrorfall"
pubDatetime: 2026-03-12T12:00:00+00:00
author: "JayJayTee"
---

The challenge combined repository forensics, classified document analysis, and deterministic ML embeddings to extract two variables X and Y forming the flag. Category was OSINT / Repository Forensics / AI Embeddings.

## Objective 1: Repository Forensics

The 2013 intelligence disclosures pointed to the Snowden archive. The target was the public GitHub mirror `iamcryptoki/snowden-archive` and specifically the BULLRUN classification guide PDF dated September 5, 2013.

The challenge asked for the commit SHA of **that specific file**, not the repo's latest commit. The key insight is using `git log` scoped to the file path:

```
git clone https://github.com/iamcryptoki/snowden-archive
cd snowden-archive
git log -- documents/2013/20130905-theguardian__bullrun.pdf
# Output:
# commit 7d88323521194ed8598624dc3a932930debdde1d
```

**Variable X = `7d88323`** (first 7 characters of the commit SHA)

## Objective 2: ECI Codeword Extraction

Downloaded and parsed the BULLRUN classification guide PDF. The challenge referenced Appendix A but the ECI list was actually in the Remarks column of row A.2 on page 2:

```
APERIODIC, AMBULANT, AUNTIE, PAINTEDEAGLE,
PAWLEYS, PITCHFORD, PENDLETON, PICARESQUE, PIEDMONT
```

The second entry — an 8-letter codeword — is `AMBULANT`. Normalized to lowercase: `ambulant`.

## Objective 3: Semantic Embedding

Passed the normalized codeword through the `all-MiniLM-L6-v2` sentence transformer model. This model is fully deterministic — the same input always produces the same vector. Index 0 of the embedding rounded to 4 decimal places gives the second variable.

**Variable Y = `0.0245`**

The flag -

```
apoorvctf{7d88323_0.0245}
```

code [here](./solve.py)