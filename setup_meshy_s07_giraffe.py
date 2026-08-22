"""
Import Meshy Free S07 giraffe GLB when present; hide MOTION_Walker_S07 proxy.

Drop file: assets/meshy/scenes/S07/s07_giraffe.glb (any *.glb in folder works)

Run on preview (HQ-safe):
  blender -b blend/africa_s1_object_motion_preview.blend -P setup_meshy_s07_giraffe.py

After HQ 10/10 on master:
  blender -b blend/africa_s1_master_v01.blend -P setup_meshy_s07_giraffe.py
"""
from __future__ import annotations

import json
from pathlib import Path

import addon_utils
import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
GLB_DIR = PROJECT / "assets" / "meshy" / "scenes" / "S07"
REPORT = PROJECT / "renders" / "quality" / "meshy_s07_giraffe_report.json"
SCENE = "07_Beat3_Gap"
COL = "MODEL_ADDITIONS"
WALKER = "MOTION_Walker_S07"
IMPORT_NAME = "Meshy_Giraffe_S07"


def find_glb() -> Path | None:
    if not GLB_DIR.is_dir():
        return None
    preferred = GLB_DIR / "s07_giraffe.glb"
    if preferred.is_file():
        return preferred
    glbs = sorted(GLB_DIR.glob("*.glb"))
    return glbs[0] if glbs else None


def ensure_collection(sc: bpy.types.Scene, name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        sc.collection.children.link(col)
    return col


def main():
    glb = find_glb()
    report = {"glb": str(glb) if glb else None, "imported": False, "walker_hidden": False}
    if not glb:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("SKIP no GLB in", GLB_DIR, flush=True)
        return

    try:
        addon_utils.enable("io_scene_gltf2", default_set=True)
    except Exception:
        pass

    sc = bpy.data.scenes.get(SCENE)
    if not sc:
        raise SystemExit(f"Scene {SCENE} missing")

    col = ensure_collection(sc, COL)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    new_objs = [o for o in bpy.data.objects if o not in before]
    if not new_objs:
        print("WARN import produced no objects", flush=True)
    else:
        root = new_objs[0]
        for o in new_objs:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            col.objects.link(o)
        root.name = IMPORT_NAME
        root.location = (-2.2, 4.0, 0.0)
        root.rotation_euler = (0, 0, 1.5708)
        root.scale = (0.55, 0.55, 0.55)
        report["imported"] = True
        report["objects"] = [o.name for o in new_objs]

    walker = sc.objects.get(WALKER)
    if walker:
        walker.hide_render = True
        walker.hide_viewport = True
        report["walker_hidden"] = True

    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    bpy.ops.wm.save_mainfile()
    print("MESHY_S07", report, flush=True)


if __name__ == "__main__":
    main()
