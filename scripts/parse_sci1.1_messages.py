# coding=utf-8

"""
    parse_sci1.1_messages.py

    This script scans a directory for all *.msg files and runs parse_msg.py on each file.
"""
import os
import sys
import subprocess


def parse_all_msg_files(input_dir, output_dir):
    """
    Scans a directory for all .msg files and processes each with parse_msg.py.

    Args:
        input_dir (str): The directory to scan for .msg files.
        output_dir (str): The output directory for processed files.
    """
    # ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # find all .msg files
    msg_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.msg'):
                msg_files.append(os.path.join(root, file))
    
    if not msg_files:
        print(f"No .msg files found in '{input_dir}'")
        return

    print(f"Found {len(msg_files)} .msg file(s) in '{input_dir}'")
    
    # process each .msg file
    processed = 0
    failed = 0
    total_lines = 0
    
    for msg_file in sorted(msg_files):
        print(f"\nProcessing: {msg_file}")
        try:
            # run parse_msg.py script
            result = subprocess.run(
                ['python', '.\\scripts\\parse_msg.py', msg_file, output_dir],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                print(result.stdout.strip())
            
            # determine the CSV file name (e.g., 130.msg -> 130_messages.csv)
            msg_basename = os.path.splitext(os.path.basename(msg_file))[0]
            csv_file = os.path.join(output_dir, f"{msg_basename}_messages.csv")
            
            # run process_messages.py on the generated CSV
            if os.path.exists(csv_file):
                print(f"  Creating text files from {csv_file}")
                result2 = subprocess.run(
                    ['python', '.\\scripts\\process_messages.py', csv_file, output_dir],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result2.stdout:
                    print(result2.stdout.strip())
                
                # count lines in generated txt files
                english_file = os.path.join(output_dir, f"{msg_basename}_messages_english.txt")
                hebrew_file = os.path.join(output_dir, f"{msg_basename}_messages_hebrew.txt")
                
                for txt_file in [english_file, hebrew_file]:
                    if os.path.exists(txt_file):
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            line_count = sum(1 for line in f)
                            total_lines += line_count
            
            processed += 1
            
        except subprocess.CalledProcessError as e:
            print(f"Error processing {msg_file}:")
            if e.stderr:
                print(e.stderr.strip())
            failed += 1
        except Exception as e:
            print(f"Unexpected error processing {msg_file}: {e}")
            failed += 1

    print(f"\n{'=' * 80}")
    print(f"Completed: {processed} successful, {failed} failed out of {len(msg_files)} total file(s)")
    print(f"Total lines in all generated text files: {total_lines}")


if __name__ == "__main__":
    # validate command line
    if len(sys.argv) != 3:
        print("Usage: python parse_sci1.1_messages.py <input-dir> <output-dir>")
        print("   -> input-dir: directory containing .msg files")
        print("   -> output-dir: directory for output files")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    # validate input directory exists
    if not os.path.isdir(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist.")
        sys.exit(1)

    parse_all_msg_files(input_directory, output_directory)
