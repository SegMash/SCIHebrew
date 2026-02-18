# coding=utf-8

"""
    mapping_to_json.py

    This script converts a mapping file (english === hebrew) to a messages.json file.
"""
import os
import sys
import json
import re
from datetime import datetime, timezone


def extract_placeholders(text):
    """
    Extracts placeholders like %s, %d, %w1, %m8, etc. from text.
    
    Args:
        text (str): The text to extract placeholders from.
    
    Returns:
        list: A list of all placeholders found in the text (including duplicates).
    """
    # Match patterns like %s, %d, %w1, %m8, %v0, etc.
    # Pattern matches: %[letter][optional digits]
    pattern = r'%[a-zA-Z]\d*'
    placeholders = re.findall(pattern, text)
    return placeholders


def convert_mapping_to_json(mapping_filepath, json_filepath, game_name=""):
    """
    Converts a mapping file to messages.json format.
    
    Args:
        mapping_filepath (str): The path to the input mapping file.
        json_filepath (str): The path to the output JSON file.
        game_name (str): The name of the game (optional).
    """
    try:
        messages = []
        
        with open(mapping_filepath, 'r', encoding='utf-8') as infile:
            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Split by delimiter
                if ' === ' not in line:
                    print(f"Warning: Line {line_num} does not contain ' === ' delimiter. Skipping.")
                    continue
                
                parts = line.split(' === ', 1)
                if len(parts) != 2:
                    print(f"Warning: Line {line_num} has invalid format. Skipping.")
                    continue
                
                original = parts[0].strip()
                translation = parts[1].strip()
                
                # Extract placeholders from both original and translation
                placeholders_original = extract_placeholders(original)
                placeholders_translation = extract_placeholders(translation)
                
                # Combine placeholders (union of both)
                all_placeholders = placeholders_original.copy()
                for p in placeholders_translation:
                    if p not in all_placeholders:
                        all_placeholders.append(p)
                
                # Create message entry
                message = {
                    "messageNumber": len(messages) + 1,
                    "original": original,
                    "translation": translation,
                    "notes": "",
                    "placeholders": all_placeholders
                }
                
                messages.append(message)
        
        # Create the full JSON structure
        output = {
            "version": "1.0",
            "metadata": {
                "gameName": game_name,
                "contentType": "messages",
                "sourceLanguage": "en",
                "targetLanguage": "he",
                "extractedDate": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "totalMessages": len(messages)
            },
            "messages": messages
        }
        
        # Write JSON file
        with open(json_filepath, 'w', encoding='utf-8') as outfile:
            json.dump(output, outfile, ensure_ascii=False, indent=2)
        
        print(f"Successfully converted {len(messages)} messages from '{mapping_filepath}' to '{json_filepath}'.")
        
    except FileNotFoundError:
        print(f"Error: The file '{mapping_filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # validate command line
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python mapping_to_json.py <directory> [game-name]")
        print("   -> directory: path to directory containing mapping_*.txt files")
        print("   -> game-name: optional game name for metadata")
        sys.exit(1)

    directory = sys.argv[1]
    game_name = sys.argv[2] if len(sys.argv) == 3 else ""

    # Check if directory exists
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        sys.exit(1)

    # Find all mapping_*.txt files
    mapping_pattern = re.compile(r'^mapping_\d+\.txt$')
    mapping_files = []
    
    for filename in os.listdir(directory):
        if mapping_pattern.match(filename):
            mapping_files.append(filename)
    
    # Sort files by number
    mapping_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    
    if not mapping_files:
        print(f"No mapping_*.txt files found in directory '{directory}'.")
        sys.exit(1)
    
    print(f"Found {len(mapping_files)} mapping file(s): {', '.join(mapping_files)}")
    print()
    
    # Collect all messages from all mapping files
    all_messages = []
    
    for mapping_file in mapping_files:
        print(f"Processing {mapping_file}...")
        mapping_filepath = os.path.join(directory, mapping_file)
        
        # Extract file number from filename
        file_number = int(re.search(r'\d+', mapping_file).group())
        
        # Track message number per file
        file_message_count = 0
        
        try:
            with open(mapping_filepath, 'r', encoding='utf-8') as infile:
                for line_num, line in enumerate(infile, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Split by delimiter
                    if ' === ' not in line:
                        print(f"  Warning: Line {line_num} does not contain ' === ' delimiter. Skipping.")
                        continue
                    
                    parts = line.split(' === ', 1)
                    if len(parts) != 2:
                        print(f"  Warning: Line {line_num} has invalid format. Skipping.")
                        continue
                    
                    original = parts[0].strip()
                    translation = parts[1].strip()
                    
                    # Extract placeholders from both original and translation
                    placeholders_original = extract_placeholders(original)
                    placeholders_translation = extract_placeholders(translation)
                    
                    # Combine placeholders (union of both)
                    all_placeholders = placeholders_original.copy()
                    for p in placeholders_translation:
                        if p not in all_placeholders:
                            all_placeholders.append(p)
                    
                    # Increment file-specific message counter
                    file_message_count += 1
                    
                    # Create message entry
                    message = {
                        "logicFile": f"{file_number}.agilogic",
                        "messageNumber": file_message_count,
                        "original": original,
                        "translation": translation,
                        "notes": "",
                        "placeholders": all_placeholders
                    }
                    
                    all_messages.append(message)
            
            print(f"  Added {file_message_count} messages")
        
        except FileNotFoundError:
            print(f"  Error: The file '{mapping_filepath}' was not found.")
            continue
        except Exception as e:
            print(f"  Error processing {mapping_file}: {e}")
            continue
    
    print()
    print(f"Total messages collected: {len(all_messages)}")
    
    # Create the full JSON structure with all messages
    output = {
        "version": "1.0",
        "metadata": {
            "gameName": game_name,
            "contentType": "messages",
            "sourceLanguage": "en",
            "targetLanguage": "he",
            "extractedDate": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "totalMessages": len(all_messages)
        },
        "messages": all_messages
    }
    
    # Write single JSON file
    output_json = os.path.join(directory, "messages.json")
    with open(output_json, 'w', encoding='utf-8') as outfile:
        json.dump(output, outfile, ensure_ascii=False, indent=2)
    
    print(f"Successfully created '{output_json}' with {len(all_messages)} messages.")
