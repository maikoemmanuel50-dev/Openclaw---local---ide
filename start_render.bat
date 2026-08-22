@echo off
set BLENDER="C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
set BLEND="C:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend"
set SCRIPT="C:\Users\HP\OneDrive\The Vault\Africa Season 1\render_scenes_mp4.py"
set LOG="C:\Users\HP\OneDrive\The Vault\Africa Season 1\render_log.txt"
echo [%date% %time%] Starting render >> %LOG%
%BLENDER% -b %BLEND% -P %SCRIPT% >> %LOG% 2>&1
echo [%date% %time%] Render exit code %ERRORLEVEL% >> %LOG%
