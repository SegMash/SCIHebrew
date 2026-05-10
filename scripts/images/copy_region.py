#!/usr/bin/env python3
"""
Copy a rectangular region from one image and paste it into another.

Usage:
    python copy_region.py source.png target.png x1 y1 x2 y2
"""

import argparse
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('source', help='image to copy from')
parser.add_argument('target', help='image to paste into (overwritten in-place)')
parser.add_argument('x1', type=int)
parser.add_argument('y1', type=int)
parser.add_argument('x2', type=int)
parser.add_argument('y2', type=int)
parser.add_argument('x3', type=int, nargs='?', default=None, help='destination x (default: same as x1)')
parser.add_argument('y3', type=int, nargs='?', default=None, help='destination y (default: same as y1)')
args = parser.parse_args()

dest_x = args.x3 if args.x3 is not None else args.x1
dest_y = args.y3 if args.y3 is not None else args.y1

source = Image.open(args.source)
target = Image.open(args.target)

region = source.crop((args.x1, args.y1, args.x2, args.y2))
target.paste(region, (dest_x, dest_y))
target.save(args.target)

print(f"Copied ({args.x1},{args.y1})-({args.x2},{args.y2}) from {args.source} -> pasted at ({dest_x},{dest_y}) in {args.target}")
