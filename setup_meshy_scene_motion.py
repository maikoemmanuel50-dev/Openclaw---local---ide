"""
Import Meshy GLB dioramas into all 10 scenes — lock camera, animate objects.

Replaces pan/push-into-still with in-scene motion (tree sway, animal walk, etc.).

SAFE DEFAULT: writes sidecar previews — does NOT save master while HQ batch runs.
  blender -b blend/africa_s1_master_v01.blend -P setup_meshy_scene_motion.py

Apply to master after HQ 10/10 (GPU free):
  set AFRICA_MESHY_APPLY_MASTER=1
  blender -b blend/africa_s1_master_v01.blend -P setup_meshy_scene_motion.py

Refs: Meshy MCP https://github.com/meshy-dev/meshy-mcp-server
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
MANIFEST = PROJECT / "scripts" / "meshy_scene_manifest.json"
MESHY_ROOT = PROJECT / "assets" / "meshy" / "scenes"
REPORT = PROJECT / "renders" / "quality" / "meshy_blender_motion_report.json"
MASTER = PROJECT / "blend" / "africa_s1_master_v01.blend"
APPLY_MASTER = os.environ.get("AFRICA_MESHY_APPLY_MASTER", "").strip() in ("1", "true", "yes")


def iter_action_fcurves(action):
    if action is None:
        return
    legacy = getattr(action, "fcurves", None)
    if legacy is not None:
        yield from legacy
        return
    if not hasattr(action, "layers"):
        return
    for layer in action.layers:
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", None) or []:
                for fc in getattr(bag, "fcurves", []) or []:
                    yield fc


def clear_camera_motion(cam: bpy.types.Object):
    if cam.animation_data:
        cam.animation_data_clear()
    # Static hold — object motion carries energy instead of Ken Burns pan
    cam.keyframe_insert(data_path="location", frame=1)
    cam.keyframe_insert(data_path="rotation_euler", frame=1)
    cam.keyframe_insert(data_path="location", frame=bpy.context.scene.frame_end)
    cam.keyframe_insert(data_path="rotation_euler", frame=bpy.context.scene.frame_end)


def hide_flat_plates(sc: bpy.types.Scene):
    hidden = []
    for o in sc.objects:
        if any(k in o.name for k in ("Background_Plane", "Foreground_Plane", "Midground_Plane")):
            o.hide_render = True
            o.hide_viewport = True
            hidden.append(o.name)
    return hidden


def find_glb(scene_id: str) -> Path | None:
    d = MESHY_ROOT / scene_id
    if not d.is_dir():
        return None
    glbs = sorted(d.glob("*.glb"))
    return glbs[0] if glbs else None


def import_glb(path: Path, name: str) -> bpy.types.Object | None:
    before = set(bpy.data.objects)
    try:
        bpy.ops.import_scene.gltf(filepath=str(path))
    except Exception as e:
        print(f"IMPORT_FAIL {path}: {e}", flush=True)
        return None
    after = [o for o in bpy.data.objects if o not in before]
    if not after:
        return None
    root = after[0]
    for o in after:
        if o.parent is None:
            root = o
            break
    root.name = name
    return root


def add_wind_driver(obj: bpy.types.Object, axis: str = "Z", amp_deg: float = 2.5, period: int = 72):
    """Gentle procedural sway via driver on rotation."""
    if obj.animation_data:
        obj.animation_data_clear()
    base = obj.rotation_euler.z if axis == "Z" else obj.rotation_euler.x
    obj.rotation_mode = "XYZ"
    fc = obj.driver_add("rotation_euler", 2 if axis == "Z" else 0).driver
    fc.type = "SCRIPTED"
    fc.expression = f"{base} + radians({amp_deg}) * sin((frame - 1) * 2 * pi / {period})"
    fc.use_self = True


def add_animal_walk(obj: bpy.types.Object, sc: bpy.types.Scene, start_f: int, end_f: int):
    """Simple lateral walk across frame."""
    if obj.animation_data:
        obj.animation_data_clear()
    x0, x1 = -3.5, 3.5
    obj.location = (x0, obj.location.y, obj.location.z)
    obj.keyframe_insert("location", frame=start_f)
    obj.location = (x1, obj.location.y, obj.location.z)
    obj.keyframe_insert("location", frame=end_f)
    ad = obj.animation_data
    if ad and ad.action:
        for fc in iter_action_fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"


def tag_and_animate(root: bpy.types.Object, motion: list[str], sc: bpy.types.Scene):
    """Apply motion recipes to imported hierarchy."""
    children = [root] + list(root.children_recursive)
    for m in motion:
        if m == "tree_sway":
            for o in children:
                nl = o.name.lower()
                if any(t in nl for t in ("tree", "acacia", "bush", "plant", "foliage", "branch")):
                    add_wind_driver(o, amp_deg=3.0, period=90)
        elif m in ("grass_sway", "sign_sway", "fabric_flutter", "plant_sway", "cloud_drift"):
            for o in children:
                add_wind_driver(o, amp_deg=1.8, period=120)
        elif m == "animal_walk":
            meshes = [o for o in children if o.type == "MESH"]
            target = root
            if meshes:
                target = max(meshes, key=lambda x: len(x.data.vertices) if x.data else 0)
            add_animal_walk(target, sc, int(sc.frame_start + sc.frame_end * 0.35), int(sc.frame_start + sc.frame_end * 0.75))
        elif m in ("thumb_scroll", "ui_pulse", "light_pulse", "window_twinkle", "panel_shimmer", "subtle_glow"):
            add_wind_driver(root, amp_deg=0.6, period=48)


def setup_scene_entry(entry: dict) -> dict:
    sc_name = entry["blender_scene"]
    sc = bpy.data.scenes.get(sc_name)
    if sc is None:
        return {"scene": sc_name, "status": "missing"}
    bpy.context.window.scene = sc
    glb = find_glb(entry["id"])
    if glb is None:
        return {"scene": sc_name, "status": "no_glb", "expected": str(MESHY_ROOT / entry["id"])}

    cam = sc.camera
    if cam and entry.get("camera_lock", True):
        clear_camera_motion(cam)

    hidden = hide_flat_plates(sc)
    root = import_glb(glb, f"MESHY_{entry['id']}_Root")
    if root is None:
        return {"scene": sc_name, "status": "import_fail"}

    # Frame diorama: center, scale to fill camera view
    root.location = (0.0, 0.0, 0.0)
    root.scale = (2.5, 2.5, 2.5)
    tag_and_animate(root, entry.get("motion", []), sc)

    return {
        "scene": sc_name,
        "status": "ok",
        "glb": str(glb),
        "hidden_plates": hidden,
        "root": root.name,
        "motion": entry.get("motion", []),
    }


def main():
    if not MANIFEST.is_file():
        raise SystemExit(f"Missing {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results = []
    for entry in manifest["scenes"]:
        print(f"SETUP {entry['id']} ...", flush=True)
        results.append(setup_scene_entry(entry))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"apply_master": APPLY_MASTER, "results": results}, indent=2), encoding="utf-8")

    if APPLY_MASTER:
        bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
        print("SAVED master", MASTER, flush=True)
    else:
        preview = PROJECT / "blend" / "africa_s1_meshy_motion_preview.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(preview))
        print("SAVED preview (master untouched — HQ safe)", preview, flush=True)
        print("Set AFRICA_MESHY_APPLY_MASTER=1 after HQ 10/10 to bake into master.", flush=True)


if __name__ == "__main__":
    main()
