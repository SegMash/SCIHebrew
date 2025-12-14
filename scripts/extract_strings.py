#!/usr/bin/env python3
"""
Extract hardcoded English strings from SCI script files.
Scans all .sc files in a folder and extracts strings between {...}.
"""

import argparse
import os
import re
from pathlib import Path


def extract_strings_from_file(file_path, delimiter='{}'):
    """
    Extract all strings between delimiters from a file.
    
    Args:
        file_path: Path to the .sc file
        delimiter: Delimiter type - '{}' for braces or '""' for quotes
        
    Returns:
        List of (string, line_number) tuples
    """
    strings = []
    
    # Build regex pattern based on delimiter
    if delimiter == '{}':
        # Match everything between { and }
        pattern = r'\{([^}]*)\}'
    elif delimiter == '""':
        # Match everything between quotes, GREEDY to get maximum length
        # This will match "abcd"efgh"ijk" as the whole string abcd"efgh"ijk
        # Using .+ (greedy) instead of .+? (non-greedy)
        pattern = r'"(.+)"'
    else:
        print(f"Error: Unsupported delimiter '{delimiter}'. Use '{{}}' or '\"\"'")
        return []
    
    try:
        with open(file_path, 'r', encoding='windows-1255', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                # Find all strings with the specified delimiter
                matches = re.finditer(pattern, line)
                for match in matches:
                    string_content = match.group(1)
                    if string_content.strip():  # Skip empty strings
                        strings.append((string_content, line_num))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return strings


def extract_all_strings(folder_path, output_file, include_duplicates=False, delimiter='{}'):
    """
    Extract all strings from all .sc files in a folder.
    
    Args:
        folder_path: Path to folder containing .sc files
        output_file: Path to output text file
        include_duplicates: If True, include duplicate strings
        delimiter: Delimiter type - '{}' for braces or '""' for quotes
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder does not exist: {folder_path}")
        return
    
    # Find all .sc files
    sc_files = sorted(folder.glob("*.sc"))
    
    if not sc_files:
        print(f"No .sc files found in {folder_path}")
        return
    
    print(f"Found {len(sc_files)} .sc files")
    print(f"Extracting strings...")
    
    all_strings = []
    seen_strings = set()
    
    for sc_file in sc_files:
        strings = extract_strings_from_file(sc_file, delimiter)
        
        for string_content, line_num in strings:
            if include_duplicates or string_content not in seen_strings:
                all_strings.append({
                    'string': string_content,
                    'file': sc_file.name,
                    'line': line_num
                })
                seen_strings.add(string_content)
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as out:
        if include_duplicates:
            # Include file and line information
            for item in all_strings:
                out.write(f"{item['string']}\t[{item['file']}:{item['line']}]\n")
        else:
            # Just the unique strings
            for item in all_strings:
                out.write(f"{item['string']}\n")
    
    print(f"\nExtraction complete!")
    print(f"Total strings extracted: {len(all_strings)}")
    if not include_duplicates:
        print(f"Unique strings: {len(seen_strings)}")
    print(f"Output file: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract hardcoded English strings from SCI script files (.sc)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Extract unique strings from braces
  python extract_strings.py kq4_resources/src output_strings.txt
  
  # Extract strings from quotes (greedy match)
  python extract_strings.py kq4_resources/src output_strings.txt --delimiter quotes
  
  # Extract all strings including duplicates with file/line info
  python extract_strings.py kq4_resources/src output_strings.txt --duplicates
        '''
    )
    
    parser.add_argument('folder', help='Path to folder containing .sc files')
    parser.add_argument('output', help='Path to output text file')
    parser.add_argument('--duplicates', action='store_true',
                        help='Include duplicate strings with file/line information')
    parser.add_argument('--delimiter', choices=['braces', 'quotes'], default='braces',
                        help='Delimiter type: "braces" for {...} (default), "quotes" for "..." (greedy match)')
    
    args = parser.parse_args()
    
    # Convert delimiter argument to symbol
    delimiter = '{}' if args.delimiter == 'braces' else '""'
    
    extract_all_strings(args.folder, args.output, args.duplicates, delimiter)


if __name__ == '__main__':
    main()
