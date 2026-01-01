@echo off
REM Extract english texts from KQ5 subtitile files (300-390)
python .\scripts\extract_english.py .\games_assets\kq5 output_kq5
for %%f in (300 330 340 350 370 390) do (
    echo Processing module %%f...
    python scripts\map_files.py .\output_kq5\%%f_english.txt .\output_kq5\%%f_hebrew.txt .\output_kq5\mapping_%%f.txt
    python scripts\replace_in_tsv.py .\games_assets\kq5\%%f.tsv .\output_kq5\mapping_%%f.txt .\output_kq5
    python scripts\tsv2tex.py .\output_kq5\%%f.tsv .\kq5_work
)

python scripts\tex2tsv.py SCICompanion-3.2.4.0\kq5_resources temp_kq5
python scripts\tex2tsv.py games_assets\kq5\0.TEX temp_kq5
python scripts\extract_english.py temp_kq5 output_kq5
REM 763 & 601  - I did manualy.
for %%f in (0 29 63 89 113 119 123 216 220 600 602 610 659 663 664 673 749 754 755 756 889 950) do (
    python scripts\map_files.py .\output_kq5\%%f_english.txt .\output_kq5\%%f_hebrew.txt .\output_kq5\mapping_%%f.txt
    python scripts\replace_in_tsv.py .\temp_kq5\%%f.tsv .\output_kq5\mapping_%%f.txt .\output_kq5
    python scripts\tsv2tex.py .\output_kq5\%%f.tsv .\kq5_work --no-selector
)
REM Copy manuall tex files
for %%f in (601 763) do (
    copy .\games_assets\kq5\%%f.tex .\kq5_work
)
REM Copy manuall SCR files
for %%f in (0 119 763) do (
    copy .\games_assets\kq5\%%f.scr .\kq5_work
)
REM Copy fonts
for %%f in (0 4 69 8) do (
    copy .\games_assets\kq5\%%f.fon .\kq5_work
)
REM Copy images
for %%f in (107) do (
    copy .\games_assets\kq5\%%f.p56 .\kq5_work
)

REM Copy all *.scr files from assets to work dir
copy .\games_assets\kq5\*.scr .\kq5_work

REM - Copy all TEX files from resources, and then from work dir (GOG patches)
REM - extract texts from tex files.
REM - translate to hebrew
REM - add 

