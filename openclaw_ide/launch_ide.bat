@echo off
REM Start OpenClaw Studio IDE Server and open browser
cd /d "%~dp0"
echo Starting OpenClaw Local IDE on http://127.0.0.1:8765 ...
start "" http://127.0.0.1:8765
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0watchdog_ide.ps1"