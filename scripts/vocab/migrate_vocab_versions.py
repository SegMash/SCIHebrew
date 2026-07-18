#!/usr/bin/env python3
"""
Merge words from an older enriched vocab.csv into a newer vocab.csv.

The files are not line-aligned. For each target row, the script finds a source
row that shares at least one word in the first column, then appends any source
words that are missing from the target row.
"""

import argparse
import csv
import re
from pathlib import Path

HEBREW_RE = re.compile(r'[\u0590-\u05FF]')


def contains_hebrew(text):
    return bool(HEBREW_RE.search(text))


def parse_words(words_col):
    return [part.strip() for part in words_col.split('|') if part.strip()]


def word_key(word):
    if contains_hebrew(word):
        return ('he', word)
    return ('en', word.lower())


def build_word_index(rows):
    """Map each word key to source row indexes."""
    index = {}
    for row_idx, row in enumerate(rows):
        words_col = row.get('words', '')
        for word in parse_words(words_col):
            index.setdefault(word_key(word), set()).add(row_idx)
    return index


def overlap_size(target_words, source_words):
    target_keys = {word_key(word) for word in target_words}
    return sum(1 for word in source_words if word_key(word) in target_keys)


def find_best_source_row(target_row, target_words, source_rows, source_index):
    candidate_indexes = set()
    for word in target_words:
        candidate_indexes.update(source_index.get(word_key(word), set()))

    if not candidate_indexes:
        return None

    target_group = target_row.get('group', '')
    best_idx = None
    best_score = (-1, -1, -1)

    for row_idx in candidate_indexes:
        source_row = source_rows[row_idx]
        source_words = parse_words(source_row.get('words', ''))
        score = (
            overlap_size(target_words, source_words),
            1 if source_row.get('group', '') == target_group else 0,
        )
        if score > best_score[:2]:
            best_idx = row_idx
            best_score = (*score, -row_idx)

    return source_rows[best_idx] if best_idx is not None else None


def merge_words(target_words, source_words):
    """Append source words that are not already present in target."""
    existing = {word_key(word) for word in target_words}
    merged = list(target_words)

    for word in source_words:
        key = word_key(word)
        if key not in existing:
            merged.append(word)
            existing.add(key)

    return merged


def format_words(words):
    return ' | '.join(words)


def migrate_vocab_versions(source_file, target_file, report_file=None):
    source_path = Path(source_file)
    target_path = Path(target_file)
    if report_file is None:
        report_path = target_path.with_name(f'{target_path.stem}_migrate_report.txt')
    else:
        report_path = Path(report_file)

    with open(source_path, newline='', encoding='utf-8') as infile:
        source_reader = csv.DictReader(infile)
        fieldnames = source_reader.fieldnames
        source_rows = list(source_reader)

    with open(target_path, newline='', encoding='utf-8') as infile:
        target_reader = csv.DictReader(infile)
        if target_reader.fieldnames != fieldnames:
            raise ValueError(
                f'CSV headers differ:\n  source: {source_reader.fieldnames}\n  target: {target_reader.fieldnames}'
            )
        target_rows = list(target_reader)

    source_index = build_word_index(source_rows)

    updated_rows = []
    unmatched_rows = []
    enriched_count = 0

    for row_num, target_row in enumerate(target_rows, start=2):
        words_col = target_row.get('words', '')
        if not words_col.strip():
            updated_rows.append(target_row)
            continue

        target_words = parse_words(words_col)
        source_row = find_best_source_row(
            target_row, target_words, source_rows, source_index,
        )

        if source_row is None:
            unmatched_rows.append({
                'line': row_num,
                'group': target_row.get('group', ''),
                'words': words_col,
            })
            updated_rows.append(target_row)
            continue

        source_words = parse_words(source_row.get('words', ''))
        merged_words = merge_words(target_words, source_words)
        if merged_words != target_words:
            enriched_count += 1
            target_row = dict(target_row)
            target_row['words'] = format_words(merged_words)

        updated_rows.append(target_row)

    with open(target_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(updated_rows)

    with open(report_path, 'w', encoding='utf-8') as report:
        if unmatched_rows:
            for item in unmatched_rows:
                report.write(
                    f"Line {item['line']} (group {item['group']}): {item['words']}\n"
                )
        else:
            report.write('All target rows matched a source row.\n')

    print('Migration complete:')
    print(f'  Source rows: {len(source_rows)}')
    print(f'  Target rows: {len(target_rows)}')
    print(f'  Enriched rows: {enriched_count}')
    print(f'  Unmatched rows: {len(unmatched_rows)}')
    print(f'  Updated target: {target_path}')
    print(f'  Report: {report_path}')

    return len(unmatched_rows) == 0


def main():
    parser = argparse.ArgumentParser(
        description='Merge missing words from an older vocab.csv into a newer vocab.csv.',
    )
    parser.add_argument('source', help='Older enriched vocab.csv file')
    parser.add_argument('target', help='Newer vocab.csv file to enrich (updated in place)')
    parser.add_argument(
        '--report',
        help='Report file for unmatched target rows '
             '(default: <target_stem>_migrate_report.txt)',
    )

    args = parser.parse_args()
    success = migrate_vocab_versions(args.source, args.target, args.report)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
