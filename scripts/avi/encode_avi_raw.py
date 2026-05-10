"""
encode_avi_raw.py
Write an uncompressed 8-bit palette AVI from PNG frames.
No codec required — pure RIFF/AVI format written directly.

Usage:
    python scripts/encode_avi_raw.py <frames_dir> <output_avi> [fps]

Example:
    python scripts/encode_avi_raw.py games_assets/kq6/opening_frames kq6_work/TOON.AVI 8
"""

import sys, os, glob, struct
from PIL import Image


def u32(n):
    return struct.pack('<I', n)

def fourcc(s):
    return s.encode('ascii')

def pad2(n):
    """Pad to 2-byte alignment (AVI chunks are word-aligned)."""
    return n + (n & 1)


def encode_frame(img, width, height):
    """Convert PIL image to bottom-up uncompressed 8-bit DIB bytes."""
    p = img.tobytes()
    rows = [p[r * width:(r + 1) * width] for r in range(height - 1, -1, -1)]
    return b''.join(rows)


def write_avi(frame_files, output_path, fps, global_palette):
    width, height = Image.open(frame_files[0]).size
    total  = len(frame_files)
    stride = width  # 8-bit, no padding needed for multiples of 4
    frame_bytes = stride * height

    # ---- Build palette bytes (256 RGBQUAD entries: B G R reserved) ----
    pal_bytes = b''
    for i in range(256):
        r = global_palette[i * 3]
        g = global_palette[i * 3 + 1]
        b = global_palette[i * 3 + 2]
        pal_bytes += struct.pack('4B', b, g, r, 0)

    # ---- BITMAPINFOHEADER + palette ----
    bmi_header = struct.pack('<IiiHHIIiiII',
        40,           # biSize
        width,
        height,       # positive = bottom-up
        1,            # biPlanes
        8,            # biBitCount
        0,            # biCompression = BI_RGB
        frame_bytes,  # biSizeImage
        0, 0,         # pixels per meter
        256,          # biClrUsed
        256,          # biClrImportant
    )
    strf_data = bmi_header + pal_bytes

    # ---- Stream header (strh) for video ----
    strh_data = struct.pack('<4s4sIHHIIIIIIiI16s',
        b'vids',       # fccType
        b'\x00\x00\x00\x00',  # fccHandler = uncompressed
        0,             # dwFlags
        0,             # wPriority
        0,             # wLanguage
        1,             # dwInitialFrames
        1,             # dwScale
        fps,           # dwRate
        0,             # dwStart
        total,         # dwLength
        frame_bytes,   # dwSuggestedBufferSize
        -1,            # dwQuality
        0,             # dwSampleSize
        struct.pack('<hhhh', 0, 0, width, height),  # rcFrame
    )

    def chunk(fcc, data):
        d = data if isinstance(data, bytes) else b''.join(data)
        size = len(d)
        raw = fcc + u32(size) + d
        if size & 1:
            raw += b'\x00'
        return raw

    def list_chunk(fcc_list, fcc_type, parts):
        inner = fcc_type + b''.join(parts)
        return fourcc('LIST') + u32(len(inner)) + inner

    # ---- AVI main header (avih) ----
    avih_data = struct.pack('<IIIIIIIIIIIIII',
        1000000 // fps,    # dwMicroSecPerFrame
        frame_bytes * fps, # dwMaxBytesPerSec
        0,                 # dwPaddingGranularity
        0x10,              # dwFlags (AVIF_HASINDEX)
        total,             # dwTotalFrames
        0,                 # dwInitialFrames
        1,                 # dwStreams
        frame_bytes,       # dwSuggestedBufferSize
        width,             # dwWidth
        height,            # dwHeight
        0, 0, 0, 0,        # reserved
    )

    strl = list_chunk(b'LIST', b'strl', [
        chunk(b'strh', strh_data),
        chunk(b'strf', strf_data),
    ])

    hdrl = list_chunk(b'LIST', b'hdrl', [
        chunk(b'avih', avih_data),
        strl,
    ])

    # ---- Encode all frames and build movi + index ----
    print(f"Encoding {total} frames ({width}x{height}) at {fps} fps...")

    def palette_to_rgbquad(pal_flat):
        """Convert [R,G,B]*256 list to RGBQUAD bytes (B,G,R,0)."""
        out = b''
        for j in range(256):
            out += struct.pack('4B', pal_flat[j*3+2], pal_flat[j*3+1], pal_flat[j*3], 0)
        return out

    def build_palette_change(pal_flat, start=0, count=256):
        """Build a 00pc palette change chunk payload.
        Uses PALETTEENTRY order: R, G, B, flags (NOT RGBQUAD B,G,R)."""
        entries = b''
        for j in range(start, start + count):
            entries += struct.pack('4B',
                pal_flat[j*3],    # peRed
                pal_flat[j*3+1],  # peGreen
                pal_flat[j*3+2],  # peBlue
                0)                # peFlags
        return struct.pack('<BBH', start, count % 256, 0) + entries

    frame_data_list = []   # list of (palette_flat, pixel_bytes)
    prev_palette = None

    for i, path in enumerate(frame_files):
        img = Image.open(path).convert('P')
        pal = img.getpalette()   # original palette from the PNG
        pixels = encode_frame(img, width, height)
        # Skip palette change for first frame — strf already sets it correctly
        palette_changed = (prev_palette is not None) and (pal != prev_palette)
        frame_data_list.append((pal, pixels, palette_changed))
        prev_palette = pal
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{total} frames processed...")

    # Build movi list and index
    movi_inner = b'movi'
    idx_entries = b''
    offset = 4  # relative to start of movi data (after 'movi' fourcc)

    for pal, raw, pal_changed in frame_data_list:
        if pal_changed:
            pc_payload = build_palette_change(pal)
            pc_entry = fourcc('00pc') + u32(len(pc_payload)) + pc_payload
            if len(pc_payload) & 1:
                pc_entry += b'\x00'
            movi_inner += pc_entry
            idx_entries += fourcc('00pc') + u32(0x00) + u32(offset) + u32(len(pc_payload))
            offset += 8 + pad2(len(pc_payload))

        entry = fourcc('00dc') + u32(len(raw)) + raw
        if len(raw) & 1:
            entry += b'\x00'
        movi_inner += entry
        idx_entries += fourcc('00dc') + u32(0x10) + u32(offset) + u32(len(raw))
        offset += 8 + pad2(len(raw))

    movi_chunk = fourcc('LIST') + u32(len(movi_inner)) + movi_inner
    idx1_chunk = chunk(b'idx1', idx_entries)

    # ---- Final RIFF AVI ----
    riff_inner = b'AVI ' + hdrl + movi_chunk + idx1_chunk
    riff = fourcc('RIFF') + u32(len(riff_inner)) + riff_inner

    with open(output_path, 'wb') as f:
        f.write(riff)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Done: {output_path}  ({size_mb:.1f} MB)")


def main():
    if len(sys.argv) < 3:
        print("Usage: python encode_avi_raw.py <frames_dir> <output_avi> [fps]")
        sys.exit(1)

    frames_dir = sys.argv[1]
    output_avi = sys.argv[2]
    fps        = int(sys.argv[3]) if len(sys.argv) > 3 else 8

    frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
    if not frame_files:
        print(f"ERROR: No frame_*.png files found in {frames_dir}")
        sys.exit(1)

    # Build initial palette from first frame for the strf chunk
    ref = Image.open(frame_files[0]).convert('P')
    global_palette = ref.getpalette()

    write_avi(frame_files, output_avi, fps, global_palette)


if __name__ == '__main__':
    main()
