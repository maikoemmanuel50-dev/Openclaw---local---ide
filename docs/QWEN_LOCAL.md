# Local Qwen (Ollama) — Africa S1

## Status (verified)

| Item | Value |
|------|--------|
| Host | `http://127.0.0.1:11434` |
| Process | `ollama` + `ollama app` running |
| Model | **`qwen2.5-coder:14b`** |
| Context | **32768** tokens |
| Ping | `QWEN_OK` |

## Use from this project

```powershell
cd "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
python scripts/qwen_local.py ping
python scripts/qwen_local.py chat "List safe next steps after power outage for HQ S03-S10"
```

### Tuned defaults (script)

| Param | Default | Env override |
|-------|---------|--------------|
| temperature | 0.2 | `AFRICA_QWEN_TEMP` |
| num_ctx | 16384 | `AFRICA_QWEN_NUM_CTX` |
| num_predict | 4096 | `AFRICA_QWEN_NUM_PREDICT` |
| model | qwen2.5-coder:14b | `AFRICA_QWEN_MODEL` |

Production system prompt baked in (Blender 5.1 / 4K HOLD / one GPU / no AI VO).

## Connect Cursor chat to local Qwen

Cursor does not auto-switch the agent model to Ollama. To use Qwen in **Cursor Chat / Custom model**:

1. Keep Ollama running (`ollama serve` if needed).
2. **Cursor Settings → Models**
3. Under **OpenAI-compatible / API**:
   - **Override OpenAI Base URL:** `http://127.0.0.1:11434/v1`
   - **API Key:** any non-empty string (e.g. `ollama`)
4. Add custom model id: **`qwen2.5-coder:14b`**
5. Select that model in the chat model picker.

OpenAI-compatible test:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/v1/models
```

## Recommended uses on this show

- Beat-sheet / kinetic cut JSON drafts (see `docs/S01_TEDED_30S_OPEN.md`)
- Fairlight cue timing suggestions from VO transcript
- Resolve marker name lists from `resolve_spec.yaml`
- **Not** for GPU render decisions that conflict with `PRODUCTION_STATUS.md` / PRE_4K gate

## Keep alive after reboot

```powershell
# If Ollama app not auto-started:
Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
ollama run qwen2.5-coder:14b ""
```
