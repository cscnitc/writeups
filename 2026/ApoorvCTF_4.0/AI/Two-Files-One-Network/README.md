---
title: "ApoorvCTF 4.0 - Two Files. One Network."
pubDatetime: 2026-03-09T12:00:00+00:00
author: "JayJayTee"
---

Interesting challenge.
You get a base model and a LoRA adapter with the hint "Alone, they're meaningless. Together... well, that's for you to figure out". The flag is hidden **inside** the merged weights. Took me a while to realize that the returned matrix was utterly nonsensical. Read on...

Quick background if you haven't touched LoRA before; it's a fine-tuning trick where instead of retraining a full weight matrix you train two small matrices A and B and add their product to the original weights at inference: `W_merged = W_base + (lora_B @ lora_A)`. Normally used to cheaply nudge model behaviour, here it's abused to hide data.

Both `.pt` files are just ZIP archives. Opening the pickle manifests shows the adapter only targets `layer2`. So the merge is just `layer2_merged = layer2_weight + lora_B @ lora_A`.

After computing that, the 256x256 result immediately looks off - values are all between 0 and 1, only ~2239 out of 65536 elements are nonzero, and the nonzero stuff is clustered in a narrow band around rows 120-143, cols 27-228. That's a pixel image. The LoRA matrices were crafted so their product, added to the base weights, encodes a hidden greyscale image right in the middle of the weight matrix.

From there it's just crop and render:

```python
l2_merged = layer2_weight + lora_B @ lora_A
img  = (l2_merged * 255).astype(np.uint8)
crop = img[118:145, 25:231]
out  = Image.fromarray(crop).resize((crop.shape[1]*4, crop.shape[0]*4), Image.NEAREST)
out.save('flag.png')
```

Opens as pixel-art text. The active region is only 24 rows tall; font-sized sgtrip hiding in a 256x256 matrix.

The flag -

```
apoorvctf{l0r4_m3rg3}
```

code [here](./solve.py)