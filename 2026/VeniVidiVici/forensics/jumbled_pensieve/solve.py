#!/usr/bin/env python3
from PIL import Image
import glob

png_signature = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
shard_files = sorted(glob.glob("shard_*.dat"))

fixed_images = []
for shard_file in shard_files:
    with open(shard_file, "rb") as f:
        data = bytearray(f.read())
    data[:8] = png_signature

    fixed_name = shard_file.replace(".dat", "_fixed.png")
    with open(fixed_name, "wb") as f:
        f.write(data)

    img = Image.open(fixed_name)
    fixed_images.append(img)

width, height = fixed_images[0].size
result_pixels = []

for y in range(height):
    for x in range(width):
        r, g, b = 0, 0, 0
        for img in fixed_images:
            pixel = img.getpixel((x, y))
            r ^= pixel[0]
            g ^= pixel[1]
            b ^= pixel[2]
        result_pixels.append((r, g, b))

result = Image.new("RGB", (width, height))
result.putdata(result_pixels)
result.save("flag.png")
