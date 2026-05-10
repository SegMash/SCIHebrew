#!/usr/bin/env python3
"""
Replace specified palette index values in an 8-bit indexed PNG with index 0.

Without --area: the whole image is filtered.
With --area:    only pixels inside the given rectangles are filtered;
                everything outside is left untouched.
Multiple --area flags are allowed.

Usage:
    python filter_palette_indexes.py image.png 5 12 37
    python filter_palette_indexes.py image.png 5 12 37 --area 60,110,420,140
    python filter_palette_indexes.py image.png 5 12 37 --area 0,0,100,50 --area 200,100,400,200
    python filter_palette_indexes.py image.png 5 12 37 -o result.png
    python scripts/filter_palette_indexes.py kq7_images/405_0_0.png 2 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 --area "35,89,455,111" --area "38,153,463,242"

Output: <image>_filtered.png  (or the path given with -o)
"""

import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('png', help='8-bit indexed PNG file')
    parser.add_argument('indexes', nargs='+', type=int,
                        help='palette indexes to replace with index 0')
    parser.add_argument('-o', '--output',
                        help='output path (default: <name>_filtered.png next to input)')
    parser.add_argument('--area', '-a', metavar='x1,y1,x2,y2', action='append',
                        help='rectangle where filtering is applied (repeatable); '
                             'if omitted the whole image is filtered')
    args = parser.parse_args()

    src = Path(args.png)
    img = Image.open(src)
    if img.mode != 'P':
        print(f"Error: image mode is '{img.mode}', expected 'P' (8-bit indexed).")
        return 1

    indexes = set(args.indexes)
    bad = [i for i in indexes if not (0 <= i <= 255)]
    if bad:
        print(f"Error: indexes out of range 0-255: {bad}")
        return 1

    # Parse optional filter areas
    areas = []
    if args.area:
        for spec in args.area:
            try:
                x1, y1, x2, y2 = map(int, spec.split(','))
                areas.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
            except ValueError:
                print(f"Error: --area must be four integers x1,y1,x2,y2 — got '{spec}'")
                return 1
        for a in areas:
            print(f"Filter area: x={a[0]}-{a[2]}  y={a[1]}-{a[3]}")

    width, height = img.size
    pixels = list(img.getdata())
    new_pixels = []
    for idx, p in enumerate(pixels):
        if p in indexes:
            if areas:
                x = idx % width
                y = idx // width
                in_area = any(a[0] <= x <= a[2] and a[1] <= y <= a[3] for a in areas)
                if not in_area:
                    new_pixels.append(p)   # outside all filter areas — keep as-is
                    continue
            new_pixels.append(0)
        else:
            new_pixels.append(p)

    out = img.copy()
    out.putdata(new_pixels)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = src.parent / (src.stem + '_filtered.png')

    # Preserve transparency info if present
    kwargs = {}
    if 'transparency' in img.info:
        kwargs['transparency'] = img.info['transparency']

    out.save(out_path, **kwargs)

    replaced = sum(1 for p in pixels if p in indexes)
    print(f"Replaced {replaced:,} pixels (indexes {sorted(indexes)}) -> index 0")
    print(f"Saved: {out_path}")


if __name__ == '__main__':
    main()
