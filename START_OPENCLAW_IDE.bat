@echo off
REM Start OpenClaw Studio IDE from workspace root
cd /d "%~dp0openclaw_ide"
echo Starting OpenClaw Local IDE on http://127.0.0.1:8765 ...
start "" http://127.0.0.1:8765
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0openclaw_ide\watchdog_ide.ps1"