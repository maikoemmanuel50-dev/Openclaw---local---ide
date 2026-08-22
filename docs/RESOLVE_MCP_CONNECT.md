# Resolve MCP — connect before deliverables

**Resolve is running** but Cursor MCP only connects after the **in-app bridge** is started (Free edition) or **External scripting = Local** is enabled (Studio).

## One-time setup (just done)

Bridge installed to:
- `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility\resolve_bridge.py`
- `AfricaS1_RunDeliverables.py` (same Utility folder)

## Connect MCP (do this now)

1. **Restart Resolve** once (so it rescans Scripts) — or continue if you already restarted since install.
2. **Open your saved project** (`Africa S1 - Silicon Savannah` / `Episode 01 - Assembly`) — Scripts menu is empty on the project manager screen.
3. **Workspace → Scripts → `resolve_bridge`** — run it **once per session**.  
   It will appear busy; that is normal (listener running on port **49632**).
4. Tell Cursor to retry — MCP tools should respond within a few seconds.

Optional probe: **Workspace → Scripts → `resolve_bridge_probe`** (run twice first time).

## Run deliverables (after bridge is up)

**From Cursor (MCP)** — agent runs import + open30 + kinetic + Fairlight.

**From Resolve menu:**
- **Workspace → Scripts → Utility → `AfricaS1_RunDeliverables`**

## Studio alternative

**DaVinci Resolve → Preferences → System → General → External scripting using → Local**  
Then external `python scripts/resolve_run_deliverables.py` works without the bridge.

## Verify connection

```powershell
Test-NetConnection 127.0.0.1 -Port 49632
# TcpTestSucceeded : True  → bridge up
```
