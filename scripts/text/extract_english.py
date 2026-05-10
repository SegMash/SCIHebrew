# coding=utf-8

"""
    extract_english.py

    This script reads a tab separated value (TSV) file and extracts the English text (5th column) to a text file.
"""
import os
import sys


def extract_english_text(tsv_filepath, output_filepath):
    """
    Extracts English text from the 5th column of a TSV file.

    Args:
        tsv_filepath (str): The path to the input TSV file.
        output_filepath (str): The path to the output text file.
    """
    try:
        # open the output file for writing in text mode
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            # open the input TSV file for reading in text mode
            with open(tsv_filepath, 'r', encoding='utf-8') as infile:
                line_count = 0
                for line in infile:
                    # strip whitespace and split line by tabs
                    fields = line.strip().split('\t')

                    # detect and skip over header
                    if not fields[0].isnumeric():
                        continue

                    # extract the 5th field (index 4), defaulting to empty
                    text = ""
                    if len(fields) >= 5:
                        text = fields[4]

                    # skip empty or whitespace-only text
                    if not text.strip():
                        continue

                    # write text to output file
                    outfile.write(text + '\n')

                    line_count += 1

        print(f"Successfully extracted {line_count} English texts from '{tsv_filepath}' to '{output_filepath}'.")

    except FileNotFoundError:
        print(f"Error: The file '{tsv_filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # validate command line
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python extract_english.py <tsv-dir> [output-dir]")
        print("   -> tsv-dir: directory containing .tsv files")
        print("   -> output-dir is optional (defaults to current directory)")
        sys.exit(1)

    tsv_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) == 3 else "."

    # validate tsv directory exists
    if not os.path.exists(tsv_dir):
        print(f"Error: Directory '{tsv_dir}' not found.")
        sys.exit(1)

    # create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # find all .tsv files in the input directory
    tsv_files = [f for f in os.listdir(tsv_dir) if f.endswith('.tsv')]
    
    if not tsv_files:
        print(f"No .tsv files found in '{tsv_dir}'.")
        sys.exit(0)

    print(f"Found {len(tsv_files)} .tsv file(s) in '{tsv_dir}'.")
    
    # extract English text from each .tsv file
    extracted_count = 0
    for tsv_filename in sorted(tsv_files):
        # derive input and output paths
        tsv_file = os.path.join(tsv_dir, tsv_filename)
        module = os.path.splitext(tsv_filename)[0]
        output_file = os.path.join(output_dir, f"{module}_english.txt")
        hebrew_file = os.path.join(output_dir, f"{module}_hebrew.txt")
        
        # extract
        try:
            extract_english_text(tsv_file, output_file)
            
            # create Hebrew file only if it doesn't exist
            if not os.path.exists(hebrew_file):
                with open(hebrew_file, 'w', encoding='utf-8') as f:
                    f.write("")  # create empty file
                print(f"Created new Hebrew file: '{hebrew_file}'")
            
            extracted_count += 1
        except Exception as e:
            print(f"Error extracting from '{tsv_filename}': {e}")
    
    print(f"\nExtraction complete. {extracted_count}/{len(tsv_files)} file(s) successfully processed.")
