"""
RBT (Sierra Robot) video encoder.

Takes a folder of numbered frame images (PNG or BMP, 8-bit palettised or RGB)
and an optional audio file (WAV), and writes a Sierra Robot v5/v6 .rbt file.

Usage:
    python encode_rbt.py <frames_dir> <output.rbt> [options]

Options:
    --fps N           Frame rate (default: 15). Must be a divisor of 11025 for
                      audio (e.g. 1,3,5,7,9,15,21,25,35,45,63,75,105,175,225,315,441,525,735)
    --audio FILE      WAV audio file (mono/stereo, any sample rate)
    --palette FILE    External palette PNG/image (uses first row of pixels as
                      the 256-colour palette). Default: auto from first frame.
    --canvas-width W  Override output canvas width.
    --canvas-height H Override output canvas height.
    --lzs             Use LZS compression for video chunks (smaller files,
                      required if frame size > ~64KB for v5).
    --v6              Force Robot v6 format (uint32 indices; needed for large
                      frames like 640×480 uncompressed).

Output:
    A .rbt file playable in ScummVM (SCI2/SCI2.1 games supporting Robot videos).

Notes:
    * Frames must be named so they sort correctly (e.g. frame_00000.png,
      frame_00001.png, ... or 00000.png, 001.png, etc.).
    * All frames must have the same dimensions.
    * If the frame count * frameSize exceeds uint16 for packet/video indices,
      v6 (uint32) is used automatically.
    * Audio is encoded as Sierra SOL DPCM-16 mono at 11025 Hz (even channel).
      The odd channel is filled by interpolation in the decoder, giving
      effective 22050 Hz output. For best quality supply 22050 Hz mono WAV.

Dependencies:
    pip install Pillow        (required for image loading/quantization)
    pip install numpy         (optional, for faster audio resampling)
"""

import struct
import os
import sys
import glob
import wave
import argparse
import bisect
import time


# ─────────────────────────────────────────────────────────────────────────────
# Progress bar (no external dependencies)
# ─────────────────────────────────────────────────────────────────────────────

class ProgressBar:
    """Simple terminal progress bar with ETA."""

    def __init__(self, total: int, label: str = '', width: int = 40):
        self.total   = max(1, total)
        self.label   = label
        self.width   = width
        self._start  = time.time()
        self._done   = 0
        self._update(0)

    def step(self, n: int = 1):
        self._done = min(self._done + n, self.total)
        self._update(self._done)

    def finish(self):
        self._done = self.total
        self._update(self.total)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def _update(self, done: int):
        frac    = done / self.total
        filled  = int(self.width * frac)
        bar     = '#' * filled + '-' * (self.width - filled)
        elapsed = time.time() - self._start
        if done > 0 and done < self.total:
            eta = elapsed / done * (self.total - done)
            eta_str = f'ETA {int(eta//60):02d}:{int(eta%60):02d}'
        elif done >= self.total:
            eta_str = f'{elapsed:.1f}s'
        else:
            eta_str = '--:--'
        line = f'\r  {self.label} [{bar}] {done}/{self.total} {eta_str}'
        sys.stdout.write(line)
        sys.stdout.flush()


# ─────────────────────────────────────────────────────────────────────────────
# LZS (STACpack) Encoder  — hash-chain O(n) average, O(n·k) worst case
# ─────────────────────────────────────────────────────────────────────────────

class LZSEncoder:
    """
    MSB-first bitstream LZS / STACpack compressor matching ScummVM's
    DecompressorLZS (engines/sci/resource/decompressor.cpp).

    Uses a hash-chain (3-byte key → most-recent position) for O(n) average
    performance instead of the O(n²) brute-force search, making it practical
    for large frames (640×480 = 307 200 bytes).
    """

    WINDOW   = 2047   # maximum back-reference distance
    MAX_MATCH = 255   # cap search depth for speed
    MIN_MATCH = 2

    def __init__(self):
        self._buf   = 0
        self._nbits = 0
        self._out   = bytearray()

    # ── Bit I/O ──────────────────────────────────────────────────────────────

    def _flush(self, force: bool = False):
        while self._nbits >= 8 or (force and self._nbits > 0):
            self._out.append((self._buf >> 24) & 0xFF)
            self._buf = (self._buf << 8) & 0xFFFFFFFF
            self._nbits -= 8

    def _put(self, value: int, nbits: int):
        self._buf |= (value & ((1 << nbits) - 1)) << (32 - nbits - self._nbits)
        self._nbits += nbits
        if self._nbits >= 8:
            self._flush()

    def _put_comp_len(self, clen: int):
        if clen == 2: self._put(0b00, 2); return
        if clen == 3: self._put(0b01, 2); return
        if clen == 4: self._put(0b10, 2); return
        self._put(0b11, 2)
        if clen == 5: self._put(0b00, 2); return
        if clen == 6: self._put(0b01, 2); return
        if clen == 7: self._put(0b10, 2); return
        self._put(0b11, 2)
        remaining = clen - 8
        while remaining >= 0xF:
            self._put(0xF, 4)
            remaining -= 0xF
        self._put(remaining, 4)

    # ── Compression ───────────────────────────────────────────────────────────

    def compress(self, data: bytes) -> bytes:
        """
        Compress `data` and return LZS-compressed bytes.

        Strategy: maintain a dict mapping each 3-byte key to the chain of
        recent positions where that key was seen (within WINDOW bytes).
        For each position we check the chain head (most recent occurrence)
        and extend the match greedily.
        """
        self._buf   = 0
        self._nbits = 0
        self._out   = bytearray()

        src = data
        n   = len(src)
        pos = 0

        # hash_head[key] = most recent position of that 3-byte sequence
        # hash_prev[pos] = previous position in chain for the same key
        hash_head = {}
        hash_prev = {}

        def _find_match(pos):
            """Return (best_offset, best_length) or (0, 0) if no useful match."""
            if pos + self.MIN_MATCH > n:
                return 0, 0
            # Build 3-byte key (or 2-byte if near end)
            key = src[pos:pos + 3] if pos + 3 <= n else src[pos:pos + 2]
            best_offs = 0
            best_len  = 0

            candidate = hash_head.get(key, -1)
            # Walk the chain (limit iterations to keep it fast)
            steps = 0
            while candidate >= 0 and steps < 32:
                offs = pos - candidate
                if offs > self.WINDOW:
                    break
                # Measure match length
                mlen = 0
                limit = min(n - pos, self.MAX_MATCH)
                while mlen < limit and src[candidate + mlen] == src[pos + mlen]:
                    mlen += 1
                if mlen > best_len:
                    best_len  = mlen
                    best_offs = offs
                    if mlen >= self.MAX_MATCH:
                        break
                candidate = hash_prev.get(candidate, -1)
                steps += 1

            return (best_offs, best_len) if best_len >= self.MIN_MATCH else (0, 0)

        def _add_to_hash(p):
            """Insert position p into the hash chain."""
            key = src[p:p + 3] if p + 3 <= n else src[p:p + 2]
            prev = hash_head.get(key, -1)
            # Expire entries that have left the window
            if prev >= 0 and pos - prev > self.WINDOW:
                prev = -1
            hash_prev[p] = prev
            hash_head[key] = p

        while pos < n:
            # Search BEFORE adding current position to hash.
            # Adding pos first would make _find_match find the current position
            # as a candidate with offset=0, which is the LZS end-of-stream
            # marker — causing the decompressor to stop immediately.
            best_offs, best_len = _find_match(pos)

            if best_len >= self.MIN_MATCH:
                self._put(1, 1)
                if best_offs <= 127:
                    self._put(1, 1)
                    self._put(best_offs, 7)
                else:
                    self._put(0, 1)
                    self._put(best_offs, 11)
                self._put_comp_len(best_len)
                # Add all positions covered by this match to the hash
                for k in range(best_len):
                    if pos + k < n:
                        _add_to_hash(pos + k)
                pos += best_len
            else:
                _add_to_hash(pos)
                self._put(0, 1)
                self._put(src[pos], 8)
                pos += 1

        # End-of-stream marker
        self._put(1, 1)
        self._put(1, 1)
        self._put(0, 7)
        self._flush(force=True)
        return bytes(self._out)


# ─────────────────────────────────────────────────────────────────────────────
# Sierra SOL DPCM-16 Encoder
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


def encode_dpcm16_block(samples_int16, carry_in: int = 0):
    """
    Encode a sequence of int16 samples as Sierra SOL DPCM-16.
    Returns (dpcm_bytes, carry_out).
    `carry_in` is the DPCM state at the start of this block.
    """
    out    = bytearray()
    sample = carry_in

    for s in samples_int16:
        delta = s - sample
        if delta >= 0:
            idx = bisect.bisect_right(_DPCM16_TABLE, delta) - 1
            idx = max(0, min(127, idx))
            out.append(idx)
            sample += _DPCM16_TABLE[idx]
        else:
            idx = bisect.bisect_right(_DPCM16_TABLE, -delta) - 1
            idx = max(0, min(127, idx))
            out.append(0x80 | idx)
            sample -= _DPCM16_TABLE[idx]

        # emulate x86 16-bit overflow
        if sample > 32767:
            sample -= 65536
        elif sample < -32768:
            sample += 65536

    return bytes(out), sample


# ─────────────────────────────────────────────────────────────────────────────
# SCI HunkPalette builder
# ─────────────────────────────────────────────────────────────────────────────

# kRawPaletteSize = 1200 bytes
# Layout (LE/SCI11ENDIAN):
#   [0-9]   : zeros
#   [10]    : numPalettes = 1
#   [11-12] : zeros (header tail)
#   [13-14] : zeros (slack)
#   [15]    : = 15  (offset to entry, written as a byte)
#   [16-36] : entry header (21 more bytes = positions 16-36)
#   But getPalPointer() = subspan(13 + 2*1) = subspan(15), and entry header starts at 15:
#   [15+0 .. 15+9]  = zeros
#   [15+10]         = startColor = 0
#   [15+11-13]      = zeros
#   [15+14-15]      = numColors = 256 (uint16 LE)
#   [15+16]         = used = 1
#   [15+17]         = sharedUsed = 0
#   [15+18-21]      = version = 1 (uint32 LE)
#   [37 ..]         = 256 × (used, r, g, b)   = 1024 bytes
#   [1061..]        = padding to 1200

def build_hunk_palette(colors):
    """
    Build a 1200-byte SCI HunkPalette from a list of 256 (R, G, B) tuples.
    """
    buf = bytearray(1200)

    # Main header
    buf[10] = 1                              # numPalettes = 1

    # palette offset stored at [15] (byte value = 15)
    buf[15] = 15

    # Entry header starts at offset 15:
    base = 15
    buf[base + 10] = 0                       # startColor = 0
    struct.pack_into('<H', buf, base + 14, 256)  # numColors = 256
    buf[base + 16] = 1                       # used = 1
    buf[base + 17] = 0                       # sharedUsed = 0
    struct.pack_into('<I', buf, base + 18, 1)    # version = 1

    # Palette data at offset 37 (= 15 + kEntryHeaderSize 22)
    pal_start = base + 22   # = 37
    for i, (r, g, b) in enumerate(colors):
        buf[pal_start + i * 4 + 0] = 1      # used flag
        buf[pal_start + i * 4 + 1] = r
        buf[pal_start + i * 4 + 2] = g
        buf[pal_start + i * 4 + 3] = b

    return bytes(buf)


# ─────────────────────────────────────────────────────────────────────────────
# Image helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_frames(frames_dir: str):
    """Return sorted list of image file paths from the directory."""
    IMAGE_EXTS = {'.png', '.bmp'}
    seen = set()
    files = []
    for entry in os.scandir(frames_dir):
        if not entry.is_file():
            continue
        if os.path.splitext(entry.name)[1].lower() in IMAGE_EXTS:
            norm = os.path.normcase(entry.path)   # case-fold on Windows
            if norm not in seen:
                seen.add(norm)
                files.append(entry.path)
    if not files:
        raise FileNotFoundError(f"No PNG/BMP files found in '{frames_dir}'")

    def sort_key(p):
        name = os.path.splitext(os.path.basename(p))[0]
        # Extract trailing number if present
        digits = ''.join(c for c in name if c.isdigit())
        return int(digits) if digits else name

    return sorted(files, key=sort_key)


def get_palette_from_image(img):
    """
    Return a list of exactly 256 (R,G,B) tuples from a Pillow Image.
    Handles palette images with fewer than 256 colours, None palettes,
    and RGB images (auto-quantized to 256 colours).
    """
    from PIL import Image

    def _raw_to_colors(raw):
        """Convert a flat R,G,B,... list (may be shorter than 768) to 256 tuples."""
        if not raw:
            return [(0, 0, 0)] * 256
        # Pad to at least 768 values with zeros
        raw = list(raw) + [0] * 768
        return [(raw[i*3], raw[i*3+1], raw[i*3+2]) for i in range(256)]

    def _getpalette(im):
        """Call getpalette() compatibly with Pillow < 9.1 and >= 9.1."""
        try:
            return im.getpalette('RGB')
        except TypeError:
            return im.getpalette()

    if img.mode == 'P':
        return _raw_to_colors(_getpalette(img))

    # For any non-palette mode: convert to RGB then quantize
    quantized = img.convert('RGB').quantize(256)
    return _raw_to_colors(_getpalette(quantized))


def image_to_indexed(img, palette_colors):
    """
    Convert a Pillow Image to an 8-bit indexed bytes object matching palette_colors.
    Handles P, RGB, RGBA, and any other mode.
    """
    from PIL import Image

    w, h = img.size

    if img.mode == 'P':
        # Already indexed — resize palette to exactly 256 entries and return pixels
        raw = img.tobytes()
        if len(raw) == w * h:
            return raw
        # Unexpected size; fall through to re-quantize

    # Flatten palette to a 768-byte list
    flat = []
    for r, g, b in palette_colors:
        flat += [r, g, b]
    flat = (flat + [0] * 768)[:768]

    # Convert to plain RGB (handles RGBA, L, etc.)
    img_rgb = img.convert('RGB')

    # Build a 1×1 palette reference image
    pal_img = Image.new('P', (1, 1))
    pal_img.putpalette(flat)

    result = img_rgb.quantize(palette=pal_img, dither=0)
    return bytes(result.tobytes())


# ─────────────────────────────────────────────────────────────────────────────
# Audio helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_audio_samples(wav_path: str, target_rate: int = 11025):
    """
    Load a WAV file and return (samples_int16_list, original_rate).
    The output is mono, resampled to target_rate.
    """
    with wave.open(wav_path, 'rb') as wf:
        nchannels   = wf.getnchannels()
        sampwidth   = wf.getsampwidth()
        framerate   = wf.getframerate()
        nframes     = wf.getnframes()
        raw         = wf.readframes(nframes)

    # Decode raw bytes to int16 list
    if sampwidth == 1:
        # 8-bit unsigned → 16-bit signed
        samples = [(b - 128) * 256 for b in raw]
    elif sampwidth == 2:
        samples = list(struct.unpack_from(f'<{len(raw)//2}h', raw))
    elif sampwidth == 3:
        samples = []
        for i in range(0, len(raw), 3):
            v = raw[i] | (raw[i+1] << 8) | (raw[i+2] << 16)
            if v & 0x800000:
                v -= 0x1000000
            samples.append(v >> 8)
    elif sampwidth == 4:
        samples32 = struct.unpack_from(f'<{len(raw)//4}i', raw)
        samples = [s >> 16 for s in samples32]
    else:
        raise ValueError(f"Unsupported sample width {sampwidth}")

    # Mix to mono
    if nchannels > 1:
        mono = []
        for i in range(0, len(samples), nchannels):
            mono.append(sum(samples[i:i+nchannels]) // nchannels)
        samples = mono

    # Resample to target_rate using nearest-neighbour (simple but fast)
    if framerate != target_rate:
        ratio   = framerate / target_rate
        out     = []
        pos     = 0.0
        n       = len(samples)
        while pos < n:
            out.append(samples[int(pos)])
            pos += ratio
        samples = out

    # Clamp to int16 range
    samples = [max(-32768, min(32767, int(s))) for s in samples]
    return samples


def build_audio_blocks(samples_11k, num_frames: int, fps: int):
    """
    Split audio into per-frame DPCM blocks.

    ScummVM's RobotAudioStream uses an EOS (every-other-sample) interleaving
    scheme.  The key parameters:
      audioRecordInterval = 22050 // fps   (loop-buffer position step per frame)
      effectivePerFrame   = audioRecordInterval // 2   (new samples written/frame)

    Every frame carries real audio.  Each frame's DPCM block overlaps with the
    previous one: the block is `audioRecordInterval` bytes long, but due to the
    _jointMin skip, only the last `effectivePerFrame` samples are actually new.
    Consecutive blocks are offset by `effectivePerFrame` samples in the source
    stream so that the decoded output is a gapless, continuous audio track.

    Layout:
      file_pos[i]   = evenPrimerSize*2 + i * audioRecordInterval
      block in file = 8-byte [abs_pos, body_size] header + DPCM body
      DPCM body     = 8 runway bytes + (audioRecordInterval+16) audio bytes
                    = audioRecordInterval+24 bytes total body
                    → audioBlockSize header field = audioRecordInterval+32 (e.g. 4442)

    Returns (blocks, audioBlockSize):
      blocks         – list of num_frames byte objects (8-byte header + DPCM body)
      audioBlockSize – total block size including header (stored in RBT file header)
    """
    runway_len            = 8
    audio_record_interval = 22050 // fps                # e.g. 4410
    # Sierra always writes 24 extra bytes past audioRecordInterval per block.
    # This matches _expectedAudioBlockSize = audioBlockSize - 8 in ScummVM.
    # Original: audioBlockSize = 4442 → _expectedAudioBlockSize = 4434 = 4410 + 24.
    expected_block_size   = audio_record_interval + 24  # e.g. 4434
    actual_per_block      = expected_block_size - runway_len   # e.g. 4426  (body only)
    audio_block_size      = expected_block_size + 8            # e.g. 4442  (+ file header)

    # New samples contributed to the loop buffer per frame (half audioRecordInterval,
    # due to the _jointMin overlap mechanism in RobotAudioStream::fillRobotBuffer).
    # The extra 24 bytes form an overlap tail reused by the next frame's skip.
    effective_per_frame = audio_record_interval // 2   # e.g. 2205

    file_pos_base = 19922 * 2   # evenPrimerSize * 2 = 39844

    blocks = []

    for frame_no in range(num_frames):
        # Loop-buffer position step is audioRecordInterval, not the block body size.
        file_pos = file_pos_base + frame_no * audio_record_interval

        if samples_11k:
            # Each frame gets effective_per_frame new samples plus a 24-sample
            # overlap tail that will be re-read (and skipped) by the next frame.
            start = frame_no * effective_per_frame
            end   = start + actual_per_block
            chunk = list(samples_11k[start:end])
            if len(chunk) < actual_per_block:
                chunk += [0] * (actual_per_block - len(chunk))
        else:
            chunk = [0] * actual_per_block

        # Build the runway: 8 copies of the first sample value so that the
        # DPCM decoder's carry state converges from 0 to the audio level before
        # the real samples begin.
        runway_val   = chunk[0] if chunk else 0
        full_samples = [runway_val] * runway_len + chunk   # runway + body

        dpcm_bytes, _ = encode_dpcm16_block(full_samples, carry_in=0)
        assert len(dpcm_bytes) == expected_block_size, \
            f"DPCM size mismatch: {len(dpcm_bytes)} != {expected_block_size}"

        block = (struct.pack('<i', file_pos) +
                 struct.pack('<i', expected_block_size) +
                 dpcm_bytes)
        blocks.append(block)

    return blocks, audio_block_size


# ─────────────────────────────────────────────────────────────────────────────
# Video frame encoder
# ─────────────────────────────────────────────────────────────────────────────

def encode_cel_uncompressed(pixels: bytes, width: int, height: int,
                             x: int = 0, y: int = 0):
    """
    Build a Robot v5/v6 cel packet (header + single uncompressed data chunk).
    NOTE: the cel header's data_size field is always uint16 — call
    encode_cel_lzs() instead when len(pixels) > ~65515.
    """
    chunk_data   = pixels
    comp_size    = len(chunk_data)
    decomp_size  = comp_size
    comp_type    = 2                   # uncompressed

    chunk_header = (struct.pack('<I', comp_size) +
                    struct.pack('<I', decomp_size) +
                    struct.pack('<H', comp_type))
    chunk        = chunk_header + chunk_data

    data_size    = len(chunk)          # 10 + pixel_count
    if data_size > 65535:
        raise ValueError(
            f"Uncompressed cel data_size {data_size} exceeds uint16 limit. "
            "Use --lzs flag or reduce the canvas size.")

    num_chunks   = 1
    v_scale      = 100

    cel_header = bytearray(22)
    cel_header[1]  = v_scale
    struct.pack_into('<H', cel_header, 2,  width)
    struct.pack_into('<H', cel_header, 4,  height)
    struct.pack_into('<H', cel_header, 10, x & 0xFFFF)
    struct.pack_into('<H', cel_header, 12, y & 0xFFFF)
    struct.pack_into('<H', cel_header, 14, data_size)
    struct.pack_into('<H', cel_header, 16, num_chunks)

    return bytes(cel_header) + chunk


def encode_cel_lzs(pixels: bytes, width: int, height: int,
                   x: int = 0, y: int = 0):
    """
    Build a Robot v5 cel packet using LZS compression.
    """
    enc          = LZSEncoder()
    compressed   = enc.compress(pixels)

    comp_size    = len(compressed)
    decomp_size  = len(pixels)          # = width * height
    comp_type    = 0                    # LZS

    chunk_header = (struct.pack('<I', comp_size) +
                    struct.pack('<I', decomp_size) +
                    struct.pack('<H', comp_type))
    chunk        = chunk_header + compressed

    data_size    = len(chunk)
    if data_size > 65535:
        raise ValueError(
            f"LZS-compressed cel data_size {data_size} still exceeds uint16 limit "
            f"(compressed {comp_size} from {len(pixels)} raw bytes). "
            "Try reducing the canvas size.")

    num_chunks   = 1
    v_scale      = 100

    cel_header   = bytearray(22)
    cel_header[1]  = v_scale
    struct.pack_into('<H', cel_header, 2,  width)
    struct.pack_into('<H', cel_header, 4,  height)
    struct.pack_into('<H', cel_header, 10, x & 0xFFFF)
    struct.pack_into('<H', cel_header, 12, y & 0xFFFF)
    struct.pack_into('<H', cel_header, 14, data_size)
    struct.pack_into('<H', cel_header, 16, num_chunks)

    return bytes(cel_header) + chunk


def encode_video_frame(pixels: bytes, width: int, height: int,
                       use_lzs: bool = False, x: int = 0, y: int = 0):
    """
    Build a complete Robot video frame blob (2-byte cel count + 1 cel).
    Returns bytes.
    """
    if use_lzs:
        cel_data = encode_cel_lzs(pixels, width, height, x, y)
    else:
        cel_data = encode_cel_uncompressed(pixels, width, height, x, y)

    num_cels = struct.pack('<H', 1)
    return num_cels + cel_data


# ─────────────────────────────────────────────────────────────────────────────
# Main encoder
# ─────────────────────────────────────────────────────────────────────────────

def encode_rbt(frames_dir: str, output_path: str, fps: int = 15,
               audio_path: str = None, palette_path: str = None,
               canvas_w: int = 0, canvas_h: int = 0,
               use_lzs: bool = False, force_v6: bool = False):
    """
    Encode a folder of frames (and optional audio) into a Robot .rbt file.
    """
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: Pillow is required: pip install Pillow")
        sys.exit(1)

    # ── Collect & validate frames ────────────────────────────────────────────
    frame_files = load_frames(frames_dir)
    num_frames  = len(frame_files)
    if num_frames == 0:
        raise ValueError("No frames found.")
    print(f"  Found {num_frames} frames in '{frames_dir}'")

    # ── Determine canvas size ────────────────────────────────────────────────
    first_img = Image.open(frame_files[0])   # keep original mode (may be 'P')
    if canvas_w == 0: canvas_w = first_img.width
    if canvas_h == 0: canvas_h = first_img.height
    print(f"  Canvas: {canvas_w}×{canvas_h}  fps: {fps}")

    # ── Build / load palette ─────────────────────────────────────────────────
    if palette_path:
        pal_img    = Image.open(palette_path)
        pal_colors = get_palette_from_image(pal_img)
    elif first_img.mode == 'P':
        # 8-bit paletted input (e.g. frames saved by parse_rbt.py):
        # use the embedded palette directly — no re-quantization needed.
        pal_colors = get_palette_from_image(first_img)
    else:
        # True-colour input: derive a palette by quantizing.
        pal_colors = get_palette_from_image(first_img.convert('RGB').quantize(256))
    print(f"  Palette: {len(pal_colors)} colours")

    hunk_pal = build_hunk_palette(pal_colors)   # 1200 bytes
    palette_size = len(hunk_pal)                 # 1200

    # ── Encode all video frames ──────────────────────────────────────────────
    raw_pixel_size   = canvas_w * canvas_h
    # The cel header's data_size field (bytes 14-15) is ALWAYS uint16 in the
    # Robot format.  If the uncompressed chunk (10-byte chunk header + raw pixels)
    # exceeds 65535, LZS compression is mandatory.
    uncompressed_chunk = 10 + raw_pixel_size
    if uncompressed_chunk > 65535:
        if not use_lzs:
            print(f"  Frame size {raw_pixel_size} px exceeds uint16 limit — "
                  f"LZS compression auto-enabled.")
        use_lzs = True

    # v6 is forced if the user requested it; otherwise we start with v5 and
    # upgrade AFTER compression once we know the real per-frame sizes.
    version = 6 if force_v6 else 5
    print(f"  Robot version: v{version} (tentative)  "
          f"compression: {'LZS' if use_lzs else 'none'}")

    encoded_videos = []
    pbar = ProgressBar(num_frames, label='Encoding frames')
    for fpath in frame_files:
        img = Image.open(fpath)
        if img.size != (canvas_w, canvas_h):
            # Paletted images must be converted to RGB before a quality resize
            # (LANCZOS on mode 'P' produces garbage — it interpolates indices).
            if img.mode == 'P':
                img = img.convert('RGB')
            img = img.resize((canvas_w, canvas_h), Image.LANCZOS)
        pixels = image_to_indexed(img, pal_colors)
        vid    = encode_video_frame(pixels, canvas_w, canvas_h, use_lzs)
        encoded_videos.append(vid)
        pbar.step()
    pbar.finish()

    video_sizes  = [len(v) for v in encoded_videos]

    # ── Encode audio ─────────────────────────────────────────────────────────
    has_audio = False
    audio_blocks = []
    audio_block_size = 0
    samples_per_block = 0

    if audio_path:
        if 22050 % fps != 0:
            print(f"  WARNING: {fps} fps does not evenly divide 22050. "
                  f"Audio sync may drift slightly.")
        print(f"  Loading audio from '{audio_path}' ...")
        samples_11k = load_audio_samples(audio_path, target_rate=11025)
        print(f"  Audio: {len(samples_11k)} samples at 11025 Hz "
              f"({len(samples_11k)/11025:.1f}s)")
        audio_blocks, audio_block_size = build_audio_blocks(samples_11k, num_frames, fps)
        has_audio = True
        print(f"  Audio encoded: {len(audio_blocks)} blocks × {audio_block_size} bytes")

    # ── Build packet sizes ───────────────────────────────────────────────────
    packet_sizes = []
    for vs in video_sizes:
        ps = vs + (audio_block_size if has_audio else 0)
        packet_sizes.append(ps)

    # Determine final version: upgrade to v6 only if actual compressed sizes
    # exceed uint16 (LZS often brings 640×480 frames well under 65535).
    if version == 5:
        max_vs = max(video_sizes) if video_sizes else 0
        max_ps = max(packet_sizes) if packet_sizes else 0
        if max_vs > 65535 or max_ps > 65535:
            print(f"  Auto-upgrading to v6 (max video={max_vs}, max packet={max_ps})")
            version = 6
    print(f"  Robot version: v{version}  (final)")

    # ── Write file ───────────────────────────────────────────────────────────
    print(f"  Writing '{output_path}' ...")
    out = bytearray()

    # — Preamble: 0x16, unused, 'SOL\0' —
    out += bytes([0x16, 0x00])
    out += b'SOL\x00'

    # — File header (starts at offset 6) —
    primer_reserved_size  = 0
    primer_zero_compress  = 1 if has_audio else 0
    # Original Sierra RBT files store 0×0 for x_res/y_res; ScummVM ignores this
    # field and uses the per-cel dimensions from the frame data instead.
    x_res = 0
    y_res = 0
    # is_hi_res: 1 for hi-res (SCI2+) games; canvas_w >= 320 matches originals.
    is_hi_res = 1 if canvas_w >= 320 else 0
    # maxSkippable: Sierra formula — audio_block_size / (audioRecordInterval/4) - 1
    # For fps=5: 22050//5//4 = 1102; 4418//1102 - 1 = 3 (matches original).
    quarter_interval = max(1, (22050 // fps) // 4) if fps > 0 else 1
    max_skippable = max(0, (audio_block_size // quarter_interval) - 1) if has_audio else 0

    out += struct.pack('<H', version)
    out += struct.pack('<H', audio_block_size)
    out += struct.pack('<h', primer_zero_compress)
    out += bytes(2)                         # unused
    out += struct.pack('<H', num_frames)
    out += struct.pack('<H', palette_size)
    out += struct.pack('<H', primer_reserved_size)
    out += struct.pack('<h', x_res)
    out += struct.pack('<h', y_res)
    out += bytes([1])                        # has_palette = 1
    out += bytes([1 if has_audio else 0])   # has_audio
    out += bytes(2)                          # unused
    out += struct.pack('<h', fps)            # frame_rate
    out += struct.pack('<h', is_hi_res)
    out += struct.pack('<h', max_skippable)
    out += struct.pack('<h', 1)             # max_cels_per_frame = 1
    # max_cel_area × 4 (4 × sint32)
    cel_area = canvas_w * canvas_h
    for _ in range(4):
        out += struct.pack('<i', cel_area)
    out += bytes(8)                          # reserved

    # Assert: we're now at byte 60 (= 6 + 54 bytes of header)
    assert len(out) == 60, f"Header size mismatch: {len(out)}"

    # — No primer audio in file (using zero-compress flag) —

    # — Palette —
    out += hunk_pal                          # 1200 bytes

    # — Video frame size index —
    if version == 5:
        for vs in video_sizes:
            out += struct.pack('<H', vs)
    else:
        for vs in video_sizes:
            out += struct.pack('<i', vs)

    # — Packet size index —
    if version == 5:
        for ps in packet_sizes:
            out += struct.pack('<H', ps)
    else:
        for ps in packet_sizes:
            out += struct.pack('<i', ps)

    # — Cue times (256 × sint32, all -1 = inactive) —
    for _ in range(256):
        out += struct.pack('<i', -1)

    # — Cue values (256 × uint16, all 0) —
    for _ in range(256):
        out += struct.pack('<H', 0)

    # — Align to 2048-byte boundary —
    rem = len(out) % 2048
    if rem:
        out += bytes(2048 - rem)

    # — Frame data —
    for i in range(num_frames):
        out += encoded_videos[i]
        if has_audio:
            out += audio_blocks[i]

        if (i + 1) % 100 == 0:
            print(f"    Written {i+1}/{num_frames} frames ...")

    # — Write to disk —
    with open(output_path, 'wb') as f:
        f.write(out)

    size_mb = len(out) / 1024 / 1024
    print(f"  Done. {output_path} written ({size_mb:.1f} MB, "
          f"{num_frames} frames, {fps} fps).")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='Encode a folder of frames (+ optional audio) into a Sierra Robot .rbt file')
    ap.add_argument('frames_dir',
                    help='Directory containing numbered frame images (PNG/BMP)')
    ap.add_argument('output_rbt',
                    help='Output .rbt file path')
    ap.add_argument('--fps', type=int, default=15,
                    help='Frame rate in fps (default: 15). For audio, must divide 11025.')
    ap.add_argument('--audio', '-a', default=None,
                    help='WAV audio file (mono/stereo, any sample rate)')
    ap.add_argument('--palette', '-p', default=None,
                    help='Image file to take palette from (256-colour)')
    ap.add_argument('--canvas-width',  type=int, default=0,
                    help='Canvas width  (default: from first frame)')
    ap.add_argument('--canvas-height', type=int, default=0,
                    help='Canvas height (default: from first frame)')
    ap.add_argument('--match-rbt', default=None,
                    help='Original .rbt file: copy its cel dimensions (width × height) '
                         'so ScummVM renders the output identically to the original. '
                         'Overrides --canvas-width / --canvas-height.')
    ap.add_argument('--lzs', action='store_true',
                    help='Compress video with LZS (smaller file, slower encode)')
    ap.add_argument('--v6', action='store_true',
                    help='Force v6 format (needed for frames > ~64KB uncompressed)')
    args = ap.parse_args()

    canvas_w = args.canvas_width
    canvas_h = args.canvas_height

    # --match-rbt: read dimensions from the original RBT's first cel
    if args.match_rbt:
        try:
            import parse_rbt as _pr
            _hdr, _pal, _frames, *_ = _pr.parse_rbt(args.match_rbt, verbose=False)
            if _frames and _frames[0].cels:
                ref_cel = _frames[0].cels[0]
                canvas_w = ref_cel.width
                canvas_h = ref_cel.height
                print(f"  Matched original RBT dimensions: {canvas_w}×{canvas_h} "
                      f"(from {os.path.basename(args.match_rbt)})")
            else:
                print("  WARNING: --match-rbt: could not read first cel; "
                      "using frame dimensions instead.")
        except Exception as e:
            print(f"  WARNING: --match-rbt failed ({e}); using frame dimensions.")

    # Auto-find audio in the frames dir if not specified
    audio = args.audio
    if audio is None:
        for ext in ('*.wav', '*.WAV'):
            found = glob.glob(os.path.join(args.frames_dir, ext))
            if found:
                audio = found[0]
                print(f"  Auto-detected audio: {os.path.basename(audio)}")
                break

    encode_rbt(
        frames_dir   = args.frames_dir,
        output_path  = args.output_rbt,
        fps          = args.fps,
        audio_path   = audio,
        palette_path = args.palette,
        canvas_w     = canvas_w,
        canvas_h     = canvas_h,
        use_lzs      = args.lzs,
        force_v6     = args.v6,
    )


if __name__ == '__main__':
    main()
