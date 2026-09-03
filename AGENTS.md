# AGENTS.md — OpenClaw Local IDE (project-neutral)

The **OpenClaw Local IDE** is a project-neutral, multi-project local web IDE for
AI-assisted production work. It is intentionally **not tied to any one
project** — the Africa Season 1 production content was moved out (2026-09-03)
to `C:\Users\HP\OneDrive\The Vault\Youtube\Africa Season 1`.

## What lives here

- `openclaw_ide/` — the IDE web app (server.py, app.js, index.html, style.css).
- `START_OPENCLAW_IDE.bat` — launcher (starts the server and opens the browser).
- `.gitignore` — repo hygiene (the Africa S1 `.bak`/logs are gone).

## How to run the IDE

```
START_OPENCLAW_IDE.bat
```

Starts the multi-threaded server on `http://127.0.0.1:8765` and opens the
browser. Requires Ollama running on port 11434.

Environment overrides (set before launching):

- `AFRICA_QWEN_HOST` / `AFRICA_QWEN_MODEL` — Ollama host / model.

## Project model (multi-project, isolated)

The IDE is project-neutral: it hosts a **workspace switcher** and treats every
project as an isolated unit. Projects are registered (Restaurant, Jenga,
Africa Season 1, plus the current workspace) and each has its **own**:

- session history and prompt log
- agent traces and thinking stream
- session search index
- chat memory (`remember_project` / `remember_preference`)
- saved plans

Switching project changes `WORKSPACE_ROOT` (which files/scripts the file APIs
and agent actions operate on) but **never** the static web root — the IDE's
HTML/JS/CSS always comes from `WEB_ROOT` (this repo's `openclaw_ide/`), so a
project switch can never break the UI.

## Runtime / server notes

- Server: `openclaw_ide/server.py` (`ThreadingHTTPServer` on 127.0.0.1:8765),
  `watchdog_ide.ps1` polls `/api/status` and relaunches if dark.
- `/api/chat` runs a multi-round agent tool loop against local Ollama
  (`_run_agent_loop`, wall-clock cap 500s, frontend watchdog 660s). Concurrent
  agent loops are serialized by `agent_semaphore`; a busy second request is told
  to wait. `POST /api/chat/cancel` stops an in-flight loop.
- Gated executable actions are allowlisted (`EXEC_ACTIONS`), resolved against
  the **active project's** `project.json` (`renderScripts` etc.). Deliverable
  actions return `"terminal": true` so the loop short-circuits after success.
- Read-only shell probes only; no arbitrary command execution.
- Escalation (`/api/escalate`) delegates to the OpenClaw gateway agent
  (port 18789).

## Guardrails retained in the IDE defaults

The copyright guardrail (YouTube policy + clearance) and production quality
standards lists remain built into `server.py` as default policy. Project- and
episode-specific creative rules (yellow-ball identity, render gates, etc.) are
NOT hardcoded here — they live in each project's own config/docs.
