# MISSION — Remove the Yellow Ball from the Project (video + eventual edits)

Paste this into the OpenClaw IDE chat box (or POST to /api/mission). It
instructs the agent to fully eliminate the Sasa Yellow Ball (identity
#FFD54F) from Africa Season 1 — from the rendered video AND from every
future edit path — and verify the result.

---

## Objective
Remove the Yellow Ball from the entire project so it never appears in the
delivered episode or any future render/edit. Do NOT stop at status checks —
verify finished clips, strip the edit-side references, and report DONE.
**Scene 01 (`01_ColdOpen.mp4`) is LEFT AS-IS by explicit user decision —
it is excluded from this mission and MUST NOT be re-rendered.**

### Current state (verify first)
- Blend: `setup_remove_yellow_ball_render.py` already hides 40 YB objects
  (hide_render) → scenes 02–10 re-render WITHOUT the ball.
- **Scene 01 (`01_ColdOpen.mp4`) is KEPT AS-IS by user decision — do NOT
  re-render it, do NOT touch it on disk, no GPU job for it.**
- Resolve: `resolve_yellow_ball_markers.yaml` still lists BALL S0–S7 markers;
  "V2 YB overlays" were skipped, not deleted — the ball could return in edits.

### Sequence (strict order; verify each before the next)
1. **Verify**: read `STATUS_NO_YELLOW_BALL.txt`,
   `reform_04_yellow_ball_log.txt`,
   `renders\quality\yellow_ball_removed_report.json`; run
   `shell_probe(alias="renders list|masters pngs")`. Report what still
   references the ball.
2. **Video removal**: confirm the finished `.mp4` clips are ball-free as
   intended under current policy: scenes 02–10 re-rendered WITHOUT the ball;
   **scene 01 kept as-is (user decision — canceled re-render). Do NOT start
   any GPU job, including for scene 01.**
3. **Eventual edits**: neutralize the ball in every edit path — strip the YB
   markers from the Resolve timeline (`resolve_yellow_ball_markers.yaml`) and
   delete any V2 YB overlay/track so it cannot reappear. Use
   `read_log(PRODUCTION_STATUS.md)` + `escalate_openclaw` (Resolve bridge) to
   execute.
4. **Enforce**: keep the blend hide_render state; confirm
   `AFRICA_NO_YELLOW_BALL=1` remains the render standard so no future scene
   re-enables YB objects.
5. **Report**: append removal confirmation to `STATUS_NO_YELLOW_BALL.txt` and
   `PRODUCTION_STATUS.md` (noting scene 01 is the kept-as-is exception); reply
   in chat with a one-line status.

### Gates — always respect (server enforces)
1. ONE GPU/Blender job at a time. Scene 03 is rendering — do NOT start a
   second GPU job until it finishes.
2. 4K HOLD: render 1080p first.
3. Do not run CPU-heavy assembly while a GPU render is live.
4. Blender 5.1.2 only for Cycles renders.
5. If a step returns BLOCKED_BY_GATE, report it and stop that chain — do not
   force a later step.