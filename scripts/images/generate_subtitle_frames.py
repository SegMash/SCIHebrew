import shutil
import subprocess
import sys
import os
from dataclasses import dataclass

FPS = 8
BASE_FRAMES_DIR = "frames_kq6"
OUTPUT_DIR = "games_assets/kq6/opening_frames"

@dataclass
class Subtitle:
    message: str
    start_second: float
    end_second: float
    y_position: int = 75


def generate_subtitle_frames(
    text,
    start_frame,
    end_frame,
    output_dir=OUTPUT_DIR,
    base_frames_dir=BASE_FRAMES_DIR,
    width=200,
    height=100,
    font="MANTM.TTF",
    font_size=20,
    font_color="#9BA3D3",
    font_color_index=None,
    background="black",
    margin=20,
    y_position=20,
    use_base_frames=True,
    use_fade=False,
    set_border=False
):
    total = end_frame - start_frame + 1

    for i, frame_num in enumerate(range(start_frame, end_frame + 1)):
        if not use_fade:
            fade = 0
        elif total == 1:
            fade = 100
        else:
            fade = max(0, 100 - round(100 * (1 - abs(2 * i / (total - 1) - 1)) * 2))

        output_path     = os.path.join(output_dir, f"frame_{frame_num:04d}.png")
        if use_base_frames:
            base_frame_path = os.path.join(base_frames_dir, f"frame_{frame_num:04d}.png")
        else:
            base_frame_path = None

        cmd = [
            sys.executable, r"scripts\generate_text_frame.py",
            "--width",      str(width),
            "--height",     str(height),
            "--font",       font,
            "--font-size",  str(font_size),
            "--font-color", font_color,
            "--background", background,
            "--margin",     str(margin),
            "--y-position", str(y_position),
            "--text",       text,
            "--output",     output_path,
            "--fade",       str(fade),
        ]

        if base_frame_path is not None:
            cmd += ["--base-frame", base_frame_path]

        if font_color_index is not None:
            cmd += ["--font-color-index", str(font_color_index)]

        if set_border:
            cmd += ["--set-border"]

        print(f"Frame {frame_num:04d}  fade={fade:3d}")
        subprocess.run(cmd, check=True)




# ---- Copy frames 70-950 from base folder to output folder ----
for frame_num in range(70, 951):
    src = os.path.join(BASE_FRAMES_DIR, f"frame_{frame_num:04d}.png")
    dst = os.path.join(OUTPUT_DIR, f"frame_{frame_num:04d}.png")
    shutil.copy2(src, dst)
print("Copied frames 70-950 from base folder to output folder.")

# ---- First subtitle (outside loop) ----
generate_subtitle_frames(
    text="לפני זמן רב, בטירתה של ממלכה בשם דבנטרי...",
    start_frame=1,
    end_frame=60,
    font_size=20,
    y_position=68,
    use_base_frames=False,
    use_fade=True,
)

# ---- Subtitle definitions ----
subtitles = [
    Subtitle(message="אלכסנדר! הנה אתה!", start_second=12, end_second=14.5),
    Subtitle(message="אתה עדיין חושב על קסימה, נכון?", start_second=14.5, end_second=19),
    Subtitle(message="המממ? אני מניח שכן.", start_second=19, end_second=21),
    Subtitle(message="בני, עברו חודשים. אתה חייב להתאושש.", start_second=21, end_second=25),
    Subtitle(message="אחרי הכל, פגשת אותה רק פעם אחת...", start_second=25, end_second=28),
    Subtitle(message="אני יודע.", start_second=28, end_second=29),
]

for sub in subtitles:
    generate_subtitle_frames(
        text=sub.message,
        start_frame=round(sub.start_second * FPS) + 1,
        end_frame=round(sub.end_second * FPS),
        font="arial.ttf",
        font_size=12,
        font_color="#ffffff",
        font_color_index=255,
        y_position=sub.y_position,
        use_base_frames=True,
        set_border=True,
    )


