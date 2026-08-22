@echo off
setlocal
set PROJECT=C:\Users\HP\OneDrive\The Vault\Africa Season 1
set BLENDER="C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
set BLEND="%PROJECT%\blend\africa_s1_master_v01.blend"
set LOG="%PROJECT%\render_log.txt"

echo [%date% %time%] === TED WORKFLOW RESTART === >> %LOG%

echo [%date% %time%] Applying TED-Ed element overlays... >> %LOG%
%BLENDER% -b %BLEND% -P "%PROJECT%\setup_teded_elements.py" >> %LOG% 2>&1
if errorlevel 1 exit /b 1

echo [%date% %time%] Starting full 3D scene render batch (64 samples)... >> %LOG%
%BLENDER% -b %BLEND% -P "%PROJECT%\render_scenes_mp4.py" >> %LOG% 2>&1
echo [%date% %time%] Render exit %ERRORLEVEL% >> %LOG%
exit /b %ERRORLEVEL%
