"""
generate_text_frame.py
Generate a PNG frame (8-bit palette) with a text message drawn inside margins.

Usage:
    python scripts/generate_text_frame.py
        --width 640 --height 480
        --font "arial.ttf" --font-size 20
        --font-color white --background black
        --margin 20
        --text "Your message here"
        --output output.png
"""

import argparse
import sys
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def main():
    parser = argparse.ArgumentParser(description='Generate a text PNG frame at 8-bit depth.')
    parser.add_argument('--width',       type=int, required=True,  help='Image width in pixels')
    parser.add_argument('--height',      type=int, required=True,  help='Image height in pixels')
    parser.add_argument('--font',        type=str, required=True,  help='Path to .ttf font file')
    parser.add_argument('--font-size',   type=int, required=True,  help='Font size in points')
    parser.add_argument('--font-color',       type=str, required=False, default=None, help='Text color (name or #RRGGBB)')
    parser.add_argument('--font-color-index',  type=int, default=None,  help='Palette index to use as font color (when using --base-frame)')
    parser.add_argument('--margin',      type=int, required=True,  help='Horizontal margin in pixels (left and right)')
    parser.add_argument('--y-position',  type=int, default=0,      help='Y position in pixels where text drawing starts (default: 0)')
    parser.add_argument('--text',        type=str, required=True,  help='Text message to draw')
    parser.add_argument('--output',      type=str, required=True,  help='Output PNG file path')
    parser.add_argument('--background',  type=str, default='black', help='Background color (default: black)')
    parser.add_argument('--fade',         type=int, default=0,       help='Fade 0-100: 0=no fade, 100=fully faded to background color')
    parser.add_argument('--base-frame',   type=str, default=None,    help='Optional base PNG frame to draw text on top of (preserves its palette)')
    parser.add_argument('--set-border',   action='store_true',        help='Draw a black 1-pixel border around each letter')

    args = parser.parse_args()

    if args.base_frame:
        base = Image.open(args.base_frame).convert('RGB')
        img = base.resize((args.width, args.height))
        base_palette_img = Image.open(args.base_frame).convert('P')
    else:
        img = Image.new('RGB', (args.width, args.height), color=args.background)
        base_palette_img = None
    draw = ImageDraw.Draw(img)

    # Determine font color — from palette index or RGB value
    if base_palette_img is not None and args.font_color_index is not None:
        pal = base_palette_img.getpalette()
        idx = args.font_color_index
        if args.font_color is not None:
            # Override the palette entry at font_color_index with the given font_color
            fc_rgb = Image.new('RGB', (1, 1), color=args.font_color).getpixel((0, 0))
            pal[idx * 3]     = fc_rgb[0]
            pal[idx * 3 + 1] = fc_rgb[1]
            pal[idx * 3 + 2] = fc_rgb[2]
            base_palette_img.putpalette(pal)
        else:
            fc_rgb = (pal[idx * 3], pal[idx * 3 + 1], pal[idx * 3 + 2])
        blended_color = fc_rgb  # no fade when using palette index
    else:
        if args.font_color is None:
            print("ERROR: --font-color or --font-color-index is required.")
            sys.exit(1)
        bg_rgb = img.getpixel((0, 0))
        fc_rgb = Image.new('RGB', (1, 1), color=args.font_color).getpixel((0, 0))
        t = max(0, min(100, args.fade)) / 100.0
        blended_color = tuple(int(fc + (bg - fc) * t) for fc, bg in zip(fc_rgb, bg_rgb))

    try:
        font = ImageFont.truetype(args.font, args.font_size)
    except (IOError, OSError):
        print(f"Warning: Could not load font '{args.font}', using default font.")
        font = ImageFont.load_default()

    max_text_width = args.width - 2 * args.margin

    lines = wrap_text(args.text, font, max_text_width, draw)
    # Apply BiDi algorithm for correct RTL visual rendering
    lines = [get_display(line) for line in lines]

    # Measure line height from a reference string
    ref_bbox = draw.textbbox((0, 0), 'Ag', font=font)
    line_height = ref_bbox[3] - ref_bbox[1]
    line_spacing = 4

    x_start = args.margin
    y = args.y_position - (len(lines) - 1) * args.font_size

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = x_start + (max_text_width - text_width) // 2
        if args.set_border:
            for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=blended_color)
        y += line_height + line_spacing

    if base_palette_img is not None:
        # Preserve the original frame's palette
        img_8bit = img.quantize(palette=base_palette_img, dither=0)
    else:
        # Build an explicit palette with index 0 = black, index 1 = text color
        # so ScummVM margins stay black.
        explicit_palette = [0] * (256 * 3)
        explicit_palette[3] = blended_color[0]
        explicit_palette[4] = blended_color[1]
        explicit_palette[5] = blended_color[2]
        palette_img = Image.new('P', (1, 1))
        palette_img.putpalette(explicit_palette)
        img_8bit = img.quantize(palette=palette_img, dither=0)

    img_8bit.save(args.output, bits=8)
    print(f"Saved: {args.output}")


if __name__ == '__main__':
    main()
