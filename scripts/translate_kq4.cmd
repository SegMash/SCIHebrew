@echo off
python scripts\text\map_files.py .\output_kq4\single_messages.txt .\output_kq4\single_messages_hebrew.txt .\output_kq4\single_mapping.txt
python scripts\text\map_files.py --multiline .\output_kq4\multi_messages.txt .\output_kq4\multi_messages_hebrew.txt .\output_kq4\single_mapping.txt --append
python scripts\text\map_files.py .\output_kq4\format_messages.txt .\output_kq4\format_messages_hebrew.txt .\output_kq4\single_mapping.txt --append
python scripts\text\translate_texts.py SCICompanion-3.2.4.0\kq4_resources games_assets\kq4\bin .\output_kq4\single_mapping.txt

python.exe .\scripts\vocab\vocab_import.py output_kq4 kq4_work games_assets\kq4\bin

REM commands to create mapping file for built-in messages and to replace in gog sources
REM python.exe .\scripts\text\map_files.py .\output_kq4\built-in-messages.txt .\output_kq4\built-in-messages_hebrew.txt .\output_kq4\built-in-mapping.txt
REM python.exe .\scripts\scripts\replace_strings.py .\kq4_gog\src .\kq4_gog\src_heb .\output_kq4\built-in-mapping.txt

makensis.exe .\kq4_hebrew_patch.nsi
powershell -Command "(Get-FileHash -Algorithm MD5 'games_assets\kq4\bin\font.000').Hash.ToLower()"