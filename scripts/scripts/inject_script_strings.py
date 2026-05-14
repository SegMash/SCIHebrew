#!/usr/bin/env python3
"""Inject (translated) strings back into a binary script file.

Format of the input strings file (same as produced by extract_script_strings.py):
    <hex_offset><TAB><string text>

Rules:
  - If the new string (encoded) is LONGER than the original slot, print an error
    with the line number and exit immediately.
  - If the new string (encoded) is SHORTER than the original slot, pad with
    spaces (0x20) on the right so the slot length is preserved.
  - The null terminator at the end of each slot is always kept.

Usage:
    python inject_script_strings.py <original_strings_file> <translated_strings_file> <binary_file> [--encoding ENC]
"""

import argparse
import sys
from pathlib import Path


ENCODING = 'windows-1255'
NULL = b'\x00'


def parse_strings_file(path):
    """Return list of (offset, text, raw_line_number)."""
    entries = []
    with open(path, encoding='utf-8') as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.rstrip('\n')
            if not line.strip():
                continue
            # Support both TAB-separated and single-space-separated (first token = offset)
            if '\t' in line:
                hex_offset, text = line.split('\t', 1)
            else:
                parts = line.split(' ', 1)
                hex_offset = parts[0]
                text = parts[1] if len(parts) > 1 else ''
            try:
                offset = int(hex_offset.strip(), 16)
            except ValueError:
                print(f'ERROR: line {lineno}: cannot parse offset "{hex_offset.strip()}"')
                sys.exit(1)
            entries.append((offset, text, lineno))
    return entries


def encode_string(text, encoding):
    return text.encode(encoding)


def compute_slot_length(data, offset):
    """Return the number of bytes from offset up to and including the NUL terminator."""
    start = offset
    while offset < len(data):
        if data[offset] == 0:
            return offset - start + 1  # +1 for the NUL
        offset += 1
    raise ValueError(f'No NUL terminator found starting at offset {hex(start)}')


def inject(original_file, translated_strings_file, source_strings_file, encoding):
    data = bytearray(Path(original_file).read_bytes())

    orig_entries = parse_strings_file(source_strings_file)
    tran_entries = parse_strings_file(translated_strings_file)

    if len(orig_entries) != len(tran_entries):
        print(f'ERROR: original strings file has {len(orig_entries)} entries '
              f'but translated file has {len(tran_entries)} entries.')
        sys.exit(1)

    errors = []
    for (orig_offset, orig_text, orig_lineno), (tran_offset, tran_text, tran_lineno) in zip(orig_entries, tran_entries):
        if orig_offset != tran_offset:
            print(f'WARNING: line {tran_lineno}: offset mismatch '
                  f'(original {hex(orig_offset)}, translated {hex(tran_offset)}) – using original offset.')

        offset = orig_offset
        slot_len = compute_slot_length(data, offset)
        payload_len = slot_len - 1  # bytes available for text (excluding NUL)

        new_bytes = encode_string(tran_text, encoding)

        if len(new_bytes) > payload_len:
            errors.append(
                f'line {tran_lineno}: "{tran_text[:40]}..." is {len(new_bytes)} bytes '
                f'but the slot at {hex(offset)} only holds {payload_len} bytes.'
            )
            continue

        # Write text, then pad with spaces, then NUL terminator
        padded = new_bytes + b'\x20' * (payload_len - len(new_bytes)) + NULL
        assert len(padded) == slot_len
        data[offset:offset + slot_len] = padded

    if errors:
        print('ERROR: the following strings are too long – binary was NOT modified:')
        for err in errors:
            print(f'  {err}')
        sys.exit(1)

    Path(original_file).write_bytes(data)
    print(f'Injected {len(orig_entries)} strings into {original_file}')


def main():
    parser = argparse.ArgumentParser(
        description='Inject translated strings back into a binary SCI script file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('source_strings_file',
                        help='Original strings file produced by extract_script_strings.py')
    parser.add_argument('translated_strings_file',
                        help='Translated strings file (same format, same offsets)')
    parser.add_argument('binary_file',
                        help='Binary script file to modify in-place')
    parser.add_argument('--encoding', default=ENCODING,
                        help='Encoding used to encode the new strings')

    args = parser.parse_args()
    inject(args.binary_file, args.translated_strings_file, args.source_strings_file, args.encoding)


if __name__ == '__main__':
    main()
