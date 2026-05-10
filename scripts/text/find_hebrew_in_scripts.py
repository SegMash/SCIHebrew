# coding=utf-8

"""
    find_hebrew_in_scripts.py

    This script scans .sc files for lines containing Hebrew letters (ASCII 224-250 in windows-1255).
"""
import os
import sys


def has_hebrew_letters(line):
    """
    Checks if a line contains Hebrew letters (Unicode range U+05D0 to U+05EA).
    
    Args:
        line (str): The line to check.
    
    Returns:
        bool: True if the line contains Hebrew letters, False otherwise.
    """
    for char in line:
        # Check if character is in the Hebrew Unicode range (U+05D0 to U+05EA)
        if '\u05D0' <= char <= '\u05EA':
            return True
    return False


def scan_script_files(directory):
    """
    Scans a directory for .sc files and finds lines with Hebrew text.
    
    Args:
        directory (str): The directory to scan.
    """
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' not found.")
        sys.exit(1)
    
    # Find all .sc files
    sc_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.sc'):
                sc_files.append(os.path.join(root, file))
    
    if not sc_files:
        print(f"No .sc files found in '{directory}'.")
        return
    
    print(f"Scanning {len(sc_files)} .sc file(s) for Hebrew text...\n")
    
    total_matches = 0
    files_with_hebrew = 0
    
    for sc_file in sorted(sc_files):
        file_matches = 0
        try:
            with open(sc_file, 'r', encoding='windows-1255') as f:
                for line_num, line in enumerate(f, 1):
                    line_stripped = line.rstrip('\n\r')
                    if has_hebrew_letters(line_stripped):
                        if file_matches == 0:
                            print(f"\n{sc_file}:")
                            print("-" * 80)
                        # Reverse the line for proper Hebrew display
                        print(f"  Line {line_num}: {line_stripped[::-1]}")
                        file_matches += 1
                        total_matches += 1
        except Exception as e:
            print(f"Error reading '{sc_file}': {e}")
        
        if file_matches > 0:
            files_with_hebrew += 1
    
    print(f"\n{'=' * 80}")
    print(f"Scan complete: {total_matches} line(s) with Hebrew text found in {files_with_hebrew} file(s).")


if __name__ == "__main__":
    # validate command line
    if len(sys.argv) != 2:
        print("Usage: python find_hebrew_in_scripts.py <scripts-directory>")
        print("   -> scripts-directory: directory containing .sc files")
        sys.exit(1)

    scripts_dir = sys.argv[1]
    scan_script_files(scripts_dir)
