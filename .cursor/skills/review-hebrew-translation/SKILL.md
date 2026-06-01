---
name: review-hebrew-translation
description: Reviews Hebrew translations in Sierra King's Quest / QFG `messages.json` files (under `output_*/`) and applies fixes for awkward, unnatural, culturally inappropriate, ungrammatical, or inconsistent Hebrew that was likely produced by AI translation. Edits `messages.json` directly with one-line-clean diffs so the user can audit changes via `git diff` and the per-fix rationale via `git commit` messages. Use when the user asks to review, audit, fix, or improve weird / "wired" / awkward / unnatural Hebrew translations in `messages.json`, when checking translation quality across King's Quest games, or when invoked by name.
---

# Review Hebrew Translation

Audit the Hebrew side of a Sierra game's `messages.json` and **fix** entries
where the Hebrew sounds wrong to a native speaker. Each fix becomes exactly
one changed line in `messages.json`. The user reviews via `git diff` and
captures rationale via `git commit` messages — there is no separate
changelog file.

## When to use

- "Review the Hebrew translations in `output_kq1/messages.json`"
- "Fix weird/awkward Hebrew translations"
- "Audit and fix the KQ5 Hebrew"
- "Review messages 1101–1200 in `output_kq1/messages.json`"

## What counts as "weird" Hebrew

Six issue categories. See [examples.md](examples.md) for grounded examples
from this repo (including the canonical `פיה סנדקית`, `דרקון מת ורירי`,
`פתח כהה`, and `דלת עץ ישירות מולך` cases).

| Category | What to look for |
|----------|-----------------|
| `cultural` | Religious/cultural terms misapplied (e.g. `סנדקית` for fairy godmother). |
| `word-choice` | Dictionary-correct but wrong-fit word (e.g. `רירי` for a dead dragon, `כהה` for an ominous opening). |
| `redundancy` | Two Hebrew words that mean the same thing (e.g. `גמד ננס`). |
| `grammar` | Missing verbs, wrong gender/number agreement, broken `סמיכות`, wrong definite article. |
| `literal` | Calque of English syntax / idiom that no native speaker would say. Includes the "too much hassle" pattern (translating every English word when Hebrew flows better with fewer). |
| `inconsistency` | Same English term translated differently across messages with no story reason; or different spellings of the same proper noun. |

Tag each finding `high`, `medium`, or `low` severity (see examples.md rubric).

**Do not flag**: transliterated proper nouns (`Daventry → דבנטרי`), lost
English wordplay that can't be preserved, or pure style preference.

## Workflow

```
Task Progress:
- [ ] Step 1: Identify target messages.json and range
- [ ] Step 2: Run inconsistency pre-pass
- [ ] Step 3: Extract a batch and review it
- [ ] Step 4: Build translation_fixes.json
- [ ] Step 5: Dry-run, then apply (script auto-cleans the fixes file)
- [ ] Step 6: Tell the user what was applied; suggest a commit message
- [ ] Step 7: Loop or stop
```

### Step 1 — Identify target file and range

Available files (only these three exist today):

- `output_kq1/messages.json`
- `output_kq5/messages.json`
- `output_kq7/messages.json`

If the user didn't say which file or range, ask. The agent does **not** track
review progress between sessions — the user provides the range explicitly,
or asks for a specific scope (e.g. "everything we haven't covered yet" must
be answered with a question back, since there's no on-disk record).

### Step 2 — Run the inconsistency pre-pass

Run on every invocation (the script is fast and the file changes between
runs as fixes are applied):

```bash
python .cursor/skills/review-hebrew-translation/scripts/find_inconsistencies.py output_kq1/messages.json --ignore-case
```

Real inconsistencies (skip homonyms with genuinely different senses) become
fix entries with `category: "inconsistency"`. Pick one canonical Hebrew
translation and standardize all occurrences.

For proper-noun spelling consistency that the script can't catch (e.g.
`ליפרקונים` vs `לפרקונים`), do a focused codepoint scan with a small ad-hoc
Python snippet — the shell-level `grep` for Hebrew can silently miss
matches due to how Hebrew text is passed through the shell.

### Step 3 — Extract a batch (default 100 messages)

**Always set `PYTHONIOENCODING=utf-8` on Windows** so Hebrew survives the console:

```powershell
$env:PYTHONIOENCODING='utf-8'; python .cursor/skills/review-hebrew-translation/scripts/extract_batch.py output_kq1/messages.json --start 1 --size 100
```

Apply the rubric. A clean batch of 100 should typically yield 5–20 fixes.
If you find yourself flagging almost everything, recalibrate against the
"DO sound natural" examples in [examples.md](examples.md).

### Step 4 — Build translation_fixes.json

Write `output_<game>/translation_fixes.json`. The apply script will
**delete** this file after a successful `--apply`, so it's strictly working
data.

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
- The `reason` field is for the agent's own commit-message planning later; it's not surfaced to a separate audit file.

### Step 5 — Dry-run, then apply

Always dry-run first. The script reports each fix as `[OK ]`, `[==]` (old == new), or `[FAIL]`. **If anything fails, stop** — do not pass `--apply`. Investigate and fix the `old` field (most common cause: stale `old` text after a manual edit).

```powershell
# Dry run (does not write or delete anything):
$env:PYTHONIOENCODING='utf-8'; python .cursor/skills/review-hebrew-translation/scripts/apply_fixes.py output_kq1/translation_fixes.json

# Apply (writes messages.json and deletes translation_fixes.json on success):
$env:PYTHONIOENCODING='utf-8'; python .cursor/skills/review-hebrew-translation/scripts/apply_fixes.py output_kq1/translation_fixes.json --apply
```

The script:
- Locates each message by `(logicFile, messageNumber)` signature.
- Asserts current translation matches `old` (refuses to overwrite drift).
- Replaces only the `translation` line — preserves CRLF/LF, BOM, indentation, every other byte.
- Re-validates that the result is still parseable JSON before writing.
- **Deletes the fixes file** after a successful apply (its `old` values are stale; pass `--keep-fixes-file` only if you specifically want to retain it for replay).

### Step 6 — Tell the user; suggest a commit message

After applying, report to the user:
- Which range was just covered.
- How many fixes were applied, broken down by severity and category.
- The most consequential fixes (high severity ones, with a one-line "why" each).
- The exact `git diff` command to audit.
- A **suggested commit message** they can copy. Include category counts and a few representative `#N` references in the body. Per-fix rationale lives in the commit body if they want it.

Suggested commit message format:

```
fix(translations/kq1): review messages <START>–<END>

<one-line summary of the most consequential fixes>

Categories: <N> word-choice, <N> literal, <N> grammar, <N> inconsistency
Severity:   <N> high, <N> medium, <N> low

Notable:
- #<msgNum>: <one-line description>
- #<msgNum>: <one-line description>
- ...
```

### Step 7 — Loop or stop

Ask the user whether to continue (next range) or stop. Do not auto-loop
through 2000+ messages without checking in.

## Output format rules

- Never modify `messages.json` outside the apply script.
- Never edit `original`, `messageNumber`, `logicFile`, `notes`, or `placeholders` — only `translation`.
- Be selective: 5–20 fixes per 100-message batch is normal. If you flag almost everything, recalibrate.
- For each fix, the `reason` field should be one sentence and cite related message numbers if you spotted the issue via cross-reference.

## Helper scripts

- `scripts/extract_batch.py` — compact `(messageNumber, EN, HE)` view of a range. Run before reviewing a batch.
- `scripts/find_inconsistencies.py` — finds same-English-different-Hebrew. Run once per invocation.
- `scripts/apply_fixes.py` — applies a `translation_fixes.json` to `messages.json` with `(logicFile, messageNumber)` lookup, `old` validation, JSON re-parse check, and auto-cleanup of the fixes file. Always dry-run first; only pass `--apply` when the dry-run is clean.

All three scripts force UTF-8 stdout. If you ever see `?` characters instead of Hebrew, the console code page is wrong — set `$env:PYTHONIOENCODING='utf-8'` before running.

## Safety guarantees

The skill never:
- Edits `original`, `messageNumber`, `logicFile`, `notes`, or `placeholders` — only `translation`.
- Re-serializes the JSON (which would risk reformatting 17k lines of unrelated content).
- Overwrites a translation that no longer matches the `old` value (protects against stale fix files).

If something does go wrong, recovery is `git checkout output_<game>/messages.json`.

## Artifacts on disk

The skill writes only `output_<game>/translation_fixes.json` while a batch is
in flight, and the apply script deletes it on success. **No persistent
audit/changelog file is written** — `git log` + `git diff` are the audit.

## Additional resources

- [examples.md](examples.md) — full rubric calibration with real examples from `output_kq1/messages.json`, including the `כהה`/`אפל` cheat sheet and the "too much hassle" anti-pattern table.
