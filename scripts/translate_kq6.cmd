@echo off
setlocal enabledelayedexpansion

python .\scripts\parse_sci1.1_messages.py .\SCICompanion-3.2.4.0\kq6_resources .\output_kq6
REM Process all *_messages.csv files in output_kq6 directory
for %%f in (.\output_kq6\*_messages.csv) do (
    REM Extract filename without extension
    set "filename=%%~nf"
    
    REM Remove "_messages" suffix to get the prefix
    set "prefix=!filename:_messages=!"
    
    echo Processing module !prefix!...
    python scripts\map_files.py .\output_kq6\!prefix!_messages_english.txt .\output_kq6\!prefix!_messages_hebrew.txt .\output_kq6\mapping_!prefix!.txt
    python .\scripts\replace_in_csv.py .\output_kq6\!prefix!_messages.csv .\output_kq6\mapping_!prefix!.txt .\output_kq6\
    python .\scripts\create_msg.py .\output_kq6\!prefix!_messages.csv .\games_assets\kq6\!prefix!.msg
)

REM Copy all files from games_assets\kq6 to kq6_work
copy .\games_assets\kq6\* .\kq6_work\

endlocal
