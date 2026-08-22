"""
Disable yellow ball / YB-Body / Sasa hero from all scene renders.

User override (2026-08-13): remove yellow ball from animation + video frame output
for remaining-scene redo. Scene 01 plate is kept as-is on disk; blend is updated
so scenes 02–10 (and any future re-render) omit the hero.

Does not delete datablocks — only hide_render / exclude from view layer render.
"""
from __future__ import annotations

import json
from pathlib import Path

import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
REPORT = PROJECT / "renders" / "quality" / "yellow_ball_removed_report.json"

NAME_PREFIXES = (
    "Sasa_",
    "YB_",
    "YB_Rig_",
    "YB_Body_",
    "YB_Head_",
    "YellowBall",
    "CTRL_Root",
    "CTRL_Squash",
    "MCH_Stretch",
)
NAME_CONTAINS = (
    "Sasa_Ball",
    "Sasa_Master",
    "YellowBall",
    "YB_Head",
    "YB_Body",
)


def is_hero(obj: bpy.types.Object) -> bool:
    n = obj.name
    if any(n.startswith(p) for p in NAME_PREFIXES):
        return True
    if any(k in n for k in NAME_CONTAINS):
        return True
    return False


def disable_object(obj: bpy.types.Object) -> None:
    obj.hide_render = True
    try:
        obj.hide_viewport = True
    except Exception:
        pass
    try:
        obj.visible_camera = False
        obj.visible_shadow = False
        obj.visible_diffuse = False
        obj.visible_glossy = False
        obj.visible_transmission = False
        obj.visible_volume_scatter = False
    except Exception:
        pass


def disable_collections() -> list[str]:
    hit = []
    for col in bpy.data.collections:
        low = col.name.lower()
        if any(k in low for k in ("sasa", "yellow", "yb_", "yb-body", "yb body")):
            col.hide_render = True
            try:
                col.hide_viewport = True
            except Exception:
                pass
            hit.append(col.name)
    return hit


def main():
    objs = []
    for obj in list(bpy.data.objects):
        if is_hero(obj):
            disable_object(obj)
            objs.append(obj.name)

    # Per-scene object instances (linked) + view-layer excludes
    scenes_touched = []
    for sc in bpy.data.scenes:
        for obj in sc.objects:
            if is_hero(obj) and not obj.hide_render:
                disable_object(obj)
                if obj.name not in objs:
                    objs.append(obj.name)
        for vl in sc.view_layers:
            for obj in sc.objects:
                if not is_hero(obj):
                    continue
                try:
                    obj.hide_set(True, view_layer=vl)
                except Exception:
                    pass
                try:
                    # Exclude from view layer if supported
                    bas = vl.objects.get(obj.name) if hasattr(vl, "objects") else None
                    if bas is not None and hasattr(bas, "exclude"):
                        bas.exclude = True
                except Exception:
                    pass
        scenes_touched.append(sc.name)

    cols = disable_collections()

    blend = Path(bpy.data.filepath) if bpy.data.filepath else PROJECT / "blend" / "africa_s1_master_v01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))

    report = {
        "objects_hidden": sorted(set(objs)),
        "collections_hidden": cols,
        "scenes": scenes_touched,
        "saved": str(blend),
        "count": len(set(objs)),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("YELLOW_BALL_REMOVED", report["count"], "objects", flush=True)
    return report


if __name__ == "__main__":
    main()
