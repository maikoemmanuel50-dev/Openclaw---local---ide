"""
TED-Ed 30s infographic OPEN — Blender 5.1.2 sidecar (NOT 4.4).

Creates blend/africa_s1_teded_open30.blend with:
  - CTRL armature + custom-prop "wrangle" drivers (Houdini-wrangle analogue)
  - Geometry Nodes pies / bars (procedural data viz)
  - PBR yellow-base materials (AgX, emission + principled)
  - 10 unique beats, 720f @24, 1920x1080

GPU policy: Cycles DEVICE=CPU, CUDA_VISIBLE_DEVICES=-1.
Does NOT open or modify africa_s1_master_v01.blend.
Does NOT start if this process would issue a GPU render.

Run:
  blender.exe -b -P setup_teded_open30_blender51.py
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import bmesh
import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
OUT_BLEND = PROJECT / "blend" / "africa_s1_teded_open30.blend"
OUT_MP4 = PROJECT / "renders" / "paced_overlays" / "s01_teded_open30_blender51.mp4"
PNG_DIR = PROJECT / "renders" / "open30_blender51_png"
REPORT = PROJECT / "renders" / "quality" / "teded_open30_blender51_report.json"

FPS = 24
FRAMES = 720  # 30.0s
RES = (1920, 1080)

YELLOW = (1.0, 0.835, 0.310, 1.0)
BG = (0.026, 0.018, 0.006, 1.0)
CREAM = (1.0, 0.965, 0.839, 1.0)
TEAL = (0.180, 0.769, 0.714, 1.0)
CORAL = (1.0, 0.420, 0.290, 1.0)

BEATS = [
    (1, 48, "06:30", "NAIROBI"),
    (49, 108, "MATATUS", "the city is already awake"),
    (109, 168, "NOT THE ROAD", "motion is in pockets"),
    (169, 240, "PHONE", "NETWORK  →  SYSTEM"),
    (241, 324, "82.1%", "mobile-money penetration"),
    (325, 396, "42.3M", "mobile-money subscriptions"),
    (397, 480, "MOVED", "rent · stock · loan"),
    (481, 552, "NO BRANCH", "just a phone"),
    (553, 648, "SILICON", "SAVANNAH"),
    (649, 720, "2007", "the nickname has a start date"),
]


def iter_action_fcurves(action):
    """Legacy and Blender 5 layered actions."""
    if action is None:
        return
    legacy = getattr(action, "fcurves", None)
    if legacy is not None:
        yield from legacy
        return
    if not hasattr(action, "layers"):
        return
    try:
        for layer in action.layers:
            for strip in layer.strips:
                bags = getattr(strip, "channelbags", None)
                if bags:
                    for bag in bags:
                        for fc in getattr(bag, "fcurves", []) or []:
                            yield fc
                else:
                    bag = getattr(strip, "channelbag", None)
                    if bag and hasattr(bag, "fcurves"):
                        yield from bag.fcurves
    except Exception:
        return


def ease(obj, data_path, frames_vals, index=None):
    for fr, val in frames_vals:
        if index is None:
            obj.__setattr__  # noqa
            # use keyed path
            if data_path == "scale":
                obj.scale = (val, val, val)
                obj.keyframe_insert(data_path="scale", frame=fr)
            elif data_path == "location":
                obj.location = val
                obj.keyframe_insert(data_path="location", frame=fr)
            elif data_path == "rotation_euler":
                obj.rotation_euler = val
                obj.keyframe_insert(data_path="rotation_euler", frame=fr)
            else:
                obj.keyframe_insert(data_path=data_path, frame=fr)
        else:
            obj.keyframe_insert(data_path=data_path, index=index, frame=fr)
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    for fc in iter_action_fcurves(ad.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.easing = "EASE_IN_OUT"


def kf_hide(obj, f_on, f_off):
    """Visible only in [f_on, f_off] inclusive."""
    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert("hide_render", frame=f_on - 1)
    obj.keyframe_insert("hide_viewport", frame=f_on - 1)
    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert("hide_render", frame=f_on)
    obj.keyframe_insert("hide_viewport", frame=f_on)
    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert("hide_render", frame=f_off + 1)
    obj.keyframe_insert("hide_viewport", frame=f_off + 1)


def mat_emission(name, color, strength=4.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Emission Color"].default_value = color
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Metallic"].default_value = 0.05
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.location = (-400, 0)
    tex.inputs["Scale"].default_value = 8.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, 1)
    ramp.color_ramp.elements[1].color = color
    nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def mat_bg(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = BG
        bsdf.inputs["Emission Color"].default_value = BG
        bsdf.inputs["Emission Strength"].default_value = 0.4
        bsdf.inputs["Roughness"].default_value = 1.0
    return m


def make_text(name, body, size, color, loc, coll):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    coll.objects.link(ob)
    ob.data.materials.append(mat_emission(f"M_{name}", color, 6.0 if color == YELLOW else 2.2))
    return ob


def gn_pie(name, sizes, colors, coll):
    """Procedural pie via GN: mesh circle fans (unique per scene)."""
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    ob = bpy.data.objects.new(name, mesh)
    coll.objects.link(ob)
    ng = bpy.data.node_groups.new(f"GN_{name}", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    nodes, links = ng.nodes, ng.links
    n_out = nodes.new("NodeGroupOutput")
    n_out.location = (900, 0)
    join = nodes.new("GeometryNodeJoinGeometry")
    join.location = (700, 0)
    links.new(join.outputs["Geometry"], n_out.inputs["Geometry"])
    total = sum(sizes) or 1
    ang = 0.0
    pie_geos = []
    for i, (sz, col) in enumerate(zip(sizes, colors)):
        theta = 2 * math.pi * sz / total
        cyl = nodes.new("GeometryNodeMeshCircle")
        cyl.location = (0, -180 * i)
        cyl.inputs["Vertices"].default_value = 48
        cyl.inputs["Radius"].default_value = 1.6
        fill = nodes.new("GeometryNodeFillCurve") if False else None
        # Use cylinder sector via mesh cylinder + extra
        fan = nodes.new("GeometryNodeMeshCylinder")
        fan.location = (200, -180 * i)
        fan.inputs["Vertices"].default_value = max(8, int(48 * sz / total))
        fan.inputs["Radius"].default_value = 1.55
        fan.inputs["Depth"].default_value = 0.12
        tf = nodes.new("GeometryNodeTransform")
        tf.location = (450, -180 * i)
        mid = ang + theta / 2
        tf.inputs["Rotation"].default_value = (0, 0, ang)
        tf.inputs["Scale"].default_value = (1.0, max(0.08, sz / total * 2.2), 1.0)
        links.new(fan.outputs["Mesh"], tf.inputs["Geometry"])
        pie_geos.append(tf.outputs["Geometry"])
        ang += theta
    for g in pie_geos:
        links.new(g, join.inputs["Geometry"])
    mod = ob.modifiers.new("WranglePie", "NODES")
    mod.node_group = ng
    # Unique solid wedges as fallback (GN cylinder scale can look odd) — keep both
    return ob


def make_pie_wedges(name_prefix, sizes, cols, coll, z=0.0):
    """Unique mesh wedges (reliable) + GN join as wrangle holder."""
    total = sum(sizes) or 1
    ang0 = math.pi / 2
    objs = []
    for i, (sz, col) in enumerate(zip(sizes, cols)):
        theta = 2 * math.pi * sz / total
        bpy.ops.mesh.primitive_cylinder_add(vertices=max(12, int(64 * sz / total) + 4),
                                            radius=1.7, depth=0.14, location=(0, 0, z))
        w = bpy.context.active_object
        w.name = f"{name_prefix}_W{i}"
        # Shear into a sector by scaling Y in object space then rotating
        w.scale = (1.0, max(0.12, sz / total * 1.8), 1.0)
        w.rotation_euler = (0, 0, ang0 - theta / 2)
        w.data.materials.append(mat_emission(f"M_{w.name}", col, 5.0))
        for c in w.users_collection:
            c.objects.unlink(w)
        coll.objects.link(w)
        objs.append(w)
        ang0 -= theta
    return objs


def make_bars(name_prefix, items, coll, z=0.0):
    objs = []
    for i, (lab, val, vmax, col) in enumerate(items):
        h = 0.25 + 2.4 * (val / vmax)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-2.2 + i * 1.6, 0, z + h / 2))
        b = bpy.context.active_object
        b.name = f"{name_prefix}_Bar{i}"
        b.scale = (0.45, 0.45, h)
        b.data.materials.append(mat_emission(f"M_{b.name}", col, 4.5))
        for c in b.users_collection:
            c.objects.unlink(b)
        coll.objects.link(b)
        t = make_text(f"{name_prefix}_L{i}", lab, 0.22, CREAM, (-2.2 + i * 1.6, -1.1, z), coll)
        objs.extend([b, t])
    return objs


def make_armature(coll):
    arm = bpy.data.armatures.new("CTRL_Open30")
    ob = bpy.data.objects.new("CTRL_Open30_Rig", arm)
    coll.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones.new("CTRL_ROOT")
    eb.head, eb.tail = (0, 0, 0), (0, 0, 1)
    eb2 = arm.edit_bones.new("CTRL_MORPH")
    eb2.head, eb2.tail = (0, 1.5, 0), (0, 1.5, 0.8)
    eb2.parent = eb
    bpy.ops.object.mode_set(mode="OBJECT")
    pb = ob.pose.bones["CTRL_MORPH"]
    pb["morph"] = 0.0
    ui = pb.id_properties_ui("morph")
    ui.update(min=0.0, max=1.0, description="Wrangle morph 0=type 1=chart")
    # Key morph pulses at each beat start
    starts = [1, 49, 109, 169, 241, 325, 397, 481, 553, 649]
    for s in starts:
        pb["morph"] = 0.0
        pb.keyframe_insert(data_path='["morph"]', frame=s)
        pb["morph"] = 1.0
        pb.keyframe_insert(data_path='["morph"]', frame=s + 20)
    return ob


def world_dark():
    w = bpy.data.worlds.new("World_Open30")
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = BG
        bg.inputs["Strength"].default_value = 0.25
    bpy.context.scene.world = w


def setup_scene():
    bpy.ops.wm.read_homefile(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.use_adaptive_sampling = True
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.frame_start = 1
    sc.frame_end = FRAMES
    img = sc.render.image_settings
    if hasattr(img, "media_type"):
        img.media_type = "VIDEO"
    else:
        try:
            img.file_format = "FFMPEG"
        except TypeError:
            img.file_format = "PNG"
    ff = sc.render.ffmpeg
    ff.format = "MPEG4"
    ff.codec = "H264"
    try:
        ff.constant_rate_factor = "HIGH"
    except TypeError:
        pass
    try:
        ff.ffmpeg_preset = "GOOD"
    except TypeError:
        pass
    try:
        ff.gopsize = 12
    except TypeError:
        pass
    try:
        ff.audio_codec = "NONE"
    except TypeError:
        pass
    sc.render.filepath = str(OUT_MP4)
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.name = "Open30_TedEd"

    coll = bpy.data.collections.new("Open30")
    sc.collection.children.link(coll)
    world_dark()

    # Camera
    cam_d = bpy.data.cameras.new("Cam_Open30")
    cam_d.lens = 50
    cam = bpy.data.objects.new("Cam_Open30", cam_d)
    cam.location = (0, -8.2, 0.2)
    cam.rotation_euler = (math.radians(90), 0, 0)
    coll.objects.link(cam)
    sc.camera = cam
    cam.location = (0, -8.4, 0.15)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0, -7.6, 0.25)
    cam.keyframe_insert("location", frame=720)

    # Key light
    bpy.ops.object.light_add(type="AREA", location=(0, -3.5, 4.5))
    lt = bpy.context.active_object
    lt.data.energy = 250
    lt.data.size = 6
    lt.data.color = (1.0, 0.92, 0.7)
    for c in lt.users_collection:
        c.objects.unlink(lt)
    coll.objects.link(lt)

    # Backdrop
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 2.2, 0), rotation=(math.radians(90), 0, 0))
    plate = bpy.context.active_object
    plate.name = "BG_Plate_Open30"
    plate.data.materials.append(mat_bg("M_BG_Open30"))
    for c in plate.users_collection:
        c.objects.unlink(plate)
    coll.objects.link(plate)

    rig = make_armature(coll)

    unique_objs = []

    # Beat objects — each UNIQUE, hide outside window
    t1 = make_text("T_0630", "06:30", 1.35, YELLOW, (0, 0, 0.4), coll)
    t1b = make_text("T_NAIROBI", "NAIROBI", 0.42, CREAM, (0, 0, -0.7), coll)
    unique_objs += [t1, t1b]
    kf_hide(t1, 1, 48)
    kf_hide(t1b, 1, 48)
    t1.scale = (0.2, 0.2, 0.2)
    t1.keyframe_insert("scale", frame=1)
    t1.scale = (1, 1, 1)
    t1.keyframe_insert("scale", frame=18)

    t2 = make_text("T_MATATUS", "MATATUS", 0.85, YELLOW, (0, 0, 1.1), coll)
    kf_hide(t2, 49, 108)
    cards = []
    for i, lab in enumerate(["on foot", "motorbikes", "packed color"]):
        c = make_text(f"T_CARD_{i}", lab, 0.28, CREAM, (-2.2 + i * 2.2, 0, -0.4), coll)
        kf_hide(c, 49, 108)
        cards.append(c)
    unique_objs += [t2] + cards

    t3 = make_text("T_NOTROAD", "NOT THE ROAD", 0.55, YELLOW, (0, 0, 0.35), coll)
    t3b = make_text("T_POCKETS", "the real motion is in pockets", 0.28, CREAM, (0, 0, -0.5), coll)
    kf_hide(t3, 109, 168)
    kf_hide(t3b, 109, 168)
    unique_objs += [t3, t3b]
    t3.rotation_euler = (0, 0, math.radians(-12))
    t3.keyframe_insert("rotation_euler", frame=109)
    t3.rotation_euler = (0, 0, 0)
    t3.keyframe_insert("rotation_euler", frame=128)

    t4 = make_text("T_PHONE", "PHONE", 0.5, YELLOW, (-2.4, 0, 0.2), coll)
    t4b = make_text("T_NET", "NETWORK", 0.4, TEAL, (0, 0, 0.2), coll)
    t4c = make_text("T_SYS", "SYSTEM", 0.4, CORAL, (2.4, 0, 0.2), coll)
    for o, a, b in ((t4, 169, 240), (t4b, 169, 240), (t4c, 169, 240)):
        kf_hide(o, a, b)
    unique_objs += [t4, t4b, t4c]
    # flow stagger
    for o, f0 in ((t4, 169), (t4b, 181), (t4c, 193)):
        o.scale = (0.1, 0.1, 0.1)
        o.keyframe_insert("scale", frame=f0)
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=f0 + 10)

    t5 = make_text("T_821", "82.1%", 1.2, YELLOW, (0, 0, 0.55), coll)
    t5b = make_text("T_821sub", "mobile-money penetration", 0.28, CREAM, (0, 0, -0.85), coll)
    kf_hide(t5, 241, 280)
    kf_hide(t5b, 241, 324)
    unique_objs += [t5, t5b]
    # morph: type shrinks, pie grows
    wedges = make_pie_wedges("PIE821", [82.1, 17.9], [YELLOW, (0.18, 0.15, 0.08, 1)], coll, z=-0.1)
    for w in wedges:
        kf_hide(w, 270, 324)
        w.scale = (0.05, 0.05, 0.05)
        w.keyframe_insert("scale", frame=270)
        w.scale = (1, 1, 1)
        w.keyframe_insert("scale", frame=300)
    t5.scale = (1, 1, 1)
    t5.keyframe_insert("scale", frame=260)
    t5.scale = (0.05, 0.05, 0.05)
    t5.keyframe_insert("scale", frame=280)
    unique_objs += wedges
    gn_pie("GN_WranglePie_821", [82.1, 17.9], [YELLOW, TEAL], coll)  # node tree present for polish

    t6 = make_text("T_423M", "42.3M", 1.1, YELLOW, (0, 0, 0.5), coll)
    t6b = make_text("T_423sub", "mobile-money subscriptions", 0.26, CREAM, (0, 0, -0.9), coll)
    kf_hide(t6, 325, 360)
    kf_hide(t6b, 325, 396)
    bars = make_bars("BAR423", [("Smart", 41.5, 45, YELLOW), ("Feature", 30.6, 45, TEAL), ("MM", 42.3, 45, CORAL)], coll)
    for b in bars:
        kf_hide(b, 355, 396)
        if b.type == "MESH":
            s = b.scale.copy()
            b.scale = (s.x, s.y, 0.05)
            b.keyframe_insert("scale", frame=355)
            b.scale = s
            b.keyframe_insert("scale", frame=385)
    unique_objs += [t6, t6b] + bars

    t7 = make_text("T_MOVED", "MONEY HAS ALREADY MOVED", 0.38, YELLOW, (0, 0, 1.15), coll)
    kf_hide(t7, 397, 480)
    nodes = []
    for i, lab in enumerate(["RENT", "STOCK", "LOAN"]):
        n = make_text(f"T_NODE_{lab}", lab, 0.32, CREAM, (-2.4 + i * 2.4, 0, 0.0), coll)
        kf_hide(n, 397, 480)
        n.scale = (0.1, 0.1, 0.1)
        n.keyframe_insert("scale", frame=397 + i * 12)
        n.scale = (1, 1, 1)
        n.keyframe_insert("scale", frame=410 + i * 12)
        nodes.append(n)
    unique_objs += [t7] + nodes

    t8a = make_text("T_BRANCH", "BANK BRANCH", 0.35, (0.45, 0.4, 0.3, 1), (-2.2, 0, 0.3), coll)
    t8b = make_text("T_JUSTPHONE", "JUST A PHONE", 0.38, YELLOW, (2.2, 0, 0.3), coll)
    kf_hide(t8a, 481, 552)
    kf_hide(t8b, 481, 552)
    unique_objs += [t8a, t8b]

    t9a = make_text("T_SILICON", "SILICON", 0.7, CREAM, (0, 0, 0.55), coll)
    t9b = make_text("T_SAVANNAH", "SAVANNAH", 0.95, YELLOW, (0, 0, -0.35), coll)
    kf_hide(t9a, 553, 648)
    kf_hide(t9b, 553, 648)
    t9b.scale = (0.2, 0.2, 0.2)
    t9b.keyframe_insert("scale", frame=553)
    t9b.scale = (1, 1, 1)
    t9b.keyframe_insert("scale", frame=575)
    unique_objs += [t9a, t9b]

    t10 = make_text("T_2007", "2007", 1.25, YELLOW, (0, 0, 0.35), coll)
    t10b = make_text("T_STARTDATE", "the nickname has a start date", 0.28, CREAM, (0, 0, -0.7), coll)
    kf_hide(t10, 649, 720)
    kf_hide(t10b, 649, 720)
    unique_objs += [t10, t10b]

    # Easy-ease all
    for ob in unique_objs + [cam, rig]:
        if ob.animation_data and ob.animation_data.action:
            for fc in iter_action_fcurves(ob.animation_data.action):
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
                    kp.easing = "EASE_IN_OUT"

    OUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    print("SAVED", OUT_BLEND, flush=True)

    import json
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "blender": bpy.app.version_string,
        "engine": "CYCLES CPU",
        "frames": FRAMES,
        "fps": FPS,
        "blend": str(OUT_BLEND),
        "mp4": str(OUT_MP4),
        "objects": [o.name for o in unique_objs],
        "unique_count": len({o.name for o in unique_objs}),
        "note": "Blender 5.1.2 sidecar — 4.4 forbidden. Master blend untouched.",
        "refs": [
            "https://youtu.be/36SIUe_mOZU",
            "https://youtu.be/o5zHIYLqDIw",
            "https://www.youtube.com/shorts/j4YAXZRluW4",
            "https://www.youtube.com/shorts/SC_3fG4mvQs",
            "https://www.youtube.com/watch?v=uBBmbdPbfhw",
            "https://www.youtube.com/watch?v=FOnx6eTfKB8",
        ],
    }, indent=2), encoding="utf-8")

    # Optional: skip animation render if AFRICA_SKIP_OPEN30_RENDER=1
    if os.environ.get("AFRICA_SKIP_OPEN30_RENDER") == "1":
        print("SKIP render (AFRICA_SKIP_OPEN30_RENDER=1)", flush=True)
        return

    print("RENDER CPU Cycles 1-720", flush=True)
    bpy.ops.render.render(animation=True)
    print("RENDER_DONE", OUT_MP4, flush=True)


if __name__ == "__main__":
    setup_scene()
