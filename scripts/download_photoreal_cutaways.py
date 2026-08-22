"""
Download high-fidelity photoreal stills + kinetic video for Africa S1 cutaways.
Sources: Unsplash (photos, w=3840) + Mixkit (CC video previews).
Output:
  assets/canva/kinetic/hq/     — source JPGs
  assets/stock/kinetic/        — MP4 B-roll
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
HQ = PROJECT / "assets" / "canva" / "kinetic" / "hq"
VID = PROJECT / "assets" / "stock" / "kinetic"
UA = {"User-Agent": "AfricaS1-Fidelity/2.0"}

# Unsplash source images — documentary niches for Silicon Savannah
# Format: filename -> unsplash photo id (images.unsplash.com/photo-...)
STILLS = {
    # S01 dawn / transit
    "pr_s01_nairobi_skyline_dawn": "1506521787437-19b9bce6e695",  # african city dawn-ish
    "pr_s01_matatu_traffic": "1464037866556-ba5fcd7f8e1e",       # busy transit
    "pr_s01_street_morning": "1477959858617-67f85cf4f1df",        # city morning
    "pr_s01_phone_commute": "1512941937669-90a1b58e7e9c",         # phone in hand
    # S02 M-Pesa / 2007 mobile
    "pr_s02_feature_phone": "1511707171634-5f897ff02aa9",         # phone close
    "pr_s02_market_stall": "1555529669-e69e7aa0ba9a",             # market commerce
    "pr_s02_cash_hands": "1556742049-0cfed4f6a45d",               # money exchange
    # S03 hubs / coworking
    "pr_s03_coworking_desk": "1497366216548-37526070297c",        # coworking
    "pr_s03_laptop_code": "1461749280684-dccba630e2f6",           # laptop code
    "pr_s03_startup_whiteboard": "1552664730-d307ca884978",       # team board (crop faces later)
    # S04 phone-first
    "pr_s04_phone_ui": "1556656793-08538906a9f8",                 # phone screen
    "pr_s04_thumbs_scroll": "1516321318423-f06f85e504b3",         # scroll
    # S05 capital / data
    "pr_s05_city_night_data": "1480714378408-67cf0d13bcbf",       # city night
    "pr_s05_chart_desk": "1551288049-bebda4e38f71",               # analytics
    # S06 solar PAYG
    "pr_s06_solar_farm": "1509391366364-4b9344020dea",            # solar farm
    "pr_s06_solar_roof": "1508514177221-188b1cf16e19",            # rooftop solar
    "pr_s06_rural_power": "1473341304170-971dccb5ac1e",           # power lines / energy
    # S07 gap / Kenya
    "pr_s07_kenya_savanna": "1516026672322-bc52d61a55d5",         # kenya landscape
    "pr_s07_dirt_road": "1469854523086-cc02fe5d8800",             # road / distance
    # S08 secondary city
    "pr_s08_town_street": "1449824913935-59a10b8d2000",           # town street
    "pr_s08_quiet_shop": "1441986300917-64674bd600d8",            # quiet retail
    # S09 closer / forecast
    "pr_s09_dusk_skyline": "1444721483937-2a2c3a5f1b4c",         # may fail — fallback below
    "pr_s09_modern_towers": "1486406149866-c6cefb3740b5",         # modern skyline
    "pr_s09_golden_hour_city": "1464619775492-0c4c5c0c8d0a",      # may fail
    # S10 end / abstract
    "pr_s10_dark_texture": "1550684841-4136e78f2d0b",             # dark abstract
    "pr_s10_gold_dust": "1518709268805-4e9042af2176",             # particles / tech glow
}

# Verified high-quality fallbacks (known working Unsplash IDs)
FALLBACKS = {
    "pr_s01_nairobi_skyline_dawn": "1477959858617-67f85cf4f1df",
    "pr_s01_matatu_traffic": "1464037866556-ba5fcd7f8e1e",
    "pr_s09_dusk_skyline": "1477959858617-67f85cf4f1df",
    "pr_s09_golden_hour_city": "1486406149866-c6cefb3740b5",
    "pr_s03_startup_whiteboard": "1497366216548-37526070297c",
    "pr_s07_dirt_road": "1469854523086-cc02fe5d8800",
}

VIDEOS = {
    "v_city_sunrise": "https://assets.mixkit.co/videos/preview/mixkit-aerial-view-of-a-city-at-sunrise-4439-large.mp4",
    "v_traffic_night": "https://assets.mixkit.co/videos/preview/mixkit-city-traffic-at-night-with-blurred-lights-4445-large.mp4",
    "v_phone_typing": "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-person-typing-on-a-smartphone-34506-large.mp4",
    "v_solar_roof": "https://assets.mixkit.co/videos/preview/mixkit-solar-panels-on-a-roof-5045-large.mp4",
    "v_laptop_work": "https://assets.mixkit.co/videos/preview/mixkit-young-woman-working-on-her-laptop-30865-large.mp4",
    "v_keyboard": "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-man-working-on-a-computer-4497-large.mp4",
    "v_city_walk": "https://assets.mixkit.co/videos/preview/mixkit-people-walking-in-a-busy-city-street-4601-large.mp4",
    "v_sunset_skyline": "https://assets.mixkit.co/videos/preview/mixkit-silhouettes-of-buildings-at-sunset-4356-large.mp4",
    "v_office_window": "https://assets.mixkit.co/videos/preview/mixkit-man-working-on-his-laptop-in-an-office-4623-large.mp4",
    "v_digital_city": "https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-a-city-11748-large.mp4",
}


def fetch(url: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 80_000:
        return {"file": dest.name, "status": "skip", "kb": dest.stat().st_size // 1024}
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=90) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        return {"file": dest.name, "status": "ok", "kb": dest.stat().st_size // 1024, "url": url}
    except Exception as e:
        if dest.is_file():
            dest.unlink()
        return {"file": dest.name, "status": "fail", "error": str(e)}


def still_url(photo_id: str) -> str:
    # High-res download, 16:9 crop preference via Unsplash params
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=3840&q=90"


def main():
    HQ.mkdir(parents=True, exist_ok=True)
    VID.mkdir(parents=True, exist_ok=True)
    results = {"stills": [], "videos": [], "public_urls": {}}

    for name, pid in STILLS.items():
        pid = FALLBACKS.get(name, pid)
        url = still_url(pid)
        dest = HQ / f"{name}.jpg"
        r = fetch(url, dest)
        r["id"] = pid
        results["stills"].append(r)
        if r["status"] in ("ok", "skip"):
            results["public_urls"][name] = url

    for name, url in VIDEOS.items():
        results["videos"].append(fetch(url, VID / f"{name}.mp4"))

    manifest = HQ / "manifest.json"
    manifest.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({
        "stills_ok": sum(1 for r in results["stills"] if r["status"] in ("ok", "skip")),
        "stills_fail": [r for r in results["stills"] if r["status"] == "fail"],
        "videos_ok": sum(1 for r in results["videos"] if r["status"] in ("ok", "skip")),
        "videos_fail": [r for r in results["videos"] if r["status"] == "fail"],
        "manifest": str(manifest),
    }, indent=2))


if __name__ == "__main__":
    main()
