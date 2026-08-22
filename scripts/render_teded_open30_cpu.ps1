# CPU Cycles render open30 sidecar — does NOT use GPU (Blender HQ keeps GPU).
$ErrorActionPreference = "Continue"
$root = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$blender = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$blend = Join-Path $root "blend\africa_s1_teded_open30.blend"
$log = Join-Path $root "renders\quality\teded_open30_render_log.txt"
$mp4 = Join-Path $root "renders\paced_overlays\s01_teded_open30_blender51.mp4"
$env:CUDA_VISIBLE_DEVICES = "-1"
Remove-Item Env:AFRICA_SKIP_OPEN30_RENDER -ErrorAction SilentlyContinue
if (-not (Test-Path $blend)) {
  Write-Host "MISSING blend — run build_teded_open30_blend.ps1 first"
  exit 1
}
# Render via blend file + inline script tail
$renderPy = @"
import bpy
bpy.ops.wm.open_mainfile(filepath=r'$blend')
bpy.context.scene.render.filepath = r'$mp4'
bpy.context.scene.cycles.device = 'CPU'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for dev in prefs.devices:
        dev.use = False
except Exception:
    pass
print('RENDER_START open30_blender51', flush=True)
bpy.ops.render.render(animation=True)
print('RENDER_DONE open30_blender51', flush=True)
"@
$tmp = Join-Path $root "renders\quality\_render_open30_inline.py"
Set-Content -Path $tmp -Value $renderPy -Encoding UTF8
& $blender -b -P $tmp 2>&1 | Tee-Object -FilePath $log
