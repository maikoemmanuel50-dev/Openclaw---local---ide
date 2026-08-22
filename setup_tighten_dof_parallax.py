"""
Tighten DOF on parallax / flat illustrated plates — sharper V1 masters.

Parallax scenes: minimum f/8 (was f/4–5.6 → mushy on PNG planes).
Flat plate scenes (kiosk, phone CU): DOF off for full sharpness.

Run before Cycles re-render:
  blender -b blend/africa_s1_master_v01.blend -P setup_tighten_dof_parallax.py
"""
from __future__ import annotations

import json
from pathlib import Path

import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
REPORT = PROJECT / "renders" / "quality" / "dof_tighten_report.json"

PARALLAX = {
    "01_ColdOpen": 8.0,
    "03_Beat1_Hubs": 8.0,
    "06_Beat2_Solar": 8.0,
    "08_Beat3_SecondaryCity": 8.0,
    "09_Closer": 7.1,
}
FLAT_OFF = {"02_Context2007", "04_Beat1_Phone", "10_EndCard"}
DEFAULT_MIN = 6.3


def tighten_scene(sc: bpy.types.Scene) -> dict:
    cam = sc.camera
    if not cam or not cam.data:
        return {"scene": sc.name, "skip": "no camera"}
    d = cam.data
    before = {"dof": d.dof.use_dof, "fstop": d.dof.aperture_fstop}
    if sc.name in FLAT_OFF:
        d.dof.use_dof = False
        after = {"dof": False, "fstop": None}
    elif sc.name in PARALLAX:
        d.dof.use_dof = True
        d.dof.aperture_fstop = max(float(d.dof.aperture_fstop or 4.0), PARALLAX[sc.name])
        after = {"dof": True, "fstop": d.dof.aperture_fstop}
    else:
        d.dof.use_dof = True
        d.dof.aperture_fstop = max(float(d.dof.aperture_fstop or 4.0), DEFAULT_MIN)
        after = {"dof": True, "fstop": d.dof.aperture_fstop}
    return {"scene": sc.name, "before": before, "after": after}


def main():
    rows = [tighten_scene(sc) for sc in bpy.data.scenes if sc.name.startswith(("0", "1"))]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"scenes": rows}, indent=2), encoding="utf-8")
    bpy.ops.wm.save_mainfile()
    print("DOF_TIGHTEN", REPORT, flush=True)


if __name__ == "__main__":
    main()
