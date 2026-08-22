"""
Render motion-review stills for S01 / S06 / S07 from object_motion_preview blend.
CPU viewport render — safe while HQ GPU batch runs.

Run:
  blender -b blend/africa_s1_object_motion_preview.blend -P scripts/blender_motion_scrub_review.py
"""
from __future__ import annotations

import json
from pathlib import Path

import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
OUT = PROJECT / "renders" / "quality" / "motion_review"
REPORT = OUT / "motion_scrub_report.json"

# Scene → frames to scrub (mid + motion peak)
REVIEW = {
    "01_ColdOpen": [1, 360, 720, 900, 1080],
    "06_Beat2_Solar": [1, 240, 480, 720, 900],
    "07_Beat3_Gap": [1, 300, 600, 720, 900, 1080],
}


def setup_render():
    scene = bpy.context.scene
    # EEVEE = fast CPU/GPU preview for motion scrub stills (HQ-safe, not master)
    scene.render.engine = "BLENDER_EEVEE"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 4
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.film_transparent = False


def render_frame(sc: bpy.types.Scene, frame: int, dest: Path) -> dict:
    sc.frame_set(frame)
    bpy.context.view_layer.update()
    sc.render.filepath = str(dest.with_suffix(""))
    bpy.ops.render.render(write_still=True)
    ok = dest.with_suffix(".png").is_file() or dest.is_file()
    actual = dest.with_suffix(".png") if dest.with_suffix(".png").is_file() else dest
    return {
        "scene": sc.name,
        "frame": frame,
        "path": str(actual) if ok else None,
        "ok": ok,
        "walker": bpy.data.objects.get("MOTION_Walker_S07") is not None if sc.name == "07_Beat3_Gap" else None,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    setup_render()
    rows = []
    for sc_name, frames in REVIEW.items():
        sc = bpy.data.scenes.get(sc_name)
        if not sc:
            rows.append({"scene": sc_name, "error": "missing"})
            continue
        bpy.context.window.scene = sc
        for f in frames:
            f = min(max(1, f), sc.frame_end)
            dest = OUT / f"{sc_name}_f{f:04d}.png"
            if dest.is_file() and dest.stat().st_size > 10_000:
                rows.append({"scene": sc_name, "frame": f, "path": str(dest), "ok": True, "skipped": True})
                print(f"SKIP {sc_name} f{f} (exists)", flush=True)
                continue
            rows.append(render_frame(sc, f, dest))
            print(f"REVIEW {sc_name} f{f}", flush=True)

    REPORT.write_text(json.dumps({"frames": rows, "blend": bpy.data.filepath}, indent=2), encoding="utf-8")
    print("REPORT", REPORT, flush=True)


if __name__ == "__main__":
    main()
