"""
Place graded kinetic stills (V3/V4) + yellow-ball overlays (V2) on
Episode 01 - Assembly. Safe to re-run: skips if V2/V3 already have items.

Uses DaVinci Resolve scripting API (Studio external or bridge).
Run: python scripts/resolve_place_kinetic_yb.py
"""
from __future__ import annotations

import glob
import os
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
GRADED = os.path.join(PROJECT, "assets", "canva", "kinetic", "graded_1080")
YB_DIR = os.path.join(PROJECT, "assets", "yellow_ball", "export")
TIMELINE = "Episode 01 - Assembly"
FPS = 24

# Relative timeline frames (0 = first frame). Scene windows from V1 spine.
SCENE_RANGES = {
    "01": (0, 1200),
    "02": (1200, 2280),
    "03": (2280, 3360),
    "04": (3360, 3960),
    "05": (3960, 5040),
    "06": (5040, 6000),
    "07": (6000, 7200),
    "08": (7200, 8040),
    "09": (8040, 9720),
    "10": (9720, 10080),
}

# Still hold lengths (frames) — kinetic ASL ~0.4–1.0s; protect stats
CUT_LEN = {
    "01": 14,
    "02": 16,
    "03": 12,
    "04": 10,
    "05": 18,  # lighter under chart
    "06": 14,
    "07": 20,  # sparse under 97%
    "08": 16,
    "09": 12,
    "10": 24,
}

# Marker-relative YB placements: (rel_frame, png_stem, duration_f)
YB_HITS = [
    (0, "yb_sun_seed", 48),
    (360, "yb_body_crowd", 36),
    (1080, "yb_mpesa_coin", 40),
    (2040, "yb_body_single", 36),
    (3240, "yb_data_orb", 32),
    (3720, "yb_data_orb", 36),
    (5400, "yb_dim_gap", 40),
    (6000, "yb_body_founder_dim", 40),
    (6840, "yb_body_crowd", 48),
    (8280, "yb_forecast_beacon", 60),
]


def get_resolve():
    try:
        import DaVinciResolveScript as dvr  # type: ignore

        return dvr.scriptapp("Resolve")
    except Exception:
        pass
    # Fallback: load from common Studio install
    candidates = [
        r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules",
        r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Developer\Scripting\Modules",
    ]
    for c in candidates:
        if c not in sys.path and os.path.isdir(c):
            sys.path.append(c)
    import DaVinciResolveScript as dvr  # type: ignore

    return dvr.scriptapp("Resolve")


def ensure_tracks(tl, n_video: int = 5):
    while tl.GetTrackCount("video") < n_video:
        tl.AddTrack("video")
    names = {1: "Spine", 2: "Ball", 3: "KineticA", 4: "KineticB", 5: "TextStat"}
    for i, name in names.items():
        try:
            tl.SetTrackName("video", i, name)
        except Exception:
            pass


def import_folder(mp, folder_path: str, subfolder: str):
    root = mp.GetRootFolder()
    # Find or create subfolder
    target = None
    for f in root.GetSubFolderList() or []:
        if f.GetName() == subfolder:
            target = f
            break
    if target is None:
        target = mp.AddSubFolder(root, subfolder)
    mp.SetCurrentFolder(target)
    paths = sorted(
        glob.glob(os.path.join(folder_path, "*.png"))
        + glob.glob(os.path.join(folder_path, "*.jpg"))
    )
    if not paths:
        return {}
    clips = mp.ImportMedia(paths) or []
    by_name = {}
    for c in clips:
        by_name[c.GetName()] = c
    # Also index existing clips in folder
    for c in target.GetClipList() or []:
        by_name[c.GetName()] = c
    return by_name


def scene_key_from_name(name: str) -> str | None:
    n = name.lower()
    for i in range(1, 11):
        tag = f"s{i:02d}"
        ktag = f"k{i:02d}"
        if tag in n or ktag in n or f"_{i:02d}_" in n:
            return f"{i:02d}"
    return None


def place_kinetic(tl, start_frame: int, clips_by_name: dict):
    # Group stills by scene
    buckets: dict[str, list] = {f"{i:02d}": [] for i in range(1, 11)}
    for name, clip in clips_by_name.items():
        sk = scene_key_from_name(name)
        if sk:
            buckets[sk].append((name, clip))

    placed = 0
    for sk, (a, b) in SCENE_RANGES.items():
        stills = buckets.get(sk) or []
        if not stills:
            continue
        # Skip end card dense inserts
        if sk == "10":
            stills = stills[:1]
        dur = CUT_LEN.get(sk, 14)
        # Leave headroom for spine; start after 18f establishing
        cursor = a + 18
        # Protect stat windows roughly (S05 mid, S07 mid)
        protect = []
        if sk == "05":
            protect = [(a + 360, a + 720)]  # chart hold
        if sk == "07":
            protect = [(a + 480, a + 900)]  # 97% hold

        track = 3  # V3
        for i, (name, clip) in enumerate(stills):
            if cursor + dur >= b - 12:
                break
            # Skip protected ranges
            skip = False
            for p0, p1 in protect:
                if cursor < p1 and cursor + dur > p0:
                    cursor = p1 + 6
                    skip = cursor + dur >= b - 12
            if skip:
                break
            record = start_frame + cursor
            # Alternate V3 / V4
            track = 3 if (i % 2 == 0) else 4
            info = {
                "mediaPoolItem": clip,
                "startFrame": 0,
                "endFrame": dur,
                "recordFrame": record,
                "trackIndex": track,
                "mediaType": 1,
            }
            ok = mp_append(tl, info)
            if ok:
                placed += 1
            cursor += dur + 4  # tiny gap / hard-cut rhythm
    return placed


def mp_append(tl, info):
    # Resolve AppendToTimeline wants media pool via project
    proj = tl.GetProject() if hasattr(tl, "GetProject") else None
    # Standard path: media pool append on current timeline
    resolve = get_resolve()
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    mp = project.GetMediaPool()
    result = mp.AppendToTimeline([info])
    return bool(result)


def place_yb(tl, start_frame: int, clips_by_name: dict):
    placed = 0
    for rel, stem, dur in YB_HITS:
        clip = None
        for name, c in clips_by_name.items():
            if stem.lower() in name.lower():
                clip = c
                break
        if clip is None:
            print(f"  miss YB asset: {stem}")
            continue
        info = {
            "mediaPoolItem": clip,
            "startFrame": 0,
            "endFrame": dur,
            "recordFrame": start_frame + rel,
            "trackIndex": 2,
            "mediaType": 1,
        }
        if mp_append(tl, info):
            placed += 1
            print(f"  YB @{rel}: {stem} ({dur}f)")
    return placed


def main():
    resolve = get_resolve()
    if not resolve:
        raise SystemExit("Resolve not running / scripting unavailable")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        raise SystemExit("No current Resolve project")
    # Prefer named timeline
    tl = None
    for i in range(1, int(project.GetTimelineCount() or 0) + 1):
        t = project.GetTimelineByIndex(i)
        if t and t.GetName() == TIMELINE:
            tl = t
            break
    if tl is None:
        tl = project.GetCurrentTimeline()
    project.SetCurrentTimeline(tl)
    start = int(tl.GetStartFrame())
    print(f"Timeline: {tl.GetName()} start={start}")

    # Skip if already populated
    v2 = tl.GetItemListInTrack("video", 2) or []
    v3 = tl.GetItemListInTrack("video", 3) or []
    if len(v2) >= 5 and len(v3) >= 10:
        print(f"Already placed (V2={len(v2)} V3={len(v3)}); skip")
        return

    ensure_tracks(tl, 5)
    mp = project.GetMediaPool()
    graded = import_folder(mp, GRADED, "Kinetic Graded")
    yb = import_folder(mp, YB_DIR, "Yellow Ball")
    print(f"Imported/indexed graded={len(graded)} yb={len(yb)}")

    n_k = place_kinetic(tl, start, graded)
    n_y = place_yb(tl, start, yb)
    project.SaveProject()
    print(f"DONE kinetic={n_k} yb={n_y}")


if __name__ == "__main__":
    main()
