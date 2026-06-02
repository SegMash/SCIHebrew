# coding=utf-8

"""
    mapping_to_json_sci0.py

    SCI0 variant that converts *-mapping.txt files to a single messages.json file.

    Input file format per line:
        <original text> === <translated text>

    Filename pattern:
        <logicFile>-mapping.txt
        <logicFile>_mapping.txt

    For each mapping file:
    - logicFile = filename prefix before "-mapping.txt" or "_mapping.txt"
      - messageNumber = sequence starting from 1 (per file)
"""

import json
import os
import re
import sys
from datetime import datetime, timezone


def extract_placeholders(text):
    """Extract placeholders like %s, %d, %w1, %m8 from text."""
    pattern = r'%[a-zA-Z]\d*'
    return re.findall(pattern, text)


def parse_mapping_file(mapping_filepath, logic_file):
    """Parse one mapping file and return message entries for it."""
    messages = []

    with open(mapping_filepath, 'r', encoding='utf-8') as infile:
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue

            if ' === ' not in line:
                print(f"  Warning: Line {line_num} does not contain ' === ' delimiter. Skipping.")
                continue

            original, translation = line.split(' === ', 1)
            original = original.strip()
            translation = translation.strip()

            placeholders_original = extract_placeholders(original)
            placeholders_translation = extract_placeholders(translation)

            all_placeholders = placeholders_original.copy()
            for placeholder in placeholders_translation:
                if placeholder not in all_placeholders:
                    all_placeholders.append(placeholder)

            message = {
                "logicFile": logic_file,
                "messageNumber": len(messages) + 1,
                "original": original,
                "translation": translation,
                "notes": "",
                "placeholders": all_placeholders,
            }
            messages.append(message)

    return messages


def find_sci0_mapping_files(directory):
    """Find all files matching <prefix>[-_]mapping.txt and return (filename, prefix)."""
    pattern = re.compile(r'^(?P<prefix>.+)[_-]mapping\.txt$')
    matches = []

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            matches.append((filename, match.group('prefix')))

    # Deterministic output order
    matches.sort(key=lambda item: item[0].lower())
    return matches


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python mapping_to_json_sci0.py <directory> [game-name]")
        print("   -> directory: path to directory containing *-mapping.txt or *_mapping.txt files")
        print("   -> game-name: optional game name for metadata")
        sys.exit(1)

    directory = sys.argv[1]
    game_name = sys.argv[2] if len(sys.argv) == 3 else ""

    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        sys.exit(1)

    mapping_files = find_sci0_mapping_files(directory)
    if not mapping_files:
        print(f"No *-mapping.txt or *_mapping.txt files found in directory '{directory}'.")
        sys.exit(1)

    print(f"Found {len(mapping_files)} mapping file(s):")
    for filename, logic_file in mapping_files:
        print(f"  - {filename} (logicFile={logic_file})")

    all_messages = []
    for filename, logic_file in mapping_files:
        mapping_filepath = os.path.join(directory, filename)
        print(f"Processing {filename}...")

        try:
            file_messages = parse_mapping_file(mapping_filepath, logic_file)
            all_messages.extend(file_messages)
            print(f"  Added {len(file_messages)} messages")
        except FileNotFoundError:
            print(f"  Error: The file '{mapping_filepath}' was not found.")
            continue
        except Exception as exc:
            print(f"  Error processing {filename}: {exc}")
            continue

    output = {
        "version": "1.0",
        "metadata": {
            "gameName": game_name,
            "contentType": "messages",
            "sourceLanguage": "en",
            "targetLanguage": "he",
            "extractedDate": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "totalMessages": len(all_messages),
        },
        "messages": all_messages,
    }

    output_json = os.path.join(directory, "messages_old.json")
    with open(output_json, 'w', encoding='utf-8') as outfile:
        json.dump(output, outfile, ensure_ascii=False, indent=2)

    print()
    print(f"Successfully created '{output_json}' with {len(all_messages)} messages.")


if __name__ == "__main__":
    main()
