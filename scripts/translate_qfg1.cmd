@echo off
python scripts\map_files.py .\output_qfg1\single_messages.txt .\output_qfg1\single_messages_hebrew.txt .\output_qfg1\single_mapping.txt
python scripts\map_files.py --multiline .\output_qfg1\multi_messages.txt .\output_qfg1\multi_messages_hebrew.txt .\output_qfg1\single_mapping.txt --append
python scripts\map_files.py .\output_qfg1\format_messages.txt .\output_qfg1\format_messages_hebrew.txt .\output_qfg1\single_mapping.txt --append
python scripts\translate_texts.py SCICompanion-3.2.4.0\qfg1_resources patch_qfg1\bin .\output_qfg1\single_mapping.txt

python.exe .\scripts\vocab_import.py output_qfg1 qfg1_work patch_qfg1\bin

copy patch_qfg1\bin\text.* qfg1_work

REM commands to create mapping file for built-in messages and to replace in gog sources
REM python.exe .\scripts\map_files.py .\output_qfg1\built-in-messages.txt .\output_qfg1\built-in-messages_hebrew.txt .\output_qfg1\built-in-mapping.txt
REM python.exe .\scripts\replace_strings.py .\qfg1_gog\src .\qfg1_gog\src_heb .\output_qfg1\built-in-mapping.txt

REM makensis.exe .\qfg1_hebrew_patch.nsi
REM powershell -Command "(Get-FileHash -Algorithm MD5 'patch_qfg1\bin\font.000').Hash.ToLower()"