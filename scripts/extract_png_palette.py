#!/usr/bin/env python3
"""
Extract the palette from a Sierra SCI2 .p56 file and save it to a file.

Palette layout used here (as discovered in this project):
    - Bytes 0x06-0x07: number of layers (uint16 little-endian)
    - Palette starts at:
            18 + (42 * (num_layers + 1)) + 1
    - Each color entry is 4 bytes:
            [unused, red, green, blue]
    - Read 255 colors

Supported output formats:
    - txt  : one line per color: index,r,g,b
    - json : JSON array of [r,g,b] entries
    - gpl  : GIMP palette file
    - bin  : raw RGB bytes (r0,g0,b0,...)

Usage:
    python scripts/extract_png_palette.py <file.p56> [-o <output>] [--format txt|json|gpl|bin]

Examples:
    python scripts/extract_png_palette.py ./kq7_work/PATCHES/2550.p56
    python scripts/extract_png_palette.py ./kq7_work/PATCHES/2550.p56 --format gpl
    python scripts/extract_png_palette.py ./kq7_work/PATCHES/2550.p56 -o ./kq7_images/2550_main.pal.txt
"""

import argparse
import json
import struct
import sys
from pathlib import Path


FORMATS = ("txt", "json", "gpl", "bin")
PALETTE_COLORS = 255


def read_p56_palette(path: Path):
    data = path.read_bytes()
    if len(data) < 8:
        raise ValueError("File is too small to contain layer count.")

    num_layers = struct.unpack_from('<H', data, 0x06)[0]
    pal_start = 18 + (42 * (num_layers + 1)) + 1
    pal_size = PALETTE_COLORS * 4
    pal_end = pal_start + pal_size

    if pal_end > len(data):
        raise ValueError(
            f"Palette range 0x{pal_start:x}-0x{pal_end:x} exceeds file size 0x{len(data):x}."
        )

    rgb = []
    pos = pal_start
    for _ in range(PALETTE_COLORS):
        _unused = data[pos]
        r = data[pos + 1]
        g = data[pos + 2]
        b = data[pos + 3]
        rgb.extend((r, g, b))
        pos += 4

    return num_layers, pal_start, rgb


def to_rows(pal):
    rows = []
    color_count = len(pal) // 3
    for i in range(color_count):
        base = i * 3
        rows.append((i, pal[base], pal[base + 1], pal[base + 2]))
    return rows


def write_txt(rows, out_path: Path):
    lines = ["index,r,g,b"]
    lines.extend(f"{i},{r},{g},{b}" for i, r, g, b in rows)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(rows, out_path: Path):
    data = [[r, g, b] for _, r, g, b in rows]
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_gpl(rows, out_path: Path, source_name: str):
    lines = [
        "GIMP Palette",
        f"Name: {source_name}",
        "Columns: 16",
        "#",
    ]
    lines.extend(f"{r:3d} {g:3d} {b:3d}\tIndex {i}" for i, r, g, b in rows)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_bin(pal, out_path: Path):
    out_path.write_bytes(bytes(pal))


def default_output_path(src: Path, fmt: str) -> Path:
    ext = {
        "txt": ".pal.txt",
        "json": ".pal.json",
        "gpl": ".pal.gpl",
        "bin": ".pal.bin",
    }[fmt]
    return src.with_name(src.stem + ext)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("p56", help="input SCI2 p56 file")
    parser.add_argument("-o", "--output", help="output file path")
    parser.add_argument("--format", choices=FORMATS, default="txt", help="palette output format")
    args = parser.parse_args()

    src = Path(args.p56)
    if not src.exists():
        sys.exit(f"Error: file not found: {src}")

    try:
        num_layers, pal_start, pal = read_p56_palette(src)
    except Exception as exc:
        sys.exit(f"Error: {exc}")

    rows = to_rows(pal)
    out_path = Path(args.output) if args.output else default_output_path(src, args.format)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "txt":
        write_txt(rows, out_path)
    elif args.format == "json":
        write_json(rows, out_path)
    elif args.format == "gpl":
        write_gpl(rows, out_path, src.stem)
    else:
        write_bin(pal, out_path)

    print(f"Layers: {num_layers}")
    print(f"Palette start: 0x{pal_start:x}")
    print(f"Colors read: {len(rows)}")
    print(f"Palette extracted: {out_path}")


if __name__ == "__main__":
    main()