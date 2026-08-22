# PROMPT — Deliverables Progress & Path to Completion (Episode 1)

Paste this into the IDE chat box (or use the 📊 **Deliverables Feedback** chip).
The local agent compiles a natural-language progress report on where the
Episode 1 production stands and exactly what remains until **full completion**
(the complete production of Africa Season 1 — Episode 1, not just this render).

## Objective
Give feedback on project deliverables progress and the path remainder to
project completion. Completion = episode 1 is fully produced: all 10 scenes
rendered, VO/audio locked, final master assembled, visual QC passed, 1080/4K
delivery staged and verified.

## Steps (use tools; do NOT just reply from memory)
1. **Gather state** with read-only tools:
   - `production_status` (server-side state: scene progress, clips, blender,
     power, vision)
   - `read_log` on `PRODUCTION_STATUS.md`, `STATUS_HOURLY_LATEST.txt`,
     `STATUS_LIVE_DELIVERY.txt`, `fairlight_locked_vo_log.txt`,
     `wait_hq_assemble_log.txt`
   - `shell_probe` aliases: `renders list`, `masters pngs`, `blender process`
2. **Score each deliverable** with evidence, as `DONE / IN_PROGRESS / PENDING`:
   - Scenes rendered 01–10 (mp4 ready or frames vs target)
   - VO / audio stems locked (Fairlight)
   - Final episode master assembled via `assemble_final` / `assemble_with_audio`
   - Visual QC passed per scene (qwen2.5vl via `inspect_image`)
   - 4K production (upgrade after 1080 clears — HOLD)
   - Delivery artifacts staged under `STATUS_LIVE_DELIVERY.txt`
3. **Compute the remaining path to completion**: an ordered, numbered checklist
   of what is left, with dependencies (e.g. Scene 03 → 04–10 → 10/10 assembly →
   audio/VO check → 1080 QC → 4K → delivery verify) and a rough ETA per step.
4. **Output**: concise markdown report — one bullet per deliverable with its
   DONE/IN_PROGRESS/PENDING status and the evidence, the "Remaining path to
   Episode 1 completion" checklist, and a final one-line status
   (scene + frames, ready clips 0/10, blender idle/busy, power %, next step).

## Rules
- This is a feedback/report mission: read chart only. Do NOT start any GPU
  job, do NOT run assemble/render, do NOT trigger escalation.
- Respect the gates: one GPU job at a time, 4K HOLD, Blender 5.1.2 only.
- Return natural language, not raw tool JSON.