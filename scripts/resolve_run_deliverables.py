"""
Run all Resolve deliverables on the CURRENT open project/timeline.

Preserves your active edit tab — does not switch projects.
Relinks offline media to workspace paths, imports deliverables, places open30 + kinetic.

Run IN Resolve (required for Free edition):
  Workspace → Scripts → Utility → AfricaS1_RunDeliverables

Or external (Resolve Studio + Local scripting enabled):
  python scripts/resolve_run_deliverables.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
REPORT = PROJECT / "renders" / "quality" / "resolve_deliverables_report.json"

# Add project scripts to path when launched from Resolve Utility folder
sys.path.insert(0, str(PROJECT / "scripts"))

from resolve_common import (  # noqa: E402
    PROJECT as PROJ,
    collect_import_paths,
    ensure_folder,
    get_resolve,
    index_clips,
    relink_offline_clips,
)


def sync_built_clips() -> list[str]:
    """Mirror HQ clips + open30 S01 into built_clips for Resolve V1 relink."""
    clips = PROJ / "renders" / "video_clips"
    built = PROJ / "renders" / "built_clips"
    built.mkdir(parents=True, exist_ok=True)
    scenes = [
        "01_ColdOpen", "02_Context2007", "03_Beat1_Hubs", "04_Beat1_Phone",
        "05_Beat2_Money", "06_Beat2_Solar", "07_Beat3_Gap", "08_Beat3_SecondaryCity",
        "09_Closer", "10_EndCard",
    ]
    copied = []
    integrated = clips / "01_ColdOpen_with_open30.mp4"
    for s in scenes:
        dst = built / f"{s}.mp4"
        if s == "01_ColdOpen" and integrated.is_file() and integrated.stat().st_size > 200_000:
            import shutil
            shutil.copy2(integrated, dst)
            copied.append(str(dst))
            continue
        src = clips / f"{s}.mp4"
        if src.is_file() and src.stat().st_size > 200_000:
            import shutil
            shutil.copy2(src, dst)
            copied.append(str(dst))
    return copied


def build_fairlight_stems() -> bool:
    stem_script = PROJ / "scripts" / "resolve_fairlight_overnight.py"
    if not stem_script.is_file():
        return False
    r = subprocess.run(
        [sys.executable, str(stem_script), "--stems-only"],
        cwd=str(PROJ),
        capture_output=True,
        text=True,
    )
    return r.returncode == 0


def run_submodule(name: str) -> dict:
    mod_path = PROJ / "scripts" / f"{name}.py"
    if not mod_path.is_file():
        return {"ok": False, "error": "missing"}
    r = subprocess.run(
        [sys.executable, str(mod_path)],
        cwd=str(PROJ),
        env={**os.environ, "AFRICA_NO_YELLOW_BALL": "1"},
        capture_output=True,
        text=True,
    )
    return {
        "ok": r.returncode == 0,
        "exit": r.returncode,
        "tail": (r.stdout or r.stderr)[-800:],
    }


def run_in_app(resolve) -> dict:
    log: dict = {"mode": "in_app", "started": datetime.now().isoformat()}
    resolve.OpenPage("edit")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        raise RuntimeError("No project open — open Africa S1 project first")

    log["project"] = project.GetName()
    log["timeline_before"] = (project.GetCurrentTimeline() or {}).GetName() if project.GetCurrentTimeline() else None

    mp = project.GetMediaPool()
    root = mp.GetRootFolder()

    log["sync_built_clips"] = sync_built_clips()
    log["relink"] = relink_offline_clips(mp)

    paths = collect_import_paths()
    imported = mp.ImportMedia(paths) or []
    log["imported_count"] = len(imported)

    africa = ensure_folder(mp, root, "Africa S1 Deliverables")
    open_folder = ensure_folder(mp, root, "TED-Ed Open30")
    for item in imported:
        name = (item.GetName() or "").lower()
        try:
            if "teded_open" in name or "open30" in name:
                mp.MoveClips([item], open_folder)
            elif any(x in name for x in ("01_coldopen", "kinetic", "cut_", "uniq_", "yb_", "fairlight")):
                mp.MoveClips([item], africa)
        except Exception:
            pass

    # Delegate placement to existing scripts (same Resolve session)
    os.environ["AFRICA_NO_YELLOW_BALL"] = "1"
    for step in (
        "import_open30_resolve",
        "import_unique_kinetic_assets",
        "resolve_open30_timeline",
        "resolve_pace_kinetic_yb",
    ):
        try:
            mod = __import__(step)
            mod.main()
            log[step] = {"ok": True}
        except Exception as e:
            log[step] = {"ok": False, "error": str(e)}

    # Fairlight stems (ffmpeg) then audio placement
    try:
        fl = __import__("resolve_fairlight_overnight")
        if hasattr(fl, "build_stems_only"):
            fl.build_stems_only()
        fl.main()
        log["fairlight"] = {"ok": True}
    except Exception as e:
        log["fairlight"] = {"ok": False, "error": str(e)}

    log["timeline_after"] = (project.GetCurrentTimeline() or {}).GetName() if project.GetCurrentTimeline() else None
    try:
        project.SaveProject()
    except Exception:
        pass
    log["finished"] = datetime.now().isoformat()
    return log


def main():
    sync_built_clips()

    resolve = get_resolve()
    if resolve:
        log = run_in_app(resolve)
    else:
        log = {
            "mode": "external_failed",
            "error": "Resolve API not reachable",
            "fix": "In Resolve: Workspace → Scripts → Utility → AfricaS1_RunDeliverables",
            "sync_built_clips": sync_built_clips(),
        }
        # Still build stems + partial stem offline
        log["fairlight_stems"] = build_fairlight_stems()
        log["partial_stem"] = run_submodule("assemble_partial_stem")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print("RESOLVE_DELIVERABLES", json.dumps(log, indent=2))
    if log.get("mode") == "external_failed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
