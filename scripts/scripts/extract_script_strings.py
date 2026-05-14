#!/usr/bin/env python3

"""Extract null-terminated strings from a binary slice.

This is intended for SCI script resources or similar binary files where a string
section can be identified by absolute file offsets.
"""

import argparse
from pathlib import Path


def decode_bytes(data, encoding):
    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        return data.decode('latin1', errors='replace')


def extract_strings_from_range(binary_path, start_offset, end_offset, encoding='windows-1255'):
    data = Path(binary_path).read_bytes()

    if start_offset < 0 or end_offset < 0:
        raise ValueError('Offsets must be non-negative')
    if end_offset <= start_offset:
        raise ValueError('End offset must be greater than start offset')
    if start_offset >= len(data):
        return []

    end_offset = min(end_offset, len(data))
    chunk = data[start_offset:end_offset]

    results = []
    current = bytearray()
    current_start = None

    for index, byte in enumerate(chunk):
        if byte == 0:
            if current:
                text = decode_bytes(bytes(current), encoding).strip()
                if text:
                    results.append({
                        'offset': start_offset + current_start,
                        'text': text,
                    })
                current.clear()
                current_start = None
            continue

        if current_start is None:
            current_start = index
        current.append(byte)

    if current:
        text = decode_bytes(bytes(current), encoding).strip()
        if text:
            results.append({
                'offset': start_offset + current_start,
                'text': text,
            })

    return results


def write_strings(output_path, strings, include_offsets=True):
    with open(output_path, 'w', encoding='utf-8', newline='') as out_file:
        for item in strings:
            if include_offsets:
                out_file.write(f"{hex(item['offset'])}\t{item['text']}\n")
            else:
                out_file.write(f"{item['text']}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Extract null-terminated strings from a binary range',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('binary_file', help='Path to the binary script/resource file')
    parser.add_argument('start_offset', help='Start offset in hex (for example 0x9be) or decimal')
    parser.add_argument('end_offset', help='End offset in hex (for example 0xa5a) or decimal')
    parser.add_argument('output_file', help='Path to write the extracted strings')
    parser.add_argument('--encoding', default='windows-1255', help='Text encoding to use when decoding strings')
    parser.add_argument('--no-offsets', action='store_true', help='Write only strings, not offsets')

    args = parser.parse_args()

    start_offset = int(args.start_offset, 0)
    end_offset = int(args.end_offset, 0)

    strings = extract_strings_from_range(
        args.binary_file,
        start_offset,
        end_offset,
        encoding=args.encoding,
    )
    write_strings(args.output_file, strings, include_offsets=not args.no_offsets)

    print(f'Extracted {len(strings)} strings to {args.output_file}')


if __name__ == '__main__':
    main()