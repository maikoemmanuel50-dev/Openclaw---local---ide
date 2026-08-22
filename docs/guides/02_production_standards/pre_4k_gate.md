---
title: PRE-4K Gate
category: Production Standards
tags: 4k, gate, hold, blender-5.1, one-gpu-job, delivery
source: docs/PRE_4K_GATE.md, docs/PRE_4K_ADDITIONAL_DELIVERABLES.md, STATUS_4K_HOLD.txt
---

# PRE-4K Gate (4K delivery is LOCKED)

4K is gated. Nothing 4K-related (resolution, presets, exports) runs until every
open item in `docs/PRE_4K_GATE.md` is explicitly closed or waived.

## Hard rules

1. Do NOT start 4K until the gate is clear — refuse "just render 4K" while open.
2. **Blender 5.1.2 only.** Never Blender 4.4 (`.blend` is 5.1-format).
   `STATUS_4K_HOLD.txt` is binding until removed.
3. One heavy GPU job at a time (Blender OR Resolve Deliver). Never restart an
   in-progress render from frame 0.
4. 1080p completion first: full 1080 delivery requires scenes 01–10 verified,
   VO/Fairlight locked, master assembled, visual QC passed.
5. 4K specs (when gate clears): 3840x2160 @ 24fps, H.264 High 35–45 Mbps,
   same audio targets (−14 LUFS, ≤ −1 dBTP).

## Current status

- `STATUS_4K_HOLD.txt`: `4K_HOLD=1`, reason `PRE_4K_GATE open`.
- Live production state tracks open gate rows — read `PRODUCTION_STATUS.md`.
- Completing 1080 delivery (D5 re-render → D8 gate steps) is the path to open
  the gate. Do not mark 4K done before files are verified (definition of done).