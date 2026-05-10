# coding=utf-8

"""
    json_to_hebrew_kq5.py

    This script reads a messages.json file and writes translations back to hebrew files.
"""
import os
import sys
import json


def update_hebrew_files(json_filepath, output_directory):
    """
    Updates hebrew files with translations from messages.json.
    
    Args:
        json_filepath (str): The path to the messages.json file.
        output_directory (str): The directory containing the *_hebrew.txt files.
    """
    try:
        # Read the JSON file
        with open(json_filepath, 'r', encoding='utf-8') as infile:
            data = json.load(infile)
        
        messages = data.get('messages', [])
        if not messages:
            print("No messages found in JSON file.")
            return
        
        print(f"Processing {len(messages)} messages from '{json_filepath}'...")
        print()
        
        # Group messages by logicFile for efficient processing
        files_to_update = {}
        for message in messages:
            logic_file = message.get('logicFile')
            message_number = message.get('messageNumber')
            translation = message.get('translation', '')
            
            if logic_file is None or message_number is None:
                print(f"Warning: Skipping message with missing logicFile or messageNumber.")
                continue
            
            if logic_file not in files_to_update:
                files_to_update[logic_file] = {}
            
            files_to_update[logic_file][message_number] = translation
        
        # Process each hebrew file
        total_updates = 0
        for logic_file, updates in sorted(files_to_update.items()):
            hebrew_filename = f"{logic_file}_messages_hebrew.txt"
            hebrew_filepath = os.path.join(output_directory, hebrew_filename)
            
            if not os.path.exists(hebrew_filepath):
                print(f"Warning: File '{hebrew_filename}' not found. Skipping {len(updates)} updates.")
                continue
            
            # Read the entire file
            with open(hebrew_filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Update specific lines
            updates_made = 0
            for line_number, translation in sorted(updates.items()):
                # Line numbers are 1-based, list indices are 0-based
                line_index = line_number - 1
                
                if line_index < 0 or line_index >= len(lines):
                    print(f"  Warning: Line {line_number} out of range in '{hebrew_filename}' (has {len(lines)} lines). Skipping.")
                    continue
                
                # Escape newlines - convert actual \n characters to literal \n string
                escaped_translation = translation.replace('\n', '\\n')
                
                # Replace the line (preserve newline if it exists)
                if lines[line_index].endswith('\n'):
                    lines[line_index] = escaped_translation + '\n'
                else:
                    lines[line_index] = escaped_translation
                
                updates_made += 1
            
            # Write the file back
            with open(hebrew_filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"Updated '{hebrew_filename}': {updates_made} lines modified")
            total_updates += updates_made
        
        print()
        print(f"Successfully updated {total_updates} lines across {len(files_to_update)} files.")
        
    except FileNotFoundError:
        print(f"Error: The file '{json_filepath}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Validate command line
    if len(sys.argv) != 3:
        print("Usage: python json_to_hebrew_kq5.py <messages.json> <output-directory>")
        print("   -> messages.json: path to the messages JSON file")
        print("   -> output-directory: directory containing the *_messages_hebrew.txt files")
        sys.exit(1)

    json_file = sys.argv[1]
    output_dir = sys.argv[2]

    # Check if JSON file exists
    if not os.path.isfile(json_file):
        print(f"Error: '{json_file}' is not a valid file.")
        sys.exit(1)

    # Check if output directory exists
    if not os.path.isdir(output_dir):
        print(f"Error: '{output_dir}' is not a valid directory.")
        sys.exit(1)

    update_hebrew_files(json_file, output_dir)
