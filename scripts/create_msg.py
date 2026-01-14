#!/usr/bin/env python3
"""
Creator for King's Quest 8 MSG files
Converts CSV format back to binary MSG file
"""

import struct
import csv
import sys
import os

def create_msg_file(csv_filename, output_filename):
    """
    Create a KQ8 MSG file from CSV data
    
    Args:
        csv_filename: Path to the CSV file
        output_filename: Path to output MSG file
    """
    messages = []
    
    # Read CSV file
    with open(csv_filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert string values back to integers for numeric fields
            message = {
                'noun': int(row['noun']),
                'verb': int(row['verb']),
                'case': int(row['case']),
                'sequence': int(row['sequence']),
                'talker': int(row['talker']),
                'text_offset': int(row['text_offset']),  # Will be recalculated
                'ref_noun': int(row['ref_noun']),
                'ref_verb': int(row['ref_verb']),
                'ref_case': int(row['ref_case']),
                'ref_sequence': int(row['ref_sequence']),
                'text': row['text']
            }
            messages.append(message)
    
    print(f"Read {len(messages)} messages from CSV")
    
    # Calculate text offsets and encode texts
    encoded_texts = []
    # Text offsets are absolute from byte 0 of the file
    # Parser reads at position: 2 + text_offset, so text should be at that exact position
    # Text starts after: 2-byte header + sciVersion(4) + dataSize(2) + lastId(2) + count(2) + all message headers(count * 11)
    # Since parser adds 2, our text_offset should point to where text actually starts minus 2
    current_text_offset = 12 + (len(messages) * 11)

    for i, message in enumerate(messages):
        # Encode text to bytes
        try:
            # Try to encode with windows-1252 first (original encoding)
            text_bytes = message['text'].encode('Windows-1255')
            #text_bytes = message['text'].encode('CP862')
        except UnicodeEncodeError:
            try:
                # Fallback to UTF-8
                text_bytes = message['text'].encode('utf-8')
            except UnicodeEncodeError:
                # Final fallback to latin1
                text_bytes = message['text'].encode('latin1')
        
        # Update text offset (parser will add 2 to this value)
        message['text_offset'] = current_text_offset - 2
        encoded_texts.append(text_bytes)
        
        # Move to next text position: 2 null bytes + text + null terminator
        current_text_offset += len(text_bytes) + 1
        
        #print(f"Message {i+1}: offset={message['text_offset']}, length={len(text_bytes)}, text='{message['text'][:30]}{'...' if len(message['text']) > 30 else ''}'")
    
    # Calculate total data size
    header_size = 2 + 2 + (len(messages) * 11)  # lastId + count + all message headers (each header is 11 bytes)
    text_size = sum(len(text) + 1 for text in encoded_texts)  # text + null terminator for each (excluding the 2 null bytes)
    data_size = header_size + text_size
    
    print(f"Data size: {data_size}")
    print(f"Header size: {header_size}")
    print(f"Text size: {text_size}")
    
    # Calculate lastId (maximum noun value, or 0 if no messages)
    last_id = 338 #max((msg['noun'] for msg in messages), default=0)
    
    # Write MSG file
    with open(output_filename, 'wb') as f:
        # Write header (2 bytes) - using common values
        f.write(struct.pack('<B', 0x0F))  # sciResType
        f.write(struct.pack('<B', 0x00))  # headerSize
        
        # Write sciVersion (4 bytes) - using a typical KQ8 value
        f.write(struct.pack('<L', 5010))  # sciVersion
        
        # Write dataSize (2 bytes)
        f.write(struct.pack('<H', data_size))
        
        # Write lastId (2 bytes)
        f.write(struct.pack('<H', last_id))
        
        # Write count (2 bytes)
        f.write(struct.pack('<H', len(messages)))
        
        # Write message headers
        
        for message in messages:
            f.write(struct.pack('<B', message['noun']))
            f.write(struct.pack('<B', message['verb']))
            f.write(struct.pack('<B', message['case']))
            f.write(struct.pack('<B', message['sequence']))
            f.write(struct.pack('<B', message['talker']))
            f.write(struct.pack('<H', message['text_offset']))
            f.write(struct.pack('<B', message['ref_noun']))
            f.write(struct.pack('<B', message['ref_verb']))
            f.write(struct.pack('<B', message['ref_case']))
            f.write(struct.pack('<B', message['ref_sequence']))
        
        # Write message texts
        for text_bytes in encoded_texts:
            #f.write(b'\x00\x00')  # 2 null bytes before text
            f.write(text_bytes)
            f.write(b'\x00')  # Null terminator
    
    print(f"Created MSG file: {output_filename}")
    print(f"File size: {os.path.getsize(output_filename)} bytes")

def verify_msg_file(original_csv, created_msg):
    """
    Verify the created MSG file by parsing it back and comparing with original CSV
    
    Args:
        original_csv: Path to original CSV file
        created_msg: Path to created MSG file
    """
    print(f"\nVerifying created MSG file...")
    
    # Import the parser from parse_msg.py
    from parse_msg import parse_msg_file
    
    try:
        # Parse the created MSG file
        parsed_messages = parse_msg_file(created_msg)
        
        # Read original CSV
        original_messages = []
        with open(original_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                original_messages.append(row)
        
        # Compare counts
        if len(parsed_messages) != len(original_messages):
            print(f"ERROR: Message count mismatch! Original: {len(original_messages)}, Parsed: {len(parsed_messages)}")
            return False
        
        # Compare each message
        errors = 0
        for i, (original, parsed) in enumerate(zip(original_messages, parsed_messages)):
            # Compare text (most important)
            if original['text'].strip() != parsed['text'].strip():
                print(f"ERROR: Text mismatch in message {i+1}")
                print(f"  Original: '{original['text']}'")
                print(f"  Parsed:   '{parsed['text']}'")
                errors += 1
            
            # Compare other fields
            for field in ['noun', 'verb', 'case', 'sequence', 'talker']:
                if int(original[field]) != parsed[field]:
                    print(f"ERROR: {field} mismatch in message {i+1}: {original[field]} vs {parsed[field]}")
                    errors += 1
        
        if errors == 0:
            print(f"SUCCESS: Verification passed! All {len(parsed_messages)} messages match.")
            return True
        else:
            print(f"FAILED: {errors} errors found during verification.")
            return False
            
    except Exception as e:
        print(f"ERROR during verification: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python create_msg.py <input_csv> [output_msg]")
        print("Example: python create_msg.py 1000_messages.csv 1000_translated.MSG")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_msg = sys.argv[2]
    else:
        # Generate output filename from input
        base_name = os.path.splitext(input_csv)[0]
        output_msg = f"{base_name}_new.MSG"
    
    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' not found")
        sys.exit(1)
    
    try:
        print(f"Creating MSG file from {input_csv}...")
        create_msg_file(input_csv, output_msg)
        
        # Verify the created file
        if verify_msg_file(input_csv, output_msg):
            print(f"\nSUCCESS: MSG file created and verified: {output_msg}")
        else:
            print(f"\nWARNING: MSG file created but verification failed: {output_msg}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()