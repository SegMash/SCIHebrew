# coding=utf-8

"""
    json_to_hebrew.py

    This script compares two messages.json files (old and new) and updates a text file
    with the changed Hebrew translations based on messageNumber.
"""
import os
import sys
import json


def update_hebrew_translations(old_json_filepath, new_json_filepath, txt_filepath):
    """
    Compares two JSON files and updates the text file with changed Hebrew translations.
    
    Args:
        old_json_filepath (str): The path to the old JSON file.
        new_json_filepath (str): The path to the new JSON file.
        txt_filepath (str): The path to the text file to update.
    """
    try:
        # Read old JSON file
        with open(old_json_filepath, 'r', encoding='utf-8') as infile:
            old_data = json.load(infile)
        
        # Read new JSON file
        with open(new_json_filepath, 'r', encoding='utf-8') as infile:
            new_data = json.load(infile)
        
        # Validate structure
        if 'messages' not in old_data:
            print(f"Error: Old JSON file does not contain 'messages' field.")
            sys.exit(1)
        
        if 'messages' not in new_data:
            print(f"Error: New JSON file does not contain 'messages' field.")
            sys.exit(1)
        
        # Build dictionaries indexed by messageNumber
        old_messages = {}
        for message in old_data['messages']:
            msg_num = message.get('messageNumber')
            if msg_num is not None:
                old_messages[msg_num] = message.get('translation', '')
        
        new_messages = {}
        for message in new_data['messages']:
            msg_num = message.get('messageNumber')
            if msg_num is not None:
                new_messages[msg_num] = message.get('translation', '')
        
        # Read the text file
        with open(txt_filepath, 'r', encoding='utf-8') as infile:
            txt_content = infile.read()
        
        # Find changed translations and update text file
        updated_content = txt_content
        changes_count = 0
        
        for msg_num in old_messages:
            if msg_num in new_messages:
                old_translation = old_messages[msg_num]
                new_translation = new_messages[msg_num]
                
                # Only replace if the translation has changed
                if old_translation != new_translation and old_translation:
                    # Check if both messages contain \n - split and replace one by one
                    if '\\n' in old_translation and '\\n' in new_translation:
                        old_parts = old_translation.split('\\n')
                        new_parts = new_translation.split('\\n')
                        
                        # Only process if both have the same number of parts
                        if len(old_parts) == len(new_parts):
                            print(f"Message #{msg_num}: Splitting message with {len(old_parts)} parts")
                            for i, (old_part, new_part) in enumerate(zip(old_parts, new_parts)):
                                if old_part != new_part and old_part:
                                    if old_part in updated_content:
                                        updated_content = updated_content.replace(old_part, new_part)
                                        changes_count += 1
                                        print(f"  Part {i+1}: Replaced '{old_part}' with '{new_part}'")
                        else:
                            print(f"Warning: Message #{msg_num} has different number of parts (old: {len(old_parts)}, new: {len(new_parts)})")
                    else:
                        # Replace old translation with new translation as a whole
                        if old_translation in updated_content:
                            updated_content = updated_content.replace(old_translation, new_translation)
                            changes_count += 1
                            print(f"Message #{msg_num}: Replaced '{old_translation}' with '{new_translation}'")
        
        # Write updated content back to text file
        with open(txt_filepath, 'w', encoding='utf-8') as outfile:
            outfile.write(updated_content)
        
        print(f"\nSuccessfully updated {changes_count} Hebrew translations in '{txt_filepath}'.")
        
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # validate command line
    if len(sys.argv) != 4:
        print("Usage: python json_to_hebrew.py <old-json> <new-json> <txt-file>")
        print("   -> old-json: Original messages.json file")
        print("   -> new-json: Updated messages.json file")
        print("   -> txt-file: Text file to update with changed Hebrew translations")
        sys.exit(1)

    old_json = sys.argv[1]
    new_json = sys.argv[2]
    txt_file = sys.argv[3]

    update_hebrew_translations(old_json, new_json, txt_file)
