import argparse
import re
import struct
from pathlib import Path

from PIL import Image


FRAME_LINE_RE = re.compile(r"^\s*(\d+)\s*\|(.*)$")
FRAME_FILE_RE = re.compile(r"(\d+)")


def parse_sci_font(font_path: Path):
    """Return (glyphs, line_height) where glyphs maps char_index -> (width, height, bitmap_bytes)."""
    glyphs = {}
    with font_path.open("rb") as f:
        _reserved = struct.unpack("<I", f.read(4))[0]
        num_chars = struct.unpack("<H", f.read(2))[0]
        line_height = struct.unpack("<H", f.read(2))[0]

        pointers = [struct.unpack("<H", f.read(2))[0] for _ in range(num_chars)]

        for char_index, ptr in enumerate(pointers):
            addr = ptr + 2
            f.seek(addr)
            width_b = f.read(1)
            height_b = f.read(1)
            if len(width_b) < 1 or len(height_b) < 1:
                continue
            width = width_b[0]
            height = height_b[0]
            if width == 0 or height == 0:
                continue

            bytes_per_row = (width + 7) // 8
            size = bytes_per_row * height
            bitmap = f.read(size)
            if len(bitmap) != size:
                continue
            glyphs[char_index] = (width, height, bitmap)

    return glyphs, line_height


def cp1255_index_for_char(ch: str):
    try:
        b = ch.encode("cp1255")
    except UnicodeEncodeError:
        return None
    if not b:
        return None
    return b[0]


def text_glyphs_and_width(text: str, glyphs):
    """Return list[(char_index, glyph, glyph_width)] and total width in pixels."""
    out = []
    total_width = 0
    for ch in text:
        char_index = cp1255_index_for_char(ch)
        if char_index is None:
            continue
        glyph = glyphs.get(char_index)
        if glyph is None:
            continue
        glyph_width = glyph[0]
        out.append((char_index, glyph, glyph_width))
        total_width += glyph_width
    return out, total_width


def draw_glyph(img: Image.Image, glyph, x_position: int, y_position: int, color_index: int = 255):
    width, height, bitmap = glyph
    bytes_per_row = (width + 7) // 8
    for y in range(height):
        for x in range(width):
            byte_index = y * bytes_per_row + (x // 8)
            bit_index = 7 - (x % 8)
            bit = (bitmap[byte_index] >> bit_index) & 1
            if bit:
                target_x = x_position + x
                target_y = y_position + y
                if 0 <= target_x < img.width and 0 <= target_y < img.height:
                    img.putpixel((target_x, target_y), color_index)


def build_frame_map(frames_dir: Path):
    """Return frame_number -> source image path."""
    frame_map = {}
    for p in sorted(frames_dir.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".png", ".bmp", ".jpg", ".jpeg", ".webp"}:
            continue
        m = FRAME_FILE_RE.search(p.stem)
        if not m:
            continue
        n = int(m.group(1))
        frame_map[n] = p
    return frame_map


def parse_subtitle_markers(path: Path):
    markers = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()
        if not stripped:
            continue
        m = FRAME_LINE_RE.match(raw)
        if not m:
            continue
        frame = int(m.group(1))
        text = m.group(2).strip()
        markers.append((frame, text, line_no))

    if not markers:
        raise ValueError(f"No valid '<frame>|<text>' lines found in {path}")

    markers.sort(key=lambda t: t[0])
    return markers


def find_max_frame_from_dir(frames_dir: Path):
    if not frames_dir.exists() or not frames_dir.is_dir():
        raise ValueError(f"Frames directory not found: {frames_dir}")

    max_frame = None
    for p in frames_dir.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".png", ".bmp", ".jpg", ".jpeg", ".webp"}:
            continue
        m = FRAME_FILE_RE.search(p.stem)
        if not m:
            continue
        n = int(m.group(1))
        if max_frame is None or n > max_frame:
            max_frame = n

    if max_frame is None:
        raise ValueError(f"Could not detect frame numbers in {frames_dir}")

    return max_frame


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Dry-run subtitle timeline: print 'frame <x>: inject <text>' per frame.",
    )
    parser.add_argument("subtitles", help="Path to subtitle marker file (e.g. 91.txt)")
    parser.add_argument(
        "--frames-dir",
        required=True,
        help="Frames folder to infer max frame number from file names",
    )
    parser.add_argument(
        "--font",
        required=True,
        help="Path to font file (validated only in dry-run)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        help="Directory for edited frames (created if missing)",
    )
    parser.add_argument(
        "--y-position",
        type=int,
        required=True,
        help="Vertical position for drawing the glyph at x=0",
    )
    parser.add_argument("--max-frame", type=int, help="Explicit last frame index (inclusive)")
    parser.add_argument("--from-frame", type=int, default=0, help="Only print from this frame")
    parser.add_argument("--to-frame", type=int, help="Only print up to this frame (inclusive)")
    parser.add_argument(
        "--frame-offset",
        type=int,
        default=0,
        help="Add this signed offset to each subtitle marker frame number",
    )
    args = parser.parse_args()

    subtitles_path = Path(args.subtitles)
    frames_dir = Path(args.frames_dir)
    font_path = Path(args.font)
    if not font_path.exists() or not font_path.is_file():
        raise ValueError(f"Font file not found: {font_path}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    glyphs, line_height = parse_sci_font(font_path)
    frame_map = build_frame_map(frames_dir)
    if not frame_map:
        raise ValueError(f"Could not detect frame files in {frames_dir}")

    markers = parse_subtitle_markers(subtitles_path)
    if args.frame_offset:
        markers = sorted(
            ((frame + args.frame_offset, text, line_no) for frame, text, line_no in markers),
            key=lambda item: item[0],
        )

    timeline_end = find_max_frame_from_dir(frames_dir)

    if args.to_frame is not None:
        timeline_end = min(timeline_end, args.to_frame)

    start_print = max(0, args.from_frame)
    paint_color_index = None

    def process_frame(frame_num: int, text: str):
        nonlocal paint_color_index
        src = frame_map.get(frame_num)
        if src is None:
            return

        with Image.open(src) as img:
            out = img.copy()

            if paint_color_index is None:
                pal = out.getpalette()
                if pal is None:
                    paint_color_index = 255
                    print(f"frame {frame_num}: palette=None, fallback paint color index={paint_color_index}")
                else:
                    triples = [tuple(pal[i:i + 3]) for i in range(0, min(len(pal), 256 * 3), 3)]
                    most_white_index, most_white_rgb = min(
                        enumerate(triples),
                        key=lambda item: sum((255 - channel) ** 2 for channel in item[1]),
                    )
                    paint_color_index = most_white_index
                    print(f"frame {frame_num}: using most white index={most_white_index} rgb={most_white_rgb}")

            if text:
                split_lines = text.split("#")
                base_y = args.y_position
                max_width = int((out.width / 2) * 0.8)

                for line_index, raw_line in enumerate(split_lines):
                    line_text = raw_line.strip()
                    if not line_text:
                        continue

                    glyph_items, text_width = text_glyphs_and_width(line_text, glyphs)
                    if not glyph_items:
                        continue

                    if text_width > max_width:
                        raise ValueError(
                            f"frame {frame_num}: subtitle line too wide ({text_width}px) > max ({max_width}px): {line_text}"
                        )

                    first_char_index, first_glyph, first_width = glyph_items[0]
                    first_x = int((out.width * 0.05) + max_width - ((max_width - text_width) / 2) - first_width)
                    line_y = base_y + line_index * line_height
                    print(
                        f"frame {frame_num}: line {line_index} first char index={first_char_index}, "
                        f"text width={text_width}px, max width={max_width}px, first x={first_x}, y={line_y}"
                    )

                    # Draw first letter at computed x, then continue right-to-left.
                    draw_glyph(
                        out,
                        first_glyph,
                        x_position=first_x,
                        y_position=line_y,
                        color_index=paint_color_index,
                    )

                    cursor_x = first_x
                    for char_index, glyph, glyph_width in glyph_items[1:]:
                        cursor_x -= glyph_width
                        draw_glyph(
                            out,
                            glyph,
                            x_position=cursor_x,
                            y_position=line_y,
                            color_index=paint_color_index,
                        )

            out_path = output_dir / src.name
            out.save(out_path)

    # Frames before first marker: no subtitle.
    first_marker_frame = markers[0][0]
    for f in range(start_print, min(first_marker_frame, timeline_end + 1)):
        #print(f"frame {f}: inject ")
        process_frame(f, "")

    # Marker spans.
    for i, (start, text, _line_no) in enumerate(markers):
        if i + 1 < len(markers):
            end = markers[i + 1][0] - 1
        else:
            end = timeline_end

        if end < start:
            continue

        span_start = max(start, start_print)
        span_end = min(end, timeline_end)
        if span_end < span_start:
            continue

        for f in range(span_start, span_end + 1):
            #print(f"frame {f}: inject {text}")
            process_frame(f, text)


if __name__ == "__main__":
    main()
