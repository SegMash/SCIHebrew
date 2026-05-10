# coding=utf-8

"""
    replace_in_tsv.py

    This script reads a TSV file and replaces English text (5th column) with Hebrew translations
    based on a mapping file.
"""
import os
import sys


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
                    #english = parts[0].rstrip()
                    #hebrew = parts[1].rstrip()
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


def replace_in_tsv(tsv_filepath, output_filepath, mapping):
    """
    Replaces English text in the 5th column of a TSV file with Hebrew translations.

    Args:
        tsv_filepath (str): The path to the input TSV file.
        output_filepath (str): The path to the output TSV file.
        mapping (dict): Dictionary mapping English text to Hebrew text.
    """
    try:
        replaced_count = 0
        total_lines = 0
        
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            with open(tsv_filepath, 'r', encoding='utf-8') as infile:
                for line in infile:
                    # split line by tabs
                    fields = line.rstrip('\n').split('\t')
                    
                    # process data rows (skip header if first field is not numeric)
                    if fields[0].isnumeric() and len(fields) >= 5:
                        english_text = fields[4]
                        
                        # check if we have a translation for this text
                        if english_text in mapping:
                            fields[4] = mapping[english_text]
                            replaced_count += 1
                        
                        total_lines += 1
                    
                    # write the line (modified or not)
                    outfile.write('\t'.join(fields) + '\n')
        
        print(f"Successfully processed {total_lines} lines, replaced {replaced_count} texts.")
        print(f"Output written to '{output_filepath}'.")
        
    except FileNotFoundError:
        print(f"Error: The file '{tsv_filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # validate command line
    if len(sys.argv) != 4:
        print("Usage: python replace_in_tsv.py <tsv-file> <mapping-file> <output-dir>")
        print("   -> tsv-file must be of the format <module>.tsv")
        sys.exit(1)

    tsv_file = sys.argv[1]
    mapping_file = sys.argv[2]
    output_dir = sys.argv[3]

    # derive module from input filename
    (module, ext) = os.path.splitext(os.path.basename(tsv_file))
    if not module.isnumeric():
        print(f"Module name '{module}' must be numeric")
        sys.exit(1)

    # derive output file path
    output_file = f"{output_dir}/{module}.tsv"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # load mapping and replace
    mapping = load_mapping(mapping_file)
    replace_in_tsv(tsv_file, output_file, mapping)
