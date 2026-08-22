"""
Africa S1 — Arch Comm IV Blender setup lock (JKUAT Blender Class 01–16).

Source media: Telegram/Blender_Class 01..16 (Arch Comm iv pack).
Frame notes: docs/telegram_imports/arch_comm_iv_frames/
Doc: docs/ARCH_COMM_IV_LOCK.md

Enforces classroom ArchViz hygiene on Blender 5.1 (not 3.0 class UI):
  - Cycles + GPU Compute + OptiX/OIDN denoise (class: Cycles GPU + Denoise)
  - Adaptive noise thresholds (class: viewport 0.1 / render 0.01) with production samples
  - Metric units (meters) + real-world scale awareness
  - Collections: ENV / LIGHTS / CAMERAS / MODEL_ADDITIONS / HERO
  - Principled BSDF PBR: Image Texture → Base Color; Normal Map; Height→Bump
  - Prefer project textures (assets/textures, Poly Haven) over missing magenta paths
  - Soft Area lights for env fill (class cafe/bar lighting language)
  - Does NOT invent faces or competing heroes — yellow ball #FFD54F remains sole hero

SAFE timing: BEFORE force HQ re-render (wired in run_full_reformulation.ps1).
Do not dual-open master .blend during an active HQ -b job.

  & "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" `
    -b "blend\\africa_s1_master_v01.blend" -P "setup_arch_comm_iv_lock.py"
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import bpy
import addon_utils

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
TEX_ROOT = PROJECT / "assets" / "textures"
POLYHAVEN = TEX_ROOT / "polyhaven"
HDRI_DIR = PROJECT / "assets" / "hdri"
REPORT = PROJECT / "renders" / "quality" / "arch_comm_iv_lock_report.json"

HERO_PREFIXES = ("Sasa_", "YB_", "YB_Rig_", "YB_Body_", "YB_Head_", "YellowBall")
COLLECTION_NAMES = (
    "HERO",
    "ENV",
    "LIGHTS",
    "CAMERAS",
    "MODEL_ADDITIONS",
)


def is_hero(obj: bpy.types.Object) -> bool:
    n = obj.name
    return any(n.startswith(p) or p in n for p in HERO_PREFIXES)


def ensure_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def link_obj_to_collection(obj: bpy.types.Object, col: bpy.types.Collection):
    for c in list(obj.users_collection):
        try:
            c.objects.unlink(obj)
        except Exception:
            pass
    if obj.name not in col.objects:
        col.objects.link(obj)


def organize_collections(report: dict):
    """Ensure Arch Comm-style collections exist; soft-link without stripping other links."""
    cols = {n: ensure_collection(n) for n in COLLECTION_NAMES}
    moved = {"HERO": 0, "ENV": 0, "LIGHTS": 0, "CAMERAS": 0, "MODEL_ADDITIONS": 0}

    def already_sorted(obj: bpy.types.Object) -> bool:
        return any(c.name in COLLECTION_NAMES for c in obj.users_collection)

    for obj in list(bpy.data.objects):
        if already_sorted(obj):
            continue
        target = None
        key = None
        if obj.type == "CAMERA":
            target, key = cols["CAMERAS"], "CAMERAS"
        elif obj.type == "LIGHT":
            target, key = cols["LIGHTS"], "LIGHTS"
        elif is_hero(obj):
            target, key = cols["HERO"], "HERO"
        elif obj.type == "MESH":
            if obj.name.startswith(("B_", "Prop_", "Asset_", "SK_")):
                target, key = cols["MODEL_ADDITIONS"], "MODEL_ADDITIONS"
            else:
                target, key = cols["ENV"], "ENV"
        if target is not None and obj.name not in target.objects:
            try:
                target.objects.link(obj)
                moved[key] += 1
            except Exception:
                pass
    report["collections"] = moved


def set_metric_units(sc: bpy.types.Scene):
    u = sc.unit_settings
    u.system = "METRIC"
    u.scale_length = 1.0
    try:
        u.length_unit = "METERS"
    except Exception:
        pass


def configure_cycles_arch(sc: bpy.types.Scene, report: dict):
    """Class 01/03/10: Cycles + GPU + Denoise + noise thresholds."""
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "GPU"
    # Production samples (class used 20 for demos — too low for episode plates)
    if hasattr(cy, "use_adaptive_sampling"):
        cy.use_adaptive_sampling = True
    if hasattr(cy, "adaptive_threshold"):
        cy.adaptive_threshold = 0.01  # class render Noise Threshold
    if hasattr(cy, "samples"):
        cy.samples = max(int(getattr(cy, "samples", 128) or 128), 256)
    if hasattr(cy, "preview_samples"):
        cy.preview_samples = 64
    if hasattr(cy, "use_denoising"):
        cy.use_denoising = True
    if hasattr(cy, "use_preview_denoising"):
        cy.use_preview_denoising = True
    # Prefer OptiX then OIDN
    for dn in ("OPTIX", "OPENIMAGEDENOISE"):
        try:
            cy.denoiser = dn
            break
        except Exception:
            continue
    # Film / color — keep AgX if already set by photoreal stack
    try:
        sc.view_settings.view_transform = "AgX"
    except Exception:
        pass
    report["cycles"] = {
        "engine": sc.render.engine,
        "device": getattr(cy, "device", None),
        "samples": getattr(cy, "samples", None),
        "adaptive_threshold": getattr(cy, "adaptive_threshold", None),
        "denoiser": getattr(cy, "denoiser", None),
        "use_denoising": getattr(cy, "use_denoising", None),
    }


def enable_gpu_devices(report: dict):
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
    except Exception as e:
        report["gpu"] = {"ok": False, "err": str(e)}
        return
    backend = None
    for b in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = b
            prefs.get_devices()
            n = 0
            for d in prefs.devices:
                name = (d.name or "").upper()
                if d.type in ("OPTIX", "CUDA") and any(
                    k in name for k in ("NVIDIA", "GEFORCE", "RTX", "QUADRO")
                ):
                    d.use = True
                    n += 1
                elif d.type == "CPU":
                    d.use = True
            if n:
                backend = b
                break
        except Exception:
            continue
    report["gpu"] = {"backend": backend, "ok": backend is not None}


def find_node(nodes, bl_idname: str):
    for n in nodes:
        if n.bl_idname == bl_idname or n.type == bl_idname.replace("ShaderNode", "").upper():
            return n
    return None


def principled_of(mat: bpy.types.Material):
    if not mat or not mat.use_nodes:
        return None
    for n in mat.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            return n
    return None


def ensure_pbr_links(mat: bpy.types.Material) -> dict:
    """Class 11/14: Image Texture → Principled; Normal Map; Height bump."""
    info = {"name": mat.name, "fixed": [], "skipped": None}
    if is_hero_mat(mat.name):
        info["skipped"] = "hero"
        return info
    if not mat.use_nodes:
        mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = principled_of(mat)
    if bsdf is None:
        info["skipped"] = "no_principled"
        return info
    out = find_node(nodes, "ShaderNodeOutputMaterial")
    if out is None:
        out = nodes.new("ShaderNodeOutputMaterial")
        out.location = (400, 0)
    if not any(l.to_node == out for l in links):
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        info["fixed"].append("output_link")

    # Collect image textures
    imgs = [n for n in nodes if n.type == "TEX_IMAGE" and n.image]
    if not imgs:
        return info

    def connected_to(sock_name: str) -> bool:
        sock = bsdf.inputs.get(sock_name)
        return bool(sock and sock.is_linked)

    # Heuristic role from filename
    def role(img_node) -> str:
        n = (img_node.image.name or "").lower()
        fp = (img_node.image.filepath or "").lower()
        s = n + " " + fp
        if any(k in s for k in ("nor", "normal", "nrm", "nor_gl")):
            return "normal"
        if any(k in s for k in ("rough", "rgh")):
            return "rough"
        if any(k in s for k in ("metal", "met")):
            return "metal"
        if any(k in s for k in ("ao", "occlusion", "arm")):
            return "ao"
        if any(k in s for k in ("height", "disp", "bump", "displacement")):
            return "height"
        if any(k in s for k in ("diff", "albedo", "col", "color", "base", "diffuse")):
            return "albedo"
        return "albedo"

    for img in imgs:
        r = role(img)
        if r == "albedo" and not connected_to("Base Color"):
            links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
            try:
                img.image.colorspace_settings.name = "sRGB"
            except Exception:
                pass
            info["fixed"].append("albedo")
        elif r == "rough" and not connected_to("Roughness"):
            # non-color
            try:
                img.image.colorspace_settings.name = "Non-Color"
            except Exception:
                pass
            links.new(img.outputs["Color"], bsdf.inputs["Roughness"])
            info["fixed"].append("rough")
        elif r == "metal" and "Metallic" in bsdf.inputs and not connected_to("Metallic"):
            try:
                img.image.colorspace_settings.name = "Non-Color"
            except Exception:
                pass
            links.new(img.outputs["Color"], bsdf.inputs["Metallic"])
            info["fixed"].append("metal")
        elif r == "normal" and not connected_to("Normal"):
            try:
                img.image.colorspace_settings.name = "Non-Color"
            except Exception:
                pass
            nmap = find_node(nodes, "ShaderNodeNormalMap")
            if nmap is None:
                nmap = nodes.new("ShaderNodeNormalMap")
                nmap.location = (-200, -300)
            if not nmap.inputs["Color"].is_linked:
                links.new(img.outputs["Color"], nmap.inputs["Color"])
            links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
            info["fixed"].append("normal")
        elif r == "height" and not connected_to("Normal"):
            try:
                img.image.colorspace_settings.name = "Non-Color"
            except Exception:
                pass
            bump = None
            for n in nodes:
                if n.type == "BUMP":
                    bump = n
                    break
            if bump is None:
                bump = nodes.new("ShaderNodeBump")
                bump.location = (-200, -450)
                bump.inputs["Strength"].default_value = 0.15
            if not bump.inputs["Height"].is_linked:
                links.new(img.outputs["Color"], bump.inputs["Height"])
            if not bsdf.inputs["Normal"].is_linked:
                links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
                info["fixed"].append("height_bump")
    return info


def is_hero_mat(name: str) -> bool:
    n = name.lower()
    return any(k in n for k in ("sasa", "yellow", "yb_", "yb-body", "ball"))


def remap_missing_images(report: dict):
    """Point broken image paths at project Poly Haven / textures when basename matches."""
    fixed = []
    missing = []
    catalog = {}
    for root in (POLYHAVEN, TEX_ROOT):
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".exr", ".hdr"}:
                catalog.setdefault(p.name.lower(), p)
                catalog.setdefault(p.stem.lower(), p)
    for img in bpy.data.images:
        fp = bpy.path.abspath(img.filepath) if img.filepath else ""
        exists = bool(fp) and os.path.isfile(fp)
        if exists:
            continue
        key = Path(img.filepath or img.name).name.lower()
        stem = Path(img.filepath or img.name).stem.lower()
        hit = catalog.get(key) or catalog.get(stem)
        if hit:
            img.filepath = str(hit)
            img.reload()
            fixed.append({"image": img.name, "to": str(hit)})
        else:
            missing.append(img.name)
    report["textures"] = {"remapped": fixed, "still_missing": missing[:40], "missing_count": len(missing)}


def ensure_area_fill_lights(report: dict):
    """Class 16: Area lights for soft interior/env fill — one soft key per scene if none."""
    added = []
    for sc in bpy.data.scenes:
        lights = [o for o in sc.objects if o.type == "LIGHT"]
        areas = [o for o in lights if o.data and o.data.type == "AREA"]
        if areas:
            continue
        # Add a soft overhead area fill (does not replace HDRI)
        data = bpy.data.lights.new(name=f"ACIV_AreaFill_{sc.name}", type="AREA")
        data.energy = 40.0
        data.size = 4.0
        try:
            data.shape = "RECTANGLE"
            data.size_y = 3.0
        except Exception:
            pass
        obj = bpy.data.objects.new(data.name, data)
        obj.location = (0.0, -2.0, 4.5)
        lights_col = ensure_collection("LIGHTS")
        if obj.name not in lights_col.objects:
            lights_col.objects.link(obj)
        added.append({"scene": sc.name, "light": obj.name})
    report["area_lights_added"] = added


def camera_arch_hygiene(report: dict):
    """Class 15: named cameras, sensor-ish lenses, keep DOF from other locks."""
    cams = []
    for obj in bpy.data.objects:
        if obj.type != "CAMERA":
            continue
        cam = obj.data
        # Prefer still / arch focal range if wildly fish-eyed
        if cam.lens and cam.lens < 24:
            cam.lens = 35.0
        cams.append({"name": obj.name, "lens": cam.lens})
    report["cameras"] = cams[:30]


def mesh_scale_audit(report: dict):
    """Class 04/07: real-world scale — flag extreme non-1 scales on env meshes."""
    weird = []
    for obj in bpy.data.objects:
        if obj.type != "MESH" or is_hero(obj):
            continue
        sx, sy, sz = obj.scale
        if max(abs(sx), abs(sy), abs(sz)) > 50 or min(abs(sx), abs(sy), abs(sz)) < 0.01:
            weird.append({"name": obj.name, "scale": [sx, sy, sz]})
    report["scale_outliers"] = weird[:40]


def enable_node_wrangler():
    try:
        addon_utils.enable("node_wrangler", default_set=True, persistent=True)
        return True
    except Exception:
        return False


def main():
    report = {
        "source": "Telegram/Blender_Class 01-16 (Arch Comm IV)",
        "blender": bpy.app.version_string,
        "scenes": [],
    }
    report["node_wrangler"] = enable_node_wrangler()
    enable_gpu_devices(report)
    organize_collections(report)

    for sc in bpy.data.scenes:
        bpy.context.window.scene = sc if hasattr(bpy.context, "window") else sc
        try:
            bpy.context.scene = sc  # type: ignore
        except Exception:
            pass
        set_metric_units(sc)
        configure_cycles_arch(sc, report)
        report["scenes"].append(sc.name)

    mat_fixes = []
    for mat in bpy.data.materials:
        info = ensure_pbr_links(mat)
        if info.get("fixed"):
            mat_fixes.append(info)
    report["materials_fixed"] = mat_fixes[:80]
    report["materials_fixed_count"] = len(mat_fixes)

    remap_missing_images(report)
    ensure_area_fill_lights(report)
    camera_arch_hygiene(report)
    mesh_scale_audit(report)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== setup_arch_comm_iv_lock ===")
    print(json.dumps({k: report[k] for k in ("gpu", "cycles", "collections", "materials_fixed_count", "textures")}, indent=2, default=str))
    print(f"Wrote {REPORT}")

    # Save if running on a filepath
    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
        print(f"Saved {bpy.data.filepath}")


if __name__ == "__main__":
    main()
