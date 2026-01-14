import csv
import re
import argparse
import os

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process messages CSV file and generate cleaned text output')
parser.add_argument('csv_file', help='Path to the input CSV file')
parser.add_argument('output_dir', help='Path to the output directory')
args = parser.parse_args()

# Validate input file exists
if not os.path.exists(args.csv_file):
    print(f"Error: Input file '{args.csv_file}' not found.")
    exit(1)

# Generate output filename from CSV filename
csv_basename = os.path.basename(args.csv_file)
csv_name_without_ext = os.path.splitext(csv_basename)[0]
output_filename = f"{csv_name_without_ext}_english.txt"
output_file = os.path.join(args.output_dir, output_filename)

# Read the CSV file and convert to list of dictionaries
messages = []
with open(args.csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Convert numeric fields to integers for proper sorting
        row['noun'] = int(row['noun'])
        row['verb'] = int(row['verb'])
        row['case'] = int(row['case'])
        row['sequence'] = int(row['sequence'])
        messages.append(row)

# Sort by noun, then verb, then case, then sequence
messages.sort(key=lambda x: (x['noun'], x['verb'], x['case'], x['sequence']))

# Function to remove all bracket sections from text
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

# Process messages and write to output file
output_lines = []
previous_case = None

for msg in messages:
    current_case = msg['case']
    text = msg['text']
    
    # Remove all bracket sections
    cleaned_text = remove_brackets(text)
    
    # Skip empty lines after bracket removal
    if not cleaned_text:
        continue
    cleaned_text = cleaned_text.replace('\n','\\n')  # Replace newlines with literal \n for consistency
    # Add empty line if case changed (and it's not the first message)
    #if previous_case is not None and current_case != previous_case:
    #    output_lines.append('')
    
    output_lines.append(cleaned_text)
    previous_case = current_case

# Create output directory if it doesn't exist
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

# Write to output file
with open(output_file, 'w', encoding='utf-8') as f:
    for line in output_lines:
        f.write(line + '\n')

# Create empty Hebrew file if it doesn't already exist
hebrew_filename = f"{csv_name_without_ext}_hebrew.txt"
hebrew_file = os.path.join(args.output_dir, hebrew_filename)

if not os.path.exists(hebrew_file):
    with open(hebrew_file, 'w', encoding='utf-8') as f:
        f.write("")  # Create empty file
    print(f"Created new Hebrew file: {hebrew_file}")
else:
    print(f"Hebrew file already exists: {hebrew_file}")

print(f"Processed {len(messages)} messages")
print(f"Output written to {output_file}")
