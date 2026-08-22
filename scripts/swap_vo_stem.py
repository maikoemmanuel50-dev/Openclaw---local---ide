"""
Swap the active A1 VO stem, then rebuild Fairlight stems + Resolve A1.

Active lock file: assets/audio/vo/episode_01_vo.wav
  (currently a copy of the placeholder — timing lock for picture/mix)

Usage:
  # After recording final performance:
  #   copy your take over assets/audio/vo/episode_01_vo.wav
  python scripts/swap_vo_stem.py

  # Or pass a source wav:
  python scripts/swap_vo_stem.py path/to/final_take.wav
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
VO_DIR = os.path.join(PROJECT, "assets", "audio", "vo")
ACTIVE = os.path.join(VO_DIR, "episode_01_vo.wav")
MARKER = os.path.join(VO_DIR, "ACTIVE_VO.txt")
FAIRLIGHT = os.path.join(PROJECT, "scripts", "resolve_fairlight_overnight.py")


def main() -> int:
    if len(sys.argv) > 1:
        src = os.path.abspath(sys.argv[1])
        if not os.path.isfile(src):
            print(f"Missing source: {src}")
            return 1
        shutil.copy2(src, ACTIVE)
        print(f"Copied -> {ACTIVE}")
    if not os.path.isfile(ACTIVE):
        print(f"Missing active VO: {ACTIVE}")
        return 1
    with open(MARKER, "w", encoding="utf-8") as f:
        f.write(
            "ACTIVE_VO=assets/audio/vo/episode_01_vo.wav\n"
            "SOURCE=user_swap\n"
            "NOTE=Re-run Fairlight after swap; A2 sidechain duck still manual in UI\n"
        )
    print("Rebuilding Fairlight stems + Resolve A1...")
    r = subprocess.call([sys.executable, FAIRLIGHT], cwd=PROJECT)
    print(f"fairlight exit={r}")
    return r


if __name__ == "__main__":
    raise SystemExit(main())
