---
title: "ApoorvCTF 4.0 - GEM (Glen's Enigmatic Module)"
pubDatetime: 2026-03-12T12:00:00+00:00
author: "JayJayTee"
---

A locked module gated by a mathematical operation on three convolutional kernels. The challenge provided two images (original and processed) and a Python script that recovered the kernels used to transform each colour channel. Category was AI / Image Processing.

## Recon

The provided script used least-squares regression to recover the 3×3 convolution kernel applied to each RGB channel. Running it against the two images produced:

```
Red:   [[ 1 -1  0], [-1  5 -1], [ 2 -1  0]]
Green: [[ 1  2  1], [-1  8 -1], [-3 -1  1]]
Blue:  [[-1 -4  1], [ 1  4  4], [-1  3  1]]
```

Flag format: `apoorvctf{d1_d2_d3}` — where d1, d2, d3 are integer scalars computed from each matrix.

## Exploitation

The scalar operation is the **determinant** of each kernel matrix:

```
det(Red)   = 1(5·0 − (−1)(−1)) − (−1)(0 − (−1)·2) + 0
           = 1(0−1) + 1(0+2) = −1 + 2 = 1

det(Green) = 1(8−1) − 2(−1−3) + 1(1+24)
           = 7 + 8 + 25 = 40

det(Blue)  = −1(4−12) + 4(1+4) + 1(3+4)
           = 8 + 20 + 7 = 35
```

The flag -

```
apoorvctf{1_40_35}
```