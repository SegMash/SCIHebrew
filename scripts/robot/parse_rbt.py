"""
RBT (Sierra Robot) video file parser.

Supports Robot format versions 5 and 6:
  - v5: KQ7 DOS, Phantasmagoria, PQ:SWAT, Lighthouse
  - v6: RAMA

Based on the format documented and implemented in ScummVM:
  engines/sci/video/robot_decoder.h / robot_decoder.cpp

Usage:
    python parse_rbt.py <file.rbt> [options]

Options:
    -o / --output-dir DIR       Output directory (default: rbt_output)
    --frames N or START-END     Extract only frame N, or a range
    --no-video                  Skip frame extraction (print header info only)
    --audio                     Extract audio as WAV (audio.wav in output dir)
    --canvas-width  W           Override output canvas width  (default: auto)
    --canvas-height H           Override output canvas height (default: auto)

Output:
    frame_NNNNN.png             One PNG per frame (requires Pillow)
    frame_NNNNN_celK.raw        Fallback if Pillow is not installed
    audio.wav                   Optional mono 22050Hz 16-bit PCM audio

Dependencies (optional but strongly recommended):
    pip install Pillow
"""

import struct
import sys
import os
import argparse


# ─────────────────────────────────────────────────────────────────────────────
# LZS (STACpack) decompressor – port of ScummVM's DecompressorLZS
# (engines/sci/resource/decompressor.cpp)
# ─────────────────────────────────────────────────────────────────────────────

class LZSDecompressor:
    """MSB-first bitstream LZS / STACpack decompressor used in SCI32."""

    def __init__(self, data: bytes):
        self._data   = data
        self._pos    = 0
        self._bitbuf = 0   # up to 32 bits cached (MSB-justified)
        self._nbits  = 0

    def _fetch(self):
        while self._nbits <= 24 and self._pos < len(self._data):
            byte = self._data[self._pos]; self._pos += 1
            self._bitbuf = (self._bitbuf | (byte << (24 - self._nbits))) & 0xFFFFFFFF
            self._nbits += 8

    def _get(self, n: int) -> int:
        if self._nbits < n:
            self._fetch()
        ret = (self._bitbuf >> (32 - n)) & ((1 << n) - 1)
        self._bitbuf = (self._bitbuf << n) & 0xFFFFFFFF
        self._nbits -= n
        return ret

    def _comp_len(self) -> int:
        """Variable-length match-length field."""
        b = self._get(2)
        if b < 3:
            return b + 2          # 0→2, 1→3, 2→4
        b = self._get(2)
        if b < 3:
            return b + 5          # 0→5, 1→6, 2→7
        clen = 8
        while True:
            nibble = self._get(4)
            clen += nibble
            if nibble != 0xF:
                break
        return clen

    def decompress(self, unpacked_size: int) -> bytes:
        out = bytearray()
        while len(out) < unpacked_size:
            if self._get(1):                 # compressed reference
                if self._get(1):             # 7-bit back-offset
                    offs = self._get(7)
                    if offs == 0:            # end-of-stream marker
                        break
                else:                        # 11-bit back-offset
                    offs = self._get(11)
                clen = self._comp_len()
                start = len(out) - offs
                for i in range(clen):
                    out.append(out[start + i])
            else:                            # literal byte
                out.append(self._get(8))
        return bytes(out)


# ─────────────────────────────────────────────────────────────────────────────
# Sierra SOL DPCM-16 decompressor – port of sol.cpp::deDPCM16Mono
# (engines/sci/sound/decoders/sol.cpp)
# ─────────────────────────────────────────────────────────────────────────────

_DPCM16_TABLE = [
    0x0000, 0x0008, 0x0010, 0x0020, 0x0030, 0x0040, 0x0050, 0x0060,
    0x0070, 0x0080, 0x0090, 0x00A0, 0x00B0, 0x00C0, 0x00D0, 0x00E0,
    0x00F0, 0x0100, 0x0110, 0x0120, 0x0130, 0x0140, 0x0150, 0x0160,
    0x0170, 0x0180, 0x0190, 0x01A0, 0x01B0, 0x01C0, 0x01D0, 0x01E0,
    0x01F0, 0x0200, 0x0208, 0x0210, 0x0218, 0x0220, 0x0228, 0x0230,
    0x0238, 0x0240, 0x0248, 0x0250, 0x0258, 0x0260, 0x0268, 0x0270,
    0x0278, 0x0280, 0x0288, 0x0290, 0x0298, 0x02A0, 0x02A8, 0x02B0,
    0x02B8, 0x02C0, 0x02C8, 0x02D0, 0x02D8, 0x02E0, 0x02E8, 0x02F0,
    0x02F8, 0x0300, 0x0308, 0x0310, 0x0318, 0x0320, 0x0328, 0x0330,
    0x0338, 0x0340, 0x0348, 0x0350, 0x0358, 0x0360, 0x0368, 0x0370,
    0x0378, 0x0380, 0x0388, 0x0390, 0x0398, 0x03A0, 0x03A8, 0x03B0,
    0x03B8, 0x03C0, 0x03C8, 0x03D0, 0x03D8, 0x03E0, 0x03E8, 0x03F0,
    0x03F8, 0x0400, 0x0440, 0x0480, 0x04C0, 0x0500, 0x0540, 0x0580,
    0x05C0, 0x0600, 0x0640, 0x0680, 0x06C0, 0x0700, 0x0740, 0x0780,
    0x07C0, 0x0800, 0x0900, 0x0A00, 0x0B00, 0x0C00, 0x0D00, 0x0E00,
    0x0F00, 0x1000, 0x1400, 0x1800, 0x1C00, 0x2000, 0x3000, 0x4000,
]


def deDPCM16(data: bytes) -> bytes:
    """
    Decompress one Sierra SOL DPCM-16 channel.
    Each input byte → one signed int16 output sample.
    Returns raw LE 16-bit PCM bytes.
    """
    pcm, _ = deDPCM16_carry(data, 0)
    return pcm


def deDPCM16_carry(data: bytes, initial_sample: int = 0):
    """
    Like deDPCM16 but accepts an initial carry state and returns
    (pcm_bytes, final_sample) so callers can chain frames correctly.

    ScummVM decodes each per-frame audio packet independently (carry=0),
    relying on the 8-byte per-frame runway to restore the DPCM accumulator
    to the correct value before decoding the body.  Use this function to
    process the runway and then the body per-frame:

        _, carry = deDPCM16_carry(raw[:8], 0)   # warm up from runway
        pcm, _  = deDPCM16_carry(raw[8:], carry) # decode body
    """
    sample = initial_sample
    out = bytearray()
    for delta in data:
        if delta & 0x80:
            sample -= _DPCM16_TABLE[delta & 0x7F]
        else:
            sample += _DPCM16_TABLE[delta]
        # emulate x86 16-bit wrap-around
        if sample > 32767:
            sample -= 65536
        elif sample < -32768:
            sample += 65536
        out += struct.pack('<h', sample)
    return bytes(out), sample


# ─────────────────────────────────────────────────────────────────────────────
# SCI HunkPalette parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_hunk_palette(data: bytes):
    """
    Parse a SCI2 HunkPalette block and return 256 (R,G,B) tuples.

    Follows ScummVM's HunkPalette layout exactly (palette32.h / palette32.cpp):
      kNumPaletteEntriesOffset = 10   (uint8 numPalettes)
      kHunkPaletteHeaderSize   = 13
      getPalPointer offset     = 13 + 2*numPalettes
      kEntryStartColorOffset   = 10  (uint8  startColor, relative to palPtr)
      kEntryNumColorsOffset    = 14  (uint16 numColors,  relative to palPtr)
      kEntryUsedOffset         = 16  (uint8  sharedUsed-flag's companion)
      kEntrySharedUsedOffset   = 17  (uint8  sharedUsed)
      kEntryHeaderSize         = 22  (colour data follows at palPtr + 22)

    If sharedUsed == True  → 3 bytes per entry (R, G, B)
    If sharedUsed == False → 4 bytes per entry (used, R, G, B)

    Only the entries from startColor … startColor+numColors-1 are set;
    the remaining slots default to black.
    """
    colors = [(0, 0, 0)] * 256

    if len(data) < 13:
        return [(i, i, i) for i in range(256)]

    num_palettes = data[10]          # kNumPaletteEntriesOffset = 10
    if num_palettes == 0:
        return colors                # palette block carries no colour data

    pal_ptr = 13 + 2 * num_palettes  # getPalPointer() offset

    if pal_ptr + 22 > len(data):
        return colors

    start_color = data[pal_ptr + 10]                              # kEntryStartColorOffset
    num_colors  = struct.unpack_from('<H', data, pal_ptr + 14)[0] # kEntryNumColorsOffset
    shared_used = data[pal_ptr + 17]                              # kEntrySharedUsedOffset

    color_base      = pal_ptr + 22   # kEntryHeaderSize = 22
    bytes_per_entry = 3 if shared_used else 4

    end_color = start_color + num_colors
    if end_color > 256:
        end_color = 256

    if color_base + num_colors * bytes_per_entry > len(data):
        return colors

    for i in range(end_color - start_color):
        idx = start_color + i
        off = color_base + i * bytes_per_entry
        if shared_used:
            colors[idx] = (data[off], data[off + 1], data[off + 2])
        else:
            # 4-byte layout: used_flag, R, G, B
            colors[idx] = (data[off + 1], data[off + 2], data[off + 3])

    return colors


# ─────────────────────────────────────────────────────────────────────────────
# Vertical-scale expand – port of RobotDecoder::expandCel
# (engines/sci/video/robot_decoder.cpp)
# ─────────────────────────────────────────────────────────────────────────────

def expand_cel(source: bytes, cel_width: int, cel_height: int, v_scale: int) -> bytes:
    """
    Reconstruct a cel that had lines deleted during compression.
    v_scale is the percentage of lines kept (100 = no decimation).

    The algorithm is a Bresenham-style distributor that replicates source rows;
    replicating the last rows more than the first ones.
    """
    if v_scale == 100:
        return source

    source_height = (cel_height * v_scale) // 100
    if source_height <= 0:
        return source

    numerator   = cel_height
    denominator = source_height
    remainder   = 0

    # Compute lines-to-draw for each source row.
    # ScummVM's loop iterates y from sourceHeight-1 DOWN TO 0,
    # while source advances forward (row 0, 1, 2, …).
    # So lines_per_row[i] is the repeat count for source row i,
    # computed with y = sourceHeight-1-i.
    lines_per_row = []
    for _ in range(source_height):
        remainder += numerator
        n = remainder // denominator
        remainder %= denominator
        lines_per_row.append(n)

    out = bytearray()
    for i in range(source_height):
        row = source[i * cel_width: (i + 1) * cel_width]
        for _ in range(lines_per_row[i]):
            out += row

    return bytes(out)


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

class RBTHeader:
    """Parsed Robot file header (v5/v6)."""
    __slots__ = [
        'version', 'audio_block_size', 'primer_zero_compress',
        'num_frames', 'palette_size', 'primer_reserved_size',
        'x_res', 'y_res', 'has_palette', 'has_audio',
        'frame_rate', 'is_hi_res', 'max_skippable', 'max_cels',
        'max_cel_area',
    ]


class RBTCel:
    """One decoded cel from a Robot video frame."""
    __slots__ = ['v_scale', 'width', 'height', 'x', 'y', 'pixels']

    def __init__(self):
        self.v_scale = 100
        self.width   = 0
        self.height  = 0
        self.x       = 0
        self.y       = 0
        self.pixels  = b''   # raw 8-bit indexed, width × height bytes, top-to-bottom


class RBTFrame:
    """One decoded Robot video frame."""
    __slots__ = ['frame_no', 'cels', 'audio_position', 'audio_size', 'audio_raw']

    def __init__(self, frame_no: int):
        self.frame_no      = frame_no
        self.cels          = []    # list[RBTCel]
        self.audio_position = 0   # absolute position in the audio stream
        self.audio_size    = 0    # compressed bytes (excluding 8-byte runway)
        self.audio_raw     = b''  # raw DPCM-compressed bytes (incl. runway)


# ─────────────────────────────────────────────────────────────────────────────
# Binary reader helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_readers(big_endian: bool):
    """Return (u16, s16, u32, s32) reader functions for the given endianness.
    Each function takes (buffer, offset) and returns (value, new_offset).
    """
    pfx = '>' if big_endian else '<'

    def u16(buf, p): return struct.unpack_from(pfx + 'H', buf, p)[0], p + 2
    def s16(buf, p): return struct.unpack_from(pfx + 'h', buf, p)[0], p + 2
    def u32(buf, p): return struct.unpack_from(pfx + 'I', buf, p)[0], p + 4
    def s32(buf, p): return struct.unpack_from(pfx + 'i', buf, p)[0], p + 4

    return u16, s16, u32, s32


# ─────────────────────────────────────────────────────────────────────────────
# Main parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_rbt(filepath: str, verbose: bool = True):
    """
    Parse an RBT file.

    Returns:
        hdr           – RBTHeader
        palette       – list of 256 (R,G,B) tuples, or None
        frames        – list of RBTFrame (cels fully decoded to 8-bit indexed pixels)
        record_pos    – list of byte offsets, one per frame
        cue_times     – list of 256 tick values
        cue_values    – list of 256 cue values
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    # ── Signature check ──────────────────────────────────────────────────────
    if data[0] != 0x16:
        raise ValueError(f"Not a Robot file: byte 0 = 0x{data[0]:02X}, expected 0x16")
    if data[2:6] != b'SOL\x00':
        raise ValueError(f"Not a Robot file: magic bytes {data[2:6]!r}, expected b'SOL\\x00'")

    # ── Endianness detection ─────────────────────────────────────────────────
    # Most files are little-endian (x86 DOS/Windows).
    # 68k/PPC Mac files are big-endian; ScummVM detects by checking whether
    # reading the version field as big-endian gives a value in [1, 255].
    ver_be = struct.unpack_from('>H', data, 6)[0]
    big_endian = (0 < ver_be <= 0x00FF)

    u16, s16, u32, s32 = make_readers(big_endian)

    # ── File header (starts at offset 6 after the 6-byte preamble) ──────────
    pos = 6
    hdr = RBTHeader()

    hdr.version,             pos = u16(data, pos)
    hdr.audio_block_size,    pos = u16(data, pos)
    hdr.primer_zero_compress,pos = s16(data, pos)
    pos += 2                                         # unused
    hdr.num_frames,          pos = u16(data, pos)
    palette_size,            pos = u16(data, pos)
    hdr.palette_size         = palette_size
    hdr.primer_reserved_size,pos = u16(data, pos)
    hdr.x_res,               pos = s16(data, pos)
    hdr.y_res,               pos = s16(data, pos)
    hdr.has_palette          = bool(data[pos]); pos += 1
    hdr.has_audio            = bool(data[pos]); pos += 1
    pos += 2                                         # unused
    hdr.frame_rate,          pos = s16(data, pos)
    hdr.is_hi_res,           pos = s16(data, pos)
    hdr.max_skippable,       pos = s16(data, pos)
    hdr.max_cels,            pos = s16(data, pos)
    hdr.max_cel_area         = []
    for _ in range(4):
        v, pos = s32(data, pos)
        hdr.max_cel_area.append(v)
    pos += 8                                         # reserved

    if verbose:
        print(f"=== Robot file: {os.path.basename(filepath)} ===")
        print(f"  Version:        v{hdr.version}  ({'big' if big_endian else 'little'}-endian)")
        print(f"  Frames:         {hdr.num_frames}")
        print(f"  Frame rate:     {hdr.frame_rate} fps")
        print(f"  Resolution:     {hdr.x_res}x{hdr.y_res}")
        print(f"  Has palette:    {hdr.has_palette}  ({palette_size} bytes)")
        print(f"  Has audio:      {hdr.has_audio}    (block size {hdr.audio_block_size} bytes)")
        print(f"  Max cels/frame: {hdr.max_cels}")

    if hdr.version not in (5, 6):
        raise ValueError(f"Unsupported Robot version {hdr.version} (only v5 and v6 are supported)")

    # ── Audio primer section ─────────────────────────────────────────────────
    even_primer_size = 0
    odd_primer_size  = 0
    primer_header_pos = pos

    if hdr.has_audio:
        if hdr.primer_reserved_size != 0:
            total_primer_size,  pos = s32(data, pos)
            compression_type,   pos = s16(data, pos)
            even_primer_size,   pos = s32(data, pos)
            odd_primer_size,    pos = s32(data, pos)
            if compression_type != 0:
                print(f"  WARNING: unknown primer compression type {compression_type}")
            if even_primer_size + odd_primer_size != hdr.primer_reserved_size:
                pos = primer_header_pos + hdr.primer_reserved_size
            else:
                pos += even_primer_size + odd_primer_size
        elif hdr.primer_zero_compress:
            even_primer_size = 19922
            odd_primer_size  = 21024
            # Zero-filled buffers – no bytes in file
        else:
            raise ValueError("Robot audio primer flags are inconsistent")
    else:
        pos += hdr.primer_reserved_size

    # ── Embedded palette ─────────────────────────────────────────────────────
    palette = None
    if hdr.has_palette and palette_size > 0:
        raw_pal = data[pos: pos + palette_size]
        palette = parse_hunk_palette(raw_pal)
    pos += palette_size

    if verbose and palette:
        print(f"  Palette:        loaded ({len(palette)} entries)")

    # ── Video frame size index ───────────────────────────────────────────────
    video_sizes = []
    if hdr.version == 5:
        for _ in range(hdr.num_frames):
            v, pos = u16(data, pos); video_sizes.append(v)
    else:  # v6
        for _ in range(hdr.num_frames):
            v, pos = s32(data, pos); video_sizes.append(v)

    # ── Packet size index (video + audio per frame) ──────────────────────────
    packet_sizes = []
    if hdr.version == 5:
        for _ in range(hdr.num_frames):
            v, pos = u16(data, pos); packet_sizes.append(v)
    else:  # v6
        for _ in range(hdr.num_frames):
            v, pos = s32(data, pos); packet_sizes.append(v)

    # ── Cue times (256 × int32) ──────────────────────────────────────────────
    cue_times  = [s32(data, pos + i*4)[0] for i in range(256)]
    pos += 256 * 4

    # ── Cue values (256 × uint16) ────────────────────────────────────────────
    cue_values = [u16(data, pos + i*2)[0] for i in range(256)]
    pos += 256 * 2

    # ── Align to next 2048-byte sector ───────────────────────────────────────
    rem = pos % 2048
    if rem:
        pos += 2048 - rem

    # ── Build frame offset table ─────────────────────────────────────────────
    record_pos = [pos]
    for i in range(hdr.num_frames - 1):
        pos += packet_sizes[i]
        record_pos.append(pos)

    if verbose:
        print(f"  First frame at: 0x{record_pos[0]:08X}")
        print(f"  File size:      {len(data)} bytes")

    # ── Decode frames ────────────────────────────────────────────────────────
    frames = []
    for frame_no in range(hdr.num_frames):
        fp   = record_pos[frame_no]
        vlen = video_sizes[frame_no]
        vid  = data[fp: fp + vlen]
        frame = RBTFrame(frame_no)

        if len(vid) >= 2:
            num_cels = u16(vid, 0)[0]
            vp = 2

            for _ in range(num_cels):
                if vp + 22 > len(vid):
                    break

                cel = RBTCel()
                cel.v_scale   = vid[vp + 1]
                cel.width,  _ = u16(vid, vp + 2)
                cel.height, _ = u16(vid, vp + 4)
                # x/y are signed int16 in Robot coordinates
                cel.x = struct.unpack_from('>h' if big_endian else '<h', vid, vp + 10)[0]
                cel.y = struct.unpack_from('>h' if big_endian else '<h', vid, vp + 12)[0]
                data_size,  _ = u16(vid, vp + 14)
                num_chunks, _ = u16(vid, vp + 16)
                vp += 22    # skip cel header (kCelHeaderSize = 22)

                pixels = bytearray()
                for _ in range(num_chunks):
                    if vp + 10 > len(vid):
                        break
                    comp_size,   _ = u32(vid, vp)
                    decomp_size, _ = u32(vid, vp + 4)
                    comp_type,   _ = u16(vid, vp + 8)
                    vp += 10

                    chunk = vid[vp: vp + comp_size]
                    vp += comp_size

                    if comp_type == 0:        # LZS
                        pixels += LZSDecompressor(chunk).decompress(decomp_size)
                    elif comp_type == 2:      # uncompressed
                        pixels += chunk[:decomp_size]
                    else:
                        print(f"  WARNING frame {frame_no}: unknown chunk compression {comp_type}")
                        pixels += bytes(decomp_size)

                if cel.v_scale != 100 and pixels:
                    pixels = expand_cel(bytes(pixels), cel.width, cel.height, cel.v_scale)

                cel.pixels = bytes(pixels)
                frame.cels.append(cel)

        # Audio packet immediately follows video data
        if hdr.has_audio:
            ap = fp + vlen
            if ap + 8 <= len(data):
                abs_pos = struct.unpack_from('<i' if not big_endian else '>i', data, ap)[0]
                blk_size= struct.unpack_from('<i' if not big_endian else '>i', data, ap + 4)[0]
                frame.audio_position = abs_pos
                frame.audio_size     = blk_size
                # The audio block includes an 8-byte DPCM runway that is discarded.
                # We store the whole block (runway + compressed data) for completeness.
                frame.audio_raw = data[ap + 8: ap + 8 + blk_size]

        frames.append(frame)

    return hdr, palette, frames, record_pos, cue_times, cue_values


# ─────────────────────────────────────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────────────────────────────────────

def save_frame_png(frame: RBTFrame, palette, output_dir: str,
                   canvas_w: int = 0, canvas_h: int = 0):
    """Composite all cels of one frame and save as a palettised PNG."""
    try:
        from PIL import Image
    except ImportError:
        save_frame_raw(frame, output_dir)
        return

    if not frame.cels:
        return

    if canvas_w == 0 or canvas_h == 0:
        canvas_w = max((c.x + c.width  for c in frame.cels), default=320)
        canvas_h = max((c.y + c.height for c in frame.cels), default=200)
        canvas_w = max(canvas_w, 1)
        canvas_h = max(canvas_h, 1)

    canvas = Image.new('P', (canvas_w, canvas_h), 0)

    flat_palette = []
    if palette:
        for r, g, b in palette:
            flat_palette += [r, g, b]
        canvas.putpalette(flat_palette)

    for cel in frame.cels:
        if not cel.pixels or cel.width <= 0 or cel.height <= 0:
            continue
        needed = cel.width * cel.height
        pix = cel.pixels[:needed].ljust(needed, b'\x00')
        cel_img = Image.frombytes('P', (cel.width, cel.height), pix)
        if flat_palette:
            cel_img.putpalette(flat_palette)
        x = max(0, cel.x)
        y = max(0, cel.y)
        if x < canvas_w and y < canvas_h:
            canvas.paste(cel_img, (x, y))

    out_path = os.path.join(output_dir, f'frame_{frame.frame_no:05d}.png')
    canvas.save(out_path)   # keep mode 'P' → 8-bit paletted PNG


def save_frame_raw(frame: RBTFrame, output_dir: str):
    """Save raw 8-bit indexed pixel bytes for each cel (fallback)."""
    for i, cel in enumerate(frame.cels):
        path = os.path.join(output_dir, f'frame_{frame.frame_no:05d}_cel{i}.raw')
        with open(path, 'wb') as f:
            # prepend a tiny header: width(u16), height(u16), then pixels
            f.write(struct.pack('<HH', cel.width, cel.height))
            f.write(cel.pixels)


def save_audio_wav(frames, output_path: str):
    """
    Decode audio frames and save as 11025 Hz mono 16-bit WAV.

    In Robot files every frame's audio_position satisfies audio_position % 4 == 0
    (even channel).  Frames with audio_position % 4 == 2 have overlapping content
    and are skipped to avoid duplicating samples and playing audio at half speed.

    Each packet starts with an 8-byte DPCM runway decoded from carry=0 to restore
    the accumulator to the correct level before the body samples.
    """
    import wave
    samples = bytearray()
    for fr in frames:
        raw = fr.audio_raw
        if not raw or len(raw) <= 8:
            continue
        if fr.audio_position % 4 == 2:   # skip overlapping odd-indexed frames
            continue
        _, carry = deDPCM16_carry(raw[:8], 0)   # runway → establish carry
        pcm, _  = deDPCM16_carry(raw[8:], carry)  # body → real audio
        samples += pcm

    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(11025)
        wf.writeframes(bytes(samples))
    n = len(samples) // 2
    print(f"  Audio saved: {output_path}  ({n} samples @ 11025 Hz, {n/11025:.1f} s)")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_frame_spec(spec: str, num_frames: int):
    """Return a set of frame numbers to extract, or None for 'all'."""
    if spec == 'all':
        return None
    if '-' in spec:
        lo, hi = spec.split('-', 1)
        return set(range(int(lo), int(hi) + 1))
    return {int(spec)}


def main():
    ap = argparse.ArgumentParser(
        description='Parse a Sierra Robot (.rbt) video file and extract frames.')
    ap.add_argument('rbt_file',
                    help='Path to the .rbt file')
    ap.add_argument('-o', '--output-dir', default='rbt_output',
                    help='Output directory (default: rbt_output)')
    ap.add_argument('--frames', default='all',
                    help='Frames to extract: "all", a single number N, or a range "A-B"')
    ap.add_argument('--no-video', action='store_true',
                    help='Skip frame extraction (print header only)')
    ap.add_argument('--audio', action='store_true',
                    help='Decode and save audio as audio.wav')
    ap.add_argument('--canvas-width',  type=int, default=0,
                    help='Canvas width in pixels (0 = auto)')
    ap.add_argument('--canvas-height', type=int, default=0,
                    help='Canvas height in pixels (0 = auto)')
    args = ap.parse_args()

    hdr, palette, frames, record_pos, cue_times, cue_values = parse_rbt(
        args.rbt_file, verbose=True)

    # Print active cue points
    active = [(t, v) for t, v in zip(cue_times, cue_values) if t != -1 and t != 0x7FFFFFFF]
    if active:
        print(f"\n  Cue points ({len(active)}):")
        for t, v in active[:20]:
            approx_frame = (t * hdr.frame_rate) // 60
            print(f"    tick {t:8d}  (~frame {approx_frame:4d})  value = {v}")
        if len(active) > 20:
            print(f"    ... ({len(active) - 20} more not shown)")

    if args.no_video:
        return

    os.makedirs(args.output_dir, exist_ok=True)

    # Canvas size: prefer file's declared resolution, fall back to 640×480
    cw = args.canvas_width  or (hdr.x_res if hdr.x_res > 0 else 640)
    ch = args.canvas_height or (hdr.y_res if hdr.y_res > 0 else 480)

    frame_set = parse_frame_spec(args.frames, hdr.num_frames)

    print(f"\nExtracting frames to '{args.output_dir}/' ...")
    extracted = 0
    for frame in frames:
        if frame_set is not None and frame.frame_no not in frame_set:
            continue
        save_frame_png(frame, palette, args.output_dir, cw, ch)
        extracted += 1
        if extracted % 100 == 0:
            print(f"  {extracted} / {hdr.num_frames} frames written ...")

    print(f"  Done. {extracted} frame(s) extracted.")

    if args.audio:
        wav_path = os.path.join(args.output_dir, 'audio.wav')
        save_audio_wav(frames, wav_path)


if __name__ == '__main__':
    main()
