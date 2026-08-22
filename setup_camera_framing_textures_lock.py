"""
Camera pacing + framing + surface/texture lock — Africa S1 (Blender 5.1).

Industry refs baked into rules:
  - Documentary push-in: slow continuous move (Fern / Imperial / LEMMiNO)
  - Ease-in/out on camera F-curves (no linear pops)
  - Photoplates cover full camera frustum (Ken Burns source, not letterbox)
  - Principled BSDF + Smart texture filtering (Poly Haven / Blender Studio hygiene)
  - AgX MHC, EEVEE RT, filter_size ~1.0–1.2 for crisp plates

SAFE: run AFTER HQ batch finishes (avoid dual -b on same .blend).
  blender -b blend/africa_s1_master_v01.blend -P setup_camera_framing_textures_lock.py

Does NOT start 4K. Does NOT fight a live render batch.
"""
from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
REPORT = PROJECT / "renders" / "quality" / "camera_framing_texture_report.json"

# Documentary camera intent — lens locked, move amplitude as % of scene duration
SCENE_CAM = {
    "01_ColdOpen": {"lens": 35.0, "fstop": 5.6, "move": "push", "amp": 0.85},
    "02_Context2007": {"lens": 40.0, "fstop": 5.6, "move": "pan", "amp": 1.1},
    "03_Beat1_Hubs": {"lens": 40.0, "fstop": 5.0, "move": "parallax", "amp": 0.7},
    "04_Beat1_Phone": {"lens": 50.0, "fstop": 4.0, "move": "push", "amp": 0.55},
    "05_Beat2_Money": {"lens": 35.0, "fstop": 8.0, "move": "push", "amp": 0.45},  # protect chart
    "06_Beat2_Solar": {"lens": 35.0, "fstop": 8.0, "move": "parallax", "amp": 0.65},
    "07_Beat3_Gap": {"lens": 40.0, "fstop": 8.0, "move": "zoom_out", "amp": 1.2},
    "08_Beat3_SecondaryCity": {"lens": 40.0, "fstop": 5.6, "move": "parallax", "amp": 0.75},
    "09_Closer": {"lens": 35.0, "fstop": 5.6, "move": "push", "amp": 0.9},
    "10_EndCard": {"lens": 50.0, "fstop": 8.0, "move": "drift", "amp": 0.35},
}


def ease_fcurves(action: bpy.types.Action):
    """Bezier + auto-clamped handles ≈ industry ease-in/out (no linear pops)."""
    if not action:
        return 0
    n = 0
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"
            n += 1
    return n


def configure_camera(cam_obj, lens: float, fstop: float):
    d = cam_obj.data
    d.lens = lens
    d.clip_start = 0.1
    d.clip_end = 500.0
    d.dof.use_dof = True
    d.dof.aperture_fstop = fstop
    if hasattr(d, "passepartout_alpha"):
        d.passepartout_alpha = 0.85


def cover_plane_in_camera(sc, cam, plane, margin: float = 1.12):
    """Scale BG photoplane so it covers camera frustum at plane depth (LEMMiNO plate)."""
    if not plane or plane.type != "MESH":
        return False
    deps = bpy.context.evaluated_depsgraph_get()
    cam_e = cam.evaluated_get(deps)
    # Distance along camera forward
    to_plane = plane.matrix_world.translation - cam.matrix_world.translation
    forward = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    dist = abs(to_plane.dot(forward))
    if dist < 0.05:
        dist = 5.0
    # Vertical FOV
    sensor = cam.data.sensor_height if cam.data.sensor_fit != "HORIZONTAL" else (
        cam.data.sensor_width / (sc.render.resolution_x / sc.render.resolution_y)
    )
    if cam.data.sensor_fit == "HORIZONTAL":
        fov_x = 2 * math.atan((cam.data.sensor_width / 2) / cam.data.lens)
        aspect = sc.render.resolution_y / sc.render.resolution_x
        fov_y = 2 * math.atan(math.tan(fov_x / 2) * aspect)
    else:
        fov_y = 2 * math.atan((sensor / 2) / cam.data.lens)
        aspect = sc.render.resolution_x / sc.render.resolution_y
        fov_x = 2 * math.atan(math.tan(fov_y / 2) * aspect)
    need_h = 2 * dist * math.tan(fov_y / 2) * margin
    need_w = 2 * dist * math.tan(fov_x / 2) * margin
    # Plane local XY size (default plane is 2x2)
    mesh = plane.data
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    base_w = max(xs) - min(xs) or 2.0
    base_h = max(ys) - min(ys) or 2.0
    sx = need_w / base_w
    sy = need_h / base_h
    # Keep uniform-ish to avoid stretch; use max so both axes cover
    s = max(sx, sy)
    plane.scale.x = s
    plane.scale.y = s
    plane.scale.z = 1.0
    return True


def hygiene_textures():
    """Poly Haven–style: Smart filter, Principled, packed paths check."""
    fixed = {"images": 0, "principled": 0, "missing": []}
    for img in bpy.data.images:
        if img.name in {"Render Result", "Viewer Node"}:
            continue
        try:
            img.interpolation = "Smart"
        except Exception:
            try:
                img.interpolation = "Cubic"
            except Exception:
                pass
        fixed["images"] += 1
        fp = bpy.path.abspath(img.filepath) if img.filepath else ""
        if img.filepath and fp and not Path(fp).exists() and not img.packed_file:
            fixed["missing"].append(img.name)
    for mat in bpy.data.materials:
        if not mat or not mat.use_nodes or not mat.node_tree:
            continue
        for n in mat.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                if hasattr(n.inputs.get("Roughness"), "default_value"):
                    # keep author roughness; ensure metallic sensible for mats
                    pass
                fixed["principled"] += 1
            if n.type == "TEX_IMAGE" and n.image:
                try:
                    n.interpolation = "Smart"
                except Exception:
                    pass
    return fixed


def frame_audit(sc, cam) -> dict:
    """Sample mid frame: BG + ball should be in camera NDC."""
    sc.frame_set((sc.frame_start + sc.frame_end) // 2)
    deps = bpy.context.evaluated_depsgraph_get()
    cam_e = cam.evaluated_get(deps)
    hits = []
    for o in sc.objects:
        if o.type != "MESH":
            continue
        if not any(k in o.name for k in ("Background", "Sasa_Ball", "Foreground", "Bar_", "Solar")):
            continue
        if o.hide_render:
            continue
        c = world_to_camera_view(sc, cam_e, o.matrix_world.translation)
        hits.append({
            "obj": o.name,
            "ndc": [round(c.x, 3), round(c.y, 3), round(c.z, 3)],
            "in_frame": (0.02 <= c.x <= 0.98 and 0.02 <= c.y <= 0.98 and c.z > 0),
        })
    return {"scene": sc.name, "objects": hits}


def lock_scene(sc) -> dict:
    cfg = SCENE_CAM.get(sc.name, {"lens": 35.0, "fstop": 5.6, "move": "push", "amp": 0.7})
    bpy.context.window.scene = sc if hasattr(bpy.context, "window") else sc
    # EEVEE crisp
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    if hasattr(sc.render, "filter_size"):
        sc.render.filter_size = 1.05
    ee = sc.eevee
    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = max(getattr(ee, "taa_render_samples", 128), 128)
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = True
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass

    cam = sc.camera
    if not cam:
        return {"scene": sc.name, "error": "no camera"}

    configure_camera(cam, cfg["lens"], cfg["fstop"])

    # Ease camera + rig empties
    eased = 0
    for obj in (cam, *[o for o in sc.objects if o.name.startswith("CAM_")]):
        if obj.animation_data and obj.animation_data.action:
            eased += ease_fcurves(obj.animation_data.action)

    # Cover BG planes
    covered = []
    for o in sc.objects:
        if "Background" in o.name and o.type == "MESH" and not o.hide_render:
            if cover_plane_in_camera(sc, cam, o, margin=1.14):
                covered.append(o.name)
        # Midground slight scale for parallax scenes
        if cfg["move"] == "parallax" and "Midground" in o.name and o.type == "MESH":
            if not o.hide_render:
                cover_plane_in_camera(sc, cam, o, margin=1.08)

    audit = frame_audit(sc, cam)
    return {
        "scene": sc.name,
        "lens": cfg["lens"],
        "move": cfg["move"],
        "eased_keys": eased,
        "covered_planes": covered,
        "audit": audit,
    }


def main():
    import json
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    tex = hygiene_textures()
    results = []
    for sc in bpy.data.scenes:
        if sc.name not in SCENE_CAM:
            continue
        try:
            results.append(lock_scene(sc))
            print(f"OK {sc.name}")
        except Exception as e:
            results.append({"scene": sc.name, "error": str(e)})
            print(f"FAIL {sc.name}: {e}")

    # Save
    out = {
        "textures": tex,
        "scenes": results,
        "note": "Camera ease + frustum plate cover + texture Smart filter. Re-render HQ if this ran after a stale batch.",
    }
    REPORT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"SAVED {bpy.data.filepath}")
    print(f"REPORT {REPORT}")
    print("CAMERA_FRAMING_TEXTURE_LOCK_DONE")


if __name__ == "__main__":
    main()
