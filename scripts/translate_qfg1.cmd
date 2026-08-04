@echo off
python scripts\text\map_files.py .\output_qfg1\single_messages.txt .\output_qfg1\single_messages_hebrew.txt .\output_qfg1\single_mapping.txt
python scripts\text\map_files.py --multiline .\output_qfg1\multi_messages.txt .\output_qfg1\multi_messages_hebrew.txt .\output_qfg1\single_mapping.txt --append
python scripts\text\map_files.py .\output_qfg1\format_messages.txt .\output_qfg1\format_messages_hebrew.txt .\output_qfg1\single_mapping.txt --append
REM python scripts\text\translate_texts.py SCICompanion-3.2.4.0\qfg1_resources_1200 games_assets\qfg1\bin_new .\output_qfg1\single_mapping.txt --csv .\output_qfg1\QFG1_Hebrew.csv --fuzzy-distance 10
python scripts\text\translate_texts.py c:\devTools\SCICompanion-3.2.4.0\qfg1_recourses games_assets\qfg1\bin_new .\output_qfg1\single_mapping.txt --csv .\output_qfg1\QFG1_Hebrew.csv --fuzzy-distance 0 --no-update-csv --unique-messages .\output_qfg1\unique_messages.txt

python.exe .\scripts\vocab\vocab_import.py output_qfg1 EGA games_assets\qfg1\bin_new

python.exe .\output_qfg1\patch_text_000.py games_assets\qfg1\bin_new\text.000 games_assets\qfg1\bin_new\text.000

copy games_assets\qfg1\bin_new\text.* EGA
REM copy games_assets\qfg1\bin\script.* EGA
copy games_assets\qfg1\bin_new\view.* EGA
copy games_assets\qfg1\bin_new\pic.* EGA

REM makensis.exe .\qfg1_hebrew_patch.nsi

REM commands to create mapping file for built-in messages and to replace in gog sources
REM python.exe .\scripts\text\map_files.py .\output_qfg1\built-in-messages.txt .\output_qfg1\built-in-messages_hebrew.txt .\output_qfg1\built-in-mapping.txt
REM python.exe .\scripts\scripts\replace_strings.py .\qfg1_gog\src .\qfg1_gog\src_heb .\output_qfg1\built-in-mapping.txt

makensis.exe .\qfg1_hebrew_patch.nsi
REM powershell -Command "(Get-FileHash -Algorithm MD5 'games_assets\qfg1\bin\font.000').Hash.ToLower()"