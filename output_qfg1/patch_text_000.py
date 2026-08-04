import sys
import os

def patch_binary_file(input_path, output_path):
    # בדיקה שהקובץ קיים
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' does not exist.")
        return

    # קריאת הקובץ הבינארי
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    # בדיקה שהקובץ מספיק גדול
    if len(data) < 90:
        print(f"Error: File is too small ({len(data)} bytes). It must be at least 90 bytes.")
        return

    # 1. הוספת רווח (0x20) בבית ה-73 (אינדקס 72)
    data.insert(72, 0x20)

    # 2. מחיקת הבית ה-90 המקורי. 
    # בגלל שהוספנו בית מקודם, המיקום של הבית ה-90 המקורי זז מאינדקס 89 לאינדקס 90.
    del data[90]

    # שמירת הקובץ החדש
    with open(output_path, 'wb') as f:
        f.write(data)

    print(f"Success! Patched file saved to: {output_path}")

if __name__ == "__main__":
    # בדיקה שכל הפרמטרים התקבלו משורת הפקודה
    if len(sys.argv) < 3:
        print("Usage: python patch_file.py <input_file> <output_file>")
        print("Example: python patch_file.py script.exe script_patched.exe")
    else:
        patch_binary_file(sys.argv[1], sys.argv[2])
