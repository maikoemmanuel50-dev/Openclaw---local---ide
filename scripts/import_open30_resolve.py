"""Import TED-Ed 30s open into Resolve Media Pool."""
from __future__ import annotations

import json
import os
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
OPEN_ENH = os.path.join(PROJECT, "renders", "paced_overlays", "s01_teded_open_30s_enhanced.mp4")
OPEN_BASE = os.path.join(PROJECT, "renders", "paced_overlays", "s01_teded_open_30s.mp4")
OPEN = OPEN_ENH if os.path.isfile(OPEN_ENH) else OPEN_BASE
REPORT = os.path.join(PROJECT, "renders", "quality", "import_open30_report.json")


def get_resolve():
    sys.path.append(
        r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
    )
    import DaVinciResolveScript as dvr
    return dvr.scriptapp("Resolve")


def main():
    if not os.path.isfile(OPEN):
        print("MISSING", OPEN)
        return 1
    resolve = get_resolve()
    if not resolve:
        raise SystemExit("Resolve not running")
    mp = resolve.GetProjectManager().GetCurrentProject().GetMediaPool()
    root = mp.GetRootFolder()
    folder = None
    for sf in root.GetSubFolderList() or []:
        if sf.GetName() == "TED-Ed Open30":
            folder = sf
            break
    if folder is None:
        folder = mp.AddSubFolder(root, "TED-Ed Open30")
    imported = mp.ImportMedia([OPEN]) or []
    for item in imported:
        try:
            mp.MoveClips([item], folder)
        except Exception:
            pass
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump({"imported": len(imported), "path": OPEN}, f, indent=2)
    print("IMPORTED open30", len(imported))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
