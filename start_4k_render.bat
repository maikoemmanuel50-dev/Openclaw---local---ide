@echo off
REM Africa S1 — 4K batch render (Blender 5.1 ONLY — blend is 5.x format)
setlocal
set PROJECT=C:\Users\HP\OneDrive\The Vault\Africa Season 1
set BLENDER="C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
set BLEND="%PROJECT%\blend\africa_s1_master_v01.blend"
set SCRIPT="%PROJECT%\render_scenes_4k.py"
set LOG="%PROJECT%\sasa_4k_render_log.txt"
set ERR="%PROJECT%\sasa_4k_render_err.txt"

if not exist %BLENDER% (
  echo ERROR: Blender 5.1 not found. Do not use 4.4 — blend file is incompatible.
  exit /b 1
)

echo [%date% %time%] 4K render starting with Blender 5.1 >> %LOG%
%BLENDER% -b %BLEND% -P %SCRIPT% >> %LOG% 2>> %ERR%
echo [%date% %time%] 4K render exit %ERRORLEVEL% >> %LOG%
exit /b %ERRORLEVEL%
