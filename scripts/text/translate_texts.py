#!/usr/bin/env python3
"""
Apply translations from mapping file to SCI text files.
Reads text files, looks up translations in mapping file, and creates new text files.
"""

import argparse
import csv
import operator
from functools import partial
from itertools import takewhile
from pathlib import Path

ENCODING_IN = 'windows-1252'
ENCODING_OUT = 'windows-1255'
SIERRA_TEXT_HEADER = b'\x83'
TEXTS_PATTERNS = ["text.*", "*.tex"]
FUZZY_MAX_PERCENT = 10


def max_edits_for_length(length, fuzzy_percent):
    """Max allowed edits based on percentage of message length."""
    if fuzzy_percent <= 0 or length <= 0:
        return 0
    return int(length * fuzzy_percent / 100)


def levenshtein_distance(s1, s2, max_distance):
    """Return edit distance if within max_distance, otherwise None."""
    if s1 == s2:
        return 0

    len1, len2 = len(s1), len(s2)
    if abs(len1 - len2) > max_distance:
        return None

    if len1 > len2:
        s1, s2 = s2, s1
        len1, len2 = len2, len1

    previous_row = list(range(len2 + 1))
    for i, c1 in enumerate(s1, 1):
        current_row = [i]
        row_min = i
        for j, c2 in enumerate(s2, 1):
            cost = 0 if c1 == c2 else 1
            current_row.append(min(
                previous_row[j] + 1,
                current_row[j - 1] + 1,
                previous_row[j - 1] + cost,
            ))
            row_min = min(row_min, current_row[j])
        if row_min > max_distance:
            return None
        previous_row = current_row

    distance = previous_row[len2]
    return distance if distance <= max_distance else None


def message_variants(message):
    """Generate message forms to try for exact and fuzzy matching."""
    message_with_literal_newlines = message.replace('\n', '\\n').replace('\r', '\\r')
    normalized_newlines = message_with_literal_newlines.replace('\\n\\n', '\\r\\n')
    trimmed_newlines = normalized_newlines.lstrip().rstrip()

    variants = [
        message,
        message_with_literal_newlines,
        message.strip(),
        message_with_literal_newlines.strip(),
        normalized_newlines,
        trimmed_newlines,
        ' '.join(message.split()),
    ]

    seen = set()
    unique_variants = []
    for variant in variants:
        if variant not in seen:
            seen.add(variant)
            unique_variants.append(variant)
    return unique_variants


def finalize_translation(hebrew, matched_variant):
    """Convert escaped newlines in Hebrew output when needed."""
    if '\\n' in matched_variant or '\\r' in matched_variant:
        hebrew = hebrew.replace('\\n', '\n')
        hebrew = hebrew.replace('\\r', '\r')
    return hebrew


def build_keys_by_length(keys):
    """Group mapping keys by string length for faster fuzzy lookup."""
    keys_by_length = {}
    for key in keys:
        keys_by_length.setdefault(len(key), []).append(key)
    return keys_by_length


def find_fuzzy_match(
    text,
    mapping_keys,
    mapping,
    fuzzy_percent=FUZZY_MAX_PERCENT,
    keys_by_length=None,
):
    """Find a unique best fuzzy match within a percentage-based edit budget."""
    max_distance = max_edits_for_length(len(text), fuzzy_percent)
    if max_distance == 0:
        return None, None

    best_key = None
    best_distance = max_distance + 1
    tied = False
    text_len = len(text)

    if keys_by_length is None:
        candidate_keys = mapping_keys
    else:
        candidate_keys = []
        for length in range(text_len - max_distance, text_len + max_distance + 1):
            candidate_keys.extend(keys_by_length.get(length, ()))

    for key in candidate_keys:
        if key == text:
            continue

        distance = levenshtein_distance(text, key, max_distance)
        if distance is None or distance == 0:
            continue

        if distance < best_distance:
            best_distance = distance
            best_key = key
            tied = False
        elif distance == best_distance:
            tied = True

    if best_key is None or tied:
        return None, None
    return mapping[best_key], best_key


def lookup_in_mapping(
    message,
    mapping,
    mapping_keys,
    fuzzy_percent,
    allow_fuzzy=True,
    keys_by_length=None,
):
    """Look up a translation in one mapping using exact and optional fuzzy matching."""
    if not mapping:
        return None, None, None, None

    for variant in message_variants(message):
        if variant in mapping:
            return finalize_translation(mapping[variant], variant), 'exact', variant, None

    if allow_fuzzy and fuzzy_percent > 0:
        for variant in message_variants(message):
            hebrew, matched_key = find_fuzzy_match(
                variant,
                mapping_keys,
                mapping,
                fuzzy_percent,
                keys_by_length,
            )
            if hebrew is not None:
                return finalize_translation(hebrew, variant), 'fuzzy', variant, matched_key

    return None, None, None, None


def lookup_translation(
    message,
    csv_mapping,
    csv_keys,
    txt_mapping,
    txt_keys,
    fuzzy_percent=FUZZY_MAX_PERCENT,
    csv_keys_by_length=None,
    txt_keys_by_length=None,
):
    """Look up a translation, preferring CSV over TXT mapping."""
    if csv_mapping:
        translated, match_type, variant, matched_key = lookup_in_mapping(
            message,
            csv_mapping,
            csv_keys,
            fuzzy_percent,
            allow_fuzzy=True,
            keys_by_length=csv_keys_by_length,
        )
        if translated:
            return translated, match_type, variant, matched_key

        translated, match_type, variant, matched_key = lookup_in_mapping(
            message,
            txt_mapping,
            txt_keys,
            fuzzy_percent,
            allow_fuzzy=False,
            keys_by_length=txt_keys_by_length,
        )
        if translated:
            return translated, match_type, variant, matched_key
        return None, None, None, None

    return lookup_in_mapping(
        message,
        txt_mapping,
        txt_keys,
        fuzzy_percent,
        allow_fuzzy=True,
        keys_by_length=txt_keys_by_length,
    )


def read_char(stream):
    c = stream.read(1)
    if not c:
        raise EOFError('Got Nothing')
    return c


def safe_readcstr(stream):
    bound_read = iter(partial(read_char, stream), b'')
    return b''.join(takewhile(partial(operator.ne, b'\00'), bound_read))


def loop_strings(stream):
    while True:
        try:
            yield safe_readcstr(stream).decode(ENCODING_IN)
        except EOFError:
            break


def load_mapping(mapping_file, existing=None):
    """Load translation mapping from file."""
    existing = existing or {}
    mapping = {}
    added = 0
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if '===' not in line:
                continue
            
            parts = line.split('===', 1)
            if len(parts) == 2:
                english = parts[0].strip()
                hebrew = parts[1].strip()
                if english and hebrew:
                    if english in existing or english in mapping:
                        continue
                    if english.strip() in existing or english.strip() in mapping:
                        continue
                    mapping[english] = hebrew
                    mapping[english.strip()] = hebrew
                    added += 1
    
    print(f"Loaded {added} translations from mapping file")
    return mapping


def load_csv_mapping(csv_file, existing=None):
    """Load translation mapping from CSV (English field 10, Hebrew field 11)."""
    existing = existing or {}
    mapping = {}
    added = 0

    with open(csv_file, 'r', encoding='windows-1255', newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header row
        for row in reader:
            if len(row) < 11:
                continue

            english = row[9].strip()
            hebrew = row[10].strip()
            if not english or not hebrew:
                continue

            if english in existing or english in mapping:
                continue
            if english.strip() in existing or english.strip() in mapping:
                continue

            mapping[english] = hebrew
            mapping[english.strip()] = hebrew
            added += 1

    print(f"Loaded {added} translations from CSV file")
    return mapping


def record_fuzzy_csv_update(updates, conflicts, matched_key, game_message):
    """Record a CSV English fix from a fuzzy game-message match."""
    if matched_key in updates:
        if updates[matched_key] != game_message:
            conflicts.append((matched_key, updates[matched_key], game_message))
        return

    for existing_key, existing_message in updates.items():
        if existing_key.strip() == matched_key.strip() and existing_message != game_message:
            conflicts.append((matched_key, existing_message, game_message))
            return

    updates[matched_key] = game_message


def apply_csv_fuzzy_updates(csv_file, updates):
    """Replace CSV English (field 10) with exact game text for fuzzy matches."""
    if not updates:
        return 0

    csv_path = Path(csv_file)
    with open(csv_path, 'r', encoding='windows-1255', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    lookup = {}
    for matched_key, game_message in updates.items():
        lookup[matched_key] = game_message
        lookup[matched_key.strip()] = game_message

    updated_rows = 0
    for row in rows:
        if len(row) < 11:
            continue

        english = row[9]
        new_english = lookup.get(english)
        if new_english is None:
            new_english = lookup.get(english.strip())
        if new_english is None or english == new_english:
            continue

        row[9] = new_english
        updated_rows += 1

    if updated_rows == 0:
        return 0

    with open(csv_path, 'w', encoding='windows-1255', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    return updated_rows


def is_covered_by_csv(
    message,
    csv_mapping,
    csv_keys,
    fuzzy_percent=FUZZY_MAX_PERCENT,
    csv_keys_by_length=None,
):
    """Return True if CSV would translate this message (exact or fuzzy)."""
    translated, _, _, _ = lookup_in_mapping(
        message,
        csv_mapping,
        csv_keys,
        fuzzy_percent,
        allow_fuzzy=True,
        keys_by_length=csv_keys_by_length,
    )
    return translated is not None


def write_unique_messages(
    mapping_file,
    csv_mapping,
    csv_keys,
    csv_keys_by_length=None,
    unique_file=None,
    fuzzy_percent=FUZZY_MAX_PERCENT,
):
    """Write mapping messages not covered by CSV (exact or fuzzy)."""
    if unique_file is None:
        unique_file = Path(mapping_file).with_name('unique_messages.txt')

    unique_path = Path(unique_file)
    unique_path.parent.mkdir(parents=True, exist_ok=True)

    unique_count = 0
    seen = set()
    checked = 0

    print(f"Generating {unique_path} (fuzzy {fuzzy_percent}%)...")
    with open(unique_path, 'w', encoding='utf-8') as out_file:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if '===' not in line:
                    continue

                parts = line.split('===', 1)
                if len(parts) != 2:
                    continue

                english = parts[0]
                hebrew = parts[1].strip()
                english_stripped = english.strip()
                if not english_stripped or not hebrew:
                    continue
                if english_stripped in seen:
                    continue

                checked += 1
                if checked % 500 == 0:
                    print(f"  Checked {checked} mapping entries, {unique_count} unique so far...")

                if is_covered_by_csv(
                    english,
                    csv_mapping,
                    csv_keys,
                    fuzzy_percent,
                    csv_keys_by_length,
                ):
                    continue

                seen.add(english_stripped)
                out_file.write(english)
                out_file.write('\n')
                out_file.flush()
                unique_count += 1

    print(f"  Unique mapping messages: {unique_count}")
    print(f"  Unique messages report: {unique_path}")
    return unique_count


def format_message_for_output(message):
    """Format a message as a single line for the not-found report."""
    return message.replace('\r', '\\r').replace('\n', '\\n')


def write_not_found_messages(not_found_messages, not_found_file):
    """Write unique not-found messages to a text file."""
    not_found_path = Path(not_found_file)
    not_found_path.parent.mkdir(parents=True, exist_ok=True)

    with open(not_found_path, 'w', encoding='utf-8') as f:
        for message in not_found_messages:
            f.write(format_message_for_output(message))
            f.write('\n')

    print(f"  Not found messages: {len(not_found_messages)}")
    print(f"  Not found report: {not_found_path}")


def apply_translations(
    input_dir,
    output_dir,
    mapping_file,
    csv_file=None,
    fuzzy_percent=FUZZY_MAX_PERCENT,
    not_found_file=None,
    unique_messages_file=None,
    update_csv=True,
):
    """Apply translations from mapping file to text files."""

    if not_found_file is None:
        not_found_file = Path(mapping_file).with_name('not_found_messages.txt')

    # Load mappings separately so CSV wins over TXT (exact and fuzzy)
    csv_mapping = load_csv_mapping(csv_file) if csv_file else {}
    csv_keys = list(dict.fromkeys(csv_mapping.keys()))
    csv_keys_by_length = build_keys_by_length(csv_keys) if csv_mapping else None
    txt_mapping = load_mapping(mapping_file, existing=csv_mapping)
    txt_keys = list(dict.fromkeys(txt_mapping.keys()))
    txt_keys_by_length = build_keys_by_length(txt_keys) if txt_mapping else None
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all text files
    filenames = [filename for pattern in TEXTS_PATTERNS for filename in Path(input_dir).glob(pattern)]
    
    if not filenames:
        print(f"No text files found in {input_dir}")
        return
    
    print(f"Found {len(filenames)} text files")
    print()
    
    total_messages = 0
    translated_messages = 0
    fuzzy_messages = 0
    not_found_messages = []
    not_found_seen = set()
    fuzzy_csv_updates = {}
    fuzzy_csv_conflicts = []
    
    for filename in sorted(filenames):
        #print(f"Processing {filename.name}...")
        
        # Read all messages from input file
        messages = []
        with open(filename, 'rb') as f:
            for idx, message in enumerate(loop_strings(f)):
                # Skip the Sierra header
                if idx == 0:
                    if message.encode(ENCODING_IN) == SIERRA_TEXT_HEADER:
                        continue
                messages.append(message)
        
        # Create output file
        output_file = output_path / filename.name
        
        with open(output_file, 'wb') as out_file:
            # Write Sierra header
            out_file.write(SIERRA_TEXT_HEADER)
            out_file.write(b'\0')
            
            # Write translated messages
            file_translated = 0
            for message in messages:
                # Ignore empty messages
                if not message.strip():
                    out_file.write(b'\0')
                    continue
                total_messages += 1
                
                translated, match_type, variant, matched_key = lookup_translation(
                    message,
                    csv_mapping,
                    csv_keys,
                    txt_mapping,
                    txt_keys,
                    fuzzy_percent,
                    csv_keys_by_length,
                    txt_keys_by_length,
                )
                
                if translated:
                    translated_messages += 1
                    file_translated += 1
                    if match_type == 'fuzzy':
                        fuzzy_messages += 1
                        max_edits = max_edits_for_length(len(variant), fuzzy_percent)
                        distance = levenshtein_distance(variant, matched_key, max_edits)
                        print(
                            f"FUZZY ({distance}/{max_edits}): |{variant}| -> |{matched_key}|"
                        )
                        if csv_file and update_csv and matched_key:
                            record_fuzzy_csv_update(
                                fuzzy_csv_updates,
                                fuzzy_csv_conflicts,
                                matched_key,
                                message,
                            )
                else:
                    if message not in not_found_seen:
                        not_found_seen.add(message)
                        not_found_messages.append(message)
                    translated = message
                
                # Write message
                #print(f"DEBUG: Original: {repr(translated)}")
                out_file.write(str.encode(translated, ENCODING_OUT))
                out_file.write(b'\0')
        
        #print(f"  {filename.name}: {file_translated}/{len(messages)} messages translated")
    
    print()
    print(f"Translation complete!")
    print(f"  Total messages: {total_messages}")
    print(f"  Translated: {translated_messages} ({100*translated_messages//total_messages if total_messages > 0 else 0}%)")
    print(f"  Fuzzy matches: {fuzzy_messages}")
    print(f"  Output directory: {output_dir}")
    write_not_found_messages(not_found_messages, not_found_file)

    if csv_file and update_csv and fuzzy_csv_updates:
        updated_rows = apply_csv_fuzzy_updates(csv_file, fuzzy_csv_updates)
        print(f"  CSV rows updated from fuzzy matches: {updated_rows}")
        print(f"  Updated CSV file: {csv_file}")
        csv_mapping = load_csv_mapping(csv_file)
        csv_keys = list(dict.fromkeys(csv_mapping.keys()))
        csv_keys_by_length = build_keys_by_length(csv_keys) if csv_mapping else None
    elif csv_file and update_csv:
        print("  CSV rows updated from fuzzy matches: 0")

    if fuzzy_csv_conflicts:
        print(f"  CSV fuzzy update conflicts: {len(fuzzy_csv_conflicts)}")
        for matched_key, existing_message, new_message in fuzzy_csv_conflicts[:10]:
            print(f"    conflict for |{matched_key}|")
            print(f"      kept: |{existing_message}|")
            print(f"      skipped: |{new_message}|")
        if len(fuzzy_csv_conflicts) > 10:
            print(f"    ... and {len(fuzzy_csv_conflicts) - 10} more conflicts")

    if csv_file:
        write_unique_messages(
            mapping_file,
            csv_mapping,
            csv_keys,
            csv_keys_by_length,
            unique_file=unique_messages_file,
            fuzzy_percent=fuzzy_percent,
        )


def main():
    parser = argparse.ArgumentParser(
        description='Apply translations from mapping file to SCI text files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  python translate_texts.py kq4_resources kq4_work translations.txt
  python translate_texts.py qfg1_resources qfg1_work translations.txt --csv QFG1_Hebrew.csv

Mapping file format (one per line):
  English message===Hebrew message

CSV mapping format (preferred when --csv is given):
  Field 10 = English (en), field 11 = Hebrew (he)
  CSV is checked first (exact and fuzzy). TXT is used only for exact matches
  not already covered by CSV.
  Fuzzy CSV matches update the CSV English text to the exact game message.
        '''
    )
    
    parser.add_argument('input_dir', help='Directory containing input text.* or *.tex files')
    parser.add_argument('output_dir', help='Directory to write translated text files')
    parser.add_argument('mapping_file', help='Translation mapping file (format: english===hebrew)')
    parser.add_argument(
        '--csv',
        metavar='CSV_FILE',
        help='Optional CSV file with translations (English col 10, Hebrew col 11); preferred over mapping file',
    )
    parser.add_argument(
        '--fuzzy-distance',
        type=int,
        default=FUZZY_MAX_PERCENT,
        metavar='PCT',
        help='Allow fuzzy matching up to PCT%% of message length (default: 10, use 0 to disable)',
    )
    parser.add_argument(
        '--no-update-csv',
        action='store_true',
        help='Do not write fuzzy-match corrections back into the CSV file',
    )
    parser.add_argument(
        '--not-found',
        metavar='FILE',
        help='Write unmatched messages to this file (default: not_found_messages.txt next to mapping file)',
    )
    parser.add_argument(
        '--unique-messages',
        metavar='FILE',
        help='Write TXT-only mapping messages to this file (default: unique_messages.txt next to mapping file; requires --csv)',
    )
    
    args = parser.parse_args()
    
    try:
        apply_translations(
            args.input_dir,
            args.output_dir,
            args.mapping_file,
            args.csv,
            args.fuzzy_distance,
            args.not_found,
            args.unique_messages,
            update_csv=not args.no_update_csv,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
