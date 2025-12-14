#!/usr/bin/env python3
"""
Simple text extractor - Extracts all messages from SCI text files to plain text files.
"""

import argparse
import operator
from functools import partial
from itertools import takewhile
from pathlib import Path

ENCODING = 'windows-1252'
SIERRA_TEXT_HEADER = b'\x83'
TEXTS_PATTERNS = ["text.*", "*.tex"]


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
            yield safe_readcstr(stream).decode(ENCODING)
        except EOFError:
            break


def extract_texts(gamedir, output_single, output_multi, output_format):
    # Find all text files
    filenames = [filename for pattern in TEXTS_PATTERNS for filename in Path(gamedir).glob(pattern)]
    
    if not filenames:
        print(f"No text files found in {gamedir}")
        return
    
    print(f"Found {len(filenames)} text files")
    
    single_line_count = 0
    multi_line_count = 0
    format_count = 0
    seen_messages = set()
    
    with open(output_single, 'w', encoding='utf-8') as single_file, \
         open(output_multi, 'w', encoding='utf-8') as multi_file, \
         open(output_format, 'w', encoding='utf-8') as format_file:
        
        for filename in sorted(filenames):
            print(f"Processing {filename.name}...")
            
            with open(filename, 'rb') as f:
                for idx, message in enumerate(loop_strings(f)):
                    # Skip the Sierra header
                    if idx == 0:
                        if message.encode(ENCODING) == SIERRA_TEXT_HEADER:
                            continue
                    
                    # Skip empty messages
                    if message.strip() == '':
                        continue
                    
                    # Skip duplicate messages
                    if message in seen_messages:
                        continue
                    seen_messages.add(message)
                    
                    # Check if message contains line breaks
                    if '\n' in message or '\r' in message:
                        # Multi-line message (takes priority over format strings)
                        multi_file.write(message)
                        multi_file.write('\n=====\n')
                        multi_line_count += 1
                    # Check if message contains format specifiers
                    elif '%' in message:
                        # Format string message (single-line only)
                        format_file.write(message)
                        format_file.write('\n')
                        format_count += 1
                    else:
                        # Single-line message
                        single_file.write(message)
                        single_file.write('\n')
                        single_line_count += 1
    
    print(f"\nExtraction complete!")
    print(f"  Single-line messages: {single_line_count} -> {output_single}")
    print(f"  Multi-line messages: {multi_line_count} -> {output_multi}")
    print(f"  Format string messages: {format_count} -> {output_format}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract all text messages from SCI text files to plain text files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  python extract_texts.py kq4_gog output_texts.txt output_texts_multi.txt output_format.txt
        '''
    )
    
    parser.add_argument('gamedir', help='Directory containing text.* or *.tex files')
    parser.add_argument('output_single', help='Output file for single-line messages')
    parser.add_argument('output_multi', help='Output file for multi-line messages')
    parser.add_argument('output_format', help='Output file for messages with % format specifiers')
    
    args = parser.parse_args()
    
    try:
        extract_texts(args.gamedir, args.output_single, args.output_multi, args.output_format)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
