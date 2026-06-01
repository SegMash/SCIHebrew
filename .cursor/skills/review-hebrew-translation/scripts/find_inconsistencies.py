"""Find English terms that have multiple different Hebrew translations.

This is a deterministic pre-pass: it does not judge translation quality, it
only surfaces cases where the same English source got translated differently
in different messages. The reviewer (LLM or human) then decides which
translation is best and whether to standardize.

Usage:
    python scripts/find_inconsistencies.py output_kq1/messages.json
    python scripts/find_inconsistencies.py output_kq1/messages.json --max-len 40
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
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
    parser.add_argument("--min-occurrences", type=int, default=2, help="Only report originals that appear at least this many times. Default: 2")
    parser.add_argument(
        "--max-len",
        type=int,
        default=80,
        help="Only consider originals up to this length (focus on terms/phrases, not long sentences). Default: 80",
    )
    parser.add_argument("--ignore-case", action="store_true", help="Treat 'Witch' and 'witch' as the same key")
    args = parser.parse_args()

    path = Path(args.messages_json)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    data = json.loads(path.read_text(encoding="utf-8"))
    bucket: dict[str, list[tuple[str, int, str, str]]] = defaultdict(list)

    for m in data.get("messages", []):
        original = (m.get("original") or "").strip()
        translation = (m.get("translation") or "").strip()
        if not original or not translation:
            continue
        if len(original) > args.max_len:
            continue
        key = original.lower() if args.ignore_case else original
        bucket[key].append((m.get("logicFile", ""), int(m["messageNumber"]), original, translation))

    findings = 0
    for key in sorted(bucket.keys()):
        items = bucket[key]
        if len(items) < args.min_occurrences:
            continue
        translations = {t for (_, _, _, t) in items}
        if len(translations) <= 1:
            continue
        findings += 1
        display = items[0][2]
        print(f"\n--- '{display}' has {len(translations)} different Hebrew translations across {len(items)} messages ---")
        for lf, num, _orig, trans in items:
            print(f"  [{lf}] #{num}: {trans}")

    if findings == 0:
        print("No inconsistencies found above thresholds.")
    else:
        print(f"\n=== {findings} inconsistent English terms found ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
