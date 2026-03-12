---
title: "ApoorvCTF 4.0 - GEM (Glen's Enigmatic Module)"
pubDatetime: 2026-03-09T12:00:00+00:00
author: "JayJayTee"
---

You get two images (original and processed) and a script that recovers the 3x3 convolution kernel used on each RGB channel via least-squares. Running the script on these two images as args gives you three matrices:

```
Red:   [[ 1 -1  0], [-1  5 -1], [ 2 -1  0]]
Green: [[ 1  2  1], [-1  8 -1], [-3 -1  1]]
Blue:  [[-1 -4  1], [ 1  4  4], [-1  3  1]]
```

Flag format is `apoorvctf{d1_d2_d3}` where d1, d2, d3 are scalars from each matrix. The operation is the determinant.

```
det(Red)   = 1
det(Green) = 40
det(Blue)  = 35
```

The flag -

```
apoorvctf{1_40_35}
```

(You do NOT need a ./solve.py for this one. It's just two commands. I'm not joking.)