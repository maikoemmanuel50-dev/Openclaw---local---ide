"""
Africa S1 — Faceless YT documentary aesthetic lock (Fern / Imperial / Lucas Edits / tinynocky).

Sources:
  https://youtu.be/Jmcg5ZSU8a8  TomsProject — Edit Faceless (Fern, Neo, Imperial)
  https://youtu.be/YJdGgpZoiAA  Lucas Edits — Aesthetic YT 3D Documentaries
  https://youtu.be/tCTkkHGRpNk  tinynocky — 18-day Blender → Resolve grade

SAFE after HQ batch. Does NOT start 4K.
  blender -b blend/africa_s1_master_v01.blend -P setup_documentary_aesthetic_lock.py
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
REPORT = PROJECT / "renders" / "quality" / "documentary_aesthetic_report.json"
HDRI_DIR = PROJECT / "assets" / "hdri"
TEX_DIR = PROJECT / "assets" / "textures" / "polyhaven"

# Fern/Imperial/Lucas: DOF + readability (charts stay deep)
SCENE_DOC = {
    "01_ColdOpen": {"fstop": 4.0, "bloom": 0.04, "mb": True},
    "02_Context2007": {"fstop": 5.0, "bloom": 0.03, "mb": True},
    "03_Beat1_Hubs": {"fstop": 4.5, "bloom": 0.035, "mb": True},
    "04_Beat1_Phone": {"fstop": 3.5, "bloom": 0.05, "mb": True},
    "05_Beat2_Money": {"fstop": 8.0, "bloom": 0.02, "mb": False},
    "06_Beat2_Solar": {"fstop": 5.6, "bloom": 0.06, "mb": True},
    "07_Beat3_Gap": {"fstop": 8.0, "bloom": 0.02, "mb": False},
    "08_Beat3_SecondaryCity": {"fstop": 4.0, "bloom": 0.03, "mb": True},
    "09_Closer": {"fstop": 5.0, "bloom": 0.045, "mb": True},
    "10_EndCard": {"fstop": 8.0, "bloom": 0.025, "mb": False},
}


def find_focus_object(sc: bpy.types.Scene):
    """Hero focus: Sasa_Master → YB_Head → Sasa_Ball (Fern faceless hero)."""
    for name in ("Sasa_Master",):
        o = sc.objects.get(name)
        if o:
            return o
    for o in sc.objects:
        if o.name.startswith("YB_Head_") and not o.hide_render:
            return o
    for o in sc.objects:
        if o.name.startswith("Sasa_Ball") and not o.hide_render:
            return o
    for o in sc.objects:
        if "Background" in o.name and o.type == "MESH":
            return o
    return None


def ensure_doc_empty(sc: bpy.types.Scene) -> bpy.types.Object:
    """tinynocky: parent null for shared speed scaling of cam + subject."""
    name = "DOC_SpeedNull"
    empty = sc.objects.get(name)
    if empty is None:
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = "PLAIN_AXES"
        empty.empty_display_size = 0.5
        sc.collection.objects.link(empty)
    return empty


def configure_camera(sc: bpy.types.Scene, cfg: dict) -> dict:
    cam = sc.camera
    if not cam:
        return {"error": "no camera"}
    d = cam.data
    d.dof.use_dof = True
    d.dof.aperture_fstop = cfg["fstop"]
    focus = find_focus_object(sc)
    if focus:
        d.dof.focus_object = focus
        # Clear fixed distance when object-driven
        try:
            d.dof.focus_distance = (cam.matrix_world.translation - focus.matrix_world.translation).length
        except Exception:
            pass
    if hasattr(d, "show_limits"):
        d.show_limits = True
    # Sensor ~full frame for Fern shallow-DOF control when f-stop is low
    if hasattr(d, "sensor_width"):
        d.sensor_width = 36.0
    return {
        "camera": cam.name,
        "fstop": cfg["fstop"],
        "focus": focus.name if focus else None,
    }


def configure_eevee(sc: bpy.types.Scene, cfg: dict):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.fps = 24
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    ee = sc.eevee
    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = max(getattr(ee, "taa_render_samples", 64), 128)
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = True
    if hasattr(ee, "use_bloom"):
        ee.use_bloom = True
        if hasattr(ee, "bloom_intensity"):
            ee.bloom_intensity = cfg.get("bloom", 0.03)
        if hasattr(ee, "bloom_threshold"):
            ee.bloom_threshold = 0.85
    # Subtle motion blur — Lucas/Fern cinematic, not sports
    if hasattr(sc.render, "use_motion_blur"):
        sc.render.use_motion_blur = bool(cfg.get("mb", True))
        if hasattr(sc.render, "motion_blur_shutter"):
            sc.render.motion_blur_shutter = 0.35


def ensure_key_light(sc: bpy.types.Scene):
    """Lucas Edits: light that shapes — soft area key if scene has none."""
    lights = [o for o in sc.objects if o.type == "LIGHT"]
    if lights:
        return lights[0].name
    data = bpy.data.lights.new(name="DOC_Key", type="AREA")
    data.energy = 80.0
    data.size = 4.0
    if hasattr(data, "spread"):
        data.spread = math.radians(46)  # soft photographic spread
    obj = bpy.data.objects.new("DOC_Key", data)
    sc.collection.objects.link(obj)
    cam = sc.camera
    if cam:
        # Key from camera-left-above
        loc = cam.matrix_world.translation.copy()
        forward = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        right = cam.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        up = cam.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        obj.location = loc - forward * 2.0 + right * -2.5 + up * 2.0
        direction = (loc - forward * 3.0) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return obj.name


def wire_polyhaven_hint() -> dict:
    """tinynocky: Poly Haven textures/HDRIs on disk for env realism."""
    hdris = sorted(p.name for p in HDRI_DIR.glob("*")) if HDRI_DIR.exists() else []
    tex_sets = []
    if TEX_DIR.exists():
        tex_sets = sorted(d.name for d in TEX_DIR.iterdir() if d.is_dir())
    return {"hdris": hdris, "pbr_sets": tex_sets}


def ease_camera_curves(sc: bpy.types.Scene) -> int:
    """Smooth documentary cams — BEZIER only (no LINEAR pops)."""
    n = 0
    cam = sc.camera
    if not cam or not cam.animation_data or not cam.animation_data.action:
        return 0
    for fc in cam.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"
            n += 1
    return n


def lock_scene(sc: bpy.types.Scene) -> dict:
    cfg = SCENE_DOC.get(sc.name, {"fstop": 5.6, "bloom": 0.03, "mb": True})
    try:
        if getattr(bpy.context, "window", None):
            bpy.context.window.scene = sc
    except Exception:
        pass
    configure_eevee(sc, cfg)
    cam_info = configure_camera(sc, cfg)
    key = ensure_key_light(sc)
    ease = ease_camera_curves(sc)
    null = ensure_doc_empty(sc)
    # Optionally parent camera to speed null if cam has no parent (tinynocky)
    cam = sc.camera
    if cam and cam.parent is None:
        # Keep world matrix: parent inverse
        mw = cam.matrix_world.copy()
        cam.parent = null
        cam.matrix_parent_inverse = null.matrix_world.inverted() @ mw
    return {
        "scene": sc.name,
        "camera": cam_info,
        "key_light": key,
        "eased_cam_keys": ease,
        "speed_null": null.name,
        "faceless_lock": True,
    }


def main():
    print("=== Documentary Aesthetic Lock (Fern/Imperial/Lucas/tinynocky) ===")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    known = list(SCENE_DOC.keys())
    results = []
    for name in known:
        if name not in bpy.data.scenes:
            results.append({"scene": name, "error": "missing"})
            continue
        try:
            results.append(lock_scene(bpy.data.scenes[name]))
            print(f"OK {name}")
        except Exception as e:
            results.append({"scene": name, "error": str(e)})
            print(f"FAIL {name}: {e}")

    out = {
        "refs": [
            "https://youtu.be/Jmcg5ZSU8a8",
            "https://youtu.be/YJdGgpZoiAA",
            "https://youtu.be/tCTkkHGRpNk",
            "docs/DOCUMENTARY_AESTHETIC_LOCK.md",
        ],
        "polyhaven": wire_polyhaven_hint(),
        "resolve_note": "Final grade in DaVinci Resolve Color (tinynocky Day 18) — chapter soft-pop, not Blender-only.",
        "scenes": results,
    }
    REPORT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"SAVED {bpy.data.filepath}")
    print(f"REPORT {REPORT}")
    print("DOCUMENTARY_AESTHETIC_LOCK_DONE")


if __name__ == "__main__":
    main()
