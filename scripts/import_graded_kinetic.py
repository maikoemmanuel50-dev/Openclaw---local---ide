"""Import graded_1080 kinetic stills into Resolve Media Pool."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
GRADED = PROJECT / "assets" / "canva" / "kinetic" / "graded_1080"
STOCK = PROJECT / "renders" / "paced_overlays" / "stock_cinematic"
REPORT = PROJECT / "renders" / "quality" / "import_graded_kinetic_report.json"


def get_resolve():
    sys.path.append(
        r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
    )
    import DaVinciResolveScript as dvr
    return dvr.scriptapp("Resolve")


def main():
    paths = []
    for root in (GRADED, STOCK):
        if root.is_dir():
            for p in sorted(root.iterdir()):
                if p.suffix.lower() in (".png", ".jpg", ".mp4", ".mov") and p.is_file():
                    paths.append(str(p))
    resolve = get_resolve()
    if not resolve:
        raise SystemExit("Resolve not running")
    project = resolve.GetProjectManager().GetCurrentProject()
    mp = project.GetMediaPool()
    root = mp.GetRootFolder()
    folder = None
    for sf in root.GetSubFolderList() or []:
        if sf.GetName() == "Kinetic Graded 1080":
            folder = sf
            break
    if folder is None:
        folder = mp.AddSubFolder(root, "Kinetic Graded 1080")
    # Import in chunks
    imported = 0
    for i in range(0, len(paths), 40):
        chunk = paths[i : i + 40]
        items = mp.ImportMedia(chunk) or []
        imported += len(items)
        try:
            mp.MoveClips(items, folder)
        except Exception:
            pass
    REPORT.write_text(json.dumps({"imported": imported, "paths": len(paths)}, indent=2), encoding="utf-8")
    print("IMPORTED_GRADED", imported, "of", len(paths))
    try:
        project.SaveProject()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
