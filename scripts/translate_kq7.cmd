@echo off
setlocal enabledelayedexpansion
python.exe .\scripts\json_to_hebrew_kq6.py .\output_kq7\messages.json .\output_kq7
python .\scripts\parse_sci1.1_messages.py .\SCICompanion-3.2.4.0\kq7_resources .\output_kq7
REM Process all *_messages.csv files in output_kq7 directory
for %%f in (.\output_kq7\*_messages.csv) do (
    REM Extract filename without extension
    set "filename=%%~nf"
    
    REM Remove "_messages" suffix to get the prefix
    set "prefix=!filename:_messages=!"
    
    echo Processing module !prefix!...
    python scripts\map_files.py .\output_kq7\!prefix!_messages_english.txt .\output_kq7\!prefix!_messages_hebrew.txt .\output_kq7\mapping_!prefix!.txt
    python .\scripts\replace_in_csv.py .\output_kq7\!prefix!_messages.csv .\output_kq7\mapping_!prefix!.txt .\output_kq7\
    python .\scripts\create_msg.py .\output_kq7\!prefix!_messages.csv .\games_assets\kq7\!prefix!.msg
)

REM Copy all files from games_assets\kq7 to kq7_work
copy .\games_assets\kq7\* .\kq7_work\PATCHES\

endlocal
REM TODO - finish logic file 30
REM  Check: This is very deep. It almost looks like a hinge. (1100)
REM  2000
REM Translate chapter titles
REM Translate replacment store sign
REM Translate screen of death