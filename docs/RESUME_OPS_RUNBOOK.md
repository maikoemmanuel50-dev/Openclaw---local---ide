# Resume-Ops Runbook — Africa Season 1 Episode 1

Companion to the IDE's **analyze → rank → sequential-execute** protocol
(`POST /api/mission` on port 8765). This is the rewritten, ranked version of
the old monolithic Resume-Ops prompt. It maps to a strict ordered plan where
each deliverable starts only after the previous one is verified done.

---

## Option A — Deterministic (recommended)

Paste into `POST /api/mission` (or the IDE's Mission box). The server runs the
planner, then executes each step in order via `dispatch_tool`, halting on
`BLOCKED_BY_GATE` or a failed step. No LLM loop churn.

```
MISSION — Resume Africa Season 1 Episode 1 and push to completion.

Rules that apply to every step:
- ONE GPU job at a time. Never start a second Blender/Resolve render.
- Never restart an in-progress render from frame 0.
- 4K HOLD: do not touch render_4k / run_1080_then_4k.
- Next step runs ONLY after the previous one is verified done.
- YB overlays are WAIVED this pass (AFRICA_NO_YELLOW_BALL); V2 may stay empty.
- VO is the user's recorded stem; never substitute AI voice.

RANKED DELIVERABLES (importance + dependency order):
1. Situation report: production_status (scene frames, ready X/10, blender pid).
2. Watcher state: read_log wait_hq_assemble_log.txt (last 40 lines).
3. Tool reachability: shell_probe for blender process + renders list + masters pngs.
4. Gate check: read_log PRODUCTION_STATUS.md (current waivers / open items).
5. When 10/10 clips ready AND no render running: run_action assemble_final
   (silent master) — verify Africa_S1_Silicon_Savannah_7min.mp4 exists.
6. Then run_action assemble_with_audio (_FINAL.mp4 + stems).
7. Delivery verify (when render completes): confirm _YT1080.mp4 + Final vs
   docs/DELIVERY_STANDARDS.md (1080p, H.264 High, 8–12 Mbps, Rec.709, −14 LUFS).
8. Escalate any structural blocker via escalate_openclaw with paths + log
   excerpts; surface its answer verbatim.

Stop the chain immediately if any step returns BLOCKED_BY_GATE or fails
— report it and wait, do not force later steps.
```

---

## Option B — Interactive chat (agent loop)

Paste this single message into the IDE chat. The system prompt's SEQUENTIAL
EXECUTION PROTOCOL makes qwen rank and run one step at a time:

```
RESUME-OPS — Africa S1 Episode 1.
Apply Sequential Execution Protocol: analyze the request, rank deliverables by
importance and dependency, then execute ONE at a time. The second deliverable
starts only after the first is verified done. After each step output
"STEP n DONE: <what was verified>".

Ranked list to follow:
1. production_status — scene frames / ready X/10 / blender pid.
2. read_log wait_hq_assemble_log.txt — watcher heartbeat.
3. shell_probe blender process + renders list — tool reachability.
4. read_log PRODUCTION_STATUS.md — waivers & open gate items.
5. If 10/10 ready and no render running: run_action assemble_final,
   verify the 7min silent master exists.
6. Then run_action assemble_with_audio, verify FINAL + stems.
7. On render completion verify delivery vs docs/DELIVERY_STANDARDS.md.
8. Escalate structural blockers to OpenClaw; return its answer verbatim.

Respect: one GPU job at a time, never restart a render from frame 0,
4K HOLD, VO is the user's stem (no AI voice). If a step is BLOCKED_BY_GATE,
report and stop the chain rather than forcing later steps.
```

---

## Why this changes

| Old | New |
|-----|-----|
| Monolithic 6-step prompt in one chat turn; qwen churned read_log/shell_probe and hit max rounds | `/api/mission` plans + executes server-side, deterministic, no LLM loop |
| Steps reordered/improvized by the 14B model | Ranked plan enforced in order; next step gated on previous "done" |
| Gate block → runaway loop | `BLOCKED_BY_GATE` halts the chain with a clear report |
| No record of what ran | Per-step report: rank / deliverable / tool / status / detail |

## Status source

Live production state and the official pre-4K checklist stay authoritative:
`PRODUCTION_STATUS.md`, `docs/PRE_4K_GATE.md`,
`.cursor/rules/africa-s1-creative-gate.mdc`, `docs/DELIVERY_STANDARDS.md`.