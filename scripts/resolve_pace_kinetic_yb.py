"""
Re-place Resolve V2/V3/V4 with dense kinetic + clearance-safe stock.
Authoritative cut list: docs/SCENES_LIBRARY_CUTS_ROADMAP.md
Clearance: docs/CLEARANCE_ALLOWLIST.json / COPYRIGHT_CLEARANCE.md

ASL: stills/stock 10–16f @ 24fps; protect S05/S07 stat windows.
YB skipped when AFRICA_NO_YELLOW_BALL=1.

Run with Resolve open:
  set AFRICA_NO_YELLOW_BALL=1
  python scripts/resolve_pace_kinetic_yb.py
"""
from __future__ import annotations

import json
import os
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
TIMELINE = "Episode 01 - Assembly"
OPEN30_ENH = os.path.join(PROJECT, "renders", "paced_overlays", "s01_teded_open_30s_enhanced.mp4")
OPEN30_BASE = os.path.join(PROJECT, "renders", "paced_overlays", "s01_teded_open_30s.mp4")
OPEN30_FILE = OPEN30_ENH if os.path.isfile(OPEN30_ENH) else OPEN30_BASE
# TED-Ed 30s intro — full V3 overlay S01 0–720f; replaces sparse kinetic in that window
OPEN30 = (os.path.basename(OPEN30_FILE), 0, 720, 3)
OPEN30_END_FRAME = 720  # skip per-beat kinetic below this (Africa whip clear @ ~720)
# Hard ceiling: no B-roll/shot longer than 5.0s @ 24fps (docs/DYNAMIC_EDIT_TRANSITIONS.md)
MAX_SHOT_FRAMES = 120
DEFAULT_FLASH = 14

YB = [
    (0, "yb_sun_seed", 48, 2),
    (360, "yb_body_crowd", 40, 2),
    (1080, "yb_mpesa_coin", 40, 2),
    (2040, "yb_body_single", 36, 2),
    (3240, "yb_data_orb", 32, 2),
    (3720, "yb_data_orb", 36, 2),
    (5400, "yb_dim_gap", 40, 2),
    (6000, "yb_body_founder_dim", 40, 2),
    (6840, "yb_body_crowd", 48, 2),
    (8280, "yb_forecast_beacon", 48, 2),
]

# (media_name_or_stem, record_rel_frame, duration_f, track)
# Unique media per beat within scene; Mixkit/Unsplash cuts + HQ graded stills only.
KINETIC = [
    # --- S01 0–1200 (clear ~700–760 for Africa whip) ---
    ("k01_nairobi_dawn_1080.png", 24, 14, 3),
    ("cut_000_city_sunrise_aerial_16f.mp4", 48, 16, 4),
    ("k01_matatu_street_1080.png", 80, 12, 3),
    ("cut_001_pan_nairobi_dawn_14f.mp4", 110, 14, 4),
    ("pr_s01_street_morning_1080.png", 140, 12, 3),
    ("cut_002_city_walk_busy_14f.mp4", 170, 14, 4),
    ("pr_s01_matatu_traffic_gen_1080.png", 200, 12, 3),
    ("cut_003_pan_street_texture_12f.mp4", 230, 12, 4),
    ("k01_phone_hands_1080.png", 280, 12, 3),
    ("cut_004_phone_hands_type_12f.mp4", 320, 12, 4),
    ("pr_s01_phone_commute_1080.png", 380, 12, 3),
    ("cut_005_pan_phone_12f.mp4", 440, 12, 4),
    ("pr_s01_nairobi_skyline_dawn_1080.png", 520, 14, 3),
    ("k11_native_skyline_1080.png", 580, 12, 4),
    # Africa whip window ~720 — keep clear
    ("cut_029_skyline_clouds_12f.mp4", 780, 12, 3),
    ("uniq_s01_k01_matatu_street_1080_right_1080.png", 900, 12, 4),  # intentional late recall OK if unique mid-scene done
    ("cut_006_city_traffic_night_14f.mp4", 1020, 14, 3),
    # --- S02 1200–2280 ---
    ("k02_feature_phone_1080.png", 1220, 14, 3),
    ("cut_007_pan_market_14f.mp4", 1260, 14, 4),
    ("pr_s02_market_stall_1080.png", 1320, 12, 3),
    ("k02_market_kiosk_1080.png", 1380, 12, 4),
    ("pr_s02_cash_hands_1080.png", 1460, 14, 3),
    ("cut_008_phone_hands_type_12f.mp4", 1540, 12, 4),
    ("pr_s02_feature_phone_1080.png", 1620, 14, 3),
    ("cut_009_pan_phone_12f.mp4", 1720, 12, 4),
    ("cut_010_keyboard_work_14f.mp4", 1860, 14, 3),
    ("cut_u801_s02_cool_14f.mp4", 2000, 12, 4),
    ("uniq_s02_k02_feature_phone_1080_warm_1080.png", 2140, 12, 3),
    # --- S03 2280–3360 ---
    ("k03_coworking_1080.png", 2300, 12, 3),
    ("cut_011_laptop_office_14f.mp4", 2340, 14, 4),
    ("pr_s03_coworking_desk_1080.png", 2400, 12, 3),
    ("k03_laptop_keys_1080.png", 2480, 12, 4),
    ("cut_012_pan_laptop_12f.mp4", 2560, 12, 3),
    ("pr_s03_laptop_code_1080.png", 2660, 12, 4),
    ("cut_013_keyboard_work_12f.mp4", 2760, 12, 3),
    ("pr_s03_startup_whiteboard_1080.png", 2880, 12, 4),
    ("cut_031_coding_screen_12f.mp4", 3000, 12, 3),
    ("cut_032_network_nodes_12f.mp4", 3120, 12, 4),
    ("cut_038_pan_office_glass_12f.mp4", 3240, 12, 3),
    # --- S04 3360–3960 ---
    ("k04_phone_scroll_1080.png", 3380, 10, 3),
    ("cut_015_phone_hands_type_10f.mp4", 3410, 10, 4),
    ("pr_s04_phone_ui_1080.png", 3460, 10, 3),
    ("cut_016_pan_phone_10f.mp4", 3500, 10, 4),
    ("pr_s04_thumbs_scroll_1080.png", 3550, 10, 3),
    ("uniq_s04_k01_phone_hands_1080_tight_1080.png", 3600, 10, 4),
    ("cut_017_pan_laptop_10f.mp4", 3660, 10, 3),
    ("cut_u806_s04_cool_12f.mp4", 3720, 10, 4),
    ("uniq_s04_pr_s04_phone_ui_1080_left_1080.png", 3800, 10, 3),
    # --- S05 3960–5040 bookends; protect ~4140–4800 ---
    ("k05_data_city_1080.png", 3980, 14, 3),
    ("cut_014_pan_data_city_14f.mp4", 4020, 14, 4),
    ("cut_019_digital_city_anim_16f.mp4", 4080, 16, 3),
    # gap for chart/stats
    ("pr_s05_chart_desk_1080.png", 4860, 12, 4),
    ("cut_033_data_center_lights_12f.mp4", 4920, 12, 3),
    ("cut_039_pan_circuit_12f.mp4", 4980, 12, 4),
    ("k16_native_fiber_1080.png", 5020, 10, 3),
    # --- S06 5040–6000 ---
    ("k06_solar_roof_1080.png", 5060, 14, 3),
    ("cut_020_solar_roof_panels_14f.mp4", 5120, 14, 4),
    ("k06_solar_field_1080.png", 5200, 12, 3),
    ("cut_021_pan_solar_14f.mp4", 5280, 14, 4),
    ("pr_s06_solar_roof_gen_1080.png", 5380, 12, 3),
    ("cut_022_pan_power_12f.mp4", 5480, 12, 4),
    ("pr_s06_rural_power_1080.png", 5580, 12, 3),
    ("cut_034_wind_turbines_12f.mp4", 5700, 12, 4),
    ("uniq_s06_k06_solar_roof_1080_cool_1080.png", 5820, 12, 3),
    ("cut_u802_s06_left_14f.mp4", 5920, 12, 4),
    # --- S07 6000–7200; clear ~6360–6480 for 97% ---
    ("k07_kenya_landscape_1080.png", 6020, 16, 3),
    ("cut_023_pan_savanna_16f.mp4", 6100, 16, 4),
    ("pr_s07_kenya_savanna_1080.png", 6200, 14, 3),
    ("cut_024_pan_city_morning_14f.mp4", 6280, 14, 4),
    # 97% protect
    ("pr_s07_dirt_road_1080.png", 6520, 14, 3),
    ("cut_037_pan_rural_road_14f.mp4", 6640, 14, 4),
    ("uniq_s07_k07_kenya_landscape_1080_left_1080.png", 6800, 14, 3),
    ("cut_u803_s07_right_16f.mp4", 6960, 14, 4),
    ("uniq_s07_pr_s07_dirt_road_1080_right_1080.png", 7100, 12, 3),
    # --- S08 7200–8040 slower ---
    ("k08_town_street_1080.png", 7220, 18, 3),
    ("cut_025_city_walk_busy_14f.mp4", 7300, 16, 4),
    ("pr_s08_town_street_1080.png", 7400, 18, 3),
    ("pr_s08_quiet_shop_1080.png", 7520, 18, 4),
    ("cut_u800_s08_warm_12f.mp4", 7660, 16, 3),
    ("uniq_s08_k08_town_street_1080_right_1080.png", 7800, 18, 4),
    ("uniq_s08_pr_s08_quiet_shop_1080_tight_1080.png", 7920, 16, 3),
    # --- S09 8040–9720 ---
    ("k09_nairobi_dusk_1080.png", 8060, 14, 3),
    ("cut_026_sunset_skyline_14f.mp4", 8120, 14, 4),
    ("k09_skyline_modern_1080.png", 8200, 12, 3),
    ("cut_027_pan_dusk_towers_14f.mp4", 8280, 14, 4),
    ("pr_s09_dusk_skyline_1080.png", 8400, 14, 3),
    ("cut_u805_s09_warm_12f.mp4", 8520, 12, 4),
    ("k17_native_skyline_b_1080.png", 8640, 12, 3),
    ("cut_035_pan_fiber_cables_12f.mp4", 8760, 12, 4),
    ("uniq_s09_k16_native_fiber_1080_warm_1080.png", 8880, 12, 3),
    ("cut_u807_s09_left_12f.mp4", 9000, 12, 4),
    ("k22_native_fiber_b_1080.png", 9120, 12, 3),
    ("cut_u804_s09_tight_14f.mp4", 9300, 14, 4),
    ("uniq_s09_pr_s09_dusk_skyline_1080_warm_1080.png", 9500, 14, 3),
    ("uniq_s09_k09_skyline_modern_1080_tight_1080.png", 9640, 12, 4),
    # --- S10 9720–10080 minimal ---
    ("k10_abstract_dark_1080.png", 9740, 12, 3),
    ("uniq_s10_k22_native_fiber_b_1080_cool_1080.png", 9820, 10, 4),
]


def get_resolve():
    sys.path.append(
        r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
    )
    import DaVinciResolveScript as dvr

    return dvr.scriptapp("Resolve")


def index_clips(mp):
    by = {}
    root = mp.GetRootFolder()

    def walk(folder):
        for c in folder.GetClipList() or []:
            by[c.GetName()] = c
        for sf in folder.GetSubFolderList() or []:
            walk(sf)

    walk(root)
    return by


def find_clip(by: dict, name: str):
    if name in by:
        return by[name]
    stem = os.path.splitext(name)[0].lower()
    for n, c in by.items():
        nl = n.lower()
        if nl == name.lower() or stem in nl or name.lower() in nl:
            return c
    return None


def clear_track(tl, track_index: int):
    items = tl.GetItemListInTrack("video", track_index) or []
    if not items:
        return 0
    ids = []
    for it in items:
        try:
            ids.append(it.GetUniqueId())
        except Exception:
            pass
    if ids:
        try:
            tl.DeleteClips(ids, False)
        except Exception:
            for it in items:
                try:
                    tl.DeleteClips([it.GetUniqueId()], False)
                except Exception:
                    pass
    return len(items)


def main():
    resolve = get_resolve()
    if not resolve:
        raise SystemExit("Resolve not running")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    tl = None
    for i in range(1, int(project.GetTimelineCount() or 0) + 1):
        t = project.GetTimelineByIndex(i)
        if t and t.GetName() == TIMELINE:
            tl = t
            break
    if not tl:
        tl = project.GetCurrentTimeline()
    project.SetCurrentTimeline(tl)
    resolve.OpenPage("edit")

    start = int(tl.GetStartFrame())
    mp = project.GetMediaPool()
    by = index_clips(mp)

    for tr in (2, 3, 4):
        n = clear_track(tl, tr)
        print(f"cleared V{tr}: {n}")

    skip_yb = os.environ.get("AFRICA_NO_YELLOW_BALL", "").strip() in ("1", "true", "TRUE", "yes")
    infos = []
    yb_placed = 0
    if skip_yb:
        print("AFRICA_NO_YELLOW_BALL=1 — clearing V2, skipping YB overlays")
    else:
        for rel, stem, dur, track in YB:
            clip = find_clip(by, stem)
            if not clip:
                print("miss YB", stem)
                continue
            infos.append({
                "mediaPoolItem": clip,
                "startFrame": 0,
                "endFrame": max(1, dur),
                "recordFrame": start + rel,
                "trackIndex": track,
                "mediaType": 1,
            })
            yb_placed += 1

    missed = []
    # 30s TED-Ed open (replaces individual kinetic beats in 0–720f window)
    open_name, open_rel, open_dur, open_track = OPEN30
    open_clip = find_clip(by, open_name)
    if open_clip:
        infos.append({
            "mediaPoolItem": open_clip,
            "startFrame": 0,
            "endFrame": open_dur,
            "recordFrame": start + open_rel,
            "trackIndex": open_track,
            "mediaType": 1,
        })
        print("placed OPEN30", open_name, "0-", open_dur)
    else:
        missed.append(open_name)
        print("miss OPEN30", open_name)

    for name, rel, dur, track in KINETIC:
        if rel < OPEN30_END_FRAME:
            continue  # open30 carries first 30s density; keep plate+whip clear
        clip = find_clip(by, name)
        if not clip:
            missed.append(name)
            print("miss kinetic/stock", name)
            continue
        infos.append({
            "mediaPoolItem": clip,
            "startFrame": 0,
            "endFrame": max(1, min(int(dur), MAX_SHOT_FRAMES)),
            "recordFrame": start + rel,
            "trackIndex": track,
            "mediaType": 1,
        })

    placed = 0
    for i in range(0, len(infos), 10):
        chunk = infos[i : i + 10]
        r = mp.AppendToTimeline(chunk)
        if r:
            placed += len(r)
            print(f"chunk {i}: {len(r)}")

    # Clarity: higher opacity, Normal composite (no muddy Screen on B-roll)
    for track, opacity, mode in ((2, 100, "Screen"), (3, 90, "Normal"), (4, 88, "Normal")):
        items = tl.GetItemListInTrack("video", track) or []
        for it in items:
            try:
                it.SetProperty("CompositeMode", mode)
            except Exception:
                pass
            try:
                it.SetProperty("Opacity", opacity)
            except Exception:
                try:
                    it.SetProperty("Opacity", float(opacity))
                except Exception:
                    pass

    try:
        project.SaveProject()
    except Exception:
        pass

    meta = {
        "placed": placed,
        "yb": 0 if skip_yb else yb_placed,
        "yb_skipped": skip_yb,
        "open30": open_name if open_clip else None,
        "kinetic_planned": len(KINETIC),
        "kinetic_skipped_under_720": sum(1 for _, rel, _, _ in KINETIC if rel < OPEN30_END_FRAME),
        "missed": missed,
        "roadmap": "docs/SCENES_LIBRARY_CUTS_ROADMAP.md",
    }
    out = os.path.join(PROJECT, "renders", "quality", "resolve_pace_report.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("DONE", meta)


if __name__ == "__main__":
    main()
