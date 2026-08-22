"""
Resolve S02 preview — V1 plate + kinetic V3/V4 only (no full episode rebuild).

Places 02_Context2007 on V1 and S02-window kinetic cuts from resolve_pace_kinetic_yb.py.
Delivers ~45s preview MP4 for QC (multi-cut density vs raw V1 plate).

Requires Resolve running:
  python scripts/resolve_s02_kinetic_preview.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
OUT = os.path.join(PROJECT, "renders", "quality", "s02_kinetic_preview.mp4")
REPORT = os.path.join(PROJECT, "renders", "quality", "s02_kinetic_preview_report.json")
S02_START = 1200
S02_END = 2280
TIMELINE = "S02 Kinetic Preview"


def get_resolve():
    sys.path.append(
        r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
    )
    import DaVinciResolveScript as dvr

    return dvr.scriptapp("Resolve")


def load_kinetic():
    spec = importlib.util.spec_from_file_location(
        "pace", os.path.join(PROJECT, "scripts", "resolve_pace_kinetic_yb.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return [(n, rel, dur, tr) for n, rel, dur, tr in mod.KINETIC if S02_START <= rel < S02_END]


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
    stem = os.path.splitext(name)[0].lower()
    for n, c in by.items():
        if stem in n.lower() or n.lower() in name.lower():
            return c
    return None


def main():
    kinetic = load_kinetic()
    v1 = os.path.join(PROJECT, "renders", "video_clips", "02_Context2007.mp4")
    if not os.path.isfile(v1):
        raise SystemExit(f"Missing V1 plate: {v1}")

    resolve = get_resolve()
    if not resolve:
        raise SystemExit("Resolve not running")
    resolve.OpenPage("edit")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    mp = project.GetMediaPool()

    # Import V1 if missing
    imported = mp.ImportMedia([v1]) or []
    by = index_clips(mp)

    # New timeline
    tl = mp.CreateEmptyTimeline(TIMELINE)
    if not tl:
        for i in range(1, int(project.GetTimelineCount() or 0) + 1):
            t = project.GetTimelineByIndex(i)
            if t and t.GetName() == TIMELINE:
                tl = t
                break
    if not tl:
        raise SystemExit("Could not create/find preview timeline")
    project.SetCurrentTimeline(tl)

    v1_clip = find_clip(by, "02_Context2007.mp4")
    if not v1_clip and imported:
        v1_clip = imported[0]
    if not v1_clip:
        raise SystemExit("V1 clip not in media pool")

    start = int(tl.GetStartFrame())
    infos = [{
        "mediaPoolItem": v1_clip,
        "startFrame": 0,
        "endFrame": S02_END - S02_START,
        "recordFrame": start,
        "trackIndex": 1,
        "mediaType": 1,
    }]

    missed = []
    for name, rel, dur, track in kinetic:
        clip = find_clip(by, name)
        if not clip:
            missed.append(name)
            continue
        local = rel - S02_START
        infos.append({
            "mediaPoolItem": clip,
            "startFrame": 0,
            "endFrame": max(1, min(int(dur), 120)),
            "recordFrame": start + local,
            "trackIndex": track,
            "mediaType": 1,
        })

    placed = mp.AppendToTimeline(infos) or []
    for track in (3, 4):
        for it in tl.GetItemListInTrack("video", track) or []:
            try:
                it.SetProperty("CompositeMode", "Normal")
                it.SetProperty("Opacity", 90)
            except Exception:
                pass

    meta = {
        "timeline": TIMELINE,
        "v1": v1,
        "kinetic_planned": len(kinetic),
        "placed": len(placed),
        "missed": missed,
        "output": OUT,
        "note": "Deliver preview from Resolve UI or Deliver page to path above",
    }
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("S02_PREVIEW_TIMELINE_READY", meta, flush=True)
    try:
        project.SaveProject()
    except Exception:
        pass


if __name__ == "__main__":
    main()
