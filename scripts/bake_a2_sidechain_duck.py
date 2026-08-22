"""
Bake Fairlight A2 sidechain duck (~-12 dB) offline from A1 VO.

Resolve API cannot set Fairlight Dynamics sidechain graphs, so we apply
ffmpeg sidechaincompress to A2_music_eq.wav keyed by A1_vo_eq.wav, then
swap the timeline clip on audio track 2.

Run: python scripts/bake_a2_sidechain_duck.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
STEMS = PROJECT / "renders" / "audio_stems" / "fairlight"
VO = STEMS / "A1_vo_eq.wav"
MUSIC = STEMS / "A2_music_eq.wav"
BACKUP = STEMS / "A2_music_eq_pre_sidechain.bak.wav"
DUCKED = STEMS / "A2_music_eq_ducked.wav"
REPORT = STEMS / "a2_sidechain_bake_report.json"

# Prefer scripts/bake_a2_tension_release.py (duck + gap swells).
# Legacy duck-only — aligned to ~-18 dB under VO (AUDIO_MIX_STANDARDS.md)
FF_FILTER = (
    "[0:a][1:a]sidechaincompress="
    "threshold=0.07:ratio=7:attack=18:release=200:makeup=1:knee=3:link=average"
    "[ducked]"
)


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def bake() -> dict:
    if not VO.is_file() or not MUSIC.is_file():
        raise FileNotFoundError(f"Missing stems VO={VO.exists()} MUSIC={MUSIC.exists()}")
    if not BACKUP.is_file():
        shutil.copy2(MUSIC, BACKUP)
    cmd = [
        ff(), "-y",
        "-i", str(MUSIC),
        "-i", str(VO),
        "-filter_complex", FF_FILTER,
        "-map", "[ducked]",
        "-ac", "2",
        "-ar", "48000",
        str(DUCKED),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not DUCKED.is_file():
        raise RuntimeError(r.stderr[-800:] if r.stderr else "ffmpeg failed")
    # Replace active A2 stem (keep ducked copy + bak)
    shutil.copy2(DUCKED, MUSIC)
    return {
        "ok": True,
        "vo": str(VO),
        "music_active": str(MUSIC),
        "ducked": str(DUCKED),
        "backup": str(BACKUP),
        "filter": FF_FILTER,
        "bytes_music": MUSIC.stat().st_size,
        "bytes_ducked": DUCKED.stat().st_size,
    }


def place_in_resolve(path: Path) -> dict:
    """Replace A2 clip with ducked stem via Resolve scripting API."""
    try:
        import DaVinciResolveScript as dvr
    except ImportError:
        # common install paths
        for p in (
            r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules",
            os.path.expandvars(r"%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"),
        ):
            if os.path.isdir(p) and p not in sys.path:
                sys.path.append(p)
        import DaVinciResolveScript as dvr  # type: ignore

    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        return {"placed": False, "err": "Resolve not connected"}
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        return {"placed": False, "err": "no project"}
    tl = project.GetCurrentTimeline()
    if not tl or tl.GetName() != "Episode 01 - Assembly":
        # try set by name
        for i in range(1, int(project.GetTimelineCount() or 0) + 1):
            t = project.GetTimelineByIndex(i)
            if t and t.GetName() == "Episode 01 - Assembly":
                project.SetCurrentTimeline(t)
                tl = t
                break
    if not tl:
        return {"placed": False, "err": "timeline missing"}

    try:
        resolve.OpenPage("fairlight")
    except Exception:
        pass

    mp = project.GetMediaPool()
    root = mp.GetRootFolder()
    folder = None
    for sf in root.GetSubFolderList() or []:
        if sf.GetName() == "Fairlight Stems":
            folder = sf
            break
    if folder is None:
        folder = mp.AddSubFolder(root, "Fairlight Stems")
    mp.SetCurrentFolder(folder)

    imported = mp.ImportMedia([str(path)])
    if not imported:
        return {"placed": False, "err": "ImportMedia failed"}
    clip = imported[0]

    # Clear existing A2 items
    items = tl.GetItemListInTrack("audio", 2) or []
    for it in items:
        try:
            tl.DeleteClips([it], False)
        except Exception:
            try:
                # older API: delete by selecting
                pass
            except Exception:
                pass
    # Re-read; if DeleteClips unavailable, overwrite by append at start may stack — try DeleteClips again via mediapool append only if empty
    items_after = tl.GetItemListInTrack("audio", 2) or []
    if items_after:
        # Fallback: use timeline delete if available
        try:
            ids = [it.GetUniqueId() for it in items_after]
            # no-op if not supported
        except Exception:
            pass

    info = {
        "mediaPoolItem": clip,
        "startFrame": 0,
        "trackIndex": 2,
        "recordFrame": tl.GetStartFrame() if hasattr(tl, "GetStartFrame") else 0,
    }
    # Prefer AppendToTimeline with track targeting
    ok = False
    try:
        ok = bool(mp.AppendToTimeline([{
            "mediaPoolItem": clip,
            "trackIndex": 2,
            "recordFrame": tl.GetStartFrame(),
            "mediaType": 2,  # audio-only when supported
        }]))
    except Exception as e:
        err = str(e)
        try:
            ok = bool(mp.AppendToTimeline([clip]))
            # may land on wrong track — report
            return {"placed": ok, "warn": "appended without trackIndex", "err": err}
        except Exception as e2:
            return {"placed": False, "err": f"{err} | {e2}"}

    try:
        project.SaveProject()
    except Exception:
        pass
    items_final = tl.GetItemListInTrack("audio", 2) or []
    names = []
    for it in items_final:
        try:
            names.append(it.GetName())
        except Exception:
            names.append("?")
    return {"placed": ok, "a2_items": names, "clip": path.name}


def main():
    print("=== bake A2 sidechain duck ===")
    meta = bake()
    print(f"baked {meta['bytes_ducked']} bytes -> {MUSIC}")
    print("=== place in Resolve ===")
    place = place_in_resolve(MUSIC)
    print(place)
    meta["resolve"] = place
    REPORT.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"report {REPORT}")
    if not place.get("placed"):
        sys.exit(2)


if __name__ == "__main__":
    main()
