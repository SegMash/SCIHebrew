#!/usr/bin/env python3
"""
Extract images from a Sierra SCI VGA view (.v56) file.

Output: <VIEW_NAME>_<LOOP>_<CELL>.png  (8-bit indexed PNG, palette embedded)
The skip_color index (transparent color) is stored in the PNG tRNS chunk.

Usage:
    python extract_v56.py <file.v56> [-o <output_dir>] [--palette <file.pal>]

If the v56 has an embedded palette it is used. Otherwise the script looks for
999.pal in the same directory, or you can supply one with --palette.
"""

import argparse
import io
from pathlib import Path

from PIL import Image

# All header offsets inside a v56 file are relative to this base address.
# Bytes 0x00..0x19 are the Sierra resource wrapper; the actual view data starts at 0x1a.
OFFSET = 0x1a


# ---------------------------------------------------------------------------
# Low-level stream helpers
# ---------------------------------------------------------------------------

def read_le(stream, n=1):
    """Read n bytes as a little-endian unsigned integer."""
    data = stream.read(n)
    if len(data) < n:
        raise EOFError(f"Unexpected end of file")
    return int.from_bytes(data, 'little')


def at(stream, pos, n=1):
    """Seek to absolute position pos and return read_le(n)."""
    stream.seek(pos)
    return read_le(stream, n)


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

def _parse_pal_stream(stream):
    """
    Parse a Sierra SCI palette from a binary stream positioned at byte 0.
    Returns a flat list of 768 ints: [r0, g0, b0, r1, g1, b1, ...] for 256 entries.
    """
    num_palettes = at(stream, 10)
    if num_palettes != 1:
        raise ValueError(f"Expected 1 palette block, got {num_palettes}")

    pal_base = 13 + 2 * num_palettes      # pointer table + entries
    start_color  = at(stream, pal_base + 10)
    num_colors   = at(stream, pal_base + 14, 2)
    global_used  = bool(at(stream, pal_base + 16))   # used when shared_used=True
    shared_used  = bool(at(stream, pal_base + 17))   # if True, no per-entry used byte
    version      = at(stream, pal_base + 18, 4)
    if version != 0:
        raise ValueError(f"Unexpected palette version {version}")

    if start_color + num_colors > 256:
        raise ValueError(f"Palette out of range: start={start_color} count={num_colors}")

    stream.seek(pal_base + 22)
    palette = [0] * 768  # default: all black
    for k in range(num_colors):
        i = start_color + k
        if not shared_used:
            _ = read_le(stream)  # per-entry 'used' flag – not needed for image export
        r = read_le(stream)
        g = read_le(stream)
        b = read_le(stream)
        palette[i * 3]     = r
        palette[i * 3 + 1] = g
        palette[i * 3 + 2] = b
    return palette


def load_palette_file(pal_path):
    """
    Load a Sierra .pal file.
    The .pal file has a 2-byte type header (0x8b 0x00) followed by palette data.
    Returns a flat 768-int list.
    """
    data = Path(pal_path).read_bytes()
    if data[:2] != b'\x8b\x00':
        raise ValueError(f"{pal_path}: not a Sierra .pal file (bad header {data[:2]!r})")
    stream = io.BytesIO(data[2:])   # strip the 2-byte header so offsets start at 0
    return _parse_pal_stream(stream)


def _embedded_palette(stream, hunk_pal_offset):
    """Read the palette embedded in the v56 file at OFFSET + hunk_pal_offset."""
    stream.seek(OFFSET + hunk_pal_offset)
    pal_stream = io.BytesIO(stream.read())  # rest of file → new stream with offset 0
    return _parse_pal_stream(pal_stream)


# ---------------------------------------------------------------------------
# RLE decompression
# ---------------------------------------------------------------------------

def _decompress_cel(stream, width, height, skip_color,
                    data_off, lit_off, ctrl_off, resource_size):
    """
    Decompress one SCI VGA11 cel.

    The row control table has two sections (each height*4 bytes):
      - RLE row offsets  (relative to data_off)
      - Literal row offsets (relative to lit_off)

    Returns a flat list of width*height palette indices.
    """
    pixels = []

    for y in range(height):
        # --- sizes of this row's compressed and literal data ---
        rle_start = at(stream, ctrl_off + y * 4, 4)
        if y + 1 < height:
            rle_size = at(stream, ctrl_off + (y + 1) * 4, 4) - rle_start
        else:
            rle_size = resource_size - (data_off + rle_start)

        lit_start = at(stream, ctrl_off + height * 4 + y * 4, 4)
        if y + 1 < height:
            lit_size = at(stream, ctrl_off + height * 4 + (y + 1) * 4, 4) - lit_start
        else:
            lit_size = resource_size - (lit_off + lit_start)

        # read raw row slices into local BytesIO for sequential access
        stream.seek(data_off + rle_start)
        rle = io.BytesIO(stream.read(rle_size))

        stream.seek(lit_off + lit_start)
        lit = io.BytesIO(stream.read(lit_size))

        row = []
        while len(row) < width:
            ctrl = read_le(rle)
            if ctrl & 0x80:
                # RLE packet
                count = ctrl & 0x3f
                if ctrl & 0x40:
                    # Transparent run – fill with skip_color
                    row.extend([skip_color] * count)
                else:
                    # Solid run – one literal pixel repeated count times
                    color = read_le(lit)
                    row.extend([color] * count)
            else:
                # Literal run – ctrl pixels read one-by-one from literal stream
                for _ in range(ctrl):
                    row.append(read_le(lit))

        pixels.extend(row[:width])  # guard against overrun on malformed data

    return pixels


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_v56(v56_path, output_dir, palette_override=None):
    """
    Extract all loop/cel images from a v56 file.

    Parameters
    ----------
    v56_path : str or Path
        The .v56 file to extract.
    output_dir : str or Path
        Directory where PNG files are written (created if needed).
    palette_override : list or None
        Flat 768-int palette to use if the v56 has no embedded palette and
        no 999.pal exists next to it. Pass None for automatic resolution.

    Returns
    -------
    list of Path objects for the written PNG files.
    """
    p = Path(v56_path)
    if p.suffix.lower() != '.v56':
        raise ValueError(f"{p.name}: expected a .v56 file")

    view_name = p.stem
    data = p.read_bytes()
    resource_size = len(data)
    stream = io.BytesIO(data)

    # --- validate resource type byte ---
    if stream.read(1) != b'\x80':
        raise ValueError(f"{p.name}: missing Sierra view magic byte 0x80")

    # --- view header (all reads relative to OFFSET) ---
    view_header_size = at(stream, OFFSET,      2)   # size of the view header block
    loop_count       = at(stream, OFFSET + 2,  1)   # number of loops
    hunk_pal_offset  = at(stream, OFFSET + 8,  4)   # offset to embedded palette (0 if none)
    loop_header_size = at(stream, OFFSET + 12, 1)   # size of each loop header entry
    cel_header_size  = at(stream, OFFSET + 13, 1)   # size of each cel header entry

    # --- resolve palette ---
    if hunk_pal_offset:
        palette = _embedded_palette(stream, hunk_pal_offset)
        print(f"  Palette: embedded in {p.name}")
    elif palette_override is not None:
        palette = palette_override
        print(f"  Palette: supplied via --palette")
    else:
        default_pal = p.parent / '999.pal'
        if default_pal.exists():
            palette = load_palette_file(default_pal)
            print(f"  Palette: {default_pal}")
        else:
            print(f"  Warning: no palette found – using grayscale fallback")
            palette = []
            for i in range(256):
                palette += [i, i, i]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    exported = []

    # Loop headers start right after the view header block.
    loops_base = OFFSET + 2 + view_header_size

    for loop_num in range(loop_count):
        loop_hdr = loops_base + loop_header_size * loop_num
        cel_count       = at(stream, loop_hdr + 2)
        cel_table_ptr   = at(stream, loop_hdr + 12, 4)   # offset (from OFFSET) to cel header table
        cel_table_start = OFFSET + cel_table_ptr

        if cel_count == 0:
            continue

        for cel_num in range(cel_count):
            cel_hdr = cel_table_start + cel_header_size * cel_num

            width       = at(stream, cel_hdr + 0,  2)
            height      = at(stream, cel_hdr + 2,  2)
            skip_color  = at(stream, cel_hdr + 8,  1)   # transparent palette index
            compression = at(stream, cel_hdr + 9,  1)   # 138 = RLE
            data_off    = OFFSET + at(stream, cel_hdr + 24, 4)
            lit_off     = OFFSET + at(stream, cel_hdr + 28, 4)
            ctrl_off    = OFFSET + at(stream, cel_hdr + 32, 4)

            if compression != 138:
                print(f"  Skip loop {loop_num} cel {cel_num}: unsupported compression {compression}")
                continue

            pixels = _decompress_cel(stream, width, height, skip_color,
                                     data_off, lit_off, ctrl_off, resource_size)

            # Build 8-bit indexed PNG preserving palette indices
            img = Image.new('P', (width, height))
            img.putpalette(palette)
            img.putdata(pixels)

            out_name = f"{view_name}_{loop_num}_{cel_num}.png"
            out_path = output_dir / out_name
            img.save(out_path, transparency=skip_color)

            print(f"  [{loop_num}][{cel_num}] {width}x{height}  skip={skip_color}  -> {out_name}")
            exported.append(out_path)

    return exported


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("v56",
                        help=".v56 file to extract")
    parser.add_argument("-o", "--output", default=".",
                        help="output directory (default: current directory)")
    parser.add_argument("--palette", "-p",
                        help="Sierra .pal file to use when the v56 has no embedded palette "
                             "(default: looks for 999.pal next to the .v56 file)")
    args = parser.parse_args()

    palette = None
    if args.palette:
        palette = load_palette_file(args.palette)

    v56_path = Path(args.v56)
    print(f"Extracting {v56_path.name}  ({v56_path.stat().st_size} bytes)")
    exported = extract_v56(v56_path, args.output, palette_override=palette)
    print(f"\nDone – {len(exported)} image(s) written to '{args.output}'")


if __name__ == "__main__":
    main()
