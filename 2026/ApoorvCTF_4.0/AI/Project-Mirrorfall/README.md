---
title: "ApoorvCTF 4.0 - Project Mirrorfall"
pubDatetime: 2026-03-09T12:00:00+00:00
author: "JayJayTee"
---

This looks like a three part challenge - git forensics, a classified PDF, and sentence embeddings. You need to find two variables X and Y to build the flag.

The challenge references the 2013 Snowden disclosures which points you to the snowden archive on github (`iamcryptoki/snowden-archive`). The target is the BULLRUN classification guide PDF from September 5 2013. The gotcha here is that the challenge wants the commit SHA for that specific file, not the latest commit on the repo... these are different. You scope `git log` to just that file path:

```
git clone https://github.com/iamcryptoki/snowden-archive
cd snowden-archive
git log -- documents/2013/20130905-theguardian__bullrun.pdf
# commit 7d88323521194ed8598624dc3a932930debdde1d
```

First 7 chars of that SHA give you **X = 7d88323**.

Next you open the PDF itself. The challenge says Appendix A but the ECI list is actually in the Remarks column of row A.2 on page 2:

```
APERIODIC, AMBULANT, AUNTIE, PAINTEDEAGLE, PAWLEYS, PITCHFORD, PENDLETON, PICARESQUE, PIEDMONT
```

Second entry, 8 letters, which refers to `AMBULANT`, normalized to `ambulant`.

Last part, run that word through `all-MiniLM-L6-v2` and take index 0 of the output vector rounded to 4 decimal places. The model is deterministic so same input always gives the same number. **Y = 0.0245**.

The flag -

```
apoorvctf{7d88323_0.0245}
```

code [here](./solve.py)