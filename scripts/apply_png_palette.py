#!/usr/bin/env python3
"""
Apply an external palette to a PNG and save a new indexed PNG.

If the input PNG is already 8-bit indexed (mode 'P'), the script preserves
the pixel indices directly and applies the new palette to them. This is safe
for edited PNGs where you want to keep your edits as indices and just change
the color mapping.

For RGB/RGBA inputs, the script performs color quantization to find the closest
matching palette color for each pixel.

Supported palette file formats:
  - txt  : CSV-style lines as produced by extract_png_palette.py
           header: index,r,g,b
           rows  : 0,12,34,56
  - json : JSON array with 256 [r,g,b] entries
  - gpl  : GIMP palette format
  - bin  : raw RGB bytes (768 bytes)

Usage:
  python scripts/apply_png_palette.py <input.png> <palette file> [-o <output.png>]

Examples:
  python scripts/apply_png_palette.py .\kq7_images\\2550_layer13.png .\kq7_images\\2550_main.pal.txt
  python scripts/apply_png_palette.py in.png palette.gpl -o out.png
"""

import argparse
import csv
import json
import sys
from pathlib import Path

from PIL import Image


def _normalize_palette(values):
    vals = list(values)
    if len(vals) < 768:
        vals.extend([0] * (768 - len(vals)))
    return vals[:768]


def _load_palette_txt(path: Path):
    entries = [0] * 768
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            if row[0].strip().lower() == "index":
                continue
            if len(row) < 4:
                continue
            idx = int(row[0])
            if not (0 <= idx <= 255):
                continue
            r, g, b = int(row[1]), int(row[2]), int(row[3])
            base = idx * 3
            entries[base] = max(0, min(255, r))
            entries[base + 1] = max(0, min(255, g))
            entries[base + 2] = max(0, min(255, b))
    return entries


def _load_palette_json(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    flat = []
    for item in raw:
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            flat.extend([int(item[0]), int(item[1]), int(item[2])])
        else:
            raise ValueError("Invalid JSON palette format; expected [[r,g,b], ...].")
    return _normalize_palette(flat)


def _load_palette_gpl(path: Path):
    flat = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lower = line.lower()
        if lower.startswith("gimp palette") or lower.startswith("name:") or lower.startswith("columns:"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        flat.extend([r, g, b])
    return _normalize_palette(flat)


def _load_palette_bin(path: Path):
    raw = path.read_bytes()
    return _normalize_palette(raw)


def load_palette(path: Path):
    ext = path.suffix.lower()
    if ext == ".txt":
        return _load_palette_txt(path)
    if ext == ".json":
        return _load_palette_json(path)
    if ext == ".gpl":
        return _load_palette_gpl(path)
    if ext == ".bin":
        return _load_palette_bin(path)
    raise ValueError("Unsupported palette file extension. Use .txt, .json, .gpl, or .bin")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_png", help="source image path")
    parser.add_argument("palette_file", help="palette file (.txt/.json/.gpl/.bin)")
    parser.add_argument("-o", "--output", help="output PNG path (default: <input>_repal.png)")
    args = parser.parse_args()

    src = Path(args.input_png)
    pal_path = Path(args.palette_file)
    if not src.exists():
        sys.exit(f"Error: input image not found: {src}")
    if not pal_path.exists():
        sys.exit(f"Error: palette file not found: {pal_path}")

    try:
        palette = load_palette(pal_path)
    except Exception as exc:
        sys.exit(f"Error reading palette: {exc}")

    with Image.open(src) as img:
        if img.mode == "P":
            pixel_bytes = img.tobytes()
            out_img = Image.frombytes("P", img.size, pixel_bytes)
            out_img.putpalette(palette)
            print(f"Preserved indices from indexed input; applied new palette.")
        else:
            src_img = img.convert("RGB")
            pal_img = Image.new("P", (1, 1))
            pal_img.putpalette(palette)
            out_img = src_img.quantize(palette=pal_img)
            print(f"Quantized from {img.mode} mode to palette; closest-color mapping used.")

    out_path = Path(args.output) if args.output else src.with_name(f"{src.stem}_repal.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out_path)

    print(f"Saved remapped PNG: {out_path}")


if __name__ == "__main__":
    main()
