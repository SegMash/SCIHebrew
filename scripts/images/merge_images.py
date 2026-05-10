#!/usr/bin/env python3
"""
Merge multiple 8-bit indexed PNG images by taking the maximum palette index
at each pixel position.

For each pixel (x, y):  result = max(image[0][x,y], image[1][x,y], ..., image[n][x,y])

All images must have the same dimensions.
The palette is taken from the first image.

Without --area: merge is applied to the whole image.
With --area:    merge is applied only inside the given rectangles;
                pixels outside are taken unchanged from image[0].
Multiple --area flags are allowed.

Usage:
    python merge_images.py a.png b.png c.png
    python merge_images.py a.png b.png c.png --area 60,110,420,140
    python merge_images.py a.png b.png c.png --area 0,0,100,50 --area 200,100,400,200
    python merge_images.py a.png b.png c.png -o merged.png --area "35,89,455,111" --area "38,153,463,242"
    python scripts/merge_images.py .\kq7_images\400_0_0_filtered.png .\kq7_images\401_0_0_filtered.png .\kq7_images\402_0_0_filtered.png .\kq7_images\403_0_0_filtered.png .\kq7_images\404_0_0_filtered.png .\kq7_images\405_0_0_filtered.png -o .\kq7_images\chapter_template.png --area "35,89,455,111" --area "38,153,463,242"
"""

import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('images', nargs='+', help='input 8-bit indexed PNG files (in merge order)')
    parser.add_argument('-o', '--output', help='output path (default: <first_image>_merged.png)')
    parser.add_argument('--area', '-a', metavar='x1,y1,x2,y2', action='append',
                        help='rectangle where merging is applied (repeatable); '
                             'if omitted the whole image is merged')
    args = parser.parse_args()

    if len(args.images) < 2:
        print("Error: at least two images are required.")
        return 1

    imgs = []
    for path in args.images:
        img = Image.open(path)
        if img.mode != 'P':
            print(f"Error: {path} mode is '{img.mode}', expected 'P' (8-bit indexed).")
            return 1
        imgs.append((path, img))

    base_size = imgs[0][1].size
    for path, img in imgs[1:]:
        if img.size != base_size:
            print(f"Error: {path} is {img.size}, expected {base_size}.")
            return 1

    # Parse optional areas
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
            print(f"Merge area: x={a[0]}-{a[2]}  y={a[1]}-{a[3]}")

    base_w, base_h = imgs[0][1].size

    def in_areas(idx):
        if not areas:
            return True
        x = idx % base_w
        y = idx // base_w
        return any(a[0] <= x <= a[2] and a[1] <= y <= a[3] for a in areas)

    # Start with first image's pixels
    result = list(imgs[0][1].getdata())

    # Merge each subsequent image
    for path, img in imgs[1:]:
        other = list(img.getdata())
        result = [max(a, b) if in_areas(i) else a
                  for i, (a, b) in enumerate(zip(result, other))]

    out_img = imgs[0][1].copy()
    out_img.putdata(result)

    if args.output:
        out_path = Path(args.output)
    else:
        first = Path(args.images[0])
        out_path = first.parent / (first.stem + '_merged.png')

    kwargs = {}
    if 'transparency' in imgs[0][1].info:
        kwargs['transparency'] = imgs[0][1].info['transparency']

    out_img.save(out_path, **kwargs)
    print(f"Merged {len(imgs)} images -> {out_path}")


if __name__ == '__main__':
    main()
