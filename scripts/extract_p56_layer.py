#!/usr/bin/env python3
"""
Extract a bitmap layer from a Sierra SCI2 picture patch (.p56) file and save it as PNG.

Each layer header is located at:
    header_offset = 42 * layer_number + 18

The header encodes:
    bytes  0-1  : width  (uint16 little-endian)
    bytes  2-3  : height (uint16 little-endian)
    bytes 24-27 : pixel data offset inside the file (uint32 little-endian)

Pixel data is raw 8-bit palette indices (width * height bytes, uncompressed).

The output PNG is 8-bit indexed (mode 'P') with a default greyscale palette so
it opens cleanly in GIMP or any image editor.  After editing, use
import_bitmap.py (or supply --offset + --count manually) to write the pixels
back into the patch file.

Usage:
    python scripts/extract_p56_layer.py <file.p56> --layer <N> [-o <out.png>]

Examples:
    python scripts/extract_p56_layer.py kq7_work/PATCHES/2550.p56 --layer 3
    python scripts/extract_p56_layer.py kq7_work/PATCHES/2550.p56 --layer 3 -o kq7_images/2550_layer3.png
"""

import argparse
import struct
import sys
from pathlib import Path
from PIL import Image


LAYER_HEADER_STRIDE   = 42   # bytes between consecutive layer header starts
LAYER_HEADERS_BASE    = 18   # offset of the first layer header in the file
HEADER_WIDTH_OFF      = 0    # uint16 LE  - width in pixels
HEADER_HEIGHT_OFF     = 2    # uint16 LE  - height in pixels
HEADER_DATA_OFFSET_OFF = 24  # uint32 LE  - absolute file offset of pixel data


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('file', help='SCI2 picture patch file (.p56)')
    parser.add_argument('--layer', '-l', required=True, type=int,
                        help='zero-based layer (image command) index to extract')
    parser.add_argument('--output', '-o',
                        help='output PNG path (default: <stem>_layer<N>.png next to source file)')
    args = parser.parse_args()

    src = Path(args.file)
    if not src.exists():
        sys.exit(f"Error: file not found: {src}")

    data = src.read_bytes()
    file_size = len(data)

    # Locate the layer header
    hdr_off = LAYER_HEADERS_BASE + LAYER_HEADER_STRIDE * args.layer
    hdr_end = hdr_off + LAYER_HEADER_STRIDE
    if hdr_end > file_size:
        sys.exit(
            f"Error: layer {args.layer} header at 0x{hdr_off:x}-0x{hdr_end:x} "
            f"is outside the file (size 0x{file_size:x})."
        )

    width = struct.unpack_from('<H', data, hdr_off + HEADER_WIDTH_OFF)[0]
    height = struct.unpack_from('<H', data, hdr_off + HEADER_HEIGHT_OFF)[0]
    px_off = struct.unpack_from('<I', data, hdr_off + HEADER_DATA_OFFSET_OFF)[0]
    count = width * height

    print(f"Layer {args.layer}:")
    print(f"  header offset : 0x{hdr_off:08x}")
    print(f"  width         : {width}  (0x{width:x})")
    print(f"  height        : {height}  (0x{height:x})")
    print(f"  pixel data    : 0x{px_off:08x}")
    print(f"  count         : {count} bytes  (0x{count:x})")

    px_end = px_off + count
    if px_end > file_size:
        sys.exit(
            f"Error: pixel data range 0x{px_off:x}-0x{px_end:x} "
            f"exceeds file size 0x{file_size:x}."
        )

    pixel_bytes = data[px_off:px_end]

    img = Image.frombytes('P', (width, height), pixel_bytes)

    # Greyscale fallback palette (index n -> grey n) so the PNG is viewable
    img.putpalette([value for index in range(256) for value in (index, index, index)])

    out_path = Path(args.output) if args.output else \
        src.parent / f"{src.stem}_layer{args.layer}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Saved {width}x{height} PNG -> {out_path}")


if __name__ == '__main__':
    main()