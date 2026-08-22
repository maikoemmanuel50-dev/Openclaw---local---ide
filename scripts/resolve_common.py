"""Shared Resolve connection + media relink helpers (in-app or external)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
MODULES = Path(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

SEARCH_ROOTS = [
    PROJECT / "renders" / "built_clips",
    PROJECT / "renders" / "video_clips",
    PROJECT / "renders" / "paced_overlays",
    PROJECT / "renders" / "paced_overlays" / "stock_cinematic",
    PROJECT / "renders" / "paced_overlays" / "unique_replacements",
    PROJECT / "assets" / "canva" / "kinetic",
    PROJECT / "assets" / "canva" / "kinetic" / "unique_replacements",
    PROJECT / "assets" / "yellow_ball" / "export",
    PROJECT / "assets" / "audio",
    PROJECT / "renders" / "audio_stems" / "fairlight",
]


def get_resolve():
    """Return Resolve app object (in-app script or external API)."""
    try:
        import DaVinciResolveScript as dvr  # noqa: F401
    except ImportError:
        if str(MODULES) not in sys.path:
            sys.path.append(str(MODULES))
        try:
            import DaVinciResolveScript as dvr
        except ImportError:
            return None
    resolve = dvr.scriptapp("Resolve")
    if resolve is None:
        resolve = dvr.scriptapp("DaVinciResolve")
    return resolve


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
    nl = name.lower()
    for n, c in by.items():
        if n.lower() == nl or stem in n.lower() or nl in n.lower():
            return c
    return None


def ensure_folder(mp, root, name: str):
    for sf in root.GetSubFolderList() or []:
        if sf.GetName() == name:
            return sf
    return mp.AddSubFolder(root, name)


def collect_import_paths() -> list[str]:
    paths: list[str] = []
    open_enh = PROJECT / "renders" / "paced_overlays" / "s01_teded_open_30s_enhanced.mp4"
    open_base = PROJECT / "renders" / "paced_overlays" / "s01_teded_open_30s.mp4"
    if open_enh.is_file():
        paths.append(str(open_enh))
    elif open_base.is_file():
        paths.append(str(open_base))

    for d in (
        PROJECT / "renders" / "built_clips",
        PROJECT / "renders" / "paced_overlays" / "stock_cinematic",
        PROJECT / "renders" / "paced_overlays" / "unique_replacements",
        PROJECT / "assets" / "canva" / "kinetic" / "unique_replacements",
        PROJECT / "assets" / "yellow_ball" / "export",
        PROJECT / "renders" / "audio_stems" / "fairlight",
    ):
        if d.is_dir():
            for p in sorted(d.iterdir()):
                if p.is_file() and p.suffix.lower() in (
                    ".mp4", ".mov", ".png", ".jpg", ".wav", ".mp3",
                ):
                    paths.append(str(p))
    stock_dir = PROJECT / "renders" / "paced_overlays" / "open30_stock_cuts"
    if stock_dir.is_dir():
        for p in stock_dir.rglob("*.mp4"):
            paths.append(str(p))
    return paths


def relink_offline_clips(mp) -> dict:
    """Relink media pool clips to workspace files by basename."""
    stats = {"attempted": 0, "relinked": 0, "still_offline": 0}
    by_name: dict[str, Path] = {}
    for root in SEARCH_ROOTS:
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.is_file():
                by_name.setdefault(p.name.lower(), p)

    root = mp.GetRootFolder()
    clips = []

    def walk(folder):
        for c in folder.GetClipList() or []:
            clips.append(c)
        for sf in folder.GetSubFolderList() or []:
            walk(sf)

    walk(root)
    for clip in clips:
        stats["attempted"] += 1
        try:
            props = clip.GetClipProperty() or {}
        except Exception:
            continue
        fp = props.get("File Path") or props.get("FilePath") or ""
        if fp and os.path.isfile(fp):
            continue
        name = (clip.GetName() or "").lower()
        target = by_name.get(name)
        if not target:
            stats["still_offline"] += 1
            continue
        try:
            if mp.RelinkClips([clip], str(target.parent)):
                stats["relinked"] += 1
            else:
                stats["still_offline"] += 1
        except Exception:
            stats["still_offline"] += 1
    return stats
