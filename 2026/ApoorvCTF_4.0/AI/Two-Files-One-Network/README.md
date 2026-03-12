---
title: "ApoorvCTF 4.0 - Two Files. One Network."
pubDatetime: 2026-03-12T12:00:00+00:00
author: "JayJayTee"
---

A base neural network model and a LoRA adapter were provided with the hint: "Alone, they're meaningless. Together... well, that's for you to figure out." Category was AI / ML Reverse Engineering.

## Background: What is LoRA?

LoRA (Low-Rank Adaptation) fine-tunes large models cheaply by training two small matrices A and B and adding their product onto the original weights at inference time:

```
W_merged = W_base + (lora_B @ lora_A)
```

In this challenge, that arithmetic was abused to hide data instead.

## Recon

Both `.pt` files are ZIP archives. Inspecting the pickle manifests showed that the LoRA adapter targets `layer2` of the base model:

```
base_model.pt  → layer1, layer2 (256x256), layer3, output
lora_adapter.pt → layer2.lora_A (64x256), layer2.lora_B (256x64)
```

Merging is: `layer2_merged = layer2_weight + lora_B @ lora_A`

## Key Observation

After computing the merge, the resulting 256×256 matrix had suspicious properties:

```
Value range    : min=0.0, max=1.0
Non-zero count : 2239 / 65536  (very sparse)
Active region  : rows 120-143, cols 27-228
```

Values in [0,1] in a sparse matrix with a narrow active band — this is a pixel image. The LoRA matrices were crafted so their product, when added to the base weights, encodes a hidden greyscale image inside the weight matrix.

## Exploitation

Read the merged matrix as pixel intensities (0 = black, 1 = white), crop the active region, and render as an image:

```python
l2_merged = layer2_weight + lora_B @ lora_A
img       = (l2_merged * 255).astype(np.uint8)
crop      = img[118:145, 25:231]
out       = Image.fromarray(crop).resize(
                (crop.shape[1]*4, crop.shape[0]*4), Image.NEAREST)
out.save('flag.png')
```

Opening `flag.png` revealed pixel-art text spelling out the flag. The active region was only 24 rows tall — a font-sized strip hidden in the centre of a 256×256 weight matrix.

The flag -

```
apoorvctf{l0r4_m3rg3}
```
code [here](./solve.py)