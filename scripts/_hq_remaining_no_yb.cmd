@echo off
REM Redo scenes 02-10 only (skip complete clips), no yellow ball, balanced EEVEE
set AFRICA_FORCE_RERENDER=
set AFRICA_NO_YELLOW_BALL=1
set AFRICA_EEVEE_SAMPLES=64
set AFRICA_RT_SCALE=2
cd /d "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b "C:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend" -P "C:\Users\HP\OneDrive\The Vault\Africa Season 1\render_scenes_mp4.py" >> "C:\Users\HP\OneDrive\The Vault\Africa Season 1\sasa_hq_rerender_log.txt" 2>> "C:\Users\HP\OneDrive\The Vault\Africa Season 1\sasa_hq_rerender_stderr.txt"
