"""Import clearance replacement stills into Resolve project Africa Season 1."""
from __future__ import annotations

import os
import sys

sys.path.append(
    r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
)
import DaVinciResolveScript as dvr  # type: ignore

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
PATHS = [
    os.path.join(PROJECT, r"assets\canva\kinetic\infographics\inf_s04_kenya_4g_device_bars.png"),
    os.path.join(PROJECT, r"assets\canva\kinetic\infographics\extra_unique\x_s01_mm_market_share_chip.png"),
    os.path.join(PROJECT, r"assets\canva\s10_africa_wordmark_endcard.png"),
]


def main() -> None:
    r = dvr.scriptapp("Resolve")
    if not r:
        print("NO_RESOLVE")
        sys.exit(1)
    pm = r.GetProjectManager()
    pm.LoadProject("Africa Season 1")
    p = pm.GetCurrentProject()
    mp = p.GetMediaPool()
    root = mp.GetRootFolder()
    folder = None
    for sf in root.GetSubFolderList() or []:
        if sf.GetName() == "Clearance Replacements":
            folder = sf
            break
    if folder is None:
        folder = mp.AddSubFolder(root, "Clearance Replacements")
    mp.SetCurrentFolder(folder)
    imp = mp.ImportMedia(PATHS) or []
    print("imported", len(imp), [c.GetName() for c in imp])
    try:
        p.SaveProject()
    except Exception:
        pass


if __name__ == "__main__":
    main()
