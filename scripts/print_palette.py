#!/usr/bin/env python3
"""
Print the palette of an 8-bit indexed PNG file.

Usage:
    python print_palette.py image.png
    python print_palette.py image.png --used      # skip all-black entries
    python print_palette.py image.png --hex       # show hex values too
"""

import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('png', help='8-bit indexed PNG file')
    parser.add_argument('--used', '-u', action='store_true',
                        help='only print non-black entries')
    parser.add_argument('--hex', '-x', action='store_true',
                        help='also show hex values')
    args = parser.parse_args()

    img = Image.open(args.png)
    if img.mode != 'P':
        print(f"Error: image mode is '{img.mode}', expected 'P' (8-bit indexed).")
        return 1

    raw = img.getpalette()   # flat list [r0,g0,b0, r1,g1,b1, ...]
    entries = [(raw[i*3], raw[i*3+1], raw[i*3+2]) for i in range(256)]

    # Transparency info (tRNS chunk), if present
    transparency = img.info.get('transparency', None)

    print(f"Palette for: {args.png}  ({len(entries)} entries)")
    print(f"{'Index':>5}  {'R':>3} {'G':>3} {'B':>3}  {'Hex':>8}  Notes")
    print("-" * 45)

    for i, (r, g, b) in enumerate(entries):
        if args.used and (r, g, b) == (0, 0, 0) and i != transparency:
            continue
        notes = []
        if i == transparency:
            notes.append('transparent/skip')
        hex_str = f"#{r:02x}{g:02x}{b:02x}"
        hex_col = f"  {hex_str}" if args.hex else ""
        print(f"  {i:3d}:  {r:3d} {g:3d} {b:3d}{hex_col}  {'  '.join(notes)}")


if __name__ == '__main__':
    main()
