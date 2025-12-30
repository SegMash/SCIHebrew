# coding=iso-8859-15

"""
    tex2tsv.py

    This script reads SCI text resource files (TEX) and transforms them back into a tab separated value (TSV) file.
"""
import os
import sys


def read_tex_strings(tex_filepath, encoding='windows-1255'):
    """
    Reads a TEX binary file and extracts all null-terminated strings.

    Args:
        tex_filepath (str): The path to the input TEX file.
        encoding (str): The encoding to use for decoding strings.

    Returns:
        list: A list of decoded strings from the TEX file.
    """
    strings = []
    
    try:
        with open(tex_filepath, 'rb') as infile:
            # read and skip header (first 2 bytes: \x83\x00)
            header = infile.read(2)
            if header != b'\x83\x00':
                print(f"Warning: Unexpected header in '{tex_filepath}': {header.hex()}")
            
            # read rest of file
            data = infile.read()
            
            # split by null terminator
            raw_strings = data.split(b'\x00')
            
            # decode each string (excluding the last empty one after final null)
            for raw_str in raw_strings[:-1]:
                try:
                    decoded = raw_str.decode(encoding)
                    strings.append(decoded)
                except UnicodeDecodeError as e:
                    print(f"Warning: Could not decode string: {e}")
                    strings.append("")
                    
    except FileNotFoundError:
        print(f"Error: The file '{tex_filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading '{tex_filepath}': {e}")
        sys.exit(1)
    
    return strings


def convert_tex_to_tsv(tex_filepath, tsv_filepath):
    """
    Converts a TEX binary file to a tab-separated value (TSV) file.

    Args:
        tex_filepath (str): The path to the input TEX file.
        tsv_filepath (str): The path to the output TSV file.
    """
    # read TEX file
    texts = read_tex_strings(tex_filepath)
    
    try:
        # write TSV file
        with open(tsv_filepath, 'w', encoding='utf-8') as outfile:
            # write header
            outfile.write("Index\tNoun\tSelector\tVerb\tText\tOriginal\n")
            
            # write each entry
            for i, text in enumerate(texts):
                # escape newlines to literal \n
                text_escaped = text.replace('\n', '\\n')
                # write: Index, Noun (empty), Selector (empty), Verb (empty), Text, Original (empty)
                outfile.write(f"{i}\t\t\t\t{text_escaped}\t\n")
        
        print(f"Successfully converted {len(texts)} entries from '{tex_filepath}' to '{tsv_filepath}'.")
        
    except Exception as e:
        print(f"An unexpected error occurred while writing TSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # validate command line
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python tex2tsv.py <tex-file-or-dir> [output-dir]")
        print("   -> tex-file-or-dir: .tex file or directory containing .tex files")
        print("   -> output-dir is optional (defaults to current directory)")
        sys.exit(1)

    tex_input = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) == 3 else "."

    # validate input exists
    if not os.path.exists(tex_input):
        print(f"Error: '{tex_input}' not found.")
        sys.exit(1)

    # create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # check if input is a file or directory
    if os.path.isfile(tex_input):
        # single file mode
        if not tex_input.lower().endswith('.tex'):
            print(f"Error: '{tex_input}' is not a .tex file.")
            sys.exit(1)
        
        tex_filename = os.path.basename(tex_input)
        module = os.path.splitext(tex_filename)[0]
        tsv_file = os.path.join(output_dir, f"{module}.tsv")
        
        convert_tex_to_tsv(tex_input, tsv_file)
        
    else:
        # directory mode
        tex_dir = tex_input
        
        # find all .tex files in the input directory (case-insensitive)
        tex_files = [f for f in os.listdir(tex_dir) if f.lower().endswith('.tex')]
        
        if not tex_files:
            print(f"No .tex files found in '{tex_dir}'.")
            sys.exit(0)

        print(f"Found {len(tex_files)} .tex file(s) to convert.")
        
        # convert each .tex file to .tsv
        converted_count = 0
        for tex_filename in sorted(tex_files):
            # derive input and output paths
            tex_file = os.path.join(tex_dir, tex_filename)
            module = os.path.splitext(tex_filename)[0]
            tsv_file = os.path.join(output_dir, f"{module}.tsv")
            
            # convert
            try:
                convert_tex_to_tsv(tex_file, tsv_file)
                converted_count += 1
            except Exception as e:
                print(f"Error converting '{tex_filename}': {e}")
        
        print(f"\nConversion complete. {converted_count}/{len(tex_files)} file(s) successfully converted.")
