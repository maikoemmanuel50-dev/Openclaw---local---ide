# AGENTS.md — Africa Season 1 Local IDE

Standalone workspace for the "Africa Season 1 — Silicon Savannah" production
local IDE. Reorganized out of the live `Africa Season 1` folder; the live
production folder remains the source of truth for renders and running jobs.

## What lives here

- `openclaw_ide/` — the IDE web app (server.py, app.js, index.html, style.css).
- `scripts/` — local Qwen client, watcher/assemble/render helpers.
- `docs/`, `templates/`, `blend/`, `.cursor/`, `assets/` — project assets and
  reference material (HDRI, audio, textures, diagrams, icons, yellow-ball SVGs).
- Root `.py` / `.ps1` / `.bat` files — assemble, render, and delivery scripts.
- `*._log.txt` — historical production logs (see `.gitignore`).

## How to run the IDE

```
START_OPENCLAW_IDE.bat
```

Starts the multi-threaded server on `http://127.0.0.1:8765` and opens the
browser. Requires Ollama running on port 11434 (default model
`qwen2.5-coder:14b`).

Environment overrides (set before launching):

- `AFRICA_WORKSPACE` — workspace root (default: this folder).
- `AFRICA_RENDER_ROOT` — where render progress is read from
  (default: live `Africa Season 1\renders`; scene progress shows live without
  copying 2GB of frames).
- `AFRICA_QWEN_HOST` / `AFRICA_QWEN_MODEL` — Ollama host / model.

Server behavior:

- On startup it warms up the Ollama model (`keep_alive=-1`) in a background
  thread so the first chat does not cold-load — the model stays resident.
- `/api/logs/tail` decodes log files robustly (UTF-16 BOM, misaligned appends,
  UTF-8 with stray bad bytes) — the tail window is scored and the cleanest
  decode is shown.

## Agentic executor (in-IDE)

`server.py` exposes a gated agent layer so the local Qwen model can actually
act on the pipeline, with OpenClaw as the escalation layer for complex work.

Endpoints:

- `POST /api/chat` — multi-round tool loop (`_run_agent_loop`, max 6 rounds).
  Ollama `tools` calling; handles native `tool_calls` AND models like
  `qwen2.5-coder:14b` that print tool-call JSON inside `content` (regex
  fallback strips the JSON and keeps the prose).
- `POST /api/exec` — run a gated action by key (see `EXEC_ACTIONS`).
- `POST /api/agent/tools` — list actions / shell probes / gate state.
- `POST /api/escalate` — delegate a task to the OpenClaw gateway agent.

Actions (`EXEC_ACTIONS`) with gates: `ping_qwen`, `qwen_chat` (ungated);
`assemble_final` / `assemble_with_audio` / `assemble_kinetic_preview`
(`gate_cpu`); `render_mp4` / `render_all_scenes` (`gate_blender`);
`render_4k` / `run_1080_then_4k` (`gate_4k_hold`). Gated refusal returns
`BLOCKED_BY_GATE` with the reason. Deliverable actions are `terminal` — a
successful run returns immediately without a follow-up LLM round.

Read-only shell probes (`ALLOWED_SHELL_PATTERNS`): blender process, port
18789, renders list, masters pngs, disk, network status. Anything else is
refused — the model never runs arbitrary commands.

Escalation (`escalation_openclaw`): invokes the OpenClaw CLI shim
`C:\Users\HP\AppData\Roaming\npm\openclaw.cmd agent --json --agent main`
(full path + `shell=True` — bare `openclaw` fails with WinError 2 on .cmd
shims). Parses `result.payloads[].text` from the JSON envelope; the local
Qwen agent treats a successful escalation as terminal (its reply is the
answer).

Agent loop observations:

- `qwen2.5-coder:14b` does NOT emit native `message.tool_calls`; it prints
  JSON tool blocks in content. The content parser is the primary path.
- First escalation round takes ~45s (gateway warm) + model think time; a
  full escalate-through-agent chat is ~2-3 min. Frontend watchdog is 660s
  (`app.js`); the loop has a 400s wall-clock hard cap so it never outlives
  the frontend.
- The agent loop (`_run_agent_loop`) converges via heuristics: max 12 rounds,
  stuck-loop detection (identical tool+args repeated), a BLOCKED_BY_GATE
  streak stops the loop (never starts a 2nd GPU job), and it stops once ALL
  tools have been called AND the model produced prose. Rounds that resolve
  (`escalate_openclaw` / terminal actions) short-circuit immediately.
- When a gated action is blocked while Blender renders, the loop returns a
  "wait for the job to finish" message instead of churning — re-run once the
  render completes.
- The OpenClaw agent's own reply style may be `update_goal`-style JSON — it
  is still the gateway's answer, returned verbatim.

## Live production facts (as of this handoff)

- Live renders root: `C:\Users\HP\OneDrive\The Vault\Africa Season 1\renders`.
- Scenes 01 and 02 are complete (`01_ColdOpen.mp4`, `02_Context2007.mp4`).
- Scene 03 (`03_Beat1_Hubs`) is the active render; Blender runs the Cycles job.
- Watcher daemon: `wait_hq_assemble.ps1` hearts every ~2 min, assembles when
  10/10 scenes are complete.
- Gate rules: Blender 5.1.2 only, 4K HOLD (render 1080 first), one GPU job at a
  time, Yellow Ball identity #FFD54F (eliminated from the frame), protect
  already-completed clips and stats holds.
- Do NOT start a second GPU job while Blender is actively rendering.

## Connected tools

OpenClaw CLI, Local Qwen 2.5, Blender 5.1 MCP, DaVinci Resolve MCP (bridge,
port 49632), Composio (Canva `airway-sasin`).

## Conventions

- Only Blender 5.1.2 for Cycles renders.
- 1080P renders first; keep 4K HOLD in effect until full 1080 delivery is done.
- Never copy the live `renders` tree into this workspace — read progress from
  `AFRICA_RENDER_ROOT` instead.