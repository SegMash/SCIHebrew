"""Apply Hebrew translation fixes to a Sierra messages.json file.

Edits are done as **targeted in-place text replacements** so that every fix
shows up as exactly one line changed in `git diff`. The script does NOT
re-serialize the JSON — that would risk reformatting whitespace, escape
sequences, or key order across 17k lines.

Each fix must specify (logicFile, messageNumber, old, new). The script:
  1. Locates the unique message by `"logicFile": "<X>"` immediately followed
     by `"messageNumber": <N>` (the canonical structural signature).
  2. Within that message block, finds `"translation": "<OLD>"` and asserts
     it matches the current file. If it doesn't match, the fix is rejected
     (prevents stale fix files from corrupting newer translations).
  3. Replaces with `"translation": "<NEW>"`.
  4. After all fixes succeed, runs `json.loads()` on the result to confirm
     the file is still valid JSON before writing.
  5. Writes back as bytes, preserving the original CRLF/LF line ending and
     absence/presence of a BOM.

Fix file (JSON) schema:
{
  "source": "output_kq1/messages.json",
  "fixes": [
    {
      "logicFile": "single",
      "messageNumber": 1002,
      "old": "<exact current Hebrew translation>",
      "new": "<replacement Hebrew translation>",
      "reason": "free-form note (optional, ignored by the script)",
      "category": "word-choice",
      "severity": "high"
    }
  ]
}

Usage:
    # Dry run (default) — report what would change, write nothing:
    python scripts/apply_fixes.py output_kq1/translation_fixes.json

    # Actually write to messages.json:
    python scripts/apply_fixes.py output_kq1/translation_fixes.json --apply

    # Override the source from CLI (rare):
    python scripts/apply_fixes.py output_kq1/translation_fixes.json --apply \
        --messages-json output_kq1/messages.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _force_utf8_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass


def _detect_line_ending(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def _has_bom(raw: bytes) -> bool:
    return raw[:3] == b"\xef\xbb\xbf"


def _json_string(s: str) -> str:
    """Encode a Python string as a JSON string literal (with surrounding quotes),
    matching the formatting that Python's json module would produce when called
    with ensure_ascii=False — which is what the messages.json file uses for
    Hebrew. This is what we put on the right-hand side of `"translation":`."""
    return json.dumps(s, ensure_ascii=False)


def apply_one_fix(
    text: str,
    logic_file: str,
    msg_num: int,
    old: str,
    new: str,
    line_ending: str,
) -> tuple[str, str]:
    """Apply a single fix. Returns (new_text, status) where status is 'applied',
    'identical' (old == new), or raises ValueError on a problem."""

    if old == new:
        return text, "identical"

    # Locate the message by its (logicFile, messageNumber) signature.
    # Inside `messages: [`, each message object has keys at 6-space indent.
    # The two opening keys are always "logicFile" then "messageNumber" in
    # that order, on consecutive lines.
    sig = (
        f'"logicFile": {_json_string(logic_file)},{line_ending}'
        f'      "messageNumber": {msg_num},{line_ending}'
    )
    sig_idx = text.find(sig)
    if sig_idx == -1:
        raise ValueError(
            f"Could not locate message {logic_file!r} #{msg_num} "
            f"(no matching logicFile+messageNumber signature)."
        )
    if text.find(sig, sig_idx + 1) != -1:
        # Defensive: the (logicFile, messageNumber) pair must be unique.
        raise ValueError(
            f"Signature for {logic_file!r} #{msg_num} is not unique in the file."
        )

    # Within this message block, find the translation line. Bound the search
    # by the next message-object closing `},` so we don't accidentally cross
    # into a neighbour.
    block_end_pat = re.compile(re.escape(line_ending) + r"    \},?", re.DOTALL)
    block_end_match = block_end_pat.search(text, sig_idx)
    if not block_end_match:
        raise ValueError(f"Could not find end of message block for {logic_file!r} #{msg_num}.")
    block_end = block_end_match.start()

    old_line = f'      "translation": {_json_string(old)},'
    block = text[sig_idx:block_end]
    rel_idx = block.find(old_line)
    if rel_idx == -1:
        # Surface the actual current translation to help diagnose drift.
        cur_match = re.search(
            r'^      "translation": (.*?),\s*$',
            block,
            re.MULTILINE,
        )
        cur = cur_match.group(1) if cur_match else "<not found>"
        raise ValueError(
            f"'old' translation does not match current file for "
            f"{logic_file!r} #{msg_num}.\n"
            f"  expected: {_json_string(old)}\n"
            f"  found:    {cur}"
        )

    abs_idx = sig_idx + rel_idx
    new_line = f'      "translation": {_json_string(new)},'
    new_text = text[:abs_idx] + new_line + text[abs_idx + len(old_line):]
    return new_text, "applied"


def main() -> int:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("fixes_json", help="Path to translation_fixes.json")
    parser.add_argument(
        "--messages-json",
        default=None,
        help="Override the messages.json path (default: read from fixes file's 'source' field)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes. Without this flag, runs as a dry run.",
    )
    parser.add_argument(
        "--keep-fixes-file",
        action="store_true",
        help="Don't delete the fixes.json after a successful --apply. By default the fixes file is removed because its 'old' values become stale immediately after apply.",
    )
    args = parser.parse_args()

    fixes_path = Path(args.fixes_json)
    if not fixes_path.exists():
        print(f"ERROR: fixes file not found: {fixes_path}", file=sys.stderr)
        return 2
    fixes_doc = json.loads(fixes_path.read_text(encoding="utf-8"))

    src = args.messages_json or fixes_doc.get("source")
    if not src:
        print("ERROR: no --messages-json given and fixes file has no 'source' field", file=sys.stderr)
        return 2
    msgs_path = Path(src)
    if not msgs_path.exists():
        print(f"ERROR: messages.json not found: {msgs_path}", file=sys.stderr)
        return 2

    raw = msgs_path.read_bytes()
    bom = _has_bom(raw)
    body = raw[3:] if bom else raw
    line_ending = _detect_line_ending(body)
    text = body.decode("utf-8")

    fixes = fixes_doc.get("fixes", [])
    print(f"Loaded {len(fixes)} fix(es) from {fixes_path}")
    print(f"Target: {msgs_path}  (line_ending={line_ending!r}, bom={bom})")
    print(f"Mode:   {'APPLY' if args.apply else 'DRY-RUN (no write)'}")
    print()

    applied = 0
    identical = 0
    failures: list[tuple[dict, str]] = []
    new_text = text
    for fix in fixes:
        try:
            new_text, status = apply_one_fix(
                new_text,
                fix["logicFile"],
                int(fix["messageNumber"]),
                fix["old"],
                fix["new"],
                line_ending,
            )
        except (KeyError, ValueError) as e:
            failures.append((fix, str(e)))
            print(f"  [FAIL] #{fix.get('messageNumber','?')} [{fix.get('logicFile','?')}]: {e}")
            continue

        tag = "[OK ]" if status == "applied" else "[==]"
        print(
            f"  {tag} #{fix['messageNumber']} [{fix['logicFile']}] "
            f"({fix.get('category','?')}/{fix.get('severity','?')})"
        )
        if status == "applied":
            applied += 1
        else:
            identical += 1

    print()
    print(f"Summary: applied={applied}, identical={identical}, failed={len(failures)}")

    if failures:
        print("\nABORTING: refusing to write because some fixes failed validation.")
        print("Inspect the [FAIL] lines above; the most common cause is that")
        print("messages.json has been edited since the fix file was authored.")
        return 1

    if applied == 0:
        print("\nNothing to write.")
        return 0

    # Re-validate JSON before writing.
    try:
        json.loads(new_text)
    except json.JSONDecodeError as e:
        print(f"\nABORTING: result is not valid JSON: {e}", file=sys.stderr)
        return 3

    if not args.apply:
        print("\nDry run complete. Re-run with --apply to write changes.")
        return 0

    out_bytes = (b"\xef\xbb\xbf" if bom else b"") + new_text.encode("utf-8")
    msgs_path.write_bytes(out_bytes)
    print(f"\nWrote {len(out_bytes):,} bytes to {msgs_path}.")
    print("Review with: git diff --word-diff " + str(msgs_path))

    if not args.keep_fixes_file:
        try:
            fixes_path.unlink()
            print(f"Cleaned up: {fixes_path} (its 'old' values are stale now). Pass --keep-fixes-file to retain.")
        except OSError as e:
            print(f"Note: could not delete {fixes_path}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
