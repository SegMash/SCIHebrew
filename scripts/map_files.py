#!/usr/bin/env python3
"""
File Mapper Script
Maps corresponding lines from two input files and creates a mapping output file.
The second file will be processed with text splitting using the specified max_length.

Usage: python map_files.py <input1> <input2> <output> [max_length] [--multiline]
"""

import sys
import os
import argparse

def split_messages(lines):
    """
    Split lines into messages using ===== as separator.
    Combines lines within each message with \\n.
    
    Args:
        lines: List of lines from file
        
    Returns:
        List of messages (each message is a string with \\n for line breaks)
    """
    messages = []
    current_message = []
    
    for line in lines:
        line = line.rstrip('\n\r')
        
        # Check if this is a separator line
        if line.strip() == '=====':
            # End of current message - join lines with \n
            if current_message:
                messages.append('\\n'.join(current_message))
                current_message = []
        else:
            # Add line to current message
            current_message.append(line)
    
    # Don't forget the last message if file doesn't end with separator
    if current_message:
        messages.append('\\n'.join(current_message))
    
    return messages

def map_files(input1_path, input2_path, output_path, max_length, multiline=False, append=False):
    """
    Read two input files and create a mapping file.
    
    Args:
        input1_path: Path to first input file
        input2_path: Path to second input file  
        output_path: Path to output mapping file
        max_length: Maximum length for text splitting
        multiline: If True, treat ===== as message separator and combine lines with \n
        append: If True, append to existing file instead of overwriting
    """
    try:
        # Read both input files
        with open(input1_path, 'r', encoding='utf-8') as f1:
            lines1 = f1.readlines()
        
        with open(input2_path, 'r', encoding='utf-8') as f2:
            lines2 = f2.readlines()
        
        if multiline:
            # Process files in multiline mode - split by ===== separator
            messages1 = split_messages(lines1)
            messages2 = split_messages(lines2)
            
            # Check if files have the same number of messages
            if len(messages1) != len(messages2):
                print(f"Warning: Files have different number of messages!")
                print(f"File 1: {len(messages1)} messages")
                print(f"File 2: {len(messages2)} messages")
                print("Proceeding with minimum number of messages...")
            
            # Use the minimum number of messages
            min_count = min(len(messages1), len(messages2))
            
            # Create or append to the mapping file
            file_mode = 'a' if append else 'w'
            with open(output_path, file_mode, encoding='utf-8') as output_file:
                for i in range(min_count):
                    msg1 = messages1[i]
                    msg2 = messages2[i]
                    
                    # Skip messages that start with ###IGNORE###
                    if msg2.startswith('###IGNORE###'):
                        continue
                    
                    # Write the mapping with preserved newlines
                    output_file.write(f"{msg1} === {msg2}\n")
            
            action = "appended to" if append else "created"
            print(f"Mapping file {action} successfully: {output_path}")
            print(f"Processed {min_count} multi-line messages")
        else:
            # Original line-by-line mode
            # Check if files have the same number of lines
            if len(lines1) != len(lines2):
                print(f"Warning: Files have different number of lines!")
                print(f"File 1: {len(lines1)} lines")
                print(f"File 2: {len(lines2)} lines")
                print("Proceeding with minimum number of lines...")
            
            # Use the minimum number of lines
            min_lines = min(len(lines1), len(lines2))
            
            # Create or append to the mapping file
            file_mode = 'a' if append else 'w'
            with open(output_path, file_mode, encoding='utf-8') as output_file:
                for i in range(min_lines):
                    line1 = lines1[i].rstrip('\n\r')  # Remove newlines but keep content
                    line2 = lines2[i].rstrip('\n\r')  # Remove newlines but keep content
                    
                    # Skip lines that start with ###IGNORE### in the Hebrew file
                    if line2.startswith('###IGNORE###'):
                        continue
                    
                    # Handle empty lines - if both lines are empty, write empty line
                    if not line1.strip() and not line2.strip():
                        output_file.write("\n")
                    else:
                        # Handle cases where only one line is empty
                        if not line1.strip():
                            line1 = ""
                        if not line2.strip():
                            line2 = ""
                        
                        # Write the mapping
                        output_file.write(f"{line1} === {line2}\n")
            
            action = "appended to" if append else "created"
            print(f"Mapping file {action} successfully: {output_path}")
            print(f"Processed {min_lines} lines")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find input file - {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: Permission denied - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description='Maps corresponding lines/messages from two input files and creates a mapping output file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Line-by-line mapping (default)
  python map_files.py english.txt hebrew.txt mapping.txt
  python map_files.py english.txt hebrew.txt mapping.txt 35
  
  # Multi-line message mapping (messages separated by =====)
  python map_files.py english.txt hebrew.txt mapping.txt --multiline
  python map_files.py english.txt hebrew.txt mapping.txt 35 --multiline
  
  # Append to existing mapping file
  python map_files.py english2.txt hebrew2.txt mapping.txt --append
  python map_files.py english2.txt hebrew2.txt mapping.txt --multiline --append
        '''
    )
    
    parser.add_argument('input1', help='Path to first input text file (English)')
    parser.add_argument('input2', help='Path to second input text file (Hebrew)')
    parser.add_argument('output', help='Path to output mapping file')
    parser.add_argument('max_length', type=int, nargs='?', default=29,
                        help='Maximum length for text splitting (default: 29)')
    parser.add_argument('--multiline', action='store_true',
                        help='Enable multi-line mode: treat ===== as message separator and combine lines with \\n')
    parser.add_argument('--append', action='store_true',
                        help='Append to existing mapping file instead of overwriting')
    
    args = parser.parse_args()
    
    input1_path = args.input1
    input2_path = args.input2
    output_path = args.output
    max_length = args.max_length
    multiline = args.multiline
    append = args.append
    
    # Validate input files exist
    if not os.path.exists(input1_path):
        print(f"Error: Input file 1 does not exist: {input1_path}")
        sys.exit(1)
    
    if not os.path.exists(input2_path):
        print(f"Error: Input file 2 does not exist: {input2_path}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    print(f"Input file 1: {input1_path}")
    print(f"Input file 2: {input2_path}")
    print(f"Output file: {output_path}")
    print(f"Max length: {max_length}")
    print(f"Multi-line mode: {multiline}")
    print(f"Append mode: {append}")
    print()
    
    map_files(input1_path, input2_path, output_path, max_length, multiline, append)

if __name__ == "__main__":
    main()