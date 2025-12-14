#!/usr/bin/env python3
"""
Apply translations from mapping file to SCI text files.
Reads text files, looks up translations in mapping file, and creates new text files.
"""

import argparse
import operator
from functools import partial
from itertools import takewhile
from pathlib import Path

ENCODING_IN = 'windows-1252'
ENCODING_OUT = 'windows-1255'
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
            yield safe_readcstr(stream).decode(ENCODING_IN)
        except EOFError:
            break


def load_mapping(mapping_file):
    """Load translation mapping from file."""
    mapping = {}
    
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
                    # Store with original key
                    mapping[english] = hebrew
                    # Also store normalized version (stripped whitespace)
                    mapping[english.strip()] = hebrew
    
    print(f"Loaded {len(mapping)} translations from mapping file")
    return mapping


def apply_translations(input_dir, output_dir, mapping_file):
    """Apply translations from mapping file to text files."""
    
    # Load mapping
    mapping = load_mapping(mapping_file)
    
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
                total_messages += 1
                
                # Try multiple matching strategies
                translated = None
                
                # Convert actual newlines to literal \n for matching with mapping file
                message_with_literal_newlines = message.replace('\n', '\\n')
                
                #if "1643" in message:
                #    print(f"DEBUG: Message with '1643': {repr(message)}")
                #    print(f"DEBUG: With literal \\n: {repr(message_with_literal_newlines)}")
                #    if message in mapping:
                #        print(f"DEBUG: Found translation for message with '1643'")
                #    elif message_with_literal_newlines in mapping:
                #        print(f"DEBUG: Found translation with literal \\n")
                #    else:
                #        print(f"DEBUG: No translation found for message with '1643'")
                
                # Strategy 1: Exact match (with original newlines)
                if message in mapping:
                    translated = mapping[message]
                # Strategy 2: Match with literal \n
                elif message_with_literal_newlines in mapping:
                    translated = mapping[message_with_literal_newlines]
                    # Convert literal \n back to actual newlines in the translated text
                    translated = translated.replace('\\n', '\n')
                # Strategy 3: Strip whitespace (original)
                elif message.strip() in mapping:
                    translated = mapping[message.strip()]
                # Strategy 4: Strip whitespace (with literal \n)
                elif message_with_literal_newlines.strip() in mapping:
                    translated = mapping[message_with_literal_newlines.strip()]
                    translated = translated.replace('\\n', '\n')
                # Strategy 5: Normalize whitespace (collapse multiple spaces, strip)
                else:
                    normalized = ' '.join(message.split())
                    if normalized in mapping:
                        translated = mapping[normalized]
                
                if translated:
                    translated_messages += 1
                    file_translated += 1
                else:
                    # No translation found - use original
                    translated = message
                
                # Write message
                out_file.write(str.encode(translated, ENCODING_OUT))
                out_file.write(b'\0')
        
        #print(f"  {filename.name}: {file_translated}/{len(messages)} messages translated")
    
    print()
    print(f"Translation complete!")
    print(f"  Total messages: {total_messages}")
    print(f"  Translated: {translated_messages} ({100*translated_messages//total_messages if total_messages > 0 else 0}%)")
    print(f"  Output directory: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Apply translations from mapping file to SCI text files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  python translate_texts.py kq4_resources kq4_work translations.txt

Mapping file format (one per line):
  English message===Hebrew message
        '''
    )
    
    parser.add_argument('input_dir', help='Directory containing input text.* or *.tex files')
    parser.add_argument('output_dir', help='Directory to write translated text files')
    parser.add_argument('mapping_file', help='Translation mapping file (format: english===hebrew)')
    
    args = parser.parse_args()
    
    try:
        apply_translations(args.input_dir, args.output_dir, args.mapping_file)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
