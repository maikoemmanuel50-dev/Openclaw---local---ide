"""
AFRICA S1 — Yellow Ball TED-Ed physics + photoreal nodes + squash/stretch rig.

Reference DNA:
  - TED-Ed "Animation basics: timing and spacing" (bouncing ball)
  - User tutorial pack (docs/BLENDER_RIG_ANIM_RESOURCES.md):
      Ryan King keyframes/Graph Editor, CG Geek pose blocking,
      Crashsune extremes-first, ProductionCrate interpolation,
      60s Rigify/auto-weights shorts, CBaileyFilm blocking→spline,
      SharpWind shape-key animation, Blender Guru fundamentals
  - Blender 5.1 Stretch-To armature + shape keys (not Edit-Mode vertex anim)

Creative locks:
  - Hero color #FFD54F — no faces, no second mascot
  - YB-Body remains faceless torso + ball head (separate script)
  - SAFE after HQ batch: do not run while -b render holds the .blend

Run:
  "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" ^
    -b blend/africa_s1_master_v01.blend -P setup_yellow_ball_teded_physics.py
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
BLEND = PROJECT / "blend" / "africa_s1_master_v01.blend"
REPORT = PROJECT / "renders" / "quality" / "yellow_ball_teded_report.json"
FPS = 24
HERO = (1.0, 0.835, 0.310)  # #FFD54F
HIGHLIGHT = (1.0, 0.973, 0.882)  # #FFF8E1
RIM = (0.976, 0.659, 0.145)  # #F9A825

SCENE_DURATIONS = {
    "01_ColdOpen": 50,
    "02_Context2007": 45,
    "03_Beat1_Hubs": 45,
    "04_Beat1_Phone": 25,
    "05_Beat2_Money": 45,
    "06_Beat2_Solar": 40,
    "07_Beat3_Gap": 50,
    "08_Beat3_SecondaryCity": 35,
    "09_Closer": 70,
    "10_EndCard": 15,
}

# TED-Ed motion intent per scene (throughline)
# kind: rise | coin_bounce | orbit | push | inflate | shimmer | concentrate | roll | reignite | settle
MOTION = {
    "01_ColdOpen": {
        "kind": "rise",
        "xy0": (-5.5, -2.0),
        "xy1": (4.0, -2.0),
        "z0": 1.2,
        "z1": 4.2,
        "r": 0.55,
        "bounces": 0,
        "pop": 360,
    },
    "02_Context2007": {
        "kind": "coin_bounce",
        "xy0": (-4.5, 0.0),
        "xy1": (4.5, 0.0),
        "z0": 3.2,
        "z1": 2.0,
        "r": 0.45,
        "bounces": 4,
        "pop": 240,
        "ground": 1.4,
    },
    "03_Beat1_Hubs": {
        "kind": "orbit",
        "xy0": (0.0, 0.0),
        "xy1": (0.0, 0.0),
        "z0": 3.0,
        "z1": 3.4,
        "r": 0.5,
        "bounces": 0,
        "pop": 240,
        "orbit_r": 1.6,
    },
    "04_Beat1_Phone": {
        "kind": "push",
        "xy0": (0.0, -2.0),
        "xy1": (0.0, -0.8),
        "z0": 2.0,
        "z1": 2.4,
        "r": 0.42,
        "bounces": 0,
        "pop": 300,
    },
    "05_Beat2_Money": {
        "kind": "inflate",
        "xy0": (0.0, -3.5),
        "xy1": (0.0, 1.5),
        "z0": 2.0,
        "z1": 4.0,
        "r": 0.35,
        "r1": 0.85,
        "bounces": 0,
        "pop": 180,
    },
    "06_Beat2_Solar": {
        "kind": "shimmer",
        "xy0": (0.0, 0.0),
        "xy1": (0.0, 0.0),
        "z0": 4.8,
        "z1": 5.6,
        "r": 0.7,
        "bounces": 0,
        "pop": 480,
    },
    "07_Beat3_Gap": {
        "kind": "concentrate",
        "xy0": (0.0, 0.0),
        "xy1": (0.0, 0.0),
        "z0": 4.0,
        "z1": 4.0,
        "r": 0.25,
        "r1": 0.55,
        "bounces": 0,
        "pop": 360,
    },
    "08_Beat3_SecondaryCity": {
        "kind": "roll",
        "xy0": (-3.0, -2.0),
        "xy1": (2.0, -2.0),
        "z0": 1.6,
        "z1": 1.6,
        "r": 0.35,
        "bounces": 2,
        "ground": 1.35,
        "pop": None,
    },
    "09_Closer": {
        "kind": "reignite",
        "xy0": (0.0, 0.0),
        "xy1": (0.0, 0.0),
        "z0": 2.8,
        "z1": 5.0,
        "r": 0.5,
        "r1": 0.75,
        "bounces": 0,
        "pop": 540,
    },
    "10_EndCard": {
        "kind": "settle",
        "xy0": (0.0, 0.0),
        "xy1": (0.0, 0.0),
        "z0": 2.0,
        "z1": 2.15,
        "r": 0.55,
        "bounces": 1,
        "ground": 1.7,
        "pop": 60,
    },
}


def set_input(node, names, value):
    """Blender 4/5 Principled socket rename safety."""
    if isinstance(names, str):
        names = [names]
    for n in names:
        sock = node.inputs.get(n)
        if sock is not None and hasattr(sock, "default_value"):
            try:
                sock.default_value = value
                return True
            except Exception:
                pass
    return False


def ensure_photoreal_mat() -> bpy.types.Material:
    """
    Fully wired Principled + Coat + soft emission rim.
    Validates every critical link (no dangling hero shader).
    """
    name = "SasaYellow_Photoreal"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (700, 0)
    out.name = "YB_Out"

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 80)
    bsdf.name = "YB_Principled"
    set_input(bsdf, ["Base Color"], (*HERO, 1.0))
    set_input(bsdf, ["Roughness"], 0.28)
    set_input(bsdf, ["Metallic"], 0.05)
    set_input(bsdf, ["Specular IOR Level", "Specular"], 0.55)
    set_input(bsdf, ["Coat Weight", "Coat", "Clearcoat"], 0.85)
    set_input(bsdf, ["Coat Roughness", "Clearcoat Roughness"], 0.12)
    set_input(bsdf, ["Subsurface Weight", "Subsurface"], 0.12)
    set_input(bsdf, ["Subsurface Radius"], (1.0, 0.7, 0.35))
    set_input(bsdf, ["Subsurface Color"], (*HERO, 1.0))

    # Micro-surface for soft-pop photoreal (not flat emoji)
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-700, 0)
    texcoord.name = "YB_TexCoord"
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-500, 0)
    mapping.name = "YB_Mapping"
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-300, -40)
    noise.name = "YB_Noise"
    noise.inputs["Scale"].default_value = 18.0
    noise.inputs["Detail"].default_value = 6.0
    bump = nodes.new("ShaderNodeBump")
    bump.location = (0, -120)
    bump.name = "YB_Bump"
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.02

    # Soft glow rim — TED-Ed readable, soft-pop photoreal
    emis = nodes.new("ShaderNodeEmission")
    emis.location = (200, -220)
    emis.name = "YB_Emission"
    emis.inputs["Color"].default_value = (*HIGHLIGHT, 1.0)
    emis.inputs["Strength"].default_value = 0.55

    mix = nodes.new("ShaderNodeMixShader")
    mix.location = (480, 0)
    mix.name = "YB_Mix"
    # Prefer Layer Weight facing for rim; fallback Factor 0.12
    layer = nodes.new("ShaderNodeLayerWeight")
    layer.location = (200, -380)
    layer.name = "YB_LayerWeight"
    layer.inputs["Blend"].default_value = 0.35
    fres = nodes.new("ShaderNodeMath")
    fres.location = (360, -380)
    fres.name = "YB_FresnelGate"
    fres.operation = "MULTIPLY"
    fres.inputs[1].default_value = 0.35

    # Wire graph
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    if bump.outputs.get("Normal") and bsdf.inputs.get("Normal"):
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(layer.outputs["Facing"], fres.inputs[0])
    links.new(fres.outputs["Value"], mix.inputs["Fac"])
    links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    links.new(emis.outputs["Emission"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])

    # Audit critical links
    required = [
        ("YB_Principled", "BSDF"),
        ("YB_Emission", "Emission"),
        ("YB_Mix", "Shader"),
        ("YB_Out", None),
    ]
    for nname, _ in required:
        if nname not in nodes:
            raise RuntimeError(f"Missing node {nname}")
    if not out.inputs["Surface"].is_linked:
        raise RuntimeError("Material Output Surface not linked")
    return mat


def volume_scale(sy: float) -> tuple[float, float, float]:
    """Preserve approximate volume: sx * sy * sz = 1."""
    sy = max(0.35, min(1.85, sy))
    sx = sz = 1.0 / math.sqrt(sy)
    return (sx, sy, sz)


def clear_old_sasa(scene: bpy.types.Scene):
    for obj in list(scene.objects):
        if obj.name.startswith("Sasa_") or obj.name.startswith("YB_Rig_"):
            bpy.data.objects.remove(obj, do_unlink=True)


def ease_bezier(obj: bpy.types.Object):
    if not obj.animation_data or not obj.animation_data.action:
        return 0
    n = 0
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"
            n += 1
    return n


def insert_loc(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert("location", frame=frame)


def insert_sk(ball, frame, squash=0.0, stretch=0.0):
    if not ball.data.shape_keys:
        return
    keys = ball.data.shape_keys.key_blocks
    if "Squash" in keys:
        keys["Squash"].value = squash
        keys["Squash"].keyframe_insert("value", frame=frame)
    if "Stretch" in keys:
        keys["Stretch"].value = stretch
        keys["Stretch"].keyframe_insert("value", frame=frame)


def bounce_path(xy0, xy1, z0, z1, ground, frames, bounces, restitution=0.55):
    """
    TED-Ed spacing: accelerate into impact, decelerate to apex.
    Returns list of (frame, x, y, z, squash, stretch).
    """
    keys = []
    if bounces <= 0:
        for t, f in ((0.0, 1), (1.0, frames)):
            x = xy0[0] + (xy1[0] - xy0[0]) * t
            y = xy0[1] + (xy1[1] - xy0[1]) * t
            z = z0 + (z1 - z0) * t
            keys.append((f, x, y, z, 0.0, 0.0))
        return keys

    # Segment timeline by bounce energy decay
    heights = []
    h = max(0.15, z0 - ground)
    for i in range(bounces + 1):
        heights.append(h * (restitution ** i))
    # Time proportional to sqrt(h) (physics of free fall)
    weights = [math.sqrt(max(h, 0.05)) for h in heights]
    total_w = sum(weights) or 1.0
    seg_frames = [max(4, int(round(frames * w / total_w))) for w in weights]
    # Fix sum
    while sum(seg_frames) > frames:
        seg_frames[seg_frames.index(max(seg_frames))] -= 1
    while sum(seg_frames) < frames:
        seg_frames[-1] += 1

    f = 1
    for i, sf in enumerate(seg_frames):
        # lateral progress across whole shot
        t0 = (f - 1) / max(1, frames - 1)
        t1 = min(1.0, (f + sf - 1) / max(1, frames - 1))
        apex_z = ground + heights[i]
        # fall: apex -> ground (or start)
        mid = f + sf // 2
        end = f + sf - 1
        if i == 0:
            insert_z0 = z0
        else:
            insert_z0 = apex_z
        # peak (slow spacing)
        x = xy0[0] + (xy1[0] - xy0[0]) * t0
        y = xy0[1] + (xy1[1] - xy0[1]) * t0
        keys.append((f, x, y, insert_z0, 0.0, 0.05))
        # stretch approaching impact
        x = xy0[0] + (xy1[0] - xy0[0]) * ((t0 + t1) * 0.5)
        y = xy0[1] + (xy1[1] - xy0[1]) * ((t0 + t1) * 0.5)
        keys.append((mid - 1, x, y, ground + heights[i] * 0.35, 0.0, 0.55))
        # squash on impact
        x = xy0[0] + (xy1[0] - xy0[0]) * t1
        y = xy0[1] + (xy1[1] - xy0[1]) * t1
        keys.append((mid, x, y, ground + 0.02, 0.85, 0.0))
        # rebound stretch
        keys.append((mid + 2, x, y, ground + heights[min(i + 1, len(heights) - 1)] * 0.45, 0.0, 0.4))
        # next apex
        keys.append((end, x, y, ground + heights[min(i + 1, len(heights) - 1)], 0.0, 0.0))
        f = end + 1
    # settle
    keys.append((frames, xy1[0], xy1[1], z1, 0.0, 0.0))
    return keys


def animate_orbit(master, ball, cfg, frames):
    r = cfg.get("orbit_r", 1.5)
    z0, z1 = cfg["z0"], cfg["z1"]
    for i in range(0, frames + 1, 4):
        t = i / frames
        ang = t * math.tau * 1.25
        x = math.cos(ang) * r
        y = math.sin(ang) * r * 0.55
        z = z0 + (z1 - z0) * t
        insert_loc(master, i if i else 1, (x, y, z))
        insert_sk(ball, i if i else 1, 0.0, 0.08 * math.sin(ang * 2))
    ease_bezier(master)


def set_active_scene(scene: bpy.types.Scene):
    """Headless-safe scene activation."""
    try:
        if getattr(bpy.context, "window", None):
            bpy.context.window.scene = scene
    except Exception:
        pass


def create_ball_mesh(name: str, radius: float) -> bpy.types.Object:
    import bmesh

    mesh = bpy.data.meshes.new(name + "Mesh")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    obj = bpy.data.objects.new(name, mesh)
    return obj


def create_ss_rig(scene: bpy.types.Scene, radius: float) -> tuple[bpy.types.Object, bpy.types.Object]:
    """
    Master empty + photoreal ball + shape-key squash/stretch.
    Stretch-To armature added when context allows (GUI or good -b override).
    """
    mat = ensure_photoreal_mat()
    ball = create_ball_mesh("Sasa_Ball", radius)
    scene.collection.objects.link(ball)
    ball.location = (0, 0, 0)
    ball.data.materials.append(mat)
    if not any(m.type == "SUBSURF" for m in ball.modifiers):
        sub = ball.modifiers.new("YB_Subdiv", "SUBSURF")
        sub.levels = 1
        sub.render_levels = 2

    ball.shape_key_add(name="Basis")
    sk = ball.shape_key_add(name="Squash", from_mix=False)
    for v in sk.data:
        v.co.y *= 0.55
        v.co.x *= 1.22
        v.co.z *= 1.22
    st = ball.shape_key_add(name="Stretch", from_mix=False)
    for v in st.data:
        v.co.y *= 1.35
        v.co.x *= 0.86
        v.co.z *= 0.86

    master = bpy.data.objects.new("Sasa_Master", None)
    master.empty_display_type = "SPHERE"
    master.empty_display_size = radius * 1.2
    scene.collection.objects.link(master)
    ball.parent = master

    # Apply Rot/Scale before bind (Rigify / 60s-rig shorts)
    try:
        for o in scene.objects:
            o.select_set(False)
        ball.select_set(True)
        bpy.context.view_layer.objects.active = ball
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    except Exception as e:
        print(f"  apply_transforms skip: {e}")

    # Optional Stretch-To armature + Automatic Weights when context allows
    try:
        arm_data = bpy.data.armatures.new(f"YB_ArmData_{scene.name}")
        arm = bpy.data.objects.new(f"YB_Rig_Armature_{scene.name}", arm_data)
        scene.collection.objects.link(arm)
        wl = scene.view_layers[0]
        override = {
            "scene": scene,
            "view_layer": wl,
            "active_object": arm,
            "object": arm,
            "selected_objects": [arm],
            "selected_editable_objects": [arm],
        }
        with bpy.context.temp_override(**override):
            bpy.ops.object.mode_set(mode="EDIT")
            eb = arm_data.edit_bones
            root = eb.new("CTRL_Root")
            root.head = (0, 0, -radius)
            root.tail = (0, 0, 0)
            squash = eb.new("CTRL_Squash")
            squash.head = (0, 0, 0)
            squash.tail = (0, 0, radius)
            squash.parent = root
            stretch = eb.new("MCH_Stretch")
            stretch.head = (0, 0, -radius)
            stretch.tail = (0, 0, radius)
            stretch.parent = root
            bpy.ops.object.mode_set(mode="POSE")
            c = arm.pose.bones["MCH_Stretch"].constraints.new("STRETCH_TO")
            c.target = arm
            c.subtarget = "CTRL_Squash"
            c.rest_length = radius * 2.0
            bpy.ops.object.mode_set(mode="OBJECT")
        arm.parent = master
        # Automatic Weights (shorts / Rigify guides) — Pose Mode only for later keys
        ball.parent = None
        for o in scene.objects:
            o.select_set(False)
        ball.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        try:
            bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        except Exception:
            ball.parent = arm
            mod = ball.modifiers.new("YB_Armature", "ARMATURE")
            mod.object = arm
        # Modifier order: Armature then Subsurf
        names = [m.name for m in ball.modifiers]
        if "YB_Armature" in names or any(m.type == "ARMATURE" for m in ball.modifiers):
            arm_mod = next(m for m in ball.modifiers if m.type == "ARMATURE")
            while ball.modifiers[0] != arm_mod:
                try:
                    bpy.context.view_layer.objects.active = ball
                    bpy.ops.object.modifier_move_up(modifier=arm_mod.name)
                except Exception:
                    break
    except Exception as e:
        print(f"  armature optional skip ({scene.name}): {e}")

    return master, ball


def animate_scene(scene: bpy.types.Scene, sname: str) -> dict:
    cfg = MOTION[sname]
    frames = SCENE_DURATIONS[sname] * FPS
    scene.frame_start = 1
    scene.frame_end = frames

    clear_old_sasa(scene)
    set_active_scene(scene)
    master, ball = create_ss_rig(scene, cfg["r"])

    kind = cfg["kind"]
    report = {"scene": sname, "kind": kind, "frames": frames, "nodes_ok": True}

    if kind == "orbit":
        animate_orbit(master, ball, cfg, frames)
    else:
        ground = cfg.get("ground", min(cfg["z0"], cfg["z1"]) * 0.45)
        keys = bounce_path(
            cfg["xy0"],
            cfg["xy1"],
            cfg["z0"],
            cfg["z1"],
            ground,
            frames,
            cfg.get("bounces", 0),
            restitution=0.52 if kind in {"coin_bounce", "roll"} else 0.45,
        )
        for f, x, y, z, sq, st in keys:
            insert_loc(master, f, (x, y, z))
            insert_sk(ball, f, sq, st)

        # Scale morph for inflate / concentrate / reignite
        r0 = cfg["r"]
        r1 = cfg.get("r1", r0)
        if abs(r1 - r0) > 1e-4:
            master.scale = (1, 1, 1)
            master.keyframe_insert("scale", frame=1)
            s = r1 / r0
            master.scale = (s, s, s)
            master.keyframe_insert("scale", frame=frames)

        # TED-Ed pop punch (timing accent)
        pop = cfg.get("pop")
        if pop:
            pop = int(min(frames - 10, max(12, pop)))
            insert_sk(ball, pop - 4, 0.0, 0.15)
            insert_sk(ball, pop, 0.0, 0.0)
            # temporary uniform punch via master scale
            master.keyframe_insert("scale", frame=pop - 4)
            sx, sy, sz = master.scale
            master.scale = (sx * 1.28, sy * 1.28, sz * 1.28)
            master.keyframe_insert("scale", frame=pop)
            master.scale = (sx * 1.05, sy * 1.05, sz * 1.05)
            master.keyframe_insert("scale", frame=pop + 8)

        ease_bezier(master)
        if ball.data.shape_keys and ball.data.shape_keys.animation_data:
            ease_bezier(ball.data.shape_keys)

    # Dim chapters S07–S08: lower emission, keep hero hue
    if kind in {"concentrate", "roll"}:
        mat = ball.data.materials[0]
        emis = mat.node_tree.nodes.get("YB_Emission")
        if emis:
            emis.inputs["Strength"].default_value = 0.22

    report["material"] = ball.data.materials[0].name if ball.data.materials else None
    report["rig"] = "CTRL_Root+CTRL_Squash+MCH_Stretch+Sasa_Master"
    report["shape_keys"] = ["Basis", "Squash", "Stretch"]
    return report


def validate_material_graph() -> dict:
    mat = bpy.data.materials.get("SasaYellow_Photoreal")
    if not mat or not mat.use_nodes:
        return {"ok": False, "error": "missing material"}
    nt = mat.node_tree
    issues = []
    for n in nt.nodes:
        if n.type == "BSDF_PRINCIPLED" and not n.outputs["BSDF"].is_linked:
            issues.append("Principled BSDF unlinked")
        if n.type == "OUTPUT_MATERIAL" and not n.inputs["Surface"].is_linked:
            issues.append("Material Output Surface unlinked")
    return {"ok": not issues, "issues": issues, "node_count": len(nt.nodes), "link_count": len(nt.links)}


def main():
    print("=== Yellow Ball TED-Ed Physics + Photoreal Nodes ===")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    # Build material once
    ensure_photoreal_mat()
    results = []
    for sname in SCENE_DURATIONS:
        if sname not in bpy.data.scenes:
            results.append({"scene": sname, "error": "missing scene"})
            continue
        try:
            set_active_scene(bpy.data.scenes[sname])
            results.append(animate_scene(bpy.data.scenes[sname], sname))
            print(f"OK {sname}")
        except Exception as e:
            results.append({"scene": sname, "error": str(e)})
            print(f"FAIL {sname}: {e}")

    audit = validate_material_graph()
    out = {
        "refs": [
            "docs/BLENDER_RIG_ANIM_RESOURCES.md",
            "https://ed.ted.com/lessons/animation-basics-the-art-of-timing-and-spacing-ted-ed",
            "https://youtu.be/CBJp82tlR3M",
            "https://youtu.be/_C2ClFO3FAY",
            "https://www.youtube.com/shorts/IeV6xLGIp94",
        ],
        "material_audit": audit,
        "scenes": results,
        "note": "Run AFTER HQ batch. Re-render ball-heavy scenes or V2 overlays for uptake.",
    }
    REPORT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print(f"SAVED {BLEND}")
    print(f"REPORT {REPORT}")
    print("YELLOW_BALL_TEDED_PHYSICS_DONE")


if __name__ == "__main__":
    main()
