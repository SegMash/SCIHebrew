@echo off
python scripts\text\map_files.py .\output_qfg1\single_messages.txt .\output_qfg1\single_messages_hebrew.txt .\output_qfg1\single_mapping.txt
python scripts\text\map_files.py --multiline .\output_qfg1\multi_messages.txt .\output_qfg1\multi_messages_hebrew.txt .\output_qfg1\single_mapping.txt --append
python scripts\text\map_files.py .\output_qfg1\format_messages.txt .\output_qfg1\format_messages_hebrew.txt .\output_qfg1\single_mapping.txt --append
python scripts\text\translate_texts.py SCICompanion-3.2.4.0\qfg1_resources games_assets\qfg1\bin .\output_qfg1\single_mapping.txt

python.exe .\scripts\vocab\vocab_import.py output_qfg1 qfg1_work games_assets\qfg1\bin

copy games_assets\qfg1\bin\text.* qfg1_work
copy games_assets\qfg1\bin\script.* qfg1_work
copy games_assets\qfg1\bin\view.* qfg1_work
copy games_assets\qfg1\bin\pic.* qfg1_work

REM commands to create mapping file for built-in messages and to replace in gog sources
REM python.exe .\scripts\text\map_files.py .\output_qfg1\built-in-messages.txt .\output_qfg1\built-in-messages_hebrew.txt .\output_qfg1\built-in-mapping.txt
REM python.exe .\scripts\scripts\replace_strings.py .\qfg1_gog\src .\qfg1_gog\src_heb .\output_qfg1\built-in-mapping.txt

REM makensis.exe .\qfg1_hebrew_patch.nsi
REM powershell -Command "(Get-FileHash -Algorithm MD5 'games_assets\qfg1\bin\font.000').Hash.ToLower()"