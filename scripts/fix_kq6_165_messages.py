import sys

csv_path = sys.argv[1]
target = '1,0,7,4,28,925,0,0,0,0'
replacement = '1,0,7,4,28,925,0,0,0,0,"""אני מוכנה."""'

with open(csv_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(csv_path, 'w', encoding='utf-8') as f:
    for line in lines:
        if target in line:
            f.write(replacement + '\n')
        else:
            f.write(line)
