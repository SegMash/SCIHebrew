#!/usr/bin/env python
"""
Script to merge split hebrew text files back into a single output file.
Looks for files matching the pattern single_messages_*_part<x>_hebrew.txt
in the given directory, merges them in numeric order of <x>.
"""

import os
import re
import argparse
import sys


def merge_files(parts_dir, output_file):
    """
    Merge split hebrew part files into a single output file.

    Args:
        parts_dir (str): Directory containing the part files
        output_file (str): Full path of the merged output file
    """
    # Find all matching files
    pattern = re.compile(r'^single_messages_part(\d+)_hebrew\.txt$', re.IGNORECASE)

    part_files = []
    for filename in os.listdir(parts_dir):
        m = pattern.match(filename)
        if m:
            part_number = int(m.group(1))
            part_files.append((part_number, filename))

    if not part_files:
        print(f"No matching part files found in: {parts_dir}")
        sys.exit(1)

    # Sort by part number
    part_files.sort(key=lambda x: x[0])

    print(f"Found {len(part_files)} part file(s) in: {parts_dir}")
    for num, name in part_files:
        print(f"  part{num}: {name}")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Merge all parts into the output file
    total_lines = 0
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for part_number, filename in part_files:
            filepath = os.path.join(parts_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as in_f:
                lines = in_f.readlines()
            out_f.writelines(lines)
            total_lines += len(lines)
            print(f"  Merged part{part_number} ({len(lines)} lines)")

    print(f"Merge complete! {total_lines} total lines written to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Merge single_messages_*_part<x>_hebrew.txt files into a single output file.'
    )
    parser.add_argument('parts_dir', help='Directory containing the hebrew part files')
    parser.add_argument('output_file', help='Full path of the merged output file')
    args = parser.parse_args()

    if not os.path.isdir(args.parts_dir):
        print(f"Error: parts directory does not exist: {args.parts_dir}")
        sys.exit(1)

    merge_files(args.parts_dir, args.output_file)


if __name__ == '__main__':
    main()
