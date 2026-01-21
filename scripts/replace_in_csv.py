# coding=utf-8

"""
    replace_in_csv.py

    This script reads a CSV file and replaces English text with Hebrew translations
    based on a mapping file.
"""
import os
import sys
import csv
import re


def load_mapping(mapping_filepath):
    """
    Loads the mapping file into a dictionary.

    Args:
        mapping_filepath (str): The path to the mapping file.

    Returns:
        dict: A dictionary mapping English text to Hebrew text.
    """
    mapping = {}
    try:
        with open(mapping_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\r\n')
                if not line:
                    continue
                
                # split by separator
                parts = line.split(' === ')
                if len(parts) == 2:
                    english = parts[0]
                    hebrew = parts[1]
                    mapping[english] = hebrew
                    
        print(f"Loaded {len(mapping)} mappings from '{mapping_filepath}'.")
        return mapping
        
    except FileNotFoundError:
        print(f"Error: The mapping file '{mapping_filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while loading mapping: {e}")
        sys.exit(1)


def replace_in_csv(csv_filepath, output_filepath, mapping, text_column='text'):
    """
    Replaces English text in a specified column of a CSV file with Hebrew translations.

    Args:
        csv_filepath (str): The path to the input CSV file.
        output_filepath (str): The path to the output CSV file.
        mapping (dict): Dictionary mapping English text to Hebrew text.
        text_column (str): The name of the column containing text to replace (default: 'text').
    """
    try:
        replaced_count = 0
        total_lines = 0
        
        with open(csv_filepath, 'r', encoding='utf-8', newline='') as infile:
            reader = csv.DictReader(infile)
            
            # Get fieldnames from the CSV
            fieldnames = reader.fieldnames
            
            if text_column not in fieldnames:
                print(f"Error: Column '{text_column}' not found in CSV file.")
                print(f"Available columns: {', '.join(fieldnames)}")
                sys.exit(1)
            
            rows = []
            for row in reader:
                english_text = row[text_column].strip()
                
                english_text=english_text.replace('\r','')
                english_text=english_text.replace('\n','\\n')
                #print(f"{english_text}")   
                english_text=remove_brackets(english_text)
                #print(f"|{english_text}|")
                
                # check if we have a translation for this text
                if english_text in mapping:
                    row[text_column] = mapping[english_text].replace('\\n','\r\n')
                    replaced_count += 1
                
                rows.append(row)
                total_lines += 1
        
        # Write output CSV
        with open(output_filepath, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Successfully processed {total_lines} lines, replaced {replaced_count} texts.")
        print(f"Output written to '{output_filepath}'.")
        
    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def remove_brackets(text):
    # Remove all patterns like ([...]), ([#]...), ([0]...), (TEXT), etc.
    # This regex matches any text in parentheses (including nested brackets)
    pattern = r'\([^)]*\)'
    cleaned = re.sub(pattern, '', text)
    # Remove the space after the first "
    cleaned = re.sub(r'^"\s+', '"', cleaned) 
    # Only strip leading/trailing whitespace, preserve original spacing
    cleaned = cleaned.strip()
    return cleaned


if __name__ == "__main__":
    # validate command line
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python replace_in_csv.py <csv-file> <mapping-file> <output-dir> [text-column]")
        print("   -> csv-file: Input CSV file")
        print("   -> mapping-file: Mapping file with format 'english === hebrew'")
        print("   -> output-dir: Directory for output CSV file")
        print("   -> text-column: Optional column name containing text to replace (default: 'text')")
        sys.exit(1)

    csv_file = sys.argv[1]
    mapping_file = sys.argv[2]
    output_dir = sys.argv[3]
    text_column = sys.argv[4] if len(sys.argv) == 5 else 'text'

    # derive output file path
    output_file = os.path.join(output_dir, os.path.basename(csv_file))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # load mapping and replace
    mapping = load_mapping(mapping_file)
    replace_in_csv(csv_file, output_file, mapping, text_column)
