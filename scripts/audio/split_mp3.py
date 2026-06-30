"""Split an MP3 file into two parts at a given timestamp.

Usage:
    python split_mp3.py <input.mp3> <MM:SS:mmm>

Example:
    python split_mp3.py intro.mp3 01:23:500
        -> intro_part1.mp3   (0:00.000 -> 1:23.500)
        -> intro_part2.mp3   (1:23.500 -> end)

Requirements:
    pip install pydub
    ffmpeg must be installed and reachable on PATH
    (pydub uses ffmpeg under the hood to decode/encode MP3).
"""

from __future__ import annotations

import sys
from pathlib import Path

from pydub import AudioSegment


def parse_time(time_str: str) -> int:
    """Parse "MM:SS:mmm" into total milliseconds."""
    parts = time_str.split(":")
    if len(parts) != 3:
        raise ValueError(
            f"Time must be in MM:SS:mmm format (e.g. 01:23:500), got: {time_str!r}"
        )
    try:
        minutes, seconds, millis = (int(p) for p in parts)
    except ValueError as exc:
        raise ValueError(f"Time parts must be integers, got: {time_str!r}") from exc
    if minutes < 0 or seconds < 0 or millis < 0:
        raise ValueError(f"Time parts must be non-negative, got: {time_str!r}")
    return minutes * 60_000 + seconds * 1_000 + millis


def split_mp3(input_path: str, time_str: str) -> tuple[Path, Path]:
    split_ms = parse_time(time_str)
    src = Path(input_path)
    if not src.is_file():
        raise FileNotFoundError(src)

    audio = AudioSegment.from_mp3(src)
    total_ms = len(audio)

    if not (0 < split_ms < total_ms):
        raise ValueError(
            f"Split point {time_str} ({split_ms} ms) is outside the file's "
            f"length ({total_ms} ms)."
        )

    out1 = src.with_name(f"{src.stem}_part1{src.suffix}")
    out2 = src.with_name(f"{src.stem}_part2{src.suffix}")

    audio[:split_ms].export(out1, format="mp3")
    audio[split_ms:].export(out2, format="mp3")

    print(f"Created: {out1}  ({split_ms} ms)")
    print(f"Created: {out2}  ({total_ms - split_ms} ms)")
    return out1, out2


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python split_mp3.py <input.mp3> <MM:SS:mmm>", file=sys.stderr)
        return 1
    try:
        split_mp3(argv[1], argv[2])
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
