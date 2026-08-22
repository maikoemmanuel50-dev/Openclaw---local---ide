---
title: Composio & MCP Manual
category: Software Manuals
tags: composio, mcp, canva, telegram, integrations, tools
source: docs/MCP_CONNECTIVITY.md, server.py EXEC_ACTIONS, ide tools
---

# Composio & MCP Manual (tool integrations)

The IDE agents reach external software through MCP servers and Composio. This
card is the "which wire goes where" reference.

## Why MCP matters

MCP standardizes tool access so agents (local qwen2.5-coder:14b, OpenClaw
gateway, this IDE) can call apps directly instead of ad-hoc scripts. The local
IDE exposes read-only shell probes and gated actions — the model never runs
arbitrary commands.

## Connected apps (in-use)

- **Canva** — Composio account `airway-sasin`. Create/edit/export designs,
  upload assets, batch import/export.
- **OpenClaw CLI** — escalation shim
  `C:\Users\HP\AppData\Roaming\npm\openclaw.cmd agent --json --agent main`
  (full path + `shell=True`; bare `openclaw` → WinError 2).
- **Blender 5.1 MCP** — socket 127.0.0.1:9876 (Blender Add-ons > Blender MCP).
- **DaVinci Resolve MCP** — bridge port 49632 (Workspace > Scripts >
  resolve_bridge; auto used in Free edition).
- **Composio Canva** — `canva` toolkit via Composio (search/manage connections
  in the IDE's Composio tools).
- Optional learned app: Telegram watcher scripts live in `scripts/`
  (`watch_s01_telegram_ping.ps1`, `poll_telegram_chat_id.ps1`).

## IDE agent layer (server.py)

- `POST /api/chat` — multi-round tool loop (`_run_agent_loop`, max 12 rounds,
  400s wall cap). Handles native `tool_calls` and content-printed JSON tool
  blocks (brace-balanced `_extract_content_tool_calls`).
- `POST /api/exec` — gated actions: `ping_qwen`, `qwen_chat` (ungated);
  `assemble_*` (gate_cpu); `render_*`, `render_all_scenes` (gate_blender);
  `render_4k`, `run_1080_then_4k` (gate_4k_hold). Gated refusal →
  `BLOCKED_BY_GATE`.
- Shell probes (allowlist): blender process, port 18789, renders list, masters
  pngs, disk, network status.
- Escalation: `escalate_openclaw` — full-path CLI shim; parses
  `result.payloads[].text`; treat success as terminal.

## Guardrails

- One GPU job at a time. Never start a 2nd Blender render / Resolve deliver.
- Blender 5.1.2 only. 4K gated. Yellow ball #FFD54F (waived per status).
- Never exfiltrate private data; no destructive commands without approval.

## Docs

- `docs/MCP_CONNECTIVITY.md` (in Vault) and `docs/RESOLVE_MCP_CONNECT.md`.
- Use the IDE's Composio/Canva guides + this card for new app setup.