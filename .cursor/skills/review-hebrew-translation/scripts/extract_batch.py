"""Extract a compact batch of messages from a Sierra messages.json file.

Outputs a token-efficient view of (messageNumber, original English, current
Hebrew translation) triples so a reviewer can scan many messages at once
without paying for the full JSON's whitespace/keys.

Usage:
    python scripts/extract_batch.py output_kq1/messages.json --start 1 --size 100
    python scripts/extract_batch.py output_kq1/messages.json --start 800 --end 900
    python scripts/extract_batch.py output_kq1/messages.json --logic-file single --start 1 --size 50
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _force_utf8_stdout() -> None:
    # Windows PowerShell defaults to a non-UTF-8 code page, which turns Hebrew
    # into '?' on print(). Force UTF-8 so the bytes survive into terminal logs.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass


def main() -> int:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("messages_json", help="Path to messages.json")
    parser.add_argument("--start", type=int, default=1, help="Starting messageNumber (inclusive). Default: 1")
    parser.add_argument("--end", type=int, default=None, help="Ending messageNumber (inclusive). Overrides --size if given.")
    parser.add_argument("--size", type=int, default=100, help="Batch size (used if --end not given). Default: 100")
    parser.add_argument("--logic-file", default=None, help="Filter to a single logicFile (e.g. 'single', 'built-in')")
    parser.add_argument("--skip-empty", action="store_true", help="Skip entries with empty translation or original")
    args = parser.parse_args()

    path = Path(args.messages_json)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    data = json.loads(path.read_text(encoding="utf-8"))
    msgs = data.get("messages", [])
    end = args.end if args.end is not None else (args.start + args.size - 1)

    out_lines: list[str] = []
    count = 0
    last_seen = 0
    for m in msgs:
        n = int(m.get("messageNumber", 0))
        last_seen = max(last_seen, n)
        lf = m.get("logicFile", "")
        if args.logic_file and lf != args.logic_file:
            continue
        if n < args.start or n > end:
            continue
        original = (m.get("original") or "").replace("\r", "").replace("\n", "\\n")
        translation = (m.get("translation") or "").replace("\r", "").replace("\n", "\\n")
        if args.skip_empty and (not original.strip() or not translation.strip()):
            continue
        out_lines.append(f"#{n} [{lf}]")
        out_lines.append(f"  EN: {original}")
        out_lines.append(f"  HE: {translation}")
        count += 1

    header = f"=== {path.as_posix()} | range {args.start}..{end}"
    if args.logic_file:
        header += f" | logicFile={args.logic_file}"
    header += f" | total_messages_in_file={len(msgs)} | max_messageNumber={last_seen} ==="
    print(header)
    print("\n".join(out_lines))
    print(f"=== End of batch (returned={count}) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
