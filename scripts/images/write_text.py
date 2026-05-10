#!/usr/bin/env python3
"""
Write text onto an 8-bit indexed PNG, using a specified palette color index.

The base image stays in 8-bit indexed mode — text pixels are set to the given
palette index, so the palette itself is never changed.

For Hebrew (RTL) text, add --rtl.

Usage:
    python write_text.py base.png "Hello" --font Arial.ttf --font-size 20 --color-index 5 --x 10 --y 50
    python write_text.py base.png "שלום" --font david.ttf --font-size 20 --color-index 5 --x 400 --y 50 --rtl
    python write_text.py base.png "Hello" --font Arial.ttf --font-size 20 --color-index 5 --x 10 --y 50 -o out.png
    python scripts/write_text.py .\\kq7_images\\400\\400_0_0.png "פ  ר  ק          ר  א  ש  ו  ן" --font "C:\\Windows\\Fonts\\frank.ttf" --font-size 38 --color-index 7 --x 390 --y 80 --rtl
    python scripts/write_text.py .\\kq7_images\\401\\401_0_0.png  "פ  ר  ק                ש  נ  י" --font "C:\\Windows\\Fonts\\frank.ttf" --font-size 38 --color-index 7 --x 390 --y 80 --rtl 
    python scripts/write_text.py .\\kq7_images\\402\\402_0_0.png  "פ  ר  ק          ש  ל  י  ש  י" --font "C:\\Windows\\Fonts\\frank.ttf" --font-size 38 --color-index 7 --x 390 --y 80 --rtl
    python scripts/write_text.py .\\kq7_images\\403\\403_0_0.png  "פ  ר  ק            ר  ב  י  ע  י" --font "C:\\Windows\\Fonts\\frank.ttf" --font-size 38 --color-index 7 --x 390 --y 80 --rtl
    python scripts/write_text.py .\\kq7_images\\404\\404_0_0.png  "פ  ר  ק           ח  מ  י  ש  י" --font "C:\\Windows\\Fonts\\frank.ttf" --font-size 38 --color-index 7 --x 390 --y 80 --rtl
    python scripts/write_text.py .\\kq7_images\\405\\405_0_0.png  "פ  ר  ק            ש  י  ש  י" --font "C:\\Windows\\Fonts\\frank.ttf" --font-size 38 --color-index 7 --x 390 --y 80 --rtl
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(font_name, font_size):
    """Try font_name as a file path first, then as a system font name."""
    p = Path(font_name)
    if p.exists():
        return ImageFont.truetype(str(p), font_size)
    # Try as a system font (look in common Windows font dirs)
    import os
    for font_dir in [r"C:\Windows\Fonts", r"C:\Users"]:
        for candidate in Path(font_dir).rglob(font_name):
            return ImageFont.truetype(str(candidate), font_size)
    # Last resort: let Pillow resolve it
    return ImageFont.truetype(font_name, font_size)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('image',       help='base 8-bit indexed PNG file')
    parser.add_argument('text',        help='text to write')
    parser.add_argument('--font',      required=True, help='font file path or name (e.g. Arial.ttf)')
    parser.add_argument('--font-size', type=int, required=True, help='font size in pixels')
    parser.add_argument('--color-index', type=int, default=1,
                        help='palette index to use for text pixels (default: 1)')
    parser.add_argument('--x', type=int, default=0, help='left edge of text (default: 0)')
    parser.add_argument('--y', type=int, default=0, help='top edge of text (default: 0)')
    parser.add_argument('--rtl', action='store_true',
                        help='right-to-left text (Hebrew etc.); --x is then the RIGHT edge')
    parser.add_argument('--shadow-width', type=int, default=0,
                        help='shadow thickness in pixels (default: 0 = no shadow)')
    parser.add_argument('--shadow-color-index', type=int, default=0,
                        help='palette index for the shadow (default: 0)')
    parser.add_argument('-o', '--output',
                        help='output path (default: <image>_text.png)')
    args = parser.parse_args()

    src = Path(args.image)
    img = Image.open(src)
    if img.mode != 'P':
        print(f"Error: image mode is '{img.mode}', expected 'P' (8-bit indexed).")
        return 1

    if not (0 <= args.color_index <= 255):
        print("Error: --color-index must be 0-255.")
        return 1

    font = load_font(args.font, args.font_size)

    text = args.text
    if args.rtl:
        try:
            from bidi.algorithm import get_display
            text = get_display(text)
        except ImportError:
            print("Warning: python-bidi not installed — RTL reordering skipped.")

    # --- Measure text to find x position ---
    probe = ImageDraw.Draw(Image.new('L', (1, 1)))
    bbox = probe.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]

    if args.rtl:
        # --x is the right edge
        x = args.x - text_w
    else:
        x = args.x

    sw = args.shadow_width
    pixels = list(img.getdata())

    # --- Draw shadow first: paint the same text at every (dx, dy) offset within
    #     the shadow radius. This keeps letter spacing identical to the main text. ---
    if sw > 0:
        shadow_mask = Image.new('L', img.size, 0)
        sdraw = ImageDraw.Draw(shadow_mask)
        for dx in range(-sw, sw + 1):
            for dy in range(-sw, sw + 1):
                if dx == 0 and dy == 0:
                    continue
                sdraw.text((x + dx, args.y + dy), text, fill=255, font=font)
        shadow_data = list(shadow_mask.getdata())
        pixels = [args.shadow_color_index if m else p for p, m in zip(pixels, shadow_data)]

    # --- Draw main text ---
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.text((x, args.y), text, fill=255, font=font)
    mask_data = list(mask.getdata())
    new_pixels = [args.color_index if m else p for p, m in zip(pixels, mask_data)]

    out_img = img.copy()
    out_img.putdata(new_pixels)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = src.parent / (src.stem + '_text.png')

    kwargs = {}
    if 'transparency' in img.info:
        kwargs['transparency'] = img.info['transparency']

    out_img.save(out_path, **kwargs)
    print(f"Text written at ({x}, {args.y}) with palette index {args.color_index} -> {out_path}")


if __name__ == '__main__':
    main()
