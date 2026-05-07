#!/usr/bin/env python3
"""
Inject a PNG image back into a bitmap layer of a Sierra SCI2 picture patch (.p56).

Each layer header is located at:
    header_offset = 42 * layer_number + 18

The header encodes:
    bytes  0-1  : width  (uint16 little-endian)
    bytes  2-3  : height (uint16 little-endian)
    bytes 24-27 : pixel data offset inside the file (uint32 little-endian)

Pixel data is written back as raw 8-bit palette indices (width * height bytes).
The PNG must therefore be in indexed mode ('P') and must match the layer size.

Usage:
    python scripts/import_p56_layer.py <file.p56> <image.png> --layer <N> [-o <out.p56> | --in-place]

Examples:
    python scripts/import_p56_layer.py kq7_work/PATCHES/2550.p56 kq7_work/PATCHES/2550_layer13.png --layer 13
    python scripts/import_p56_layer.py kq7_work/PATCHES/2550.p56 edited.png --layer 13 -o kq7_work/PATCHES/2550.p56
    python scripts/import_p56_layer.py kq7_work/PATCHES/2550.p56 edited.png --layer 13 --in-place
"""

import argparse
import struct
import sys
from pathlib import Path

from PIL import Image


LAYER_HEADER_STRIDE = 42
LAYER_HEADERS_BASE = 18
HEADER_WIDTH_OFF = 0
HEADER_HEIGHT_OFF = 2
HEADER_DATA_OFFSET_OFF = 24


def get_layer_info(data, layer_number):
    file_size = len(data)
    hdr_off = LAYER_HEADERS_BASE + LAYER_HEADER_STRIDE * layer_number
    hdr_end = hdr_off + LAYER_HEADER_STRIDE
    if hdr_end > file_size:
        raise ValueError(
            f"Layer {layer_number} header at 0x{hdr_off:x}-0x{hdr_end:x} is outside the file "
            f"(size 0x{file_size:x})."
        )

    width = struct.unpack_from('<H', data, hdr_off + HEADER_WIDTH_OFF)[0]
    height = struct.unpack_from('<H', data, hdr_off + HEADER_HEIGHT_OFF)[0]
    px_off = struct.unpack_from('<I', data, hdr_off + HEADER_DATA_OFFSET_OFF)[0]
    count = width * height
    px_end = px_off + count
    if px_end > file_size:
        raise ValueError(
            f"Pixel data range 0x{px_off:x}-0x{px_end:x} exceeds file size 0x{file_size:x}."
        )

    return hdr_off, width, height, px_off, count


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('file', help='SCI2 picture patch file (.p56)')
    parser.add_argument('png', help='replacement 8-bit indexed PNG for the layer')
    parser.add_argument('--layer', '-l', required=True, type=int,
                        help='zero-based layer (image command) index to replace')
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('--output', '-o',
                              help='output p56 path (default: <stem>_patched.p56 next to source file)')
    output_group.add_argument('--in-place', action='store_true',
                              help='overwrite the source p56 file in place')
    args = parser.parse_args()

    src = Path(args.file)
    png_path = Path(args.png)
    if not src.exists():
        sys.exit(f"Error: file not found: {src}")
    if not png_path.exists():
        sys.exit(f"Error: PNG file not found: {png_path}")

    data = bytearray(src.read_bytes())
    try:
        hdr_off, width, height, px_off, count = get_layer_info(data, args.layer)
    except ValueError as exc:
        sys.exit(f"Error: {exc}")

    with Image.open(png_path) as img:
        if img.mode != 'P':
            sys.exit(
                f"Error: PNG must be 8-bit indexed (mode 'P'), got '{img.mode}'."
            )
        if img.size != (width, height):
            sys.exit(
                f"Error: PNG size {img.size[0]}x{img.size[1]} does not match layer {args.layer} "
                f"size {width}x{height}."
            )
        pixel_bytes = img.tobytes()

    if len(pixel_bytes) != count:
        sys.exit(
            f"Error: PNG produced {len(pixel_bytes)} bytes but layer expects {count}."
        )

    print(f"Layer {args.layer}:")
    print(f"  header offset : 0x{hdr_off:08x}")
    print(f"  width         : {width}  (0x{width:x})")
    print(f"  height        : {height}  (0x{height:x})")
    print(f"  pixel data    : 0x{px_off:08x}")
    print(f"  count         : {count} bytes  (0x{count:x})")
    print(f"  png           : {png_path}")

    data[px_off:px_off + count] = pixel_bytes

    if args.in_place:
        out_path = src
    else:
        out_path = Path(args.output) if args.output else src.with_name(f"{src.stem}_patched{src.suffix}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    print(f"Saved patched p56 -> {out_path}")


if __name__ == '__main__':
    main()