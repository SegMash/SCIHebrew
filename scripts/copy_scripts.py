#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copy script files based on scripts.list file.
Reads a scripts.list file and copies corresponding script.XXX files from source to target folder.
"""

import os
import sys
import shutil
import argparse


def copy_scripts(scripts_list_path, source_folder, target_folder):
    """
    Copy script files from source to target folder based on scripts.list.
    
    Args:
        scripts_list_path: Path to the scripts.list file
        source_folder: Source folder containing script.XXX files
        target_folder: Target folder where files will be copied
    """
    # Check if scripts.list exists
    if not os.path.exists(scripts_list_path):
        print(f"Error: scripts.list file not found: {scripts_list_path}")
        return False
    
    # Check if source folder exists
    if not os.path.exists(source_folder):
        print(f"Error: Source folder not found: {source_folder}")
        return False
    
    # Create target folder if it doesn't exist
    if not os.path.exists(target_folder):
        print(f"Creating target folder: {target_folder}")
        os.makedirs(target_folder, exist_ok=True)
    
    # Read scripts.list
    with open(scripts_list_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process each line
    copied_count = 0
    skipped_count = 0
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Construct source and target file paths
        script_filename = f"script.{line}"
        source_file = os.path.join(source_folder, script_filename)
        target_file = os.path.join(target_folder, script_filename)
        
        # Check if source file exists
        if not os.path.exists(source_file):
            print(f"Warning: Source file not found, skipping: {script_filename}")
            skipped_count += 1
            continue
        
        # Copy the file
        try:
            shutil.copy2(source_file, target_file)
            print(f"Copied: {script_filename}")
            copied_count += 1
        except Exception as e:
            print(f"Error copying {script_filename}: {e}")
            skipped_count += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files copied: {copied_count}")
    print(f"  Files skipped: {skipped_count}")
    print(f"  Total processed: {copied_count + skipped_count}")
    print(f"{'='*60}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Copy script files based on scripts.list file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s scripts.list source_folder target_folder
  %(prog)s output_kq4/scripts.list kq4_gog/src kq4_gog/src_backup
        '''
    )
    
    parser.add_argument('scripts_list', help='Path to scripts.list file')
    parser.add_argument('source_folder', help='Source folder containing script.XXX files')
    parser.add_argument('target_folder', help='Target folder where files will be copied')
    
    args = parser.parse_args()
    
    print(f"Copying scripts from scripts.list...")
    print(f"  Scripts list: {args.scripts_list}")
    print(f"  Source folder: {args.source_folder}")
    print(f"  Target folder: {args.target_folder}")
    print()
    
    success = copy_scripts(args.scripts_list, args.source_folder, args.target_folder)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
