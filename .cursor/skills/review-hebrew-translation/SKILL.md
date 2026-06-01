---
name: review-hebrew-translation
description: Reviews Hebrew translations in Sierra King's Quest / QFG `messages.json` files (under `output_*/`) and applies fixes for awkward, unnatural, culturally inappropriate, ungrammatical, or inconsistent Hebrew that was likely produced by AI translation. Edits `messages.json` directly with one-line-clean diffs so the user can audit changes via `git diff`. Use when the user asks to review, audit, fix, or improve weird / "wired" / awkward / unnatural Hebrew translations in `messages.json`, when checking translation quality across King's Quest games, or when invoked by name.
---

# Review Hebrew Translation

Audit the Hebrew side of a Sierra game's `messages.json` and **fix** entries
where the Hebrew sounds wrong to a native speaker. Each fix becomes exactly
one changed line in `messages.json`, so the user reviews via `git diff`.

A human-readable changelog is also written to
`output_<game>/translation_review.md` so the user can see *why* each fix was
made — `git diff` shows the *what*.

## When to use

- "Review the Hebrew translations in `output_kq1/messages.json`"
- "Fix weird/awkward Hebrew translations"
- "Audit and fix the KQ5 Hebrew"
- "Continue the Hebrew translation review where we left off"

## What counts as "weird" Hebrew

Six issue categories. See [examples.md](examples.md) for grounded examples
from this repo (including the canonical `פיה סנדקית` and `דרקון מת ורירי` cases).

| Category | What to look for |
|----------|-----------------|
| `cultural` | Religious/cultural terms misapplied (e.g. `סנדקית` for fairy godmother). |
| `word-choice` | Dictionary-correct but wrong-fit word (e.g. `רירי` for a dead dragon). |
| `redundancy` | Two Hebrew words that mean the same thing (e.g. `גמד ננס`). |
| `grammar` | Missing verbs, wrong gender/number agreement, broken `סמיכות`, wrong definite article. |
| `literal` | Calque of English syntax / idiom that no native speaker would say. |
| `inconsistency` | Same English term translated differently across messages with no story reason. |

Tag each finding `high`, `medium`, or `low` severity (see examples.md rubric).

**Do not flag**: transliterated proper nouns (`Daventry → דבנטרי`), lost
English wordplay that can't be preserved, or pure style preference.

## Workflow

```
Task Progress:
- [ ] Step 1: Identify target messages.json
- [ ] Step 2: Run inconsistency pre-pass
- [ ] Step 3: Determine starting messageNumber (resume or start fresh)
- [ ] Step 4: Extract a batch and review it
- [ ] Step 5: Build translation_fixes.json
- [ ] Step 6: Dry-run, then apply
- [ ] Step 7: Append a changelog entry to translation_review.md
- [ ] Step 8: Loop or stop
```

### Step 1 — Identify target file

Available files (only these three exist today):

- `output_kq1/messages.json`
- `output_kq5/messages.json`
- `output_kq7/messages.json`

If the user didn't say which, ask. The artifacts are always written next to
the source:

- `output_<game>/messages.json` — edited in place.
- `output_<game>/translation_review.md` — human-readable changelog (append-only).
- `output_<game>/translation_fixes.json` — machine-readable batch input to `apply_fixes.py`. Overwritten each batch.

### Step 2 — Run the inconsistency pre-pass (once per file)

```bash
python .cursor/skills/review-hebrew-translation/scripts/find_inconsistencies.py output_kq1/messages.json --ignore-case
```

Real inconsistencies (skip homonyms with genuinely different senses) become
fix entries with `category: "inconsistency"`. Pick one canonical Hebrew
translation and standardize all occurrences to it.

### Step 3 — Determine starting messageNumber

If `output_<game>/translation_review.md` already exists, read its
`<!-- progress: last_reviewed=NNN -->` marker and start at `NNN+1`.
Otherwise start at `1`.

### Step 4 — Extract a batch (default 100 messages)

Use the helper. **Always set `PYTHONIOENCODING=utf-8` on Windows** so Hebrew
survives the console:

```powershell
$env:PYTHONIOENCODING='utf-8'; python .cursor/skills/review-hebrew-translation/scripts/extract_batch.py output_kq1/messages.json --start 1 --size 100
```

Apply the rubric. A clean batch of 100 should typically yield 5–20 fixes.
If you find yourself flagging almost everything, recalibrate against the
"DO sound natural" examples in [examples.md](examples.md).

### Step 5 — Build translation_fixes.json

Write `output_<game>/translation_fixes.json`. **Overwrite** the file each
batch (the apply script consumes it once, then it's stale).

```json
{
  "source": "output_kq1/messages.json",
  "fixes": [
    {
      "logicFile": "single",
      "messageNumber": 1002,
      "old": "<exact current Hebrew translation, byte-for-byte>",
      "new": "<replacement Hebrew translation>",
      "reason": "חזהו ('his bosom') → תיבתו (treasure chest, matches #1005/#1006/#1007)",
      "category": "word-choice",
      "severity": "high"
    }
  ]
}
```

**Critical rules** for the fix entries:

- `logicFile` + `messageNumber` together identify the entry. A bare `messageNumber` is **not** unique — e.g. `#497` exists in both `built-in` and `single`.
- `old` must match the current `translation` field **exactly**, character-for-character (including punctuation, spaces, RTL marks, escaped quotes). The apply script aborts on mismatch.
- `new` must be the full replacement translation, not a diff. The apply script swaps the entire string.
- Don't include placeholder fields you didn't change. If two entries share an English source but you only want to change one, list only that one.

### Step 6 — Dry-run, then apply

Always dry-run first. The script reports each fix as `[OK ]`, `[==]` (old == new), or `[FAIL]`. **If anything fails, stop** — do not pass `--apply`. Investigate and fix the `old` field (most common cause: stale `old` text after a manual edit).

```powershell
# Dry run:
$env:PYTHONIOENCODING='utf-8'; python .cursor/skills/review-hebrew-translation/scripts/apply_fixes.py output_kq1/translation_fixes.json

# Apply (only after dry-run is clean):
$env:PYTHONIOENCODING='utf-8'; python .cursor/skills/review-hebrew-translation/scripts/apply_fixes.py output_kq1/translation_fixes.json --apply
```

The script:
- Locates each message by `(logicFile, messageNumber)` signature.
- Asserts current translation matches `old` (refuses to overwrite drift).
- Replaces only the `translation` line — preserves CRLF/LF, BOM, indentation, every other byte.
- Re-validates that the result is still parseable JSON before writing.

### Step 7 — Append changelog to translation_review.md

The review file is now a **changelog of applied fixes**, not a list of suggestions. Use this structure (append batches; never rewrite earlier entries):

```markdown
# Hebrew Translation Review — output_kq1/messages.json

<!-- progress: last_reviewed=100 -->
<!-- ranges_reviewed: 1-100 -->

> Audit changes with: `git diff output_kq1/messages.json`

## Applied

### Messages 1–100 (applied YYYY-MM-DD)

Summary: 13 fixes applied (6 high, 5 medium, 2 low).

#### #1002 — word-choice (high)
- **EN**: `The giant, with his chest, has all the treasure he needs; ...`
- **Was**: `לענק, עם חזהו, יש את כל האוצרות שהוא צריך; ...`
- **Now**: `לענק, יחד עם תיבתו, יש את כל האוצרות שהוא צריך; ...`
- **Why**: `חזהו` means "his bosom"; English "chest" here is the treasure chest (cf. #1005, #1006, #1007 which use `תיבה`).
```

After applying, **update the progress marker** to the last messageNumber covered.

### Step 8 — Loop or stop

After each batch, tell the user:
- which range was just covered,
- how many fixes were applied (broken down by severity),
- the next range that would run,
- the exact `git diff` command to audit the changes.

Then ask whether to continue. Don't auto-loop through 2000+ messages without checking in.

## Output format rules

- One H4 (`####`) per fix in the changelog, headed `#<number> — <category> (<severity>)`.
- Always quote both the English and the **before** Hebrew verbatim. Show the **after** Hebrew in full as well.
- `Why` is a one-sentence explanation; cite related message numbers when you found them via consistency analysis.
- Group entries by batch under H3 `### Messages X–Y (applied YYYY-MM-DD)` so the changelog reads chronologically.
- Reverting a previously applied fix is its own changelog entry, not an in-place edit of the original.

## Helper scripts

- `scripts/extract_batch.py` — compact `(messageNumber, EN, HE)` view of a range. Run before reviewing a batch.
- `scripts/find_inconsistencies.py` — finds same-English-different-Hebrew. Run once per file before batch review.
- `scripts/apply_fixes.py` — applies a `translation_fixes.json` to `messages.json` with `(logicFile, messageNumber)` lookup, `old` validation, and a JSON re-parse check. Always dry-run first; only pass `--apply` when the dry-run is clean.

All three scripts force UTF-8 stdout. If you ever see `?` characters instead of Hebrew, the console code page is wrong — set `$env:PYTHONIOENCODING='utf-8'` before running.

## Safety guarantees

The skill never:
- Edits `original`, `messageNumber`, `logicFile`, `notes`, or `placeholders` — only `translation`.
- Re-serializes the JSON (which would risk reformatting 17k lines of unrelated content).
- Overwrites a translation that no longer matches the `old` value (protects against stale fix files).

If something does go wrong, recovery is `git checkout output_<game>/messages.json`.

## Additional resources

- [examples.md](examples.md) — full rubric calibration with real examples from `output_kq1/messages.json`.
