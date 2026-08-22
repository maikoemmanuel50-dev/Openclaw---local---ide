@echo off
REM Africa S1 — called from Windows Startup / Scheduled Task after power returns
cd /d "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\power_outage_auto_resume.ps1"
