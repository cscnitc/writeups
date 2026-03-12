#!/usr/bin/env python3

import torch
import numpy as np
from PIL import Image


def load_weights(base_path: str, adapter_path: str):
    base    = torch.load(base_path,    map_location="cpu")
    adapter = torch.load(adapter_path, map_location="cpu")
    return base, adapter


def merge_lora(base: dict, adapter: dict) -> np.ndarray:
    w  = base["layer2.weight"].float().numpy()          # (256, 256)
    lA = adapter["layer2.lora_A"].float().numpy()       # (64,  256)
    lB = adapter["layer2.lora_B"].float().numpy()       # (256, 64)
    merged = w + lB @ lA                                # (256, 256)
    return merged


def extract_flag_image(merged: np.ndarray, out_path: str = "flag.png"):
    # Pixel intensities live in [0, 1]; active region rows 118-144, cols 25-230
    img  = (merged * 255).astype(np.uint8)
    crop = img[118:145, 25:231]

    h, w = crop.shape
    out  = Image.fromarray(crop).resize((w * 4, h * 4), Image.NEAREST)
    out.save(out_path)
    print(f"[+] Flag image saved to {out_path}")
    return out_path


def main():
    import sys
    base_path    = sys.argv[1] if len(sys.argv) > 1 else "base_model.pt"
    adapter_path = sys.argv[2] if len(sys.argv) > 2 else "lora_adapter.pt"

    print(f"[*] Loading base model from   : {base_path}")
    print(f"[*] Loading LoRA adapter from : {adapter_path}")

    base, adapter = load_weights(base_path, adapter_path)
    merged        = merge_lora(base, adapter)

    print(f"[*] Merged layer2 shape       : {merged.shape}")
    print(f"[*] Value range               : min={merged.min():.3f}, max={merged.max():.3f}")
    nonzero = np.count_nonzero(merged)
    print(f"[*] Non-zero elements         : {nonzero} / {merged.size}")

    extract_flag_image(merged)
    print("[*] Open flag.png to read the flag.")


if __name__ == "__main__":
    main()