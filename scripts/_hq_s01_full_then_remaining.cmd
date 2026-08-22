@echo off
REM 1) Scene 01 full quality (128 / full RT), no YB
REM 2) Then remaining 02-10 at balanced 64 / half RT
set PROJECT=C:\Users\HP\OneDrive\The Vault\Africa Season 1
set BLENDER=C:\Program Files\Blender Foundation\Blender 5.1\blender.exe
set BLEND=%PROJECT%\blend\africa_s1_master_v01.blend
set LOG=%PROJECT%\sasa_hq_rerender_log.txt
set ERR=%PROJECT%\sasa_hq_rerender_stderr.txt

echo === %DATE% %TIME% S01 full then remaining NO-YB ===>> "%LOG%"

set AFRICA_NO_YELLOW_BALL=1
set AFRICA_FORCE_RERENDER=
set AFRICA_EEVEE_SAMPLES=128
set AFRICA_RT_SCALE=1
set AFRICA_ONLY_SCENES=01_ColdOpen
"%BLENDER%" -b "%BLEND%" -P "%PROJECT%\render_scenes_mp4.py" >> "%LOG%" 2>> "%ERR%"

set AFRICA_ONLY_SCENES=
set AFRICA_EEVEE_SAMPLES=64
set AFRICA_RT_SCALE=2
"%BLENDER%" -b "%BLEND%" -P "%PROJECT%\render_scenes_mp4.py" >> "%LOG%" 2>> "%ERR%"
