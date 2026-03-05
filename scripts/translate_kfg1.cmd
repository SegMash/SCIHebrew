@echo off
python scripts\map_files.py .\output_kfg1\single_messages.txt .\output_kfg1\single_messages_hebrew.txt .\output_kfg1\single_mapping.txt
REM python scripts\map_files.py --multiline .\output_kq4\multi_messages.txt .\output_kq4\multi_messages_hebrew.txt .\output_kq4\single_mapping.txt --append
REM python scripts\map_files.py .\output_kq4\format_messages.txt .\output_kq4\format_messages_hebrew.txt .\output_kq4\single_mapping.txt --append
REM python scripts\translate_texts.py SCICompanion-3.2.4.0\kq4_resources patch_kq4\bin .\output_kq4\single_mapping.txt

REM python.exe .\scripts\vocab_import.py output_kq4 kq4_work patch_kq4\bin

REM commands to create mapping file for built-in messages and to replace in gog sources
REM python.exe .\scripts\map_files.py .\output_kq4\built-in-messages.txt .\output_kq4\built-in-messages_hebrew.txt .\output_kq4\built-in-mapping.txt
REM python.exe .\scripts\replace_strings.py .\kq4_gog\src .\kq4_gog\src_heb .\output_kq4\built-in-mapping.txt

REM makensis.exe .\kq4_hebrew_patch.nsi
REM powershell -Command "(Get-FileHash -Algorithm MD5 'patch_kq4\bin\font.000').Hash.ToLower()"