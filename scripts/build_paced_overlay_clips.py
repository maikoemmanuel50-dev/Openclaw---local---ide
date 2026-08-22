"""
Build short paced overlay MP4s from stills so Resolve honors ASL
(stills default to 5s / 120f in this project; API cannot change still duration).

Kinetic: 10–18f | YB: 32–48f @ 24fps
Output: renders/paced_overlays/{kinetic,yb}/
Then place via resolve_pace_from_mp4.py path in this file.

Run: python scripts/build_paced_overlay_clips.py
"""
from __future__ import annotations

import os
import shutil
import subprocess

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
GRADED = os.path.join(PROJECT, "assets", "canva", "kinetic", "graded_1080")
YB_DIR = os.path.join(PROJECT, "assets", "yellow_ball", "export")
OUT_K = os.path.join(PROJECT, "renders", "paced_overlays", "kinetic")
OUT_Y = os.path.join(PROJECT, "renders", "paced_overlays", "yb")
FPS = 24

# (png, frames) — kinetic
KINETIC = [
    ("k01_nairobi_dawn_1080.png", 14),
    ("k01_matatu_street_1080.png", 12),
    ("pr_s01_phone_commute_1080.png", 14),
    ("pr_s01_street_morning_1080.png", 12),
    ("k02_feature_phone_1080.png", 16),
    ("k02_market_kiosk_1080.png", 14),
    ("pr_s02_cash_hands_1080.png", 14),
    ("k03_coworking_1080.png", 12),
    ("k03_laptop_keys_1080.png", 12),
    ("pr_s03_startup_whiteboard_1080.png", 12),
    ("k04_phone_scroll_1080.png", 10),
    ("pr_s04_thumbs_scroll_1080.png", 10),
    ("k05_data_city_1080.png", 16),
    ("k06_solar_roof_1080.png", 14),
    ("k06_solar_field_1080.png", 12),
    ("pr_s06_rural_power_1080.png", 12),
    ("k07_kenya_landscape_1080.png", 18),
    ("pr_s07_dirt_road_1080.png", 14),
    ("k08_town_street_1080.png", 16),
    ("pr_s08_quiet_shop_1080.png", 14),
    ("k09_nairobi_dusk_1080.png", 12),
    ("k09_skyline_modern_1080.png", 12),
    ("pr_s09_dusk_skyline_1080.png", 14),
    ("k11_native_skyline_1080.png", 14),
    ("k12_native_solar_1080.png", 12),
    ("k13_native_datagrid_1080.png", 14),
    ("k14_native_road_dusk_1080.png", 14),
    ("k15_native_market_1080.png", 12),
    ("k16_native_fiber_1080.png", 12),
    ("k17_native_skyline_b_1080.png", 12),
    ("k18_native_solar_b_1080.png", 12),
    ("k19_native_datagrid_b_1080.png", 12),
    ("k20_native_road_b_1080.png", 12),
    ("k21_native_market_b_1080.png", 12),
    ("k22_native_fiber_b_1080.png", 12),
]

YB = [
    ("yb_sun_seed.png", 48),
    ("yb_body_crowd.png", 40),
    ("yb_mpesa_coin.png", 40),
    ("yb_body_single.png", 36),
    ("yb_data_orb.png", 36),
    ("yb_dim_gap.png", 40),
    ("yb_body_founder_dim.png", 40),
    ("yb_forecast_beacon.png", 48),
]

# Mild Ken Burns (Resolve Dynamic Zoom equivalent) — documentary micro-push
MOTIONS = [
    "z='min(1.0+0.0015*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "z='1.08':x='(iw-iw/zoom)*on/{d}':y='(ih-ih/zoom)/2'",
    "z='1.1':x='(iw-iw/zoom)*(1-on/{d})':y='(ih-ih/zoom)/2'",
]


def ffmpeg() -> str:
    ff = shutil.which("ffmpeg")
    if not ff:
        raise RuntimeError("ffmpeg not found")
    return ff


def still_to_mp4(ff: str, src: str, frames: int, out: str, motion_i: int, alpha: bool = False) -> None:
    d = max(1, frames)
    m = MOTIONS[motion_i % len(MOTIONS)].format(d=d)
    # High quality short plate — fidelity guide: one encode only
    vf = (
        f"scale=1920:1080:force_original_aspect_ratio=increase,"
        f"crop=1920:1080,zoompan={m}:d={d}:s=1920x1080:fps={FPS}"
    )
    cmd = [
        ff, "-y", "-loop", "1", "-i", src,
        "-vf", vf, "-frames:v", str(frames),
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{os.path.basename(out)}: {r.stderr[-300:]}")


def main():
    ff = ffmpeg()
    os.makedirs(OUT_K, exist_ok=True)
    os.makedirs(OUT_Y, exist_ok=True)
    for i, (name, frames) in enumerate(KINETIC):
        src = os.path.join(GRADED, name)
        if not os.path.isfile(src):
            print("skip", name)
            continue
        out = os.path.join(OUT_K, name.replace(".png", f"_{frames}f.mp4"))
        still_to_mp4(ff, src, frames, out, i)
        print("OK", os.path.basename(out))
    for i, (name, frames) in enumerate(YB):
        src = os.path.join(YB_DIR, name)
        if not os.path.isfile(src):
            print("skip", name)
            continue
        out = os.path.join(OUT_Y, name.replace(".png", f"_{frames}f.mp4"))
        still_to_mp4(ff, src, frames, out, i)
        print("OK", os.path.basename(out))
    print("PACED_OVERLAYS_DONE")


if __name__ == "__main__":
    main()
