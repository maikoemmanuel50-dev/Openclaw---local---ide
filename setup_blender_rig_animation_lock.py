"""
Africa S1 — Blender rig + animation hygiene lock (post-HQ).

Enforces practices from the curated tutorial pack in
docs/BLENDER_RIG_ANIM_RESOURCES.md (Ryan King, CG Geek, Crashsune,
ProductionCrate, Blender Guru, CBaileyFilm, SharpWind, Rigify shorts, etc.).

SAFE: run AFTER HQ batch finishes.
  blender -b blend/africa_s1_master_v01.blend -P setup_blender_rig_animation_lock.py
"""
from __future__ import annotations

import json
from pathlib import Path

import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
REPORT = PROJECT / "renders" / "quality" / "rig_animation_lock_report.json"
FPS = 24

HERO_PREFIXES = ("Sasa_", "YB_", "YB_Rig_", "YB_Body_", "YB_Head_")


def enable_rigify() -> bool:
    try:
        import addon_utils

        addon_utils.enable("rigify", default_set=True, persistent=True)
        return "rigify" in bpy.context.preferences.addons.keys()
    except Exception as e:
        print(f"Rigify enable skip: {e}")
        return False


def ensure_object_mode():
    try:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass


def apply_transforms(obj: bpy.types.Object) -> bool:
    """Apply Loc/Rot/Scale before skinning (60s-rig shorts / Rigify guides)."""
    if obj.type not in {"MESH", "EMPTY", "ARMATURE"}:
        return False
    if obj.parent and obj.parent_type == "BONE":
        return False  # bone-parented heads keep local offset
    try:
        ensure_object_mode()
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        return True
    except Exception as e:
        print(f"  apply_transforms skip {obj.name}: {e}")
        return False


def ease_all_fcurves(id_data) -> int:
    """Ryan King / CG Geek / CBaileyFilm: BEZIER ease, no LINEAR pops."""
    n = 0
    ad = getattr(id_data, "animation_data", None)
    if not ad or not ad.action:
        return 0
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points:
            if kp.interpolation == "LINEAR":
                kp.interpolation = "BEZIER"
            if kp.interpolation == "BEZIER":
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"
            n += 1
    return n


def add_cycles_modifier(id_data, data_paths_substr: tuple[str, ...], cycles: int = 0) -> int:
    """Idle bob/breath: Graph Editor Cycles modifier (not endless duplicated keys)."""
    ad = getattr(id_data, "animation_data", None)
    if not ad or not ad.action:
        return 0
    added = 0
    for fc in ad.action.fcurves:
        if not any(s in fc.data_path for s in data_paths_substr):
            continue
        if any(m.type == "CYCLES" for m in fc.modifiers):
            continue
        # Only cycle short idle ranges (≤ 48 keys worth of motion)
        if len(fc.keyframe_points) < 2 or len(fc.keyframe_points) > 24:
            continue
        m = fc.modifiers.new(type="CYCLES")
        if cycles > 0:
            m.cycles_after = cycles
            m.cycles_before = 0
        m.mode_after = "REPEAT"
        m.mode_before = "REPEAT"
        added += 1
    return added


def armature_before_subsurf(obj: bpy.types.Object) -> bool:
    """Deform then smooth — standard character pipeline."""
    mods = list(obj.modifiers)
    arm_i = next((i for i, m in enumerate(mods) if m.type == "ARMATURE"), None)
    sub_i = next((i for i, m in enumerate(mods) if m.type == "SUBSURF"), None)
    if arm_i is None or sub_i is None or arm_i < sub_i:
        return False
    # Move armature up
    while arm_i > sub_i:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.modifier_move_up(modifier=obj.modifiers[arm_i].name)
        except Exception:
            # Fallback: recreate order by moving subsurf down conceptually — skip if ops fail
            return False
        mods = list(obj.modifiers)
        arm_i = next((i for i, m in enumerate(mods) if m.type == "ARMATURE"), None)
        sub_i = next((i for i, m in enumerate(mods) if m.type == "SUBSURF"), None)
        if arm_i is None or sub_i is None:
            break
    return True


def ensure_fps(sc: bpy.types.Scene):
    sc.render.fps = FPS
    sc.render.fps_base = 1.0


def name_action(obj: bpy.types.Object, prefix: str):
    ad = obj.animation_data
    if ad and ad.action and not ad.action.name.startswith(prefix):
        ad.action.name = f"{prefix}{obj.name}"[:63]


def is_hero(obj: bpy.types.Object) -> bool:
    return any(obj.name.startswith(p) for p in HERO_PREFIXES)


def lock_scene(sc: bpy.types.Scene) -> dict:
    ensure_fps(sc)
    report = {
        "scene": sc.name,
        "fps": sc.render.fps,
        "eased": 0,
        "applied": [],
        "cycles": 0,
        "mod_order": [],
        "actions": [],
    }
    try:
        if getattr(bpy.context, "window", None):
            bpy.context.window.scene = sc
    except Exception:
        pass

    for obj in list(sc.objects):
        if not is_hero(obj):
            continue
        if obj.type == "MESH" and not (obj.parent and obj.parent_type == "BONE"):
            if apply_transforms(obj):
                report["applied"].append(obj.name)
        if obj.type == "MESH":
            if armature_before_subsurf(obj):
                report["mod_order"].append(obj.name)
        report["eased"] += ease_all_fcurves(obj)
        if obj.type == "ARMATURE":
            report["eased"] += ease_all_fcurves(obj)
            # Pose bones don't have their own action usually — on object
            report["cycles"] += add_cycles_modifier(obj, ("rotation_euler", "location"), cycles=0)
        if obj.data and hasattr(obj.data, "shape_keys") and obj.data.shape_keys:
            report["eased"] += ease_all_fcurves(obj.data.shape_keys)
        prefix = "Sasa_" if obj.name.startswith("Sasa_") else "YB_"
        name_action(obj, prefix)
        if obj.animation_data and obj.animation_data.action:
            report["actions"].append(obj.animation_data.action.name)

    return report


def validate_bindings() -> list:
    """Flag meshes that look like YB bodies without armature modifiers."""
    issues = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        if not (obj.name.startswith("YB_Body_") or obj.get("yb_body")):
            continue
        has_arm = any(m.type == "ARMATURE" and m.object for m in obj.modifiers)
        if not has_arm:
            issues.append(f"{obj.name}: missing Armature modifier")
        elif not obj.vertex_groups:
            issues.append(f"{obj.name}: no vertex groups (weights)")
    return issues


def main():
    print("=== Blender Rig + Animation Lock ===")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    ensure_object_mode()
    rigify = enable_rigify()
    scenes = []
    for sc in bpy.data.scenes:
        if sc.name[:2].isdigit() or sc.name.startswith("0"):
            scenes.append(lock_scene(sc))
        elif any(k in sc.name for k in ("Cold", "Beat", "Closer", "End", "Context")):
            scenes.append(lock_scene(sc))

    # Also sweep all numbered episode scenes by known names
    known = [
        "01_ColdOpen",
        "02_Context2007",
        "03_Beat1_Hubs",
        "04_Beat1_Phone",
        "05_Beat2_Money",
        "06_Beat2_Solar",
        "07_Beat3_Gap",
        "08_Beat3_SecondaryCity",
        "09_Closer",
        "10_EndCard",
    ]
    done = {s["scene"] for s in scenes}
    for name in known:
        if name in bpy.data.scenes and name not in done:
            scenes.append(lock_scene(bpy.data.scenes[name]))

    out = {
        "rigify_enabled": rigify,
        "refs_doc": "docs/BLENDER_RIG_ANIM_RESOURCES.md",
        "binding_issues": validate_bindings(),
        "scenes": scenes,
        "note": "Hygiene only — does not start 4K. Re-run ball/YB setup first if objects missing.",
    }
    REPORT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"SAVED {bpy.data.filepath}")
    print(f"REPORT {REPORT}")
    print("RIG_ANIMATION_LOCK_DONE")


if __name__ == "__main__":
    main()
