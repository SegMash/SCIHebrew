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
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python mapping_to_json.py <mapping-file> [output-json] [game-name]")
        print("   -> mapping-file: text file with 'english === hebrew' format")
        print("   -> output-json: optional (defaults to messages.json)")
        print("   -> game-name: optional game name for metadata")
        sys.exit(1)

    mapping_file = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) >= 3 else "messages.json"
    game_name = sys.argv[3] if len(sys.argv) == 4 else ""

    convert_mapping_to_json(mapping_file, output_json, game_name)
