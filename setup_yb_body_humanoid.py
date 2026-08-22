"""
YB-Body v2 — Fern-style faceless humanoid with true anthropometrics + armature.

Replaces the 8-vert cube placeholder with:
- ISO 7250 / Roy Mech 50th-percentile adult ratios scaled to 1.70 m stature
- Smooth mannequin mesh (shoulders, chest taper, waist, hips, arms, legs)
- Spine + clavicle + limb armature (Rigify bone-placement rules, no Rigify req)
- Auto weights + Subdivision Surface
- Idle breath / sway / walk-bob keyed per scene morph windows

Refs:
- ISO 7250-1 basic body measurements
- Blender Manual Rigify bone positioning (spine offset back, slight limb bend)
- Fern / Imperial faceless mannequin rule (no faces; ball = head)
- Tutorial pack: docs/BLENDER_RIG_ANIM_RESOURCES.md
  (auto-weights, Pose Mode keys, Apply Transforms, Graph Editor ease,
   Rigify enable, blocking→spline — CG Geek / Ryan King / Crashsune / shorts)

Optional upgrade: append Blender Studio Human Base Meshes (CC0) if present under
assets/humanoid/ — see docs/yb_body_humanoid.md

Run in Blender (MCP or CLI):
  blender -b blend/africa_s1_master_v01.blend -P setup_yb_body_humanoid.py
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import bpy
from mathutils import Vector, Euler, Matrix

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
HUMAN_DIR = PROJECT / "assets" / "humanoid"
BALL_HEX = (1.0, 0.835, 0.310, 1.0)  # #FFD54F
CHARCOAL = (0.149, 0.125, 0.098, 1.0)


def enable_rigify() -> bool:
    try:
        import addon_utils

        addon_utils.enable("rigify", default_set=True, persistent=True)
        return True
    except Exception:
        return False


# ── Anthropometrics @ 1.70 m stature (scaled from ~1.745 m 50th male) ──
STATURE = 1.70
SCALE = STATURE / 1.745
# Heights from floor (m)
Z_SHOULDER = 1.445 * SCALE   # ~1.408
Z_ELBOW = 1.100 * SCALE      # ~1.071
Z_HIP = 0.935 * SCALE        # ~0.911
Z_KNEE = 0.490 * SCALE       # approx
Z_NECK = 1.480 * SCALE       # cervicale-ish
Z_HEAD_CTR = 1.560 * SCALE   # head center for ball
# Breadths / depths (m)
BIACROMIAL = 0.405 * SCALE   # ~0.394 shoulder bone width
BIDELTOID = 0.485 * SCALE    # ~0.472 overall shoulder
CHEST_BREADTH = 0.320 * SCALE
WAIST_BREADTH = 0.280 * SCALE
HIP_BREADTH = 0.390 * SCALE
CHEST_DEPTH = 0.245 * SCALE
WAIST_DEPTH = 0.220 * SCALE
HIP_DEPTH = 0.240 * SCALE
HEAD_DIAM = 0.24
UPPER_ARM_LEN = (Z_SHOULDER - Z_ELBOW)
FOREARM_LEN = 0.26 * SCALE
THIGH_LEN = Z_HIP - Z_KNEE
SHIN_LEN = Z_KNEE - 0.08

# Scenes that show humanity (YB morph markers)
HUMANITY_SCENES = {
    "01_ColdOpen": "crowd",       # morph to crowd
    "03_Beat1_Hubs": "builder",   # ball-head at desk
    "08_Beat3_SecondaryCity": "founder_dim",
    "09_Closer": "crowd",
}


def ensure_mat(name: str, color, rough=0.88):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = rough
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.15
    return mat


def link_obj(obj, sc):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    sc.collection.objects.link(obj)


def delete_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


def find_ball(sc):
    for o in sc.objects:
        if o.type == "MESH" and "Ball" in o.name and "YB_Body" not in o.name and "YB_Head" not in o.name:
            return o
    return None


def find_old_bodies(sc):
    return [o for o in list(sc.objects) if o.get("yb_body") or (
        o.type == "MESH" and o.name.startswith("YB_Body_")
    )]


def build_mannequin_mesh(name: str) -> bpy.types.Object:
    """
    Procedural Fern mannequin — stacked tapered capsules / ellipsoids joined.
    True human silhouette: shoulders wider than hips, waist inset, arms hang,
    legs for standing mass. Faceless: head is separate yellow ball.
    """
    import bmesh

    # Build from metaballs then convert — smooth organic Fern look
    mb_data = bpy.data.metaballs.new(name + "_MB")
    mb_data.resolution = 0.08
    mb_data.render_resolution = 0.05
    mb_obj = bpy.data.objects.new(name + "_MB_OBJ", mb_data)
    bpy.context.scene.collection.objects.link(mb_obj)

    def add_el(loc, radius, stiff=2.0, typ="ELLIPSOID", size=(1, 1, 1)):
        el = mb_data.elements.new(type=typ)
        el.co = loc
        el.radius = radius
        el.stiffness = stiff
        if typ == "ELLIPSOID":
            el.size_x, el.size_y, el.size_z = size
        return el

    # Pelvis / hips
    add_el((0, 0, Z_HIP), 0.12, size=(HIP_BREADTH * 0.55, HIP_DEPTH * 0.55, 0.12))
    # Waist
    add_el((0, 0.01, (Z_HIP + Z_SHOULDER) * 0.42), 0.09, size=(WAIST_BREADTH * 0.5, WAIST_DEPTH * 0.5, 0.10))
    # Chest / ribcage
    add_el((0, 0.02, (Z_HIP + Z_SHOULDER) * 0.72), 0.11, size=(CHEST_BREADTH * 0.55, CHEST_DEPTH * 0.55, 0.14))
    # Shoulders / deltoids
    add_el((0, 0.01, Z_SHOULDER - 0.02), 0.10, size=(BIDELTOID * 0.52, CHEST_DEPTH * 0.42, 0.08))
    # Neck stump (faceless — ball sits on top)
    add_el((0, 0.01, Z_NECK), 0.045, size=(0.055, 0.055, 0.06))

    # Upper arms (slight forward bend for IK friendliness)
    for side, sx in (("L", 1), ("R", -1)):
        sx = 1 if side == "L" else -1
        sh_x = BIDELTOID * 0.42 * sx
        add_el((sh_x, 0.02, Z_SHOULDER - 0.02), 0.055, size=(0.06, 0.06, 0.05))  # deltoid
        # upper arm mid
        add_el((sh_x * 1.05, 0.04, (Z_SHOULDER + Z_ELBOW) * 0.5), 0.045, size=(0.045, 0.05, UPPER_ARM_LEN * 0.45))
        # elbow / forearm start
        add_el((sh_x * 1.08, 0.06, Z_ELBOW), 0.038, size=(0.04, 0.045, 0.08))
        # forearm
        add_el((sh_x * 1.1, 0.08, Z_ELBOW - FOREARM_LEN * 0.45), 0.035, size=(0.035, 0.04, FOREARM_LEN * 0.4))

    # Thighs + shins (standing mass)
    for sx in (1, -1):
        hx = HIP_BREADTH * 0.22 * sx
        add_el((hx, 0.01, (Z_HIP + Z_KNEE) * 0.55), 0.07, size=(0.08, 0.09, THIGH_LEN * 0.4))
        add_el((hx, 0.02, Z_KNEE), 0.05, size=(0.055, 0.06, 0.05))
        add_el((hx, 0.03, Z_KNEE * 0.5), 0.045, size=(0.05, 0.055, SHIN_LEN * 0.4))
        # foot stub
        add_el((hx, 0.08, 0.04), 0.04, size=(0.05, 0.12, 0.035))

    # Force metaball polygonization
    bpy.context.view_layer.objects.active = mb_obj
    mb_obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    body = bpy.context.active_object
    body.name = name

    # Clean mesh
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.002)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Shade smooth + SubD
    for p in body.data.polygons:
        p.use_smooth = True
    if not any(m.type == "SUBSURF" for m in body.modifiers):
        subd = body.modifiers.new("YB_SubD", "SUBSURF")
        subd.levels = 1
        subd.render_levels = 2

    mat = ensure_mat("SoftPop_YB_Body", CHARCOAL, 0.9)
    body.data.materials.clear()
    body.data.materials.append(mat)
    body["yb_body"] = 1
    body["yb_body_v"] = 2
    body["anthropometric_height_m"] = STATURE
    body["biacromial_m"] = BIACROMIAL
    body["bideltoid_m"] = BIDELTOID
    return body


def build_armature(name: str) -> bpy.types.Object:
    """Minimal humanoid armature following Rigify torso placement rules."""
    arm_data = bpy.data.armatures.new(name + "_Data")
    arm_data.display_type = "OCTAHEDRAL"
    arm = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    def bone(bname, head, tail, parent=None, connect=False, deform=True):
        b = eb.new(bname)
        b.head = Vector(head)
        b.tail = Vector(tail)
        if parent:
            b.parent = eb[parent]
            b.use_connect = connect
        b.use_deform = deform
        return b

    # Root at pelvis floor projection
    bone("root", (0, 0, 0), (0, 0, 0.1), deform=False)
    # Hips (rigid) — slight back offset for spine
    bone("hips", (0, -0.02, Z_HIP - 0.05), (0, -0.02, Z_HIP + 0.05), parent="root")
    # Spine flexible zone
    bone("spine", (0, -0.03, Z_HIP + 0.05), (0, -0.02, (Z_HIP + Z_SHOULDER) * 0.55), parent="hips", connect=True)
    # Chest rigid
    bone("chest", (0, -0.02, (Z_HIP + Z_SHOULDER) * 0.55), (0, -0.01, Z_SHOULDER - 0.04), parent="spine", connect=True)
    # Neck
    bone("neck", (0, -0.01, Z_SHOULDER - 0.04), (0, 0.0, Z_NECK + 0.02), parent="chest", connect=True)
    # Head (non-deform — ball parented separately)
    bone("head", (0, 0.0, Z_NECK + 0.02), (0, 0.02, Z_HEAD_CTR + HEAD_DIAM * 0.35), parent="neck", connect=True, deform=False)

    for side, sx in (("L", 1.0), ("R", -1.0)):
        sh = BIDELTOID * 0.40 * sx
        bone(f"shoulder.{side}", (0, -0.01, Z_SHOULDER - 0.02), (sh, 0.01, Z_SHOULDER - 0.01), parent="chest")
        # Upper arm with slight forward bend (Y+) for IK pole
        bone(f"upper_arm.{side}", (sh, 0.01, Z_SHOULDER - 0.01), (sh * 1.05, 0.05, Z_ELBOW), parent=f"shoulder.{side}", connect=True)
        bone(f"forearm.{side}", (sh * 1.05, 0.05, Z_ELBOW), (sh * 1.1, 0.1, Z_ELBOW - FOREARM_LEN), parent=f"upper_arm.{side}", connect=True)
        bone(f"hand.{side}", (sh * 1.1, 0.1, Z_ELBOW - FOREARM_LEN), (sh * 1.12, 0.14, Z_ELBOW - FOREARM_LEN - 0.08), parent=f"forearm.{side}", connect=True)

        hx = HIP_BREADTH * 0.22 * sx
        # Thigh with slight forward knee bend
        bone(f"thigh.{side}", (hx, -0.01, Z_HIP), (hx, 0.03, Z_KNEE), parent="hips")
        bone(f"shin.{side}", (hx, 0.03, Z_KNEE), (hx, 0.04, 0.08), parent=f"thigh.{side}", connect=True)
        bone(f"foot.{side}", (hx, 0.04, 0.08), (hx, 0.16, 0.02), parent=f"shin.{side}", connect=True)

    bpy.ops.object.mode_set(mode="OBJECT")
    arm.show_in_front = True
    return arm


def bind_mesh(body, arm):
    # Apply Rot/Scale before Automatic Weights (60s rig shorts / Rigify guides)
    body.parent = None
    for m in list(body.modifiers):
        if m.type == "ARMATURE":
            body.modifiers.remove(m)
    try:
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    except Exception as e:
        print(f"  apply_transforms body skip: {e}")
    body.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    # Keep SubD after Armature
    if not any(m.type == "SUBSURF" for m in body.modifiers):
        subd = body.modifiers.new("YB_SubD", "SUBSURF")
        subd.levels = 1
        subd.render_levels = 2
    # Ensure armature modifier is first
    arm_mod = next((m for m in body.modifiers if m.type == "ARMATURE"), None)
    if arm_mod:
        guard = 0
        while body.modifiers[0] != arm_mod and guard < 12:
            try:
                bpy.context.view_layer.objects.active = body
                bpy.ops.object.modifier_move_up(modifier=arm_mod.name)
            except Exception:
                break
            guard += 1


def place_head_ball(sc, ball, arm):
    """Yellow ball as faceless head — parent to head bone."""
    if not ball:
        # create head ball
        bpy.ops.mesh.primitive_uv_sphere_add(radius=HEAD_DIAM * 0.5, location=(0, 0, Z_HEAD_CTR))
        ball = bpy.context.active_object
        ball.name = f"YB_Head_{sc.name[:8]}"
        link_obj(ball, sc)
        mat = ensure_mat("SoftPop_YB_Head", BALL_HEX, 0.35)
        ball.data.materials.clear()
        ball.data.materials.append(mat)
        for p in ball.data.polygons:
            p.use_smooth = True

    # Scale existing hero ball or dedicated head
    # Use a dedicated head duplicate so hero graphic ball can stay independent when needed
    head_name = f"YB_Head_{sc.name[:8]}"
    head = sc.objects.get(head_name)
    if head is None:
        head = ball.copy()
        head.data = ball.data.copy()
        head.name = head_name
        link_obj(head, sc)

    # Diameter
    head.scale = (1, 1, 1)
    bpy.context.view_layer.update()
    cur = max(head.dimensions) or 1.0
    s = HEAD_DIAM / cur
    head.scale = (s, s, s)
    head.location = (0, 0.02, Z_HEAD_CTR)
    mat = ensure_mat("SoftPop_YB_Head", BALL_HEX, 0.35)
    if head.data.materials:
        head.data.materials[0] = mat
    else:
        head.data.materials.append(mat)

    # Parent to armature head bone
    head.parent = arm
    head.parent_type = "BONE"
    head.parent_bone = "head"
    # Offset so ball sits at bone tip region
    head.location = (0, 0, 0)
    head["yb_head"] = 1
    return head


def animate_idle(arm, sc, style="builder"):
    """Keyframed breath + sway; walk-bob for crowd/founder."""
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    pb = arm.pose.bones
    f0, f1 = sc.frame_start, sc.frame_end
    mid = (f0 + f1) // 2

    def key_rot(bone_name, frame, euler):
        b = pb.get(bone_name)
        if not b:
            return
        b.rotation_mode = "XYZ"
        b.rotation_euler = euler
        b.keyframe_insert(data_path="rotation_euler", frame=frame)

    def key_loc(bone_name, frame, loc):
        b = pb.get(bone_name)
        if not b:
            return
        b.location = loc
        b.keyframe_insert(data_path="location", frame=frame)

    # Clear old pose keys on this armature for this scene range
    if arm.animation_data and arm.animation_data.action:
        pass  # keep; we overwrite via inserts

    breath_amp = 0.025  # rad chest
    sway_amp = 0.04
    period = 48  # 2s @ 24fps

    frames = list(range(f0, f1 + 1, period // 2))
    if frames[-1] != f1:
        frames.append(f1)

    for i, f in enumerate(frames):
        phase = (f - f0) / period * math.pi * 2
        breath = math.sin(phase) * breath_amp
        sway = math.sin(phase * 0.5) * sway_amp
        key_rot("chest", f, (breath, 0, sway * 0.3))
        key_rot("spine", f, (breath * 0.5, 0, -sway * 0.2))
        key_rot("hips", f, (0, 0, sway * 0.15))
        # Arms slight hang sway
        key_rot("upper_arm.L", f, (0.08 + breath * 0.3, 0.05, 0.15 + sway * 0.2))
        key_rot("upper_arm.R", f, (0.08 + breath * 0.3, -0.05, -0.15 - sway * 0.2))

        if style in ("crowd", "founder_dim"):
            bob = abs(math.sin(phase)) * 0.02
            key_loc("root", f, (0, 0, bob))
            key_rot("thigh.L", f, (math.sin(phase) * 0.12, 0, 0))
            key_rot("thigh.R", f, (math.sin(phase + math.pi) * 0.12, 0, 0))

    # Interpolation bezier (Ryan King / CG Geek Graph Editor practice)
    if arm.animation_data and arm.animation_data.action:
        act = arm.animation_data.action
        if not act.name.startswith("YB_"):
            act.name = f"YB_Idle_{sc.name}"[:63]
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"
            # Idle loop via Cycles modifier (prefer over endless keys)
            if len(fc.keyframe_points) <= 16 and not any(m.type == "CYCLES" for m in fc.modifiers):
                # Only if we keyed a short repeating pattern — skip full-timeline dense keys
                span = fc.keyframe_points[-1].co.x - fc.keyframe_points[0].co.x
                if span <= period * 2 + 2:
                    m = fc.modifiers.new(type="CYCLES")
                    m.mode_after = "REPEAT"
                    m.mode_before = "REPEAT"

    bpy.ops.object.mode_set(mode="OBJECT")


def try_append_studio_base() -> bpy.types.Object | None:
    """If Blender Studio Human Base Meshes are extracted, append stylized male."""
    blends = list(HUMAN_DIR.rglob("*.blend"))
    if not blends:
        return None
    # Prefer files with 'human' in name
    blends = sorted(blends, key=lambda p: (0 if "human" in p.name.lower() else 1, p.stat().st_size), reverse=True)
    src = blends[0]
    # Probe object names
    with bpy.data.libraries.load(str(src), link=False) as (data_from, data_to):
        candidates = [n for n in data_from.objects if any(
            k in n.lower() for k in ("stylized male", "stylized_male", "male", "body", "human")
        )]
        if not candidates:
            candidates = list(data_from.objects)[:5]
        data_to.objects = candidates[:3]
    imported = [o for o in data_to.objects if o is not None]
    if not imported:
        return None
    # Pick tallest mesh
    meshes = [o for o in imported if o.type == "MESH"]
    if not meshes:
        return None
    body = max(meshes, key=lambda o: o.dimensions.z)
    for o in imported:
        if o != body:
            try:
                bpy.data.objects.remove(o, do_unlink=True)
            except Exception:
                pass
    body["yb_from_studio_base"] = 1
    return body


def deploy_scene(sc: bpy.types.Scene, style: str | None):
    bpy.context.window.scene = sc
    # Remove old cube bodies
    for old in find_old_bodies(sc):
        # Unparent ball first
        for ch in list(old.children):
            mw = ch.matrix_world.copy()
            ch.parent = None
            ch.matrix_world = mw
        delete_object(old)
    # Remove old armatures
    for o in list(sc.objects):
        if o.type == "ARMATURE" and o.name.startswith("YB_Arm_"):
            delete_object(o)
        if o.get("yb_head"):
            delete_object(o)

    body_name = f"YB_Body_{sc.name[:8]}"
    arm_name = f"YB_Arm_{sc.name[:8]}"

    # Always use procedural Fern mannequin for consistent ball-head look;
    # studio base can be opted in later via custom prop.
    body = build_mannequin_mesh(body_name)
    link_obj(body, sc)

    arm = build_armature(arm_name)
    link_obj(arm, sc)

    bind_mesh(body, arm)

    ball = find_ball(sc)
    head = place_head_ball(sc, ball, arm)

    # Place character near ball / origin on ground
    if ball:
        target = Vector((ball.location.x, ball.location.y, 0.0))
    else:
        target = Vector((0, 0, 0))
    arm.location = target
    body.location = (0, 0, 0)  # bound to armature

    visible = style is not None
    for o in (body, arm, head):
        o.hide_render = not visible
        o.hide_viewport = False  # keep editable in viewport
        if not visible:
            o.hide_render = True

    if visible:
        animate_idle(arm, sc, style=style)
        # Dim founder variant
        if style == "founder_dim":
            mat = ensure_mat("SoftPop_YB_Body_Dim", (0.10, 0.09, 0.08, 1.0), 0.95)
            if body.data.materials:
                body.data.materials[0] = mat

    # Frame check — ensure body in camera view roughly
    body["yb_style"] = style or "hidden"
    return {
        "scene": sc.name,
        "style": style,
        "visible": visible,
        "verts": len(body.data.vertices),
        "bones": len(arm.data.bones),
        "height": round(body.dimensions.z, 3),
        "width": round(body.dimensions.x, 3),
        "depth": round(body.dimensions.y, 3),
        "head": head.name,
    }


def run():
    enable_rigify()
    ensure_mat("SoftPop_YB_Body", CHARCOAL, 0.9)
    ensure_mat("SoftPop_YB_Head", BALL_HEX, 0.35)
    report = []
    # Probe studio pack once (informational)
    blends = list(HUMAN_DIR.rglob("*.blend")) if HUMAN_DIR.exists() else []
    for sc in bpy.data.scenes:
        sc.render.fps = 24
        sc.render.fps_base = 1.0
        style = HUMANITY_SCENES.get(sc.name)
        report.append(deploy_scene(sc, style))
    bpy.ops.wm.save_mainfile()
    return {
        "bodies": report,
        "rigify_enabled": "rigify" in bpy.context.preferences.addons.keys(),
        "studio_blends_found": [str(p.relative_to(PROJECT)) for p in blends[:10]],
        "saved": bpy.data.filepath,
        "refs": "docs/BLENDER_RIG_ANIM_RESOURCES.md",
        "anthropometrics": {
            "stature_m": STATURE,
            "shoulder_z": round(Z_SHOULDER, 3),
            "hip_z": round(Z_HIP, 3),
            "bideltoid_m": round(BIDELTOID, 3),
            "hip_breadth_m": round(HIP_BREADTH, 3),
            "chest_depth_m": round(CHEST_DEPTH, 3),
            "head_diam_m": HEAD_DIAM,
        },
    }


if __name__ == "__main__":
    print(run())
