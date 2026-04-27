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
REM TODO - when finished make sure all files are in assets dir - and uncomment the next time !!!!!!!!!!!!!!!!!!!!!!!!!
REM copy .\games_assets\kq7\* .\kq7_work\PATCHES\

endlocal
REM TODO - finish logic file 30
REM  Check: This is very deep. It almost looks like a hinge. (1100)
REM Translate chapter titles - Done.
REM Translate replacment store sign (המסך של העכבר המחליף) - מוזרים ונדירים - Done
REM Translate screen of death- Done!
REM Translate "Bowl with Green Water" to "קערה עם מים ירוקים" (or something better)  - 24.SRC - to check!
REM Translate the dirty board . Before and After! - Gal Shemesh
REM Translate board- Done!
REM זה תק  ו ע - Done.
REM לתרגם שלט של ד"ר קדבר Dot is Out - 4107
REM לתרגם קופסת חלקי חילוף - 4211
REM כתוביות לסרטון בסוף
REM כתוביות לסרטון ההתחלה?
REM translate view 985 - Bookmark options
REM translate view 940 - chapter progress
REM translate view 970 - You have already 10 games...
REM translate view 972 - warning before delete
