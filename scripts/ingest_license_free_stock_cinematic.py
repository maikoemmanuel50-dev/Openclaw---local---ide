"""
License-free stock ingest + cinematic pans for Africa S1 kinetic track.
Sources: Mixkit (free license) + Unsplash (photos → pans) + Coverr/Pexels-style public MP4s.
Respects soft-pop palette; inserts only — does NOT extend past 7:00.

Run: python scripts/ingest_license_free_stock_cinematic.py
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
RAW = PROJECT / "assets" / "stock" / "license_free" / "raw"
GRADED = PROJECT / "assets" / "stock" / "license_free" / "graded_1080"
CUTS = PROJECT / "renders" / "paced_overlays" / "stock_cinematic"
MANIFEST = PROJECT / "assets" / "stock" / "license_free" / "manifest.json"
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AfricaS1Stock/1.0",
    "Accept": "*/*",
}

# Soft-pop grade (cream / mustard warmth, indigo shadows) — documentary grade
# Keep ball hero #FFD54F separate; this is for B-roll only.
SOFTPOP_VF = (
    "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
    "eq=contrast=1.06:saturation=0.88:brightness=0.015,"
    "colorbalance=rs=0.06:gs=0.02:bs=-0.04:rm=0.04:gm=0.01:bm=-0.03:"
    "rh=0.03:gh=0.01:bh=-0.02,"
    "unsharp=5:5:0.6:3:3:0.0"
)

# Mixkit free stock (license: Mixkit License — free for commercial)
# Prefer /videos/ download CDN paths; preview URLs often 403 now.
VIDEOS = {
    # dawn / city
    "city_sunrise_aerial": "https://assets.mixkit.co/videos/4439/4439-720.mp4",
    "city_traffic_night": "https://assets.mixkit.co/videos/4445/4445-720.mp4",
    "city_walk_busy": "https://assets.mixkit.co/videos/4601/4601-720.mp4",
    "sunset_skyline": "https://assets.mixkit.co/videos/4356/4356-720.mp4",
    "city_rain_street": "https://assets.mixkit.co/videos/416/416-720.mp4",
    "highway_timelapse": "https://assets.mixkit.co/videos/3246/3246-720.mp4",
    "skyline_clouds": "https://assets.mixkit.co/videos/4870/4870-720.mp4",
    # tech / phone / office (avoid face-hero — crop/grade later)
    "phone_hands_type": "https://assets.mixkit.co/videos/34506/34506-720.mp4",
    "keyboard_work": "https://assets.mixkit.co/videos/4497/4497-720.mp4",
    "laptop_office": "https://assets.mixkit.co/videos/4623/4623-720.mp4",
    "coding_screen": "https://assets.mixkit.co/videos/3248/3248-720.mp4",
    "data_center_lights": "https://assets.mixkit.co/videos/11749/11749-720.mp4",
    # energy / solar
    "solar_roof_panels": "https://assets.mixkit.co/videos/5045/5045-720.mp4",
    "wind_turbines": "https://assets.mixkit.co/videos/4822/4822-720.mp4",
    # abstract / data feel
    "digital_city_anim": "https://assets.mixkit.co/videos/11748/11748-720.mp4",
    "network_nodes": "https://assets.mixkit.co/videos/11750/11750-720.mp4",
}

# Fallback preview URLs if CDN id path fails
VIDEO_FALLBACKS = {
    "city_sunrise_aerial": "https://assets.mixkit.co/videos/preview/mixkit-aerial-view-of-a-city-at-sunrise-4439-large.mp4",
    "city_traffic_night": "https://assets.mixkit.co/videos/preview/mixkit-city-traffic-at-night-with-blurred-lights-4445-large.mp4",
    "city_walk_busy": "https://assets.mixkit.co/videos/preview/mixkit-people-walking-in-a-busy-city-street-4601-large.mp4",
    "sunset_skyline": "https://assets.mixkit.co/videos/preview/mixkit-silhouettes-of-buildings-at-sunset-4356-large.mp4",
    "phone_hands_type": "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-person-typing-on-a-smartphone-34506-large.mp4",
    "keyboard_work": "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-man-working-on-a-computer-4497-large.mp4",
    "laptop_office": "https://assets.mixkit.co/videos/preview/mixkit-man-working-on-his-laptop-in-an-office-4623-large.mp4",
    "solar_roof_panels": "https://assets.mixkit.co/videos/preview/mixkit-solar-panels-on-a-roof-5045-large.mp4",
    "digital_city_anim": "https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-a-city-11748-large.mp4",
    "city_rain_street": "https://assets.mixkit.co/videos/preview/mixkit-cars-driving-through-a-rainy-city-416-large.mp4",
    "highway_timelapse": "https://assets.mixkit.co/videos/preview/mixkit-time-lapse-of-a-busy-highway-at-night-3246-large.mp4",
    "skyline_clouds": "https://assets.mixkit.co/videos/preview/mixkit-city-skyline-with-clouds-passing-by-4870-large.mp4",
    "coding_screen": "https://assets.mixkit.co/videos/preview/mixkit-software-developer-working-on-code-3248-large.mp4",
    "data_center_lights": "https://assets.mixkit.co/videos/preview/mixkit-server-room-with-glowing-lights-11749-large.mp4",
    "wind_turbines": "https://assets.mixkit.co/videos/preview/mixkit-wind-turbines-in-a-field-4822-large.mp4",
    "network_nodes": "https://assets.mixkit.co/videos/preview/mixkit-digital-network-connections-11750-large.mp4",
}

# Extra Unsplash stills for cinematic pans (license: Unsplash)
STILL_IDS = {
    "pan_nairobi_dawn": "1477959858617-67f85cf4f1df",
    "pan_city_morning": "1449824913935-59a10b8d2000",
    "pan_market": "1555529907-de80095be0e5",
    "pan_laptop": "1461749280684-dccba630e2f6",
    "pan_phone": "1511707171634-5f897ff02aa9",
    "pan_solar": "1509391366364-4b9344020dea",
    "pan_savanna": "1516026672322-bc52d61a55d5",
    "pan_dusk_towers": "1486406149866-c6cefb3740b5",
    "pan_street_texture": "1477959858617-67f85cf4f1df",
    "pan_data_city": "1480714378408-67cf0d13bcbf",
    "pan_gold_abstract": "1518709268805-4e9042af2176",
    "pan_power": "1473341304170-971dccb5ac1e",
    "pan_fiber_cables": "1558494949-ef010cbdcc31",
    "pan_container_port": "1494412574643-ff11b1a4ab91",
    "pan_rural_road": "1500382017468-9049fed747ef",
    "pan_night_market": "1517248135467-4c7deda6e0f5",
    "pan_office_glass": "1497366216548-37526070297c",
    "pan_circuit": "1518770660439-4636190af475",
}

# Scene windows (relative frames) — dense inserts, protect stats
# Each cut: (scene_tag, record_rel, frames)
INSERT_PLAN = [
    # S01 cold open — high density
    ("city_sunrise_aerial", 36, 16),
    ("pan_nairobi_dawn", 70, 14),
    ("city_walk_busy", 100, 14),
    ("pan_street_texture", 150, 12),
    ("phone_hands_type", 200, 12),
    ("pan_phone", 260, 12),
    ("city_traffic_night", 320, 14),
    # S02
    ("pan_market", 1240, 14),
    ("phone_hands_type", 1300, 12),
    ("pan_phone", 1380, 12),
    ("keyboard_work", 1500, 14),
    # S03 hubs
    ("laptop_office", 2320, 14),
    ("pan_laptop", 2380, 12),
    ("keyboard_work", 2480, 12),
    ("pan_data_city", 2600, 14),
    # S04 phone
    ("phone_hands_type", 3400, 10),
    ("pan_phone", 3460, 10),
    ("pan_laptop", 3520, 10),
    # S05 light only
    ("pan_data_city", 4100, 14),
    ("digital_city_anim", 4300, 16),
    # S06 solar
    ("solar_roof_panels", 5080, 14),
    ("pan_solar", 5140, 14),
    ("pan_power", 5220, 12),
    # S07 sparse
    ("pan_savanna", 6100, 16),
    # S08
    ("pan_city_morning", 7260, 14),
    ("city_walk_busy", 7400, 14),
    # S09
    ("sunset_skyline", 8080, 14),
    ("pan_dusk_towers", 8200, 14),
    ("pan_gold_abstract", 8400, 12),
    # Extra density inserts (still under 7:00)
    ("skyline_clouds", 180, 12),
    ("highway_timelapse", 400, 12),
    ("coding_screen", 2440, 12),
    ("network_nodes", 2680, 12),
    ("data_center_lights", 4200, 12),
    ("wind_turbines", 5300, 12),
    ("pan_fiber_cables", 4360, 12),
    ("pan_container_port", 7520, 12),
    ("pan_rural_road", 6200, 14),
    ("pan_office_glass", 2540, 12),
    ("pan_circuit", 4440, 12),
    ("pan_night_market", 1480, 12),
]

PAN_MOTIONS = [
    "z='1.15':x='(iw-iw/zoom)*on/{d}':y='(ih-ih/zoom)*0.35'",
    "z='1.12':x='(iw-iw/zoom)*(1-on/{d})':y='(ih-ih/zoom)*0.4'",
    "z='min(1.0+0.002*on,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "z='1.2':x='(iw-iw/zoom)*0.5':y='(ih-ih/zoom)*on/{d}'",
]


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def download(url: str, dest: Path) -> bool:
    if dest.is_file() and dest.stat().st_size > 80_000:
        print(f"SKIP {dest.name}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=180) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        if dest.stat().st_size < 40_000:
            dest.unlink(missing_ok=True)
            return False
        print(f"OK {dest.name} ({dest.stat().st_size // 1024} KB)")
        return True
    except Exception as e:
        print(f"FAIL {dest.name}: {e}")
        dest.unlink(missing_ok=True)
        return False


def download_all() -> dict:
    results = {"videos": {}, "stills": {}}
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in VIDEOS.items():
        dest = RAW / f"{name}.mp4"
        ok = download(url, dest)
        if not ok and name in VIDEO_FALLBACKS:
            ok = download(VIDEO_FALLBACKS[name], dest)
        results["videos"][name] = {"ok": ok, "path": str(dest) if ok else None}
    for name, pid in STILL_IDS.items():
        dest = RAW / f"{name}.jpg"
        url = f"https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&w=3840&q=92"
        ok = download(url, dest)
        results["stills"][name] = {"ok": ok, "path": str(dest) if ok else None, "id": pid}
    return results


def grade_video(src: Path, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 80_000:
        return True
    cmd = [
        ff(), "-y", "-i", str(src),
        "-vf", SOFTPOP_VF,
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an",
        "-movflags", "+faststart",
        str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"grade fail {src.name}: {r.stderr[-200:]}")
        return False
    print(f"GRADED {dest.name}")
    return True


def cinematic_cut_from_video(src: Path, frames: int, out: Path, motion_i: int) -> bool:
    """Take a random-ish mid window and apply slow cinematic pan/zoom."""
    out.parent.mkdir(parents=True, exist_ok=True)
    d = max(8, frames)
    # Probe duration
    fp = shutil.which("ffprobe")
    start = 1.0
    if fp:
        pr = subprocess.run(
            [fp, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(src)],
            capture_output=True, text=True,
        )
        try:
            dur = float(pr.stdout.strip())
            start = max(0.2, min(dur - (d / 24) - 0.5, dur * 0.25 + (motion_i % 5) * 0.8))
        except ValueError:
            start = 1.0
    m = PAN_MOTIONS[motion_i % len(PAN_MOTIONS)].format(d=d)
    vf = (
        f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
        f"zoompan={m}:d={d}:s=1920x1080:fps=24,"
        "eq=contrast=1.05:saturation=0.9,"
        "colorbalance=rs=0.05:bs=-0.03:rm=0.03:bm=-0.02,"
        "unsharp=5:5:0.55:3:3:0.0"
    )
    cmd = [
        ff(), "-y", "-ss", f"{start:.2f}", "-i", str(src),
        "-vf", vf, "-frames:v", str(d),
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and out.is_file()


def cinematic_cut_from_still(src: Path, frames: int, out: Path, motion_i: int) -> bool:
    out.parent.mkdir(parents=True, exist_ok=True)
    d = max(8, frames)
    m = PAN_MOTIONS[motion_i % len(PAN_MOTIONS)].format(d=d)
    vf = (
        f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
        f"zoompan={m}:d={d}:s=1920x1080:fps=24,"
        "eq=contrast=1.06:saturation=0.88:brightness=0.01,"
        "colorbalance=rs=0.06:bs=-0.04:rm=0.04:bm=-0.03,"
        "unsharp=5:5:0.6:3:3:0.0"
    )
    cmd = [
        ff(), "-y", "-loop", "1", "-i", str(src),
        "-vf", vf, "-frames:v", str(d),
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and out.is_file()


def build_cuts(dl: dict) -> list[dict]:
    CUTS.mkdir(parents=True, exist_ok=True)
    GRADED.mkdir(parents=True, exist_ok=True)
    built = []
    for i, (tag, rel, frames) in enumerate(INSERT_PLAN):
        out = CUTS / f"cut_{i:03d}_{tag}_{frames}f.mp4"
        # prefer graded video if tag is video
        vraw = RAW / f"{tag}.mp4"
        sraw = RAW / f"{tag}.jpg"
        ok = False
        if vraw.is_file():
            g = GRADED / f"{tag}.mp4"
            if grade_video(vraw, g):
                ok = cinematic_cut_from_video(g, frames, out, i)
        elif sraw.is_file():
            ok = cinematic_cut_from_still(sraw, frames, out, i)
        else:
            # try pan_ still naming
            print(f"missing source {tag}")
        built.append({
            "index": i,
            "tag": tag,
            "record_rel": rel,
            "frames": frames,
            "path": str(out) if ok else None,
            "ok": ok,
            "track": 3 if i % 2 == 0 else 4,
        })
        print(("OK" if ok else "FAIL"), out.name if ok else tag)
    return built


def main():
    print("=== download license-free stock ===")
    dl = download_all()
    print("=== build cinematic cuts ===")
    cuts = build_cuts(dl)
    ok_n = sum(1 for c in cuts if c["ok"])
    meta = {
        "download": dl,
        "cuts": cuts,
        "ok_cuts": ok_n,
        "note": "Inserts only under 7:00; soft-pop grade; Mixkit+Unsplash license-free",
        "palette": ["#D9A441", "#2E3A50", "#C1552E", "#F1E4C8", "#262019"],
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"DONE ok_cuts={ok_n}/{len(cuts)} manifest={MANIFEST}")


if __name__ == "__main__":
    main()
