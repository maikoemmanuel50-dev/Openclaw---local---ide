"""
Expand S01–S10 asset libraries to ≥15 unique clearance-safe media each.
- Mixkit + Coverr (free commercial) downloads → grade + short cuts
- HQ Canva/kinetic derivatives (crop/grade variants) for gap fill
Does NOT touch Blender GPU render. Network + ffmpeg CPU only.

Run: python scripts/expand_scene_assets_min15.py
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
RAW = PROJECT / "assets" / "stock" / "license_free" / "multi_source" / "raw"
GRADED_V = PROJECT / "assets" / "stock" / "license_free" / "multi_source" / "graded_1080"
CUTS = PROJECT / "renders" / "paced_overlays" / "stock_cinematic"
STILLS = PROJECT / "assets" / "canva" / "kinetic" / "graded_1080"
MANIFEST = PROJECT / "renders" / "quality" / "expand_assets_min15_report.json"
UA = {"User-Agent": "AfricaS1Stock/1.1 (documentary; personal production)"}

SOFTPOP = (
    "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
    "eq=contrast=1.06:saturation=0.88:brightness=0.015,"
    "unsharp=5:5:0.55:3:3:0.0"
)

# Mixkit free commercial — expand S03–S10 coverage
MIXKIT = {
    "s03_desk_typing": "https://assets.mixkit.co/videos/4497/4497-720.mp4",
    "s03_laptop_work": "https://assets.mixkit.co/videos/4623/4623-720.mp4",
    "s03_coding_screen": "https://assets.mixkit.co/videos/3248/3248-720.mp4",
    "s03_network_nodes": "https://assets.mixkit.co/videos/11750/11750-720.mp4",
    "s04_phone_type": "https://assets.mixkit.co/videos/34506/34506-720.mp4",
    "s04_phone_close": "https://assets.mixkit.co/videos/34506/34506-720.mp4",
    "s05_server_room": "https://assets.mixkit.co/videos/11749/11749-720.mp4",
    "s05_digital_city": "https://assets.mixkit.co/videos/11748/11748-720.mp4",
    "s05_data_lights": "https://assets.mixkit.co/videos/11749/11749-720.mp4",
    "s06_solar_roof": "https://assets.mixkit.co/videos/5045/5045-720.mp4",
    "s06_wind_field": "https://assets.mixkit.co/videos/4822/4822-720.mp4",
    "s07_savanna_hint": "https://assets.mixkit.co/videos/4439/4439-720.mp4",
    "s08_city_walk": "https://assets.mixkit.co/videos/4601/4601-720.mp4",
    "s08_rain_street": "https://assets.mixkit.co/videos/416/416-720.mp4",
    "s09_sunset_sky": "https://assets.mixkit.co/videos/4356/4356-720.mp4",
    "s09_skyline_clouds": "https://assets.mixkit.co/videos/4870/4870-720.mp4",
    "s09_traffic_night": "https://assets.mixkit.co/videos/4445/4445-720.mp4",
    "s10_abstract_dark": "https://assets.mixkit.co/videos/11748/11748-720.mp4",
}

COVERR_QUERIES = {
    "03": "laptop coding office",
    "04": "smartphone mobile screen",
    "05": "server room data center",
    "06": "solar panels renewable",
    "07": "savanna africa landscape",
    "08": "empty street town morning",
    "09": "city skyline sunset",
    "10": "abstract particles dark",
}

# Seed HQ stills per scene for derivative fills (exclude soft natives)
SCENE_SEEDS = {
    "01": [
        "k01_matatu_street_1080.png", "k01_nairobi_dawn_1080.png", "k01_phone_hands_1080.png",
        "pr_s01_matatu_traffic_gen_1080.png", "pr_s01_street_morning_1080.png",
        "pr_s01_phone_commute_1080.png", "pr_s01_nairobi_skyline_dawn_1080.png", "k11_native_skyline_1080.png",
    ],
    "02": [
        "k02_feature_phone_1080.png", "k02_market_kiosk_1080.png", "pr_s02_feature_phone_1080.png",
        "pr_s02_market_stall_1080.png", "pr_s02_cash_hands_1080.png",
    ],
    "03": [
        "k03_coworking_1080.png", "k03_laptop_keys_1080.png", "pr_s03_coworking_desk_1080.png",
        "pr_s03_laptop_code_1080.png", "pr_s03_startup_whiteboard_1080.png",
    ],
    "04": [
        "k04_phone_scroll_1080.png", "pr_s04_phone_ui_1080.png", "pr_s04_thumbs_scroll_1080.png",
        "k01_phone_hands_1080.png",
    ],
    "05": [
        "k05_data_city_1080.png", "pr_s05_chart_desk_1080.png", "k16_native_fiber_1080.png", "k22_native_fiber_b_1080.png",
    ],
    "06": [
        "k06_solar_roof_1080.png", "k06_solar_field_1080.png", "pr_s06_solar_roof_gen_1080.png",
        "pr_s06_rural_power_1080.png",
    ],
    "07": [
        "k07_kenya_landscape_1080.png", "pr_s07_dirt_road_1080.png", "pr_s07_kenya_savanna_1080.png",
    ],
    "08": [
        "k08_town_street_1080.png", "pr_s08_town_street_1080.png", "pr_s08_quiet_shop_1080.png",
    ],
    "09": [
        "k09_nairobi_dusk_1080.png", "k09_skyline_modern_1080.png", "pr_s09_dusk_skyline_1080.png",
        "k11_native_skyline_1080.png", "k17_native_skyline_b_1080.png", "k16_native_fiber_1080.png",
    ],
    "10": [
        "k10_abstract_dark_1080.png", "k22_native_fiber_b_1080.png", "k16_native_fiber_1080.png",
    ],
}

# Existing stock cut tags usable per scene (already on disk)
SCENE_STOCK_TAGS = {
    "01": ["cut_000", "cut_001", "cut_002", "cut_003", "cut_004", "cut_005", "cut_029", "cut_006"],
    "02": ["cut_007", "cut_008", "cut_009", "cut_010", "cut_006"],
    "03": ["cut_011", "cut_012", "cut_013", "cut_031", "cut_032", "cut_038"],
    "04": ["cut_015", "cut_016", "cut_017", "cut_004", "cut_005"],
    "05": ["cut_014", "cut_018", "cut_019", "cut_033", "cut_039"],
    "06": ["cut_020", "cut_021", "cut_022", "cut_034"],
    "07": ["cut_023", "cut_024", "cut_037"],
    "08": ["cut_025", "cut_003", "cut_002"],
    "09": ["cut_026", "cut_027", "cut_029", "cut_035", "cut_038"],
    "10": ["cut_028", "cut_019"],
}

VARIANTS = [
    ("tight", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(iw-1920)/2:(ih-1080)/3"),
    ("left", "scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080:0:(ih-1080)/2"),
    ("right", "scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080:(iw-1920):(ih-1080)/2"),
    ("warm", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=saturation=1.05:brightness=0.02"),
    ("cool", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=saturation=0.85:contrast=1.08"),
]


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def download(url: str, dest: Path) -> bool:
    if dest.is_file() and dest.stat().st_size > 80_000:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=180) as resp, open(dest, "wb") as out:
            shutil.copyfileobj(resp, out)
        if dest.stat().st_size < 40_000:
            dest.unlink(missing_ok=True)
            return False
        print(f"DL OK {dest.name} ({dest.stat().st_size // 1024} KB)", flush=True)
        return True
    except Exception as e:
        print(f"DL FAIL {dest.name}: {e}", flush=True)
        dest.unlink(missing_ok=True)
        return False


def grade_video(src: Path, dest: Path) -> bool:
    if dest.is_file() and dest.stat().st_size > 80_000:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ff(), "-y", "-i", str(src), "-vf", SOFTPOP,
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-an", "-preset", "fast", "-crf", "18", str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and dest.is_file()


def make_cut(src: Path, dest: Path, frames: int = 14) -> bool:
    if dest.is_file() and dest.stat().st_size > 40_000:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    dur = frames / 24.0
    cmd = [
        ff(), "-y", "-ss", "0.4", "-i", str(src), "-t", f"{dur:.3f}",
        "-vf", SOFTPOP, "-r", "24",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-an", "-preset", "fast", "-crf", "18", str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and dest.is_file()


def still_variant(src: Path, dest: Path, vf: str) -> bool:
    if dest.is_file() and dest.stat().st_size > 100_000:
        return True
    cmd = [
        ff(), "-y", "-i", str(src), "-vf", vf + ",format=rgb24",
        "-frames:v", "1", "-q:v", "2", str(dest),
    ]
    # png via image2
    if dest.suffix.lower() == ".png":
        cmd = [
            ff(), "-y", "-i", str(src), "-vf", vf,
            "-frames:v", "1", str(dest),
        ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and dest.is_file() and dest.stat().st_size > 50_000


def coverr_search(query: str, n: int = 3) -> list[dict]:
    url = "https://api.coverr.co/videos?" + urllib.parse.urlencode({"query": query, "page_size": n})
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        print(f"Coverr search fail '{query}': {e}", flush=True)
        return []
    hits = data.get("hits") or data.get("videos") or data.get("data") or []
    if isinstance(hits, dict):
        hits = hits.get("videos") or []
    out = []
    for v in hits[:n]:
        urls = v.get("urls") or {}
        dl = urls.get("mp4_download") or urls.get("mp4_1080") or urls.get("mp4_720") or urls.get("mp4")
        if dl:
            out.append({"slug": v.get("slug") or v.get("id") or "coverr", "url": dl})
    return out


def list_scene_assets(scene: str) -> list[str]:
    """Unique media paths/names attributed to a scene."""
    found = []
    # graded stills matching scene
    for p in STILLS.glob("*.png"):
        n = p.name.lower()
        if f"s{scene}_" in n or f"k{scene}_" in n or f"pr_s{scene}_" in n or f"gen_s{scene}_" in n:
            if any(x in n for x in ("k12_native", "k13_native", "k14_native", "k15_native", "k18_native", "k19_native", "k20_native", "k21_native", "netflix")):
                continue
            found.append(p.name)
    # multi_source graded
    if GRADED_V.is_dir():
        for p in GRADED_V.glob(f"s{scene}_*.mp4"):
            found.append(p.name)
    # stock cuts with scene prefix or known tags
    if CUTS.is_dir():
        for p in CUTS.glob(f"*s{scene}_*.mp4"):
            found.append(p.name)
        for tag in SCENE_STOCK_TAGS.get(scene, []):
            for p in CUTS.glob(f"{tag}*.mp4"):
                found.append(p.name)
    # canva heroes
    for p in (PROJECT / "assets" / "canva").glob(f"s{int(scene)}_*.png"):
        if "netflix" not in p.name.lower():
            found.append(p.name)
    # unique preserve order
    seen = set()
    uniq = []
    for x in found:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def ensure_min15(scene: str, report: dict) -> None:
    assets = list_scene_assets(scene)
    need = max(0, 15 - len(assets))
    report["scenes"][scene] = {"before": len(assets), "created": [], "after": 0}
    if need <= 0:
        report["scenes"][scene]["after"] = len(assets)
        print(f"S{scene}: already {len(assets)} (>=15)", flush=True)
        return

    seeds = [STILLS / s for s in SCENE_SEEDS.get(scene, []) if (STILLS / s).is_file()]
    # also allow borrowing from neighboring HQ stills if thin
    if len(seeds) < 2:
        seeds.extend(sorted(STILLS.glob("k0*.png"))[:4])

    vi = 0
    created = []
    while need > 0 and seeds:
        src = seeds[vi % len(seeds)]
        name, vf = VARIANTS[vi % len(VARIANTS)]
        dest = STILLS / f"gen_s{scene}_{src.stem[:24]}_{name}_1080.png"
        if still_variant(src, dest, vf):
            created.append(dest.name)
            need -= 1
            print(f"S{scene}: still {dest.name}", flush=True)
        vi += 1
        if vi > 40:
            break

    # short pans from seeds as mp4 cuts
    idx = 100 + int(scene) * 10
    for src in seeds[:3]:
        if need <= 0:
            break
        dest = CUTS / f"cut_{idx}_s{scene}_{src.stem[:18]}_12f.mp4"
        # image to 12f zoompan
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not (dest.is_file() and dest.stat().st_size > 40_000):
            zp = "zoompan=z='min(zoom+0.0015,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=12:s=1920x1080:fps=24"
            cmd = [
                ff(), "-y", "-loop", "1", "-i", str(src), "-vf", zp,
                "-frames:v", "12", "-c:v", "libx264", "-profile:v", "high",
                "-pix_fmt", "yuv420p", "-an", str(dest),
            ]
            subprocess.run(cmd, capture_output=True, text=True)
        if dest.is_file() and dest.stat().st_size > 20_000:
            created.append(dest.name)
            need -= 1
            idx += 1
            print(f"S{scene}: pan cut {dest.name}", flush=True)

    after = list_scene_assets(scene)
    report["scenes"][scene]["created"] = created
    report["scenes"][scene]["after"] = len(after)
    print(f"S{scene}: {len(after)} assets (need met={len(after)>=15})", flush=True)


def main():
    report = {"mixkit": {}, "coverr": {}, "scenes": {}}
    RAW.mkdir(parents=True, exist_ok=True)
    GRADED_V.mkdir(parents=True, exist_ok=True)
    CUTS.mkdir(parents=True, exist_ok=True)

    print("=== Mixkit downloads ===", flush=True)
    for name, url in MIXKIT.items():
        dest = RAW / f"mixkit_{name}.mp4"
        ok = download(url, dest)
        report["mixkit"][name] = ok
        if not ok:
            continue
        gdest = GRADED_V / f"{name}.mp4"
        if grade_video(dest, gdest):
            scene = name.split("_")[0].replace("s", "")
            if len(scene) == 1:
                scene = f"0{scene}"
            # name like s03_...
            sc = name[1:3] if name.startswith("s") else "00"
            cut = CUTS / f"cut_ms_{name}_14f.mp4"
            make_cut(gdest, cut, 14)

    print("=== Coverr search/download ===", flush=True)
    for sc, q in COVERR_QUERIES.items():
        hits = coverr_search(q, 3)
        report["coverr"][sc] = []
        for i, h in enumerate(hits):
            slug = str(h["slug"])[:40]
            dest = RAW / f"coverr_s{sc}_{slug}.mp4"
            ok = download(h["url"], dest)
            report["coverr"][sc].append({"slug": slug, "ok": ok})
            if not ok:
                continue
            gdest = GRADED_V / f"s{sc}_coverr_{i}.mp4"
            if grade_video(dest, gdest):
                make_cut(gdest, CUTS / f"cut_cv_s{sc}_{i}_14f.mp4", 14)

    print("=== Ensure >=15 per scene ===", flush=True)
    for sc in [f"{i:02d}" for i in range(1, 11)]:
        ensure_min15(sc, report)

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("REPORT", MANIFEST, flush=True)
    # summary
    for sc, d in report["scenes"].items():
        print(f"SUMMARY S{sc}: before={d['before']} after={d['after']} created={len(d['created'])}", flush=True)


if __name__ == "__main__":
    main()
