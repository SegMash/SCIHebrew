"""
play_rbt.py – Sierra Robot (.rbt) video player

Plays an RBT file directly, replicating how ScummVM renders it:
  • 8-bit palettised frames composited from per-frame cels
  • Sierra SOL DPCM-16 audio decoded to PCM and played via pygame.mixer

Usage:
    python play_rbt.py <file.rbt> [options]

Options:
    --scale N          Window scale factor (default: 1.0)
    --no-audio         Disable audio playback
    --canvas-width  W  Override canvas width  (default: from file header)
    --canvas-height H  Override canvas height (default: from file header)

Controls:
    Space            Pause / Resume
    Left / Right     Step one frame (while paused)
    R                Restart from frame 0
    Q / Escape       Quit

Dependencies:
    pip install pygame Pillow
"""

import sys
import os
import argparse
import array as _array

try:
    import pygame
except ImportError:
    sys.exit("pygame is required:  pip install pygame")

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")

# Reuse the parser from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from parse_rbt import parse_rbt, deDPCM16, deDPCM16_carry
except ImportError:
    sys.exit("parse_rbt.py not found – it must be in the same directory as play_rbt.py")


# ─────────────────────────────────────────────────────────────────────────────
# Audio helpers
# ─────────────────────────────────────────────────────────────────────────────

def adapt_pcm(pcm: bytes, src_rate: int, dst_rate: int, dst_channels: int) -> bytes:
    """
    Adapt raw mono 16-bit LE PCM (at src_rate Hz) to the mixer's actual
    settings (dst_rate Hz, dst_channels channels).

    Uses numpy when available (fast); falls back to a pure-Python path.
    Windows audio drivers frequently reject 11025 Hz mono and silently fall
    back to a different rate or stereo; this function compensates so the
    audio plays at the correct pitch and in both speakers.
    """
    try:
        import numpy as np
        samples = np.frombuffer(pcm, dtype='<i2').copy()   # int16 LE
        if dst_rate != src_rate:
            n_out   = int(len(samples) * dst_rate / src_rate)
            indices = np.clip(
                (np.arange(n_out) * src_rate / dst_rate).astype(np.int64),
                0, len(samples) - 1)
            samples = samples[indices]
        if dst_channels == 2:
            samples = np.repeat(samples[:, np.newaxis], 2, axis=1).flatten()
        return samples.astype('<i2').tobytes()
    except ImportError:
        pass

    # ── Pure-Python fallback ──────────────────────────────────────────────
    samples = _array.array('h', pcm)
    if dst_rate != src_rate:
        n_out     = int(len(samples) * dst_rate / src_rate)
        ratio     = src_rate / dst_rate
        resampled = _array.array('h', [0] * n_out)
        for i in range(n_out):
            resampled[i] = samples[min(int(i * ratio), len(samples) - 1)]
        samples = resampled
    if dst_channels == 2:
        stereo = _array.array('h', [0] * (len(samples) * 2))
        for i, s in enumerate(samples):
            stereo[i * 2]     = s
            stereo[i * 2 + 1] = s
        samples = stereo
    return samples.tobytes()


def build_pcm(frames) -> bytes:
    """
    Decode the EVEN-channel audio frames into one continuous 11025 Hz mono
    16-bit PCM buffer.

    ScummVM's RobotAudioStream uses an EOS (every-other-sample) interleaving
    scheme with two sub-channels determined by audio_position % 4:
        audio_position % 4 == 0  →  even channel (DPCM-decoded samples written here)
        audio_position % 4 == 2  →  odd  channel (interpolated by ScummVM at playback)

    In both the original Sierra files and files produced by encode_rbt.py, every
    frame's audio_position is a multiple of 4 (audio_position % 4 == 0), meaning
    all frames are even-channel packets.  The odd-channel positions are never
    written; ScummVM fills them by interpolation.

    Because consecutive frames overlap in the loop buffer (the RobotAudioStream
    _jointMin mechanism), each frame's DPCM body covers a range that includes
    the previous frame's tail.  The non-overlapping new content per frame is
    exactly half the block size.  Even-numbered frames (by frame index, not
    audio_position parity) have non-overlapping bodies when extracted directly,
    so decoding them yields the full audio track.

    Concretely for 912.RBT (76 frames, 5 fps):
        38 even frames × 4426 body bytes = 168,188 samples / 11025 Hz = 15.26 s ✓

    Each packet starts with an 8-byte DPCM runway.  ScummVM decodes each packet
    independently from carry=0, relying on the runway to restore the accumulator
    to the correct level.  We must do the same.
    """
    out = bytearray()
    for fr in frames:
        raw = fr.audio_raw
        if not raw or len(raw) <= 8:
            continue
        # Skip odd-indexed frames (audio_position % 4 == 2).
        # These frames' audio overlaps with adjacent even-indexed frames and
        # is not needed for a faithful mono reconstruction.
        if fr.audio_position % 4 == 2:
            continue
        # Process the 8-byte runway from carry=0 to establish the correct
        # initial DPCM accumulator state, then decode the body from there.
        _, carry = deDPCM16_carry(raw[:8], 0)
        pcm, _  = deDPCM16_carry(raw[8:], carry)
        out += pcm
    return bytes(out)



# ─────────────────────────────────────────────────────────────────────────────
# Frame rendering helpers
# ─────────────────────────────────────────────────────────────────────────────

def composite_frame(frame, flat_pal: list, canvas_w: int, canvas_h: int) -> pygame.Surface:
    """
    Composite all cels of `frame` onto a PIL canvas using `flat_pal` (768-element
    flat RGB list), then return a pygame.Surface suitable for blitting.
    """
    canvas = Image.new('P', (canvas_w, canvas_h), 0)
    canvas.putpalette(flat_pal)

    for cel in frame.cels:
        if not cel.pixels or cel.width <= 0 or cel.height <= 0:
            continue
        needed = cel.width * cel.height
        pix    = cel.pixels[:needed].ljust(needed, b'\x00')
        cel_img = Image.frombytes('P', (cel.width, cel.height), pix)
        cel_img.putpalette(flat_pal)
        x = max(0, cel.x)
        y = max(0, cel.y)
        if x < canvas_w and y < canvas_h:
            canvas.paste(cel_img, (x, y))

    rgb_bytes = canvas.convert('RGB').tobytes()
    return pygame.image.frombuffer(rgb_bytes, (canvas_w, canvas_h), 'RGB').convert()


# ─────────────────────────────────────────────────────────────────────────────
# OSD (on-screen display)
# ─────────────────────────────────────────────────────────────────────────────

def draw_osd(screen, font, frame_no: int, num_frames: int, fps: int, paused: bool, speed: float):
    state  = '[PAUSED]' if paused else f'{fps} fps'
    spd    = f'  {speed:.2g}×' if speed != 1.0 else ''
    label  = f'  Frame {frame_no + 1}/{num_frames}  {state}{spd}  Space=mark  P=pause  [/]=speed  '
    text   = font.render(label, True, (255, 255, 0))
    shadow = font.render(label, True, (0, 0, 0))
    screen.blit(shadow, (5, 5))
    screen.blit(text,   (4, 4))


# ─────────────────────────────────────────────────────────────────────────────
# Main player
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='Play a Sierra Robot (.rbt) video file.')
    ap.add_argument('rbt_file',
                    help='Path to the .rbt file')
    ap.add_argument('--scale', type=float, default=1.0,
                    help='Window scale factor (default: 1.0)')
    ap.add_argument('--no-audio', action='store_true',
                    help='Disable audio playback')
    ap.add_argument('--canvas-width',  type=int, default=0,
                    help='Override canvas width (default: from file)')
    ap.add_argument('--canvas-height', type=int, default=0,
                    help='Override canvas height (default: from file)')
    ap.add_argument('--speed', type=float, default=1.0,
                    help='Playback speed multiplier (default: 1.0, e.g. 0.5=half, 2.0=double)')
    ap.add_argument('--subtitle', action='store_true',
                    help='Enable subtitle cue recording and write <rbt>.txt')
    args = ap.parse_args()

    # ── Parse RBT ─────────────────────────────────────────────────────────────
    print(f'Loading {args.rbt_file} ...')
    hdr, palette, frames, _, _, _ = parse_rbt(args.rbt_file, verbose=True)

    if not frames:
        sys.exit('No frames found in the RBT file.')

    fps      = hdr.frame_rate or 15
    canvas_w = args.canvas_width  or (hdr.x_res  if hdr.x_res  > 0 else 640)
    canvas_h = args.canvas_height or (hdr.y_res  if hdr.y_res  > 0 else 480)
    num_frames = len(frames)

    # Build flat 768-byte palette list for PIL
    if palette:
        flat_pal = []
        for r, g, b in palette:
            flat_pal += [r, g, b]
        flat_pal += [0] * max(0, 768 - len(flat_pal))
    else:
        # Greyscale fallback
        flat_pal = [v for v in range(256) for _ in range(3)]

    frame_ms = 1000.0 / fps   # base ms-per-frame at 1× speed

    # ── Decode audio ──────────────────────────────────────────────────────────
    pcm = b''
    if hdr.has_audio and not args.no_audio:
        print('Decoding audio ...')
        pcm = build_pcm(frames)
        if pcm:
            # len(pcm) is output bytes from deDPCM16; each int16 sample = 2 bytes
            n_samples = len(pcm) // 2
            dur = n_samples / 11025
            print(f'  Audio: {n_samples} samples @ 11025 Hz  ({dur:.1f} s)')

    # ── Initialize pygame ─────────────────────────────────────────────────────
    # pre_init MUST come before pygame.init(); otherwise pygame.init() starts
    # the mixer with its 44100 Hz stereo default and pre_init has no effect.
    # RBT audio: two interleaved 11025 Hz channels (even/odd). Only even-channel
    # frames (audio_position % 4 == 0) carry real voice; 168,188 samples / 11025 Hz
    # = 15.26 s → matches 76 frames @ 5 fps = 15.2 s.
    if pcm:
        pygame.mixer.pre_init(frequency=11025, size=-16, channels=1, buffer=512)

    pygame.init()

    actual_freq, actual_size, actual_ch = 11025, -16, 1
    audio_sound = None
    if pcm:
        try:
            actual_freq, actual_size, actual_ch = pygame.mixer.get_init()
            print(f'  Mixer: {actual_freq} Hz  {abs(actual_size)}-bit  '
                  f'{"stereo" if actual_ch == 2 else "mono"}')

            audio_pcm = adapt_pcm(pcm, src_rate=11025,
                                  dst_rate=actual_freq, dst_channels=actual_ch)
            audio_sound = pygame.mixer.Sound(buffer=audio_pcm)
        except pygame.error as e:
            print(f'  WARNING: audio init failed ({e}); continuing without audio')
            audio_sound = None

    def make_audio_sound(from_frame: int, spd: float):
        """
        Build a pygame Sound starting at the audio position for from_frame,
        resampled to play at spd× speed (with proportional pitch change).

        Trick: tell adapt_pcm the source rate is 11025*spd.  The resampler
        then produces N/spd output samples, which pygame plays at actual_freq
        → the audio lasts (original duration)/spd seconds, matching the video.
        """
        if not pcm:
            return None
        sample_offset = max(0, int(from_frame / fps * 11025))
        pcm_slice = pcm[sample_offset * 2:]
        if not pcm_slice:
            return None
        try:
            adapted = adapt_pcm(pcm_slice,
                                src_rate=max(1, int(11025 * spd)),
                                dst_rate=actual_freq,
                                dst_channels=actual_ch)
            return pygame.mixer.Sound(buffer=adapted)
        except pygame.error:
            return None

    disp_w = max(1, int(canvas_w * args.scale))
    disp_h = max(1, int(canvas_h * args.scale))
    screen  = pygame.display.set_mode((disp_w, disp_h))
    pygame.display.set_caption(
        f'RBT Player – {os.path.basename(args.rbt_file)}'
        f'  ({canvas_w}×{canvas_h}  {fps} fps)')
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont('monospace', 14)

    # ── Pre-render all frames ─────────────────────────────────────────────────
    # Composite every frame to a pygame Surface once so the playback loop only
    # needs a fast blit rather than per-frame PIL work.
    print(f'Pre-rendering {num_frames} frames ...')
    surfaces = []
    bar_width = 40
    for i, fr in enumerate(frames):
        surf = composite_frame(fr, flat_pal, canvas_w, canvas_h)
        if args.scale != 1.0:
            surf = pygame.transform.smoothscale(surf, (disp_w, disp_h))
        surfaces.append(surf)
        # Simple terminal progress bar
        done = int(bar_width * (i + 1) / num_frames)
        bar  = '#' * done + '-' * (bar_width - done)
        print(f'\r  [{bar}] {i + 1}/{num_frames}', end='', flush=True)
    print()   # newline after progress bar

    print(f'\nPlaying {num_frames} frames @ {fps} fps  ({canvas_w}×{canvas_h})  speed={args.speed}×')
    print('Controls:  Space=mark   P=pause   [/]=speed   Left/Right=step   R=restart   Q/Esc=quit\n')

    # ── Subtitle cue file ─────────────────────────────────────────────────────
    cue_path = os.path.splitext(args.rbt_file)[0] + '.txt'
    cue_file = None
    if args.subtitle:
        cue_file = open(cue_path, 'w', encoding='utf-8')
        print(f'Cue file: {cue_path}  (frame numbers written on each Space press)')
    else:
        print('Cue recording disabled (use --subtitle to create subtitle cue file).')

    # ── Playback state ─────────────────────────────────────────────────────────
    current_frame  = 0
    paused         = False
    speed          = max(0.1, args.speed)
    play_start_ms  = pygame.time.get_ticks()   # ticks when frame 0 was shown
    audio_channel  = None
    cur_audio_sound = make_audio_sound(0, speed)  # speed-adjusted sound from frame 0

    def effective_frame_ms():
        return frame_ms / speed

    def audio_play_from(frame_no: int):
        """Start (or restart) audio from frame_no at the current speed."""
        nonlocal audio_channel, cur_audio_sound
        if audio_channel:
            try:
                audio_channel.stop()
            except Exception:
                pass
        cur_audio_sound = make_audio_sound(frame_no, speed)
        if cur_audio_sound:
            audio_channel = cur_audio_sound.play()

    def audio_pause():
        if audio_channel:
            try:
                audio_channel.pause()
            except Exception:
                pass

    def audio_unpause():
        if audio_channel:
            try:
                audio_channel.unpause()
            except Exception:
                pass

    def audio_stop():
        if audio_channel:
            try:
                audio_channel.stop()
            except Exception:
                pass

    def restart():
        nonlocal current_frame, paused, play_start_ms
        current_frame = 0
        paused        = False
        play_start_ms = pygame.time.get_ticks()
        audio_play_from(0)

    def set_speed(new_speed):
        """Change speed and resample audio from the current frame position."""
        nonlocal speed, play_start_ms
        speed = max(0.1, min(8.0, round(new_speed, 2)))
        play_start_ms = pygame.time.get_ticks() - int(current_frame * effective_frame_ms())
        if not paused:
            audio_play_from(current_frame)
        print(f'  Speed: {speed}×')

    audio_play_from(0)

    running = True
    while running:

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                key = event.key

                if key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

                elif key == pygame.K_SPACE:
                    # Write current frame number to cue file only when recording is enabled.
                    if cue_file:
                        cue_file.write(f'{current_frame}\n')
                        cue_file.flush()
                        print(f'  Marked frame {current_frame}')
                    else:
                        print('  Cue recording is disabled (run with --subtitle).')

                elif key == pygame.K_p:
                    paused = not paused
                    if paused:
                        audio_pause()
                    else:
                        # Recalculate the logical start time so elapsed → current frame
                        play_start_ms = pygame.time.get_ticks() - int(current_frame * effective_frame_ms())
                        audio_unpause()

                elif key == pygame.K_LEFTBRACKET:
                    set_speed(speed - 0.25)

                elif key == pygame.K_RIGHTBRACKET:
                    set_speed(speed + 0.25)

                elif key == pygame.K_LEFT and paused:
                    current_frame = max(0, current_frame - 1)

                elif key == pygame.K_RIGHT and paused:
                    current_frame = min(num_frames - 1, current_frame + 1)

                elif key == pygame.K_r:
                    restart()

        if not running:
            break

        # ── Advance frame on wall-clock ────────────────────────────────────────
        if not paused:
            elapsed_ms    = pygame.time.get_ticks() - play_start_ms
            fms           = effective_frame_ms()
            current_frame = min(int(elapsed_ms / fms), num_frames - 1)
            if elapsed_ms >= num_frames * fms:
                # Reached the end — hold last frame
                paused = True
                audio_stop()
                current_frame = num_frames - 1

        # ── Display ───────────────────────────────────────────────────────────
        screen.blit(surfaces[current_frame], (0, 0))
        draw_osd(screen, font, current_frame, num_frames, fps, paused, speed)
        pygame.display.flip()

        # Sleep until the next frame boundary (or a short poll while paused)
        if not paused:
            clock.tick(fps * speed + 5)   # safety cap; real throttle via wall-clock above
        else:
            clock.tick(30)

    audio_stop()
    if cue_file:
        cue_file.close()
    pygame.quit()


if __name__ == '__main__':
    main()
