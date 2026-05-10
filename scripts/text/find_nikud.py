#!/usr/bin/env python3
"""
Find lines containing Hebrew nikud (vowel marks, U+05B0–U+05C7) in a file.

Usage:
    python find_nikud.py messages.json
    python find_nikud.py messages.json --show-text   # also print the matching line
"""

import argparse
import re
import sys

NIKUD_RE = re.compile(r'[\u05B0-\u05C7]')


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('file', help='file to scan')
    parser.add_argument('--show-text', '-s', action='store_true',
                        help='also print the content of each matching line')
    args = parser.parse_args()

    found = 0
    with open(args.file, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            if NIKUD_RE.search(line):
                found += 1
                if args.show_text:
                    print(f"Line {lineno}: {line.rstrip()}")
                else:
                    print(f"Line {lineno}")

    if found == 0:
        print("No nikud found.")
    else:
        print(f"\nTotal: {found} line(s) with nikud.")


if __name__ == '__main__':
    main()
