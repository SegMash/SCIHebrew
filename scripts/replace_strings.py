#!/usr/bin/env python3
"""
Replace hardcoded English strings in SCI script files with Hebrew translations.
Reads a mapping file and replaces strings between {...} with Hebrew equivalents.
"""

import argparse
import os
import re
import shutil
from pathlib import Path


def load_mapping(mapping_file):
    """
    Load translation mapping from file.
    
    Args:
        mapping_file: Path to mapping file (format: english === hebrew)
        
    Returns:
        Dictionary mapping English strings to Hebrew strings
    """
    mapping = {}
    
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n')
                if '===' not in line:
                    continue
                
                parts = line.split(' === ', 1)
                if len(parts) == 2:
                    english = parts[0]
                    hebrew = parts[1]
                    if english and hebrew:
                        mapping[english] = hebrew
    except Exception as e:
        print(f"Error loading mapping file: {e}")
        return {}
    
    print(f"Loaded {len(mapping)} translations from mapping file")
    return mapping


def replace_strings_in_file(file_path, mapping, output_path):
    """
    Replace English strings with Hebrew in a single file.
    
    Args:
        file_path: Path to input .sc file
        mapping: Dictionary of English -> Hebrew translations
        output_path: Path to output file
        
    Returns:
        Number of replacements made
    """
    replacements = 0
    
    try:
        # Read file with windows-1255 encoding
        with open(file_path, 'r', encoding='windows-1255', errors='replace') as f:
            content = f.read()
        
        # Replace all strings between {...}
        def replace_match(match):
            nonlocal replacements
            english_text = match.group(1)
            
            # Try to find translation
            if english_text in mapping:
                replacements += 1
                return '{' + mapping[english_text] + '}'
            else:
                # No translation found - keep original
                return match.group(0)
        
        # Replace all {...} patterns
        new_content = re.sub(r'\{([^}]*)\}', replace_match, content)
        
        # Only write output file if replacements were made
        if replacements > 0:
            with open(output_path, 'w', encoding='windows-1255', errors='replace') as f:
                f.write(new_content)
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0
    
    return replacements


def replace_all_strings(src_folder, output_folder, mapping_file, backup=True):
    """
    Replace strings in all .sc files in a folder.
    
    Args:
        src_folder: Path to folder containing source .sc files
        output_folder: Path to output folder
        mapping_file: Path to mapping file
        backup: If True, create backup of original files
    """
    src_path = Path(src_folder)
    output_path = Path(output_folder)
    
    if not src_path.exists():
        print(f"Error: Source folder does not exist: {src_folder}")
        return
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load mapping
    mapping = load_mapping(mapping_file)
    if not mapping:
        print("No translations loaded. Exiting.")
        return
    
    # Find all .sc files
    sc_files = sorted(src_path.glob("*.sc"))
    
    if not sc_files:
        print(f"No .sc files found in {src_folder}")
        return
    
    print(f"Found {len(sc_files)} .sc files")
    print(f"Processing files...")
    print()
    
    total_replacements = 0
    files_modified = 0
    
    for sc_file in sc_files:
        output_file = output_path / sc_file.name
        
        # Replace strings (this writes the file only if replacements > 0)
        replacements = replace_strings_in_file(sc_file, mapping, output_file)
        
        if replacements > 0:
            # Create backup from SOURCE file only if we actually modified it
            if backup:
                backup_file = output_path / (sc_file.name + '.bak')
                # Backup the original source file (not the output)
                shutil.copy2(sc_file, backup_file)
            
            print(f"  {sc_file.name}: {replacements} replacements")
            files_modified += 1
            total_replacements += replacements
    
    print()
    print(f"Translation complete!")
    print(f"Files processed: {len(sc_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total replacements: {total_replacements}")
    print(f"Output folder: {output_folder}")


def main():
    parser = argparse.ArgumentParser(
        description='Replace hardcoded English strings in SCI script files with Hebrew translations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Replace strings and save to output folder
  python replace_strings.py kq4_resources/src kq4_hebrew/src mapping.txt
  
  # Replace without creating backups
  python replace_strings.py kq4_resources/src kq4_hebrew/src mapping.txt --no-backup

Mapping file format (one per line):
  English message === Hebrew message
  
Output files are encoded in windows-1255 for Hebrew support.
        '''
    )
    
    parser.add_argument('src_folder', help='Path to folder containing source .sc files')
    parser.add_argument('output_folder', help='Path to output folder for modified files')
    parser.add_argument('mapping_file', help='Path to translation mapping file')
    parser.add_argument('--no-backup', action='store_true',
                        help='Do not create backup files (.bak)')
    
    args = parser.parse_args()
    
    replace_all_strings(args.src_folder, args.output_folder, args.mapping_file, 
                       backup=not args.no_backup)


if __name__ == '__main__':
    main()
