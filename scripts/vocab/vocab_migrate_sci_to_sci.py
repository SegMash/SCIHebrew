# Migrate Hebrew translations from one SCI vocab.csv to another SCI vocab.csv
# Source file: vocab.csv (already has Hebrew translations)
# Target file: vocab.csv (to be enhanced with translations)
#
# For each English word in target:
# 1. Try to find it in source vocab.csv
# 2. If found, copy its Hebrew translation to the target line
# 3. If not found, log error and continue

import argparse
import csv
import os
import re
from pathlib import Path


HEBREW_RE = re.compile(r'[\u0590-\u05FF]')


def contains_hebrew(text):
    return bool(HEBREW_RE.search(text))


def dedupe_pipe_parts(parts):
    seen = set()
    result = []
    for part in parts:
        key = part.strip()
        if key and key not in seen:
            seen.add(key)
            result.append(key)
    return result


def extract_hebrew_parts(words_col):
    parts = [p.strip() for p in words_col.split('|') if p.strip()]
    return [part for part in parts if contains_hebrew(part)]

def read_sci_vocab(vocab_file):
    """
    Read SCI vocab.csv and build a lookup dictionary
    Returns: dict where key=english_word, value=hebrew_translation (already in words column)
    
    SCI vocab format: words | class | group | rooms | comments
    words column format: "english_word | hebrew_translation" or just "english_word"
    """
    lookup = {}
    with open(vocab_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            words_col = row.get('words', '')
            
            if not words_col or words_col.strip() == '':
                continue
            
            # Split by pipe and detect where Hebrew section starts
            parts = [p.strip() for p in words_col.split('|') if p.strip()]
            
            if len(parts) < 1:
                continue
            
            first_hebrew_idx = None
            for i, part in enumerate(parts):
                if contains_hebrew(part):
                    first_hebrew_idx = i
                    break

            if first_hebrew_idx is None:
                # No Hebrew translation in this source row
                continue

            english_words = parts[:first_hebrew_idx]
            hebrew_parts = dedupe_pipe_parts(parts[first_hebrew_idx:])
            hebrew_str = ' | '.join(hebrew_parts) if hebrew_parts else ''
            
            # Map every English synonym in the row to the same Hebrew translation block.
            for eng_word in english_words:
                if eng_word and hebrew_str:
                    lookup[eng_word.lower()] = hebrew_str
    
    return lookup


def migrate_vocab_sci_to_sci(source_file, target_file, output_file, debug=False):
    """
    Migrate Hebrew translations from source SCI vocab to target SCI vocab
    """
    # Read source lookup
    source_lookup = read_sci_vocab(source_file)
    
    print(f"Loaded {len(source_lookup)} translations from source")
    
    # Process target vocab
    errors = []
    updates = []
    
    with open(target_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Build a global set of Hebrew words that already exist in target.
    existing_hebrew_words = set()
    for row in rows:
        words_col = row.get('words', '')
        if not words_col or words_col.strip() == '':
            continue
        for hebrew_part in extract_hebrew_parts(words_col):
            existing_hebrew_words.add(hebrew_part)
    
    updated_rows = []
    for row_idx, row in enumerate(rows, start=2):  # Start at 2 because row 1 is header
        words_col = row.get('words', '')
        
        if not words_col or words_col.strip() == '':
            updated_rows.append(row)
            continue
        
        # If this row already has Hebrew, do not touch it.
        parts = [p.strip() for p in words_col.split('|') if p.strip()]
        if any(contains_hebrew(part) for part in parts):
            if debug:
                print(f"Row {row_idx}: Already has Hebrew, skipping")
            updated_rows.append(row)
            continue
        
        # Extract English words from this line
        english_words = [w.strip() for w in words_col.split('|') if w.strip()]
        
        # Try to find Hebrew translation
        hebrew_found = None
        matched_word = None
        
        for eng_word in english_words:
            eng_lower = eng_word.lower()
            if eng_lower in source_lookup:
                hebrew_found = source_lookup[eng_lower]
                matched_word = eng_word
                break
        
        if hebrew_found:
            hebrew_candidates = dedupe_pipe_parts([p.strip() for p in hebrew_found.split('|') if p.strip()])
            hebrew_to_add = [h for h in hebrew_candidates if h not in existing_hebrew_words]

            if hebrew_to_add:
                # Append only Hebrew words that are not already present in target anywhere.
                row['words'] = words_col + ' | ' + ' | '.join(hebrew_to_add)
                for h in hebrew_to_add:
                    existing_hebrew_words.add(h)
                updates.append((row_idx, matched_word, ' | '.join(hebrew_to_add)))
                if debug:
                    print(f"Row {row_idx}: Matched '{matched_word}' -> {' | '.join(hebrew_to_add)}")
            elif debug:
                print(f"Row {row_idx}: Matched '{matched_word}' but all Hebrew words already exist in target, skipping")
        else:
            error_msg = f"Row {row_idx}: No source match found for: {', '.join(english_words)}"
            errors.append(error_msg)
            if debug:
                print(f"ERROR: {error_msg}")
        
        updated_rows.append(row)
    
    # Write output
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(updated_rows)
    
    # Summary
    print(f"\nMigration complete:")
    print(f"  Updated: {len(updates)} lines")
    print(f"  Errors: {len(errors)} lines")
    
    if errors and not debug:
        print("\nUnmatched words (first 10):")
        for err in errors[:10]:
            print(f"  {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    return len(errors) == 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Migrate Hebrew translations from one SCI vocab.csv to another'
    )
    parser.add_argument('source_file', help='Source SCI vocab.csv (with Hebrew translations)')
    parser.add_argument('target_file', help='Target SCI vocab.csv (to be enhanced)')
    parser.add_argument('output_file', help='Output vocab.csv with merged translations')
    parser.add_argument('--debug', action='store_true', help='Show detailed progress for each match')
    
    args = parser.parse_args()
    
    success = migrate_vocab_sci_to_sci(args.source_file, args.target_file, args.output_file, args.debug)
    exit(0 if success else 1)
