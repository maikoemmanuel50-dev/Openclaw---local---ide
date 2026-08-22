# Africa Season 1 — Episode 1 Completion Mission

Paste this into the OpenClaw IDE chat (or POST to /api/mission) to drive the
episode to full completion. It uses the routed dual-model system: qwen2.5-coder
(14b) executes all agentic/production work; qwen2.5vl (7b) handles every visual
QC pass. Remove the "Running from..." line before pasting if you prefer.

---

## MISSION: Complete Africa Season 1 Episode 1 to final delivery

### Objective
Drive the pipeline from its current state to **10/10 scenes rendered, VA/audio
locked, final episode master assembled, QC-passed, and delivery artifacts staged
under the live production folder**. Do NOT stop at partial milestones — the
mission is only complete when every deliverable below is verified DONE and
written to PRODUCTION_STATUS.md.

Running from workspace: C:\Users\HP\OneDrive\The Vault\Local ide
Live renders root: C:\Users\HP\OneDrive\The Vault\Africa Season 1\renders

### Current state (verify first with /api/status + /api/render/progress)
- 01_ColdOpen ✅, 02_Context2007 ✅
- 03_Beat1_Hubs → in progress (~35%, 379/1080 frames)
- 04..10 → queued
- Use `production_status`, `read_log`,
  `shell_probe(alias="renders list|masters pngs|blender process")`, and
  `escalate_openclaw` for anything Blender/Resolve/Canva/Composio heavy.

### Gate rules — ALWAYS respect (server enforces; never try to bypass)
1. ONE GPU/Blender job at a time. Blender is currently rendering Scene 03 —
   do NOT start a second GPU job until it finishes.
2. 4K HOLD: render 1080p first; keep 4K held until full 1080 delivery is done.
3. Do not run CPU-heavy assembly while a GPU render is live.
4. Blender 5.1.2 only for Cycles renders.
5. Yellow Ball identity #FFD54F: eliminated from the frame / enforced per
   reform_04_yellow_ball + reform_05_yb_body specs.
6. Protect already-completed clips and stats holds.

### Sequence (execute strictly in order; each step verified before the next)
1. **Inform-verify**: read PRODUCTION_STATUS.md, STATUS_HOURLY_LATEST.txt,
   session logs (sasa_hq_rerender_log.txt, wait_hq_assemble_log.txt).
   Report current scene/frame/clip counts.
2. **Scene 03 finish**: wait for the active Blender render to complete
   (poll `blender process` + `renders list`; re-run once the job finishes).
   Then render the remaining scenes 04→10 in order, one GPU job at a time,
   watching for frame/target and percent to advance.
3. **Visual QC every completed scene** using the 7B vision model
   (`inspect_image` tool or the /api/vision endpoint against the latest master
   frame): confirm expected framing, no Yellow Ball residue, no artifacts.
4. **Audio / VO**: confirm VO track locked (fairlight_locked_vo_log), detect
   issues, escalate to Resolve bridge as needed.
5. **Assembly**: once 10/10 scenes are ready, run the HQ assemble
   (`assemble_final` / `assemble_with_audio` / `assemble_kinetic_preview`) —
   only after the GPU job completes.
6. **4K production**: after the 1080p delivery is fully verified, run
   `render_4k` / `run_1080_then_4k` per the 4K HOLD gate.
7. **Final QC + delivery**: espouse live render progress, verify masters exist,
   stage delivery artifacts, and write the completion block to
   PRODUCTION_STATUS.md and STATUS_LIVE_DELIVERY.txt.

### HOURLY PROGRESS REPORT (mandatory)
Every hour on the hour (and at every major milestone), write an hourly report:
1. Append to **STATUS_HOURLY_LATEST.txt** in the exact existing single-line
   format, e.g.:
   `Africa S1 hourly - YYYY-MM-DD HH:MM | scene=03_Beat1_Hubs frame=1080/1080 clips=10/10 eta_h=0 batch=3 vo=True`
2. Then in chat, reply with a **one-line status**: current scene, frames,
   ready clips, Blender active/idle, battery, and what the next step is.
3. Keep the line short — it is polled by the IDE and other tools.

### Session scope
Work the mission start-to-finish; if a step is BLOCKED_BY_GATE, report the
reason and stop that chain (do not force later steps). Prefer fewer high-value
steps over many small ones. Escalate anything needing multi-step cross-app
execution (Blender MCP scripting, Resolve, Canva/Composio) via
`escalate_openclaw` with a precise task description; treat a successful
escalation as terminal.