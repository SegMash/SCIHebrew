@echo off
python scripts\text\map_files.py .\output_kq1\single_messages_english.txt .\output_kq1\single_messages_hebrew.txt .\output_kq1\single_mapping.txt
python scripts\text\map_files.py --multiline .\output_kq1\multi_messages_english.txt .\output_kq1\multi_messages_hebrew.txt .\output_kq1\single_mapping.txt --append
python scripts\text\map_files.py .\output_kq1\format_messages_english.txt .\output_kq1\format_messages_hebrew.txt .\output_kq1\single_mapping.txt --append
python scripts\text\translate_texts.py SCICompanion-3.2.4.0\kq1_resources games_assets\kq1\bin .\output_kq1\single_mapping.txt

python.exe .\scripts\vocab\vocab_import.py output_kq1 kq1_work .\games_assets\kq1\bin --output-vocab-file vocab.900
copy .\games_assets\kq1\bin\text.* kq1_work\
REM commands to create mapping file for built-in messages and to replace in gog sources
REM python.exe .\scripts\text\map_files.py .\output_kq1\built_in_messages_english.txt .\output_kq1\built_in_messages_hebrew.txt .\output_kq1\built-in-mapping.txt
REM python.exe .\scripts\scripts\replace_strings.py .\kq1_new\src .\kq1_new\src_heb .\output_kq1\built-in-mapping.txt

REM makensis.exe .\kq1_hebrew_patch.nsi
REM powershell -Command "(Get-FileHash -Algorithm MD5 'games_assets\kq1\bin\font.000').Hash.ToLower()"