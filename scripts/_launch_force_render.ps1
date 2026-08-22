$env:AFRICA_FORCE_RERENDER='1'
Set-Location -LiteralPath 'c:\Users\HP\OneDrive\The Vault\Africa Season 1'
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' -b 'c:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend' -P 'c:\Users\HP\OneDrive\The Vault\Africa Season 1\render_scenes_mp4.py' *>> 'c:\Users\HP\OneDrive\The Vault\Africa Season 1\sasa_hq_rerender_log.txt' 2>> 'c:\Users\HP\OneDrive\The Vault\Africa Season 1\sasa_hq_rerender_err.txt'
