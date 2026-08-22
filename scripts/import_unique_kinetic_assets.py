"""
Import unique kinetic replacement stills/cuts into Resolve Media Pool.
Run before resolve_pace_kinetic_yb.py (called from finish_after_hq.ps1).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
STILLS = PROJECT / "assets" / "canva" / "kinetic" / "unique_replacements"
CUTS = PROJECT / "renders" / "paced_overlays" / "unique_replacements"
REPORT = PROJECT / "renders" / "quality" / "import_unique_kinetic_report.json"


def get_resolve():
    sys.path.append(
        r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
    )
    import DaVinciResolveScript as dvr

    return dvr.scriptapp("Resolve")


def main():
    paths = []
    for root in (STILLS, CUTS):
        if root.is_dir():
            paths.extend(str(p) for p in sorted(root.glob("*")) if p.is_file())

    if not paths:
        REPORT.write_text(json.dumps({"imported": 0, "note": "no unique assets"}, indent=2), encoding="utf-8")
        print("No unique replacement files — skip")
        return

    resolve = get_resolve()
    if not resolve:
        raise SystemExit("Resolve not running")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    mp = project.GetMediaPool()
    root = mp.GetRootFolder()

    def find_folder(name: str):
        for sf in root.GetSubFolderList() or []:
            if sf.GetName() == name:
                return sf
        return mp.AddSubFolder(root, name)

    folder = find_folder("Kinetic Unique Replacements")
    imported = mp.ImportMedia(paths) or []
    for item in imported:
        try:
            mp.MoveClips([item], folder)
        except Exception:
            pass

    REPORT.write_text(
        json.dumps({"imported": len(imported), "paths": len(paths), "folder": "Kinetic Unique Replacements"}, indent=2),
        encoding="utf-8",
    )
    print("IMPORTED", len(imported), "of", len(paths))


if __name__ == "__main__":
    main()
