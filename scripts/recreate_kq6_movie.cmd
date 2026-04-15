@echo off
REM ffmpeg -i .\kq6_gog\TOON.AVI .\frames_kq6\frame_%04d.png
python .\scripts\generate_subtitle_frames.py
python scripts\encode_avi_raw.py .\games_assets\kq6\opening_frames kq6_work\TOON_no_sound.AVI 8
ffmpeg -y -i .\kq6_work\TOON_no_sound.AVI -i kq6_gog\TOON.AVI -map 0:v -map 1:a -c copy kq6_work\TOON.AVI
