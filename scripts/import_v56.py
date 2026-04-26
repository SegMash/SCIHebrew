#!/usr/bin/env python3
"""
Import modified PNG images back into a Sierra SCI VGA view (.v56) file.

Scans an images directory for files named  <VIEW_NAME>_<LOOP>_<CELL>.png
(the naming convention used by extract_v56.py), compresses each image using
the Sierra SCI VGA11 RLE scheme, and writes a new .v56 file.

Cels that have no matching PNG in the directory are preserved (original pixels
are decompressed and re-compressed verbatim).

Requirements
------------
Replacement PNGs MUST be 8-bit indexed (palette mode 'P').  extract_v56.py
already saves them in that format.  If you edit with GIMP, use
Image → Mode → Indexed before saving.  Pixel values are raw palette indices
and are written to the file unchanged — colours are not re-quantised.

Usage
-----
    python import_v56.py file.v56 images_dir/
    python import_v56.py file.v56 images_dir/ -o output.v56
"""

import argparse
import io
import re
import struct
from pathlib import Path

from PIL import Image

# All field offsets inside a v56 file are measured from here.
# Bytes 0x00-0x19 are a Sierra resource wrapper with no view-specific data.
OFFSET = 0x1A


# ---------------------------------------------------------------------------
# Stream helpers
# ---------------------------------------------------------------------------

def _read_le(stream, n=1):
    data = stream.read(n)
    if len(data) < n:
        raise EOFError("Unexpected end of file")
    return int.from_bytes(data, 'little')


def _at(stream, pos, n=1):
    """Seek to absolute position and read n bytes as little-endian unsigned int."""
    stream.seek(pos)
    return _read_le(stream, n)


# ---------------------------------------------------------------------------
# Decompression   (exact mirror of view_export.py / extract_v56.py)
# ---------------------------------------------------------------------------

def _decompress_cel(stream, width, height, skip_color,
                    data_off, lit_off, ctrl_off, resource_size):
    """Return a flat list of width*height palette indices."""
    pixels = []
    for y in range(height):
        # --- row slice sizes from control table ---
        rle_start = _at(stream, ctrl_off + y * 4, 4)
        if y + 1 < height:
            rle_size = _at(stream, ctrl_off + (y + 1) * 4, 4) - rle_start
        else:
            rle_size = resource_size - (data_off + rle_start)

        lit_start = _at(stream, ctrl_off + height * 4 + y * 4, 4)
        if y + 1 < height:
            lit_size = _at(stream, ctrl_off + height * 4 + (y + 1) * 4, 4) - lit_start
        else:
            lit_size = resource_size - (lit_off + lit_start)

        stream.seek(data_off + rle_start)
        rle_buf = io.BytesIO(stream.read(rle_size))
        stream.seek(lit_off + lit_start)
        lit_buf = io.BytesIO(stream.read(lit_size))

        row = []
        while len(row) < width:
            ctrl_byte = _read_le(rle_buf)
            if ctrl_byte & 0x80:
                count = ctrl_byte & 0x3F
                if ctrl_byte & 0x40:
                    row.extend([skip_color] * count)           # transparent run
                else:
                    row.extend([_read_le(lit_buf)] * count)    # solid run
            else:
                for _ in range(ctrl_byte):                     # literal run
                    row.append(_read_le(lit_buf))
        pixels.extend(row[:width])
    return pixels


# ---------------------------------------------------------------------------
# Compression   (inverse of the RLE scheme above)
# ---------------------------------------------------------------------------

_MAX_RUN = 0x3F   # 6-bit length field → max 63 pixels per packet


def _compress_row(row, skip_color):
    """
    Compress one row of palette indices.

    Packet encoding:
      0xC0 | n              — n transparent (skip_color) pixels
      0x80 | n  + 1 lit     — n pixels of one solid colour (1 byte to literal stream)
      n         + n lits    — n literal pixels (n bytes to literal stream)

    Returns (rle_bytes, literal_bytes).
    """
    rle = bytearray()
    lit = bytearray()
    i = 0
    length = len(row)

    while i < length:
        color = row[i]

        # Transparent run
        if color == skip_color:
            j = i + 1
            while j < length and row[j] == skip_color and j - i < _MAX_RUN:
                j += 1
            rle.append(0xC0 | (j - i))
            i = j
            continue

        # Solid run (≥2 identical non-transparent pixels)
        j = i + 1
        while j < length and row[j] == color and row[j] != skip_color and j - i < _MAX_RUN:
            j += 1
        if j - i >= 2:
            rle.append(0x80 | (j - i))
            lit.append(color)
            i = j
            continue

        # Literal run — collect until the next compressible boundary
        literals = [color]
        j = i + 1
        while j < length and len(literals) < _MAX_RUN:
            c = row[j]
            if c == skip_color:
                break
            # Stop before a solid run of 3+ identical pixels
            if j + 2 < length and row[j] == row[j + 1] == row[j + 2]:
                break
            literals.append(c)
            j += 1
        rle.append(len(literals))
        lit.extend(literals)
        i = j

    return bytes(rle), bytes(lit)


def _compress_cel(pixels, width, height, skip_color):
    """
    Compress a flat pixel list into the three Sierra sections.

    Control table layout (each entry is a little-endian uint32):
      ctrl[0 .. height-1]         cumulative RLE byte offsets per row
      ctrl[height .. 2*height-1]  cumulative literal byte offsets per row

    Returns (ctrl_table_bytes, rle_bytes, lit_bytes).
    """
    rle_chunks = []
    lit_chunks = []
    for y in range(height):
        r, l = _compress_row(pixels[y * width:(y + 1) * width], skip_color)
        rle_chunks.append(r)
        lit_chunks.append(l)

    # Build cumulative offset arrays
    rle_offsets, lit_offsets = [], []
    cum = 0
    for chunk in rle_chunks:
        rle_offsets.append(cum)
        cum += len(chunk)
    cum = 0
    for chunk in lit_chunks:
        lit_offsets.append(cum)
        cum += len(chunk)

    ctrl = struct.pack(f'<{len(rle_offsets) + len(lit_offsets)}I',
                       *(rle_offsets + lit_offsets))
    return ctrl, b''.join(rle_chunks), b''.join(lit_chunks)


# ---------------------------------------------------------------------------
# Main import
# ---------------------------------------------------------------------------

def import_v56(v56_path, images_dir, output_path):
    """
    Rebuild *v56_path* replacing any cels whose PNG is found in *images_dir*,
    and write the result to *output_path*.
    """
    p = Path(v56_path)
    images_dir = Path(images_dir)
    output_path = Path(output_path)

    raw = p.read_bytes()
    resource_size = len(raw)
    stream = io.BytesIO(raw)

    if raw[0:1] != b'\x80':
        raise ValueError(f"{p.name}: not a Sierra VGA view file (expected 0x80 at byte 0)")

    # --- View header fields ---
    view_header_size = _at(stream, OFFSET,      2)
    loop_count       = _at(stream, OFFSET + 2,  1)
    hunk_pal_offset  = _at(stream, OFFSET + 8,  4)   # 0 if no embedded palette
    loop_header_size = _at(stream, OFFSET + 12, 1)
    cel_header_size  = _at(stream, OFFSET + 13, 1)

    view_name  = p.stem
    loops_base = OFFSET + 2 + view_header_size

    # --- Find replacement PNGs ---
    pattern = re.compile(rf'^{re.escape(view_name)}_(\d+)_(\d+)\.png$', re.IGNORECASE)
    replacements = {}   # (loop, cel) -> Path
    for img in sorted(images_dir.glob('*.png')):
        m = pattern.match(img.name)
        if m:
            replacements[(int(m.group(1)), int(m.group(2)))] = img

    if not replacements:
        print(f"No images matching '{view_name}_<loop>_<cel>.png' found in {images_dir}")
        return

    print(f"Replacement images found: {len(replacements)}")

    # --- Parse every loop → cel, gather pixels ---
    cel_list = []   # all cels in encounter order

    for loop_num in range(loop_count):
        loop_hdr        = loops_base + loop_header_size * loop_num
        cel_count       = _at(stream, loop_hdr + 2,  1)
        cel_table_ptr   = _at(stream, loop_hdr + 12, 4)   # offset from OFFSET
        cel_table_start = OFFSET + cel_table_ptr

        for cel_num in range(cel_count):
            hdr_pos     = cel_table_start + cel_header_size * cel_num
            width       = _at(stream, hdr_pos + 0,  2)
            height      = _at(stream, hdr_pos + 2,  2)
            skip_color  = _at(stream, hdr_pos + 8,  1)
            compression = _at(stream, hdr_pos + 9,  1)   # 138 = RLE
            # The three data-section pointers stored in the cel header
            data_off    = OFFSET + _at(stream, hdr_pos + 24, 4)   # RLE data
            lit_off     = OFFSET + _at(stream, hdr_pos + 28, 4)   # literal data
            ctrl_off    = OFFSET + _at(stream, hdr_pos + 32, 4)   # control table

            key = (loop_num, cel_num)

            if key in replacements:
                img = Image.open(replacements[key])
                if img.mode != 'P':
                    raise ValueError(
                        f"{replacements[key].name}: must be 8-bit indexed (mode 'P'), "
                        f"got '{img.mode}'. In GIMP: Image → Mode → Indexed."
                    )
                new_w, new_h = img.size
                pixels = list(img.getdata())
                tag = 'REPLACED'
            elif compression == 138:
                pixels = _decompress_cel(
                    stream, width, height, skip_color,
                    data_off, lit_off, ctrl_off, resource_size)
                new_w, new_h = width, height
                tag = 'kept'
            else:
                # Non-RLE cel — cannot recompress; leave as a warning
                pixels = None
                new_w, new_h = width, height
                tag = f'SKIPPED (unsupported compression {compression})'

            print(f"  loop {loop_num}  cel {cel_num}  {new_w}x{new_h}  [{tag}]")

            cel_list.append({
                'hdr_pos':    hdr_pos,
                'width':      new_w,
                'height':     new_h,
                'skip_color': skip_color,
                'compression': compression,
                'pixels':     pixels,
                # originals needed to detect data_section_start
                'orig_data_off': data_off,
                'orig_lit_off':  lit_off,
                'orig_ctrl_off': ctrl_off,
            })

    # --- Determine where the data section begins ---
    # Everything below this offset is "header territory" that we copy verbatim
    # (view header, loop headers, cel header tables).  We only patch specific
    # fields (width, height, ctrl_off, data_off, lit_off) inside that region.
    data_section_start = resource_size   # pessimistic default
    for ci in cel_list:
        if ci['compression'] == 138:
            earliest = min(ci['orig_data_off'], ci['orig_lit_off'], ci['orig_ctrl_off'])
            if earliest < data_section_start:
                data_section_start = earliest

    if data_section_start == resource_size:
        raise ValueError("Could not locate any RLE data section in the file")

    print(f"\nHeader zone: 0x0000–{data_section_start - 1:#06x}")

    # Mutable copy of the header zone — we'll patch fields in-place with struct.pack_into
    header = bytearray(raw[:data_section_start])

    # --- Build fresh data section ---
    # Layout per cel: [ctrl_table][rle_data][lit_data]
    new_data = bytearray()
    cur = data_section_start   # running absolute file offset

    for ci in cel_list:
        hdr_pos = ci['hdr_pos']

        if ci['pixels'] is None:
            # Skipped (unsupported compression) — leave header fields as-is.
            # The original data has been discarded, so the file will be faulty for
            # this cel, but that mirrors a situation we can't handle anyway.
            print(f"  Warning: cel at hdr_pos=0x{hdr_pos:x} — offsets left stale")
            continue

        ctrl_bytes, rle_bytes, lit_bytes = _compress_cel(
            ci['pixels'], ci['width'], ci['height'], ci['skip_color'])

        # Absolute offsets from OFFSET (as the file format expects)
        new_ctrl_off = cur - OFFSET
        new_rle_off  = new_ctrl_off + len(ctrl_bytes)
        new_lit_off  = new_rle_off  + len(rle_bytes)

        new_data += ctrl_bytes + rle_bytes + lit_bytes
        cur += len(ctrl_bytes) + len(rle_bytes) + len(lit_bytes)

        # Patch cel header fields inside the header zone
        struct.pack_into('<H', header, hdr_pos,      ci['width'])   # +0  width
        struct.pack_into('<H', header, hdr_pos + 2,  ci['height'])  # +2  height
        struct.pack_into('<I', header, hdr_pos + 24, new_rle_off)   # +24 data_off  (RLE)
        struct.pack_into('<I', header, hdr_pos + 28, new_lit_off)   # +28 lit_off   (literals)
        struct.pack_into('<I', header, hdr_pos + 32, new_ctrl_off)  # +32 ctrl_off  (control table)

    # --- Re-attach the embedded palette (hunk palette) if present ---
    if hunk_pal_offset:
        pal_abs = OFFSET + hunk_pal_offset
        if pal_abs < data_section_start:
            # Palette sits inside the header zone (raw[:data_section_start]) that we
            # already copied verbatim — nothing to do, offset in header is still valid.
            print(f"Hunk palette already in header zone at {pal_abs:#x} — preserved as-is")
        else:
            # Palette lives after pixel data — re-append it and update the pointer.
            pal_raw = raw[pal_abs:]
            new_pal_off = cur - OFFSET
            new_data += pal_raw
            struct.pack_into('<I', header, OFFSET + 8, new_pal_off)
            print(f"Hunk palette relocated to offset {new_pal_off:#x}")

    result = bytes(header) + bytes(new_data)
    output_path.write_bytes(result)
    print(f"\nDone — {len(result):,} bytes written to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('v56',
                        help='.v56 file to update')
    parser.add_argument('images_dir',
                        help='directory containing replacement PNG images')
    parser.add_argument('-o', '--output',
                        help='output .v56 path (default: overwrite the source file)')
    args = parser.parse_args()

    v56_path = Path(args.v56)
    output   = Path(args.output) if args.output else v56_path

    import_v56(v56_path, args.images_dir, output)


if __name__ == '__main__':
    main()
