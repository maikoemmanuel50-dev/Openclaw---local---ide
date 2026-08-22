"""
AFRICA S1 — Yellow Ball entrypoint (redirect).

Canonical TED-Ed physics + photoreal nodes + squash/stretch rig:
  setup_yellow_ball_teded_physics.py

Run:
  blender -b blend/africa_s1_master_v01.blend -P setup_yellow_ball.py
"""
import runpy
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).with_name("setup_yellow_ball_teded_physics.py")
    runpy.run_path(str(target), run_name="__main__")
