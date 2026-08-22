"""
Africa S1 — Object motion lock (Option D: Blender-native, Meshy Free only if needed).

Replaces Ken-Burns-into-still energy with in-scene object motion:
  Geometry Nodes wind sway · Graph Editor BEZIER walks · emission pulses.

Refs baked in:
  - Telegram Arch Comm IV (Class 01–16): collections, Principled wiring, Node Wrangler
    docs/ARCH_COMM_IV_LOCK.md · docs/BLENDER_RIG_ANIM_RESOURCES.md
  - Ryan King / CG Geek / CBaileyFilm: BEZIER ease, Graph Editor, Pose/object keys
  - Blender Manual: Geometry Nodes Set Position + Noise; Drivers (#frame)
  - TED-Ed timing & spacing

SAFE: Never open/save master while HQ -b is writing.
  1) Copy master → blend/africa_s1_object_motion_preview.blend
  2) Run this script on the COPY only.

  powershell:
    Copy-Item blend\\africa_s1_master_v01.blend blend\\africa_s1_object_motion_preview.blend -Force
    $env:CUDA_VISIBLE_DEVICES='-1'
    & \"C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe\" `
      -b blend\\africa_s1_object_motion_preview.blend -P setup_object_motion_all_scenes.py

Meshy Free browser: only for missing hero props listed in
  renders/quality/meshy_free_optional_queue.json (optional giraffe for S07).
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import addon_utils
import bpy
from mathutils import Vector

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
REPORT = PROJECT / "renders" / "quality" / "object_motion_lock_report.json"
MESHY_QUEUE = PROJECT / "renders" / "quality" / "meshy_free_optional_queue.json"
OUT_BLEND = PROJECT / "blend" / "africa_s1_object_motion_preview.blend"
# Set AFRICA_OUT_BLEND to master path when GPU batch is finished (merge_motion_after_hq.ps1).

# Per-scene motion recipes (camera stays; objects carry life)
SCENE_MOTION = {
    "01_ColdOpen": {"sway": ["Midground", "Foreground", "Background_Plane"], "pulse": [], "walk": False, "cam_dampen": 0.55},
    "02_Context2007": {"sway": ["Midground", "Foreground", "Background"], "pulse": [], "walk": False, "cam_dampen": 0.5},
    "03_Beat1_Hubs": {"sway": ["Midground", "Foreground"], "pulse": ["Screen", "Laptop", "Monitor"], "walk": False, "cam_dampen": 0.45},
    "04_Beat1_Phone": {"sway": [], "pulse": ["Phone", "UI", "Screen"], "walk": False, "cam_dampen": 0.4},
    "05_Beat2_Money": {"sway": ["Midground"], "pulse": ["Bar_", "Chart", "Screen"], "walk": False, "cam_dampen": 0.35},
    "06_Beat2_Solar": {"sway": ["Midground", "Foreground", "Solar"], "pulse": ["Solar", "Panel"], "walk": False, "cam_dampen": 0.45},
    "07_Beat3_Gap": {"sway": ["Midground", "Foreground", "Background"], "pulse": [], "walk": True, "cam_dampen": 0.4},
    "08_Beat3_SecondaryCity": {"sway": ["Midground", "Foreground", "Background"], "pulse": ["Lamp", "Light"], "walk": False, "cam_dampen": 0.5},
    "09_Closer": {"sway": ["Midground", "Foreground"], "pulse": ["Window", "Building"], "walk": False, "cam_dampen": 0.45},
    "10_EndCard": {"sway": [], "pulse": ["Africa", "Logo", "Title"], "walk": False, "cam_dampen": 0.25},
}


def enable_addons(report: dict):
    """Arch Comm / production add-ons — Node Wrangler for proper socket wiring."""
    wanted = [
        "node_wrangler",
        "add_curve_extra_objects",
        "add_mesh_extra_objects",
        "io_scene_gltf2",
        "cycles",
    ]
    ok, fail = [], []
    for mod in wanted:
        try:
            addon_utils.enable(mod, default_set=True)
            ok.append(mod)
        except Exception as e:
            fail.append({"addon": mod, "err": str(e)})
    report["addons"] = {"enabled": ok, "failed": fail}


def ensure_collection(sc: bpy.types.Scene, name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        sc.collection.children.link(col)
    # Ensure linked to this scene's view layer root if missing
    if col.name not in [c.name for c in sc.collection.children]:
        try:
            sc.collection.children.link(col)
        except Exception:
            pass
    return col


def link_to(col: bpy.types.Collection, obj: bpy.types.Object):
    if obj.name not in col.objects:
        col.objects.link(obj)


def iter_action_fcurves(action):
    if action is None:
        return
    legacy = getattr(action, "fcurves", None)
    if legacy is not None:
        yield from legacy
        return
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                bags = getattr(strip, "channelbags", None)
                if bags:
                    for bag in bags:
                        yield from getattr(bag, "fcurves", []) or []


def ease_action(action):
    for fc in iter_action_fcurves(action):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            try:
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"
            except Exception:
                pass


def dampen_camera(cam: bpy.types.Object, factor: float):
    """Reduce existing camera travel (keep intentional move, less Ken Burns)."""
    if not cam or not cam.animation_data or not cam.animation_data.action:
        return 0
    n = 0
    locs = []
    for fc in iter_action_fcurves(cam.animation_data.action):
        if fc.data_path != "location":
            continue
        for kp in fc.keyframe_points:
            locs.append((fc.array_index, kp.co.x, kp.co.y))
    if not locs:
        return 0
    # Pivot around first key per channel
    first = {}
    for idx, fr, val in locs:
        if idx not in first:
            first[idx] = val
    for fc in iter_action_fcurves(cam.animation_data.action):
        if fc.data_path != "location":
            continue
        base = first.get(fc.array_index, 0.0)
        for kp in fc.keyframe_points:
            kp.co.y = base + (kp.co.y - base) * factor
            n += 1
        fc.update()
    ease_action(cam.animation_data.action)
    return n


def build_wind_sway_group(name: str = "GN_WindSway") -> bpy.types.NodeTree:
    """
    Geometry Nodes: Set Position offset by 4D Noise (#frame as W).
    Manual: Geometry Nodes → Set Position + Noise Texture (Blender Manual).
    """
    existing = bpy.data.node_groups.get(name)
    if existing:
        return existing

    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    # Blender 4+/5 interface
    iface = ng.interface
    iface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    sock_amp = iface.new_socket(name="Amplitude", in_out="INPUT", socket_type="NodeSocketFloat")
    sock_amp.default_value = 0.035
    sock_scale = iface.new_socket(name="Noise Scale", in_out="INPUT", socket_type="NodeSocketFloat")
    sock_scale.default_value = 1.8
    sock_speed = iface.new_socket(name="Speed", in_out="INPUT", socket_type="NodeSocketFloat")
    sock_speed.default_value = 0.08
    iface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

    nodes = ng.nodes
    links = ng.links
    n_in = nodes.new("NodeGroupInput")
    n_in.location = (-800, 0)
    n_out = nodes.new("NodeGroupOutput")
    n_out.location = (600, 0)

    pos = nodes.new("GeometryNodeInputPosition")
    pos.location = (-600, -120)

    # Scene time → seconds (Blender 5: GeometryNodeInputSceneTime)
    try:
        time_n = nodes.new("GeometryNodeInputSceneTime")
    except Exception:
        time_n = nodes.new("FunctionNodeInputVector")  # fallback unused
    time_n.location = (-600, 160)

    # Speed * Seconds → W
    mul_w = nodes.new("ShaderNodeMath")
    mul_w.operation = "MULTIPLY"
    mul_w.location = (-400, 160)

    comb = nodes.new("ShaderNodeCombineXYZ")
    comb.location = (-200, 40)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (0, 40)
    try:
        noise.noise_dimensions = "4D"
    except Exception:
        pass

    # Map noise 0–1 → -1..1 then * amplitude on X/Z only (gentle sway)
    map_r = nodes.new("ShaderNodeMapRange")
    map_r.location = (200, 40)
    map_r.inputs[1].default_value = 0.0
    map_r.inputs[2].default_value = 1.0
    map_r.inputs[3].default_value = -1.0
    map_r.inputs[4].default_value = 1.0

    sep = nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (200, -160)
    mul_x = nodes.new("ShaderNodeMath")
    mul_x.operation = "MULTIPLY"
    mul_x.location = (400, 80)
    mul_z = nodes.new("ShaderNodeMath")
    mul_z.operation = "MULTIPLY"
    mul_z.location = (400, -40)
    comb_off = nodes.new("ShaderNodeCombineXYZ")
    comb_off.location = (560, 0)

    setpos = nodes.new("GeometryNodeSetPosition")
    setpos.location = (400, 200)

    # Wire: time.Seconds * Speed → noise W via Combine XYZ (X=pos.x scaled, Y=pos.y, Z=pos.z, W via 4D)
    # Noise Vector = position; W = time*speed
    links.new(n_in.outputs["Geometry"], setpos.inputs["Geometry"])
    links.new(pos.outputs["Position"], sep.inputs["Vector"])

    # Build 4D vector: use Noise's Vector=Position, and W input if present
    links.new(pos.outputs["Position"], noise.inputs["Vector"])
    try:
        links.new(n_in.outputs["Noise Scale"], noise.inputs["Scale"])
    except Exception:
        pass

    seconds_out = None
    for out in time_n.outputs:
        if out.name.lower() in ("seconds", "time"):
            seconds_out = out
            break
    if seconds_out is None and len(time_n.outputs):
        seconds_out = time_n.outputs[0]

    if seconds_out and "Speed" in n_in.outputs:
        links.new(seconds_out, mul_w.inputs[0])
        links.new(n_in.outputs["Speed"], mul_w.inputs[1])
        if "W" in noise.inputs:
            links.new(mul_w.outputs[0], noise.inputs["W"])

    links.new(noise.outputs["Fac"], map_r.inputs["Value"])
    links.new(map_r.outputs["Result"], mul_x.inputs[0])
    links.new(n_in.outputs["Amplitude"], mul_x.inputs[1])
    half = nodes.new("ShaderNodeMath")
    half.operation = "MULTIPLY"
    half.location = (400, -160)
    half.inputs[1].default_value = 0.5
    links.new(n_in.outputs["Amplitude"], half.inputs[0])
    links.new(map_r.outputs["Result"], mul_z.inputs[0])
    links.new(half.outputs[0], mul_z.inputs[1])

    links.new(mul_x.outputs[0], comb_off.inputs["X"])
    # Y near zero so plates don't swim in depth too hard
    comb_off.inputs["Y"].default_value = 0.0
    links.new(mul_z.outputs[0], comb_off.inputs["Z"])
    links.new(comb_off.outputs["Vector"], setpos.inputs["Offset"])
    links.new(setpos.outputs["Geometry"], n_out.inputs["Geometry"])

    return ng


def apply_gn_sway(obj: bpy.types.Object, ng: bpy.types.NodeTree, amp: float = 0.03) -> bool:
    if obj.type != "MESH":
        return False
    # Remove stale WindSway from wrong-scene passes
    mod = obj.modifiers.get("WindSway")
    if mod is None:
        mod = obj.modifiers.new("WindSway", "NODES")
    mod.node_group = ng
    try:
        for item in mod.node_group.interface.items_tree:
            if getattr(item, "in_out", "") != "INPUT":
                continue
            if item.name == "Amplitude":
                mod[item.identifier] = amp
            elif item.name == "Noise Scale":
                mod[item.identifier] = 1.6 if "Background" in obj.name else 2.2
            elif item.name == "Speed":
                mod[item.identifier] = 0.06 if "Background" in obj.name else 0.1
    except Exception:
        pass
    return True


def strip_foreign_wind(sc: bpy.types.Scene):
    """Keep WindSway only on this scene's suffix planes + allowed heroes."""
    suffix = SCENE_SUFFIX.get(sc.name, "")
    for o in list(sc.objects):
        mod = o.modifiers.get("WindSway")
        if not mod:
            continue
        keep = False
        if "Solar" in o.name and sc.name == "06_Beat2_Solar":
            keep = True
        if "plane" in o.name.lower() and suffix and (o.name.endswith(suffix) or f".{suffix}" in o.name):
            keep = True
        if not keep and "plane" in o.name.lower():
            o.modifiers.remove(mod)


def add_object_rotation_sway(obj: bpy.types.Object, sc: bpy.types.Scene, amp_deg: float = 1.8, period: int = 96):
    """Fallback / extra: Graph Editor BEZIER rotation keys (Ryan King / CG Geek)."""
    if obj.animation_data:
        # Don't clear unrelated anim — only add rot if no rot keys
        pass
    f0 = sc.frame_start
    f1 = sc.frame_end
    mid = (f0 + f1) // 2
    base = list(obj.rotation_euler)
    keys = [
        (f0, base[2]),
        (f0 + period // 4, base[2] + math.radians(amp_deg)),
        (mid, base[2] - math.radians(amp_deg * 0.6)),
        (f1 - period // 4, base[2] + math.radians(amp_deg * 0.8)),
        (f1, base[2]),
    ]
    for fr, z in keys:
        obj.rotation_euler = (base[0], base[1], z)
        obj.keyframe_insert("rotation_euler", index=2, frame=fr)
    if obj.animation_data and obj.animation_data.action:
        ease_action(obj.animation_data.action)


def wire_emission_pulse(mat: bpy.types.Material, strength_a: float, strength_b: float, sc: bpy.types.Scene) -> bool:
    """Principled Emission Strength keyed — Arch Comm IV Principled wiring."""
    if not mat or not mat.use_nodes:
        return False
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not bsdf or "Emission Strength" not in bsdf.inputs:
        return False
    sock = bsdf.inputs["Emission Strength"]
    # Ensure emission color not black
    if "Emission Color" in bsdf.inputs:
        col = bsdf.inputs["Emission Color"].default_value
        if col[0] + col[1] + col[2] < 0.05:
            bsdf.inputs["Emission Color"].default_value = (1.0, 0.85, 0.35, 1.0)
    f0, f1 = sc.frame_start, sc.frame_end
    sock.default_value = strength_a
    sock.keyframe_insert("default_value", frame=f0)
    sock.default_value = strength_b
    sock.keyframe_insert("default_value", frame=(f0 + f1) // 2)
    sock.default_value = strength_a
    sock.keyframe_insert("default_value", frame=f1)
    if nt.animation_data and nt.animation_data.action:
        ease_action(nt.animation_data.action)
    return True


def make_illustrated_walker(sc: bpy.types.Scene, col: bpy.types.Collection) -> bpy.types.Object:
    """
    Stylized faceless walker for S07 (illustrated-doc — not photoreal animal).
    Simple armature-free Loc keys across frame (ProductionCrate object animation).
    Optional Meshy Free GLB can replace this later in MODEL_ADDITIONS.
    """
    name = "MOTION_Walker_S07"
    existing = sc.objects.get(name)
    if existing:
        return existing

    # Body + neck + head (faceless) — yellow-base cream
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = name
    body.scale = (0.35, 0.9, 1.1)
    bpy.ops.object.transform_apply(scale=True)

    mat = bpy.data.materials.get("M_MOTION_Walker") or bpy.data.materials.new("M_MOTION_Walker")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.92, 0.78, 0.42, 1.0)  # soft gold
    bsdf.inputs["Roughness"].default_value = 0.55
    try:
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.84, 0.3, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.15
    except Exception:
        pass
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if body.data.materials:
        body.data.materials[0] = mat
    else:
        body.data.materials.append(mat)

    # Place in front of typical BG plate depth
    body.location = (-4.2, -2.2, 0.6)
    link_to(col, body)

    f0, f1 = sc.frame_start, sc.frame_end
    # Enter mid-scene, cross, exit — ≤5s readable holds via slow travel
    t0 = int(f0 + (f1 - f0) * 0.28)
    t1 = int(f0 + (f1 - f0) * 0.72)
    body.location = (-4.5, -2.2, 0.6)
    body.keyframe_insert("location", frame=t0)
    body.location = (4.5, -2.0, 0.6)
    body.keyframe_insert("location", frame=t1)
    # Subtle bob
    body.location.z = 0.55
    body.keyframe_insert("location", index=2, frame=t0)
    body.location.z = 0.72
    body.keyframe_insert("location", index=2, frame=(t0 + t1) // 2)
    body.location.z = 0.55
    body.keyframe_insert("location", index=2, frame=t1)
    if body.animation_data and body.animation_data.action:
        ease_action(body.animation_data.action)
    # Hide outside walk window
    body.hide_render = True
    body.keyframe_insert("hide_render", frame=t0 - 1)
    body.hide_render = False
    body.keyframe_insert("hide_render", frame=t0)
    body.hide_render = True
    body.keyframe_insert("hide_render", frame=t1 + 1)
    return body


SCENE_SUFFIX = {
    "01_ColdOpen": "001",
    "02_Context2007": "002",
    "03_Beat1_Hubs": "003",
    "04_Beat1_Phone": "004",
    "05_Beat2_Money": "005",  # may be missing; fallback name match
    "06_Beat2_Solar": "006",
    "07_Beat3_Gap": "007",
    "08_Beat3_SecondaryCity": "008",
    "09_Closer": "009",
    "10_EndCard": "010",
}


def match_objects(sc: bpy.types.Scene, needles: list[str]) -> list[bpy.types.Object]:
    """Prefer this scene's numbered planes (Arch Comm naming hygiene)."""
    suffix = SCENE_SUFFIX.get(sc.name, "")
    out = []
    for o in sc.objects:
        # Skip motion helpers from other recipes
        if o.name.startswith("MOTION_"):
            continue
        name = o.name
        for n in needles:
            nl = n.lower()
            if nl not in name.lower():
                continue
            # Plane stacks: require scene suffix when present (.001 … .010)
            if "plane" in name.lower() and suffix:
                if not name.endswith(suffix) and f".{suffix}" not in name:
                    continue
            # Solar array only in solar scene
            if "solar" in name.lower() and sc.name != "06_Beat2_Solar":
                continue
            out.append(o)
            break
    return out


def process_scene(sc: bpy.types.Scene, cfg: dict, ng: bpy.types.NodeTree) -> dict:
    bpy.context.window.scene = sc
    additions = ensure_collection(sc, "MODEL_ADDITIONS")
    env = ensure_collection(sc, "ENV")
    strip_foreign_wind(sc)

    result = {"scene": sc.name, "sway": [], "pulse": [], "walk": None, "cam_keys": 0}

    if sc.camera:
        result["cam_keys"] = dampen_camera(sc.camera, cfg.get("cam_dampen", 0.5))

    for o in match_objects(sc, cfg.get("sway", [])):
        if o.type != "MESH":
            continue
        # Prefer GN; also light rotation sway on mid/fg
        amp = 0.02 if "Background" in o.name else 0.045
        if apply_gn_sway(o, ng, amp=amp):
            result["sway"].append(o.name + ":GN")
        if any(k in o.name for k in ("Midground", "Foreground", "Solar", "Tree")):
            add_object_rotation_sway(o, sc, amp_deg=1.2 if "Background" in o.name else 2.2)
            result["sway"].append(o.name + ":ROT")
        link_to(env, o)

    for o in match_objects(sc, cfg.get("pulse", [])):
        for slot in o.material_slots:
            if slot.material and wire_emission_pulse(slot.material, 0.2, 1.4, sc):
                result["pulse"].append(f"{o.name}/{slot.material.name}")

    if cfg.get("walk"):
        walker = make_illustrated_walker(sc, additions)
        result["walk"] = walker.name

    return result


def write_meshy_optional_queue():
    """Only where a browser Free mesh would clearly beat our proxy."""
    q = {
        "policy": "Meshy Free web UI only — no API. Optional upgrades only.",
        "items": [
            {
                "scene": "07_Beat3_Gap",
                "why": "Replace MOTION_Walker_S07 stylized block with textured giraffe GLB if credits allow",
                "source_still": "assets/canva/kinetic/graded_1080/k07_kenya_landscape_1080.png",
                "drop_glb_to": "assets/meshy/scenes/S07/s07_giraffe.glb",
                "credits_note": "Free plan ~100 credits/mo; 1–2 props max",
            }
        ],
        "not_needed": "S01–S06, S08–S10 — GN sway + emission pulse cover motion without Meshy",
    }
    MESHY_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    MESHY_QUEUE.write_text(json.dumps(q, indent=2), encoding="utf-8")


def main():
    report = {"blender": bpy.app.version_string, "scenes": []}
    enable_addons(report)
    write_meshy_optional_queue()

    ng = build_wind_sway_group("GN_WindSway")
    report["node_group"] = ng.name

    for sc_name, cfg in SCENE_MOTION.items():
        sc = bpy.data.scenes.get(sc_name)
        if not sc:
            report["scenes"].append({"scene": sc_name, "status": "missing"})
            continue
        print(f"MOTION {sc_name}", flush=True)
        report["scenes"].append(process_scene(sc, cfg, ng))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    out = Path(os.environ.get("AFRICA_OUT_BLEND", str(OUT_BLEND)))
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    print("SAVED", out, flush=True)
    print("REPORT", REPORT, flush=True)
    print("MESHY_OPTIONAL", MESHY_QUEUE, flush=True)


if __name__ == "__main__":
    main()
