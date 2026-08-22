"""
Real-world camera + anthropometrics + overlay deployment for Africa S1 master.
Grounded in Blender 5.1 docs / EEVEE DOF manual + photographic practice:
- Metric units, full-frame 36mm sensor
- Human eye height ~1.55–1.70 m (street); mild elevate only when story needs it
- Normal FOV ~35–50mm; chart/detail 35mm; portrait-ish holds 50–65mm
- Ball as readable hero prop ~0.42 m Ø; YB-Body adult ~1.70 m (ISO 7250-ish)
- EEVEE DOF: use_dof + realistic f-stops; enable jitter when available (5.1)
"""
from __future__ import annotations

import math
import bpy
from mathutils import Vector, Euler

# Anthropometrics (meters) — adult standing reference
ADULT_HEIGHT = 1.70
EYE_HEIGHT = 1.60
HEAD_DIAM = 0.24          # approximate cranial width for ball-as-head
HERO_BALL_DIAM = 0.42     # graphic hero prop (readable, still human-scale)
YB_TORSO_H = 0.55
YB_TORSO_W = 0.38
YB_TORSO_D = 0.22

# Full-frame cinema defaults
SENSOR_WIDTH = 36.0
CLIP_START = 0.05
CLIP_END = 500.0

# Per-scene photographic intent
SCENE_CAM = {
    # name: (lens_mm, cam_z_eye, fstop, slight_elevate_ok)
    "01_ColdOpen": (35.0, 1.65, 5.6, True),       # establishing — mild elevate allowed via look target
    "02_Context2007": (40.0, 1.55, 5.6, False),
    "03_Beat1_Hubs": (40.0, 1.55, 4.5, False),
    "04_Beat1_Phone": (50.0, 1.45, 4.0, False),    # closer prop / phone
    "05_Beat2_Money": (35.0, 1.70, 8.0, False),    # chart readability
    "06_Beat2_Solar": (35.0, 1.60, 8.0, False),
    "07_Beat3_Gap": (40.0, 1.60, 8.0, False),      # map graphic
    "08_Beat3_SecondaryCity": (40.0, 1.55, 5.6, False),
    "09_Closer": (35.0, 1.70, 5.6, True),
    "10_EndCard": (50.0, 1.55, 8.0, False),
}


def ensure_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def link_to_scene(obj: bpy.types.Object, sc: bpy.types.Scene):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    sc.collection.objects.link(obj)


def set_ball_diameter(obj: bpy.types.Object, diameter: float):
    """Uniform scale so dimensions ≈ diameter (mesh may already be unit sphere)."""
    # Reset scale then set from current mesh bound
    obj.scale = (1, 1, 1)
    bpy.context.view_layer.update()
    dims = obj.dimensions
    cur = max(dims.x, dims.y, dims.z) or 1.0
    s = diameter / cur
    obj.scale = (s, s, s)
    for p in obj.data.polygons:
        p.use_smooth = True
    if not any(m.type == "SUBSURF" for m in obj.modifiers):
        m = obj.modifiers.new("Realism_SubD", "SUBSURF")
        m.levels = 2
        m.render_levels = 3


def make_yb_body(sc: bpy.types.Scene, ball: bpy.types.Object) -> bpy.types.Object:
    """Faceless adult YB-Body: charcoal torso + ball as head (Fern anthropometrics)."""
    name = f"YB_Body_{sc.name[:8]}"
    existing = sc.objects.get(name)
    if existing:
        return existing

    # Torso cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    torso = bpy.context.active_object
    torso.name = name
    torso.dimensions = (YB_TORSO_W, YB_TORSO_D, YB_TORSO_H)
    bpy.ops.object.transform_apply(scale=True)

    # Material charcoal
    mat = bpy.data.materials.get("SoftPop_YB_Body")
    if mat is None:
        mat = bpy.data.materials.new("SoftPop_YB_Body")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.149, 0.125, 0.098, 1)
            bsdf.inputs["Roughness"].default_value = 0.88
    if torso.data.materials:
        torso.data.materials[0] = mat
    else:
        torso.data.materials.append(mat)

    # Place: feet near ground z=0, head = ball
    # Adult: torso center ~ 1.05 m, head center ~ 1.55 m
    bx, by, _ = ball.location
    torso.location = (bx, by, YB_TORSO_H * 0.5 + 0.75)  # pelvis/chest stack
    # Head ball on top of torso
    head_z = torso.location.z + YB_TORSO_H * 0.5 + HEAD_DIAM * 0.55
    ball.location = (bx, by, head_z)
    set_ball_diameter(ball, HEAD_DIAM)

    # Parent ball to torso for unit motion
    ball.parent = torso
    ball.matrix_parent_inverse = torso.matrix_world.inverted()

    # Hide by default — enable when morph beat needs humanity
    torso.hide_render = True
    torso.hide_viewport = True
    torso["yb_body"] = 1
    torso["anthropometric_height_m"] = ADULT_HEIGHT
    return torso


def build_camera_rig(sc: bpy.types.Scene, cam: bpy.types.Object, target: bpy.types.Object | None, lens, eye_z, fstop, elevate):
    """Empty-based camera rig: root at human height, cam child, Track To subject."""
    root_name = f"CAM_RIG_{sc.name}"
    root = sc.objects.get(root_name)
    if root is None:
        root = bpy.data.objects.new(root_name, None)
        root.empty_display_type = "PLAIN_AXES"
        root.empty_display_size = 0.5
        sc.collection.objects.link(root)

    aim_name = f"CAM_AIM_{sc.name}"
    aim = sc.objects.get(aim_name)
    if aim is None:
        aim = bpy.data.objects.new(aim_name, None)
        aim.empty_display_type = "SPHERE"
        aim.empty_display_size = 0.2
        sc.collection.objects.link(aim)

    # Preserve roughly current horizontal framing distance
    dist = abs(cam.location.y) if abs(cam.location.y) > 1 else 8.0
    dist = max(4.0, min(dist, 18.0))

    # Human eye height; mild elevate for establishing only
    z = eye_z + (0.85 if elevate else 0.0)
    root.location = (0.0, -dist, z)
    if target:
        aim.location = target.location.copy()
    else:
        aim.location = (0.0, 0.0, eye_z)

    # Re-parent camera under root
    cam.parent = None
    cam.location = (0.0, 0.0, 0.0)
    cam.rotation_euler = (math.radians(90), 0.0, 0.0)  # look along +Y from root? 
    # Standard: camera default looks -Z. Parent to root, clear loc, Track To aim.
    cam.parent = root
    cam.matrix_parent_inverse = root.matrix_world.inverted()
    cam.location = (0, 0, 0)
    cam.rotation_euler = (0, 0, 0)

    # Track To constraint
    for c in list(cam.constraints):
        if c.type == "TRACK_TO":
            cam.constraints.remove(c)
    tr = cam.constraints.new("TRACK_TO")
    tr.target = aim
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"

    d = cam.data
    d.type = "PERSP"
    d.sensor_fit = "HORIZONTAL"
    d.sensor_width = SENSOR_WIDTH
    d.lens = lens
    d.clip_start = CLIP_START
    d.clip_end = CLIP_END
    d.dof.use_dof = True
    d.dof.aperture_fstop = fstop
    d.dof.aperture_blades = 6
    if target:
        d.dof.focus_object = target
    else:
        d.dof.focus_object = aim
    d.show_passepartout = True
    d.passepartout_alpha = 0.7

    sc.camera = cam
    return root, aim


def setup_eevee_realism(sc: bpy.types.Scene):
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = "METERS"
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.fps = 24
    ee = sc.eevee
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = True
    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = 64
    # Blender 5.1 EEVEE DOF quality — jitter when available
    if hasattr(ee, "use_bokeh_jittered"):
        ee.use_bokeh_jittered = True
    # Some builds expose dof via eevee.bokeh_* 
    for attr, val in (
        ("bokeh_max_size", 100.0),
        ("bokeh_threshold", 1.0),
        ("bokeh_neighbor_max", 10.0),
        ("bokeh_overblur", 0.05),
    ):
        if hasattr(ee, attr):
            setattr(ee, attr, val)


def face_overlays_to_camera(sc: bpy.types.Scene):
    """Make text/chart labels camera-facing and readable at human scale."""
    cam = sc.camera
    if not cam:
        return []
    fixed = []
    for ob in sc.objects:
        if ob.type != "FONT":
            continue
        # Clear bad parents; Track To camera
        for c in list(ob.constraints):
            if c.type == "TRACK_TO":
                ob.constraints.remove(c)
        tr = ob.constraints.new("TRACK_TO")
        tr.target = cam
        tr.track_axis = "TRACK_Z"
        tr.up_axis = "UP_Y"
        # Size: Blender text size in meters — readable ~0.15–0.35 m letter height
        if ob.data.size < 0.08:
            ob.data.size = 0.18
        if ob.data.size > 1.2:
            ob.data.size = 0.35
        # Extrude slight for presence
        ob.data.extrude = 0.008
        fixed.append(ob.name)
    return fixed


def light_chart_scene(sc: bpy.types.Scene):
    """S05 was rendering black — ensure key + fill lights exist."""
    if sc.name != "05_Beat2_Money":
        return
    key = sc.objects.get("Chart_KeyLight")
    if key is None:
        light_data = bpy.data.lights.new("Chart_KeyLight_data", "AREA")
        light_data.energy = 250.0
        light_data.size = 4.0
        key = bpy.data.objects.new("Chart_KeyLight", light_data)
        sc.collection.objects.link(key)
    key.location = (2.0, -6.0, 4.0)
    key.rotation_euler = (math.radians(50), 0, math.radians(20))
    fill = sc.objects.get("Chart_FillLight")
    if fill is None:
        ld = bpy.data.lights.new("Chart_FillLight_data", "AREA")
        ld.energy = 80.0
        ld.size = 6.0
        fill = bpy.data.objects.new("Chart_FillLight", ld)
        sc.collection.objects.link(fill)
    fill.location = (-3.0, -5.0, 3.0)
    # Soft world strength bump if background exists
    if sc.world and sc.world.use_nodes:
        for n in sc.world.node_tree.nodes:
            if n.type == "BACKGROUND":
                n.inputs["Strength"].default_value = max(0.35, n.inputs["Strength"].default_value)


def run():
    report = []
    for sname, (lens, eye_z, fstop, elevate) in SCENE_CAM.items():
        sc = bpy.data.scenes.get(sname)
        if not sc:
            report.append({"scene": sname, "status": "missing"})
            continue
        bpy.context.window.scene = sc
        setup_eevee_realism(sc)

        ball = next((o for o in sc.objects if "Sasa_Ball" in o.name), None)
        cam = sc.camera
        if not cam:
            report.append({"scene": sname, "status": "no_camera"})
            continue

        # Hero ball anthropometrics (prop size); YB body prepared but hidden
        if ball:
            # Keep symbolic hero prop size (not head) for non-body scenes
            set_ball_diameter(ball, HERO_BALL_DIAM)
            # Place ball near eye-line in front of camera subject area
            ball.location.z = max(eye_z - 0.15, HERO_BALL_DIAM * 0.5 + 0.3)
            make_yb_body(sc, ball)
            # After YB creation ball may be head-sized if parented — restore hero prop for plate scenes
            if ball.parent and ball.parent.get("yb_body"):
                # Unparent for plate hero mode; keep YB asset available
                mw = ball.matrix_world.copy()
                ball.parent = None
                ball.matrix_world = mw
                set_ball_diameter(ball, HERO_BALL_DIAM)
                ball.location.z = max(eye_z - 0.1, 0.9)

        root, aim = build_camera_rig(sc, cam, ball, lens, eye_z, fstop, elevate)
        overlays = face_overlays_to_camera(sc)
        light_chart_scene(sc)

        report.append({
            "scene": sname,
            "status": "ok",
            "lens_mm": lens,
            "eye_z_m": eye_z,
            "elevate": elevate,
            "fstop": fstop,
            "rig": root.name,
            "aim": aim.name,
            "ball_diam_m": HERO_BALL_DIAM if ball else None,
            "overlays_tracked": overlays,
            "cam_world_z": round(root.location.z, 3),
        })

    bpy.ops.wm.save_mainfile()
    return {"saved": bpy.data.filepath, "scenes": report}


if __name__ == "__main__":
    print(run())
