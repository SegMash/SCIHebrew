#!/usr/bin/env python3
"""
Parser for King's Quest 8 MSG files
Extracts messages and exports them to CSV format
"""

import struct
import csv
import sys
import os
import argparse

def parse_msg_file(filename, debug=False):
    """
    Parse a KQ8 MSG file and extract all messages
    
    Args:
        filename: Path to the MSG file
        debug: Whether to print debug information
        
    Returns:
        List of message dictionaries
    """
    messages = []
    
    with open(filename, 'rb') as f:
        # Skip header (2 bytes) - not important
        f.read(2)
        
        # Skip sciVersion (4 bytes) - not important  
        f.read(4)
        
        # Read dataSize (2 bytes) - important
        data_size = struct.unpack('<H', f.read(2))[0]
        if debug:
            print(f"Data size: {data_size}")
        
        # Read lastId (2 bytes)
        last_id = struct.unpack('<H', f.read(2))[0]
        if debug:
            print(f"Last ID: {last_id}")
        
        # Read count (2 bytes)
        count = struct.unpack('<H', f.read(2))[0]
        if debug:
            print(f"Message count: {count}")
        
        # First loop: Read message headers
        message_headers = []
        for i in range(count):
            # Read each message header (10 bytes total)
            noun = struct.unpack('<B', f.read(1))[0]
            verb = struct.unpack('<B', f.read(1))[0]
            case = struct.unpack('<B', f.read(1))[0]
            sequence = struct.unpack('<B', f.read(1))[0]
            talker = struct.unpack('<B', f.read(1))[0]
            text_offset = struct.unpack('<H', f.read(2))[0]
            ref_noun = struct.unpack('<B', f.read(1))[0]
            ref_verb = struct.unpack('<B', f.read(1))[0]
            ref_case = struct.unpack('<B', f.read(1))[0]
            ref_sequence = struct.unpack('<B', f.read(1))[0]
            
            header = {
                'noun': noun,
                'verb': verb,
                'case': case,
                'sequence': sequence,
                'talker': talker,
                'text_offset': text_offset,
                'ref_noun': ref_noun,
                'ref_verb': ref_verb,
                'ref_case': ref_case,
                'ref_sequence': ref_sequence
            }
            message_headers.append(header)
        
        # Second loop: Read message texts
        # Store current position to calculate text offsets correctly
        text_section_start = f.tell()
        
        for i, header in enumerate(message_headers):
            # Calculate absolute position for this text
            # textOffset is relative to resData (which starts after the 6-byte header)
            text_pos = 2 + header['text_offset']
            f.seek(text_pos)
            
            # Read null-terminated string
            text_bytes = bytearray()
            while True:
                byte = f.read(1)
                if not byte or byte[0] == 0:
                    break
                text_bytes.append(byte[0])
            
            # Decode text (assuming Windows-1252 or similar encoding for now)
            try:
                text = text_bytes.decode('CP862')
            except UnicodeDecodeError:
                try:
                    text = text_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    text = text_bytes.decode('latin1')  # Fallback
            
            # Combine header info with text
            message = header.copy()
            message['text'] = text
            messages.append(message)
            
            if debug:
                print(f"Message {i+1}: noun={header['noun']}, verb={header['verb']}, text_offset={header['text_offset']} text='{text[:50]}{'...' if len(text) > 50 else ''}'")
    
    return messages

def export_to_csv(messages, output_filename, debug=False):
    """
    Export messages to CSV file
    
    Args:
        messages: List of message dictionaries
        output_filename: Path to output CSV file
        debug: Whether to print debug information
    """
    if not messages:
        if debug:
            print("No messages to export")
        return
    
    # Define column order
    columns = ['noun', 'verb', 'case', 'sequence', 'talker', 'text_offset', 
               'ref_noun', 'ref_verb', 'ref_case', 'ref_sequence', 'text']
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(messages)
    
    if debug:
        print(f"Exported {len(messages)} messages to {output_filename}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Parse KQ8 MSG files and export to CSV format')
    parser.add_argument('input_file', help='Path to the input MSG file')
    parser.add_argument('output_dir', help='Directory to save the output CSV file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_dir = args.output_dir
    debug = args.debug
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # Check if output directory exists, create if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if debug:
            print(f"Created output directory: {output_dir}")
    
    # Generate output filename based on input file base name
    input_basename = os.path.splitext(os.path.basename(input_file))[0]  # Remove extension
    output_filename = f"{input_basename}_messages.csv"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        if debug:
            print(f"Parsing {input_file}...")
        messages = parse_msg_file(input_file, debug)
        
        if debug:
            print(f"\nExporting to {output_path}...")
        export_to_csv(messages, output_path, debug)
        
        if debug:
            print(f"\nDone! Found {len(messages)} messages.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()