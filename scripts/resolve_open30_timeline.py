"""
Resolve timeline: S01 TED-Ed Open30 (30s intro module).

Layers:
  V1 — optional S01 plate (first 30s) for context
  V2 — stock underlays (open30_stock_cuts)
  V3 — graphic open (enhanced or base)
  A1 — episode VO (unchanged timing; open is silent overlay window)

Run with Resolve open:
  python scripts/resolve_open30_timeline.py
"""
from __future__ import annotations

import json
import os
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
TIMELINE = "S01 TED-Ed Open30"
OPEN_ENH = os.path.join(PROJECT, "renders", "paced_overlays", "s01_teded_open_30s_enhanced.mp4")
OPEN_BASE = os.path.join(PROJECT, "renders", "paced_overlays", "s01_teded_open_30s.mp4")
PLATE = os.path.join(PROJECT, "renders", "video_clips", "01_ColdOpen.mp4")
STOCK_DIR = os.path.join(PROJECT, "renders", "paced_overlays", "open30_stock_cuts")
REPORT = os.path.join(PROJECT, "renders", "quality", "resolve_open30_timeline_report.json")
OPEN_FRAMES = 720


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


def find_clip(by, name):
    if name in by:
        return by[name]
    stem = os.path.basename(name).lower()
    for n, c in by.items():
        if stem in n.lower():
            return c
    return None


def import_paths(mp, paths):
    existing = []
    todo = [p for p in paths if os.path.isfile(p)]
    if todo:
        mp.ImportMedia(todo)
    return todo


def main():
    open_path = OPEN_ENH if os.path.isfile(OPEN_ENH) else OPEN_BASE
    if not os.path.isfile(open_path):
        raise SystemExit(f"Missing open mp4: {open_path}")

    resolve = get_resolve()
    if not resolve:
        raise SystemExit("Resolve not running")
    resolve.OpenPage("edit")
    project = resolve.GetProjectManager().GetCurrentProject()
    mp = project.GetMediaPool()

    paths = [open_path]
    if os.path.isfile(PLATE):
        paths.append(PLATE)
    if os.path.isdir(STOCK_DIR):
        paths.extend(
            os.path.join(STOCK_DIR, f)
            for f in os.listdir(STOCK_DIR)
            if f.endswith(".mp4")
        )
    import_paths(mp, paths)
    by = index_clips(mp)

    tl = mp.CreateEmptyTimeline(TIMELINE)
    if not tl:
        for i in range(1, int(project.GetTimelineCount() or 0) + 1):
            t = project.GetTimelineByIndex(i)
            if t and t.GetName() == TIMELINE:
                tl = t
                break
    if not tl:
        raise SystemExit("Could not create Open30 timeline")
    project.SetCurrentTimeline(tl)
    start = int(tl.GetStartFrame())
    infos = []

    plate = find_clip(by, os.path.basename(PLATE))
    if plate:
        infos.append({
            "mediaPoolItem": plate,
            "startFrame": 0,
            "endFrame": OPEN_FRAMES,
            "recordFrame": start,
            "trackIndex": 1,
            "mediaType": 1,
        })

    if os.path.isdir(STOCK_DIR):
        stock_clips = sorted(f for f in os.listdir(STOCK_DIR) if f.endswith(".mp4"))
        # stagger stock on V2 in 4-beat windows
        offsets = [0, 48, 169, 553]
        for i, fn in enumerate(stock_clips[:4]):
            c = find_clip(by, fn)
            if not c:
                continue
            infos.append({
                "mediaPoolItem": c,
                "startFrame": 0,
                "endFrame": 48,
                "recordFrame": start + offsets[i % len(offsets)],
                "trackIndex": 2,
                "mediaType": 1,
            })

    open_clip = find_clip(by, os.path.basename(open_path))
    if open_clip:
        infos.append({
            "mediaPoolItem": open_clip,
            "startFrame": 0,
            "endFrame": OPEN_FRAMES,
            "recordFrame": start,
            "trackIndex": 3,
            "mediaType": 1,
        })

    placed = mp.AppendToTimeline(infos) or []
    for track, opacity in ((2, 35), (3, 92)):
        for it in tl.GetItemListInTrack("video", track) or []:
            try:
                it.SetProperty("CompositeMode", "Normal")
                it.SetProperty("Opacity", opacity)
            except Exception:
                pass

    meta = {
        "timeline": TIMELINE,
        "open": open_path,
        "placed": len(placed),
        "tracks": "V1 plate · V2 stock · V3 graphics",
        "integration": "Episode 01 - Assembly uses same open on V3 frames 0-720",
    }
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    try:
        project.SaveProject()
    except Exception:
        pass
    print("OPEN30_TIMELINE", meta)


if __name__ == "__main__":
    main()
