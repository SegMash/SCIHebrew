#!/usr/bin/env python3
"""
SCI Font Builder - Creates SCI font files from PNG character images.
Reverse operation of parse_font.py.
"""

import argparse
import struct
import os
from pathlib import Path
from PIL import Image


def read_png_to_bitmap(png_path):
    """Read a PNG file and convert to SCI bitmap format."""
    img = Image.open(png_path)
    
    # Convert to 1-bit black and white if needed
    if img.mode != '1':
        img = img.convert('1')
    
    width, height = img.size
    
    # Convert image to bitmap data
    bitmap_data = bytearray()
    bytes_per_row = (width + 7) // 8
    
    for y in range(height):
        for byte_idx in range(bytes_per_row):
            row_byte = 0
            for bit_idx in range(8):
                x = byte_idx * 8 + bit_idx
                if x < width:
                    pixel = img.getpixel((x, y))
                    # In PNG: 0=black, 1=white (for mode '1')
                    # In SCI: 1=draw (white), 0=background (black)
                    if pixel:  # White pixel
                        row_byte |= (1 << (7 - bit_idx))
            bitmap_data.append(row_byte)
    
    return width, height, bytes(bitmap_data)


def build_font(input_dir, output_dir, font_name, line_height):
    """Build SCI font file from BMP character images."""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all PNG files and sort by character number
    png_files = {}
    for png_file in input_path.glob("*.png"):
        try:
            char_num = int(png_file.stem)
            png_files[char_num] = png_file
        except ValueError:
            print(f"Skipping non-numeric file: {png_file.name}")
            continue
    
    if not png_files:
        print(f"Error: No PNG files found in {input_dir}")
        return 1
    
    # Determine character range
    min_char = min(png_files.keys())
    max_char = max(png_files.keys())
    num_chars = max_char + 1  # Total number of character slots
    
    print(f"Building font '{font_name}':")
    print(f"  Character range: {min_char} to {max_char}")
    print(f"  Total characters: {num_chars}")
    print(f"  Line height: {line_height}")
    print()
    
    # Read all character data
    char_data = {}
    
    for char_num in range(num_chars):
        if char_num in png_files:
            try:
                width, height, bitmap = read_png_to_bitmap(png_files[char_num])
                char_data[char_num] = (width, height, bitmap)
                print(f"Character {char_num}: {width}x{height} pixels from {png_files[char_num].name}")
            except Exception as e:
                print(f"Error reading {png_files[char_num].name}: {e}")
                char_data[char_num] = (0, 0, b'')  # Empty character
        else:
            # Empty character slot
            char_data[char_num] = (0, 0, b'')
    
    # Build font file
    font_data = bytearray()
    
    # Header
    font_data.extend(struct.pack('<I', 0x87))  # Reserved (4 bytes)
    font_data.extend(struct.pack('<H', num_chars))  # Number of characters (2 bytes)
    font_data.extend(struct.pack('<H', line_height))  # Line height (2 bytes)
    
    # Calculate pointers
    pointer_table_size = num_chars * 2
    header_size = 8  # 4 + 2 + 2
    data_start = header_size + pointer_table_size
    
    pointers = []
    current_offset = data_start
    
    for char_num in range(num_chars):
        # Pointer needs to be offset by -2 (as per the +2 correction in parse_font.py)
        pointers.append(current_offset - 2)
        
        width, height, bitmap = char_data[char_num]
        char_size = 2 + len(bitmap)  # 1 byte height + 1 byte width + bitmap data
        current_offset += char_size
    
    # Write pointer table
    for pointer in pointers:
        font_data.extend(struct.pack('<H', pointer))
    
    # Write character data
    for char_num in range(num_chars):
        width, height, bitmap = char_data[char_num]
        font_data.append(width)   # 1 byte
        font_data.append(height)  # 1 byte
        font_data.extend(bitmap)
    
    # Write font file
    output_file = output_path / font_name
    with open(output_file, 'wb') as f:
        f.write(font_data)
    
    print(f"\nSuccessfully created font file: {output_file}")
    print(f"Total file size: {len(font_data)} bytes")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Build SCI font files from PNG character images.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  python build_font.py fonts/001 output_fonts
  
This will create output_fonts/font.001 from PNG files in fonts/001/
        '''
    )
    
    parser.add_argument('input_dir', help='Directory containing PNG character files (e.g., fonts/001)')
    parser.add_argument('output_dir', help='Directory to save the font file')
    parser.add_argument('--line-height', type=lambda x: int(x, 16) if x.startswith('0x') else int(x), 
                        default=0x0C, 
                        help='Line height for the font (default: 0x0C / 12)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' not found.")
        return 1
    
    # Extract font number from input directory (e.g., "fonts/001" -> "001")
    input_path = Path(args.input_dir)
    font_number = input_path.name
    font_name = f"font.{font_number}"
    
    try:
        return build_font(args.input_dir, args.output_dir, font_name, args.line_height)
    except Exception as e:
        print(f"Error building font: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
