@echo off
set AFRICA_FORCE_RERENDER=1
cd /d "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b "C:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend" -P "C:\Users\HP\OneDrive\The Vault\Africa Season 1\render_scenes_mp4.py" >> "C:\Users\HP\OneDrive\The Vault\Africa Season 1\sasa_hq_rerender_log.txt" 2>> "C:\Users\HP\OneDrive\The Vault\Africa Season 1\sasa_hq_rerender_stderr.txt"
