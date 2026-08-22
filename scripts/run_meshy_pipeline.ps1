# Meshy 3D motion — one-shot orchestrator (CPU/API safe; no GPU HQ interrupt)
$ErrorActionPreference = "Continue"
$root = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$blender = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$env:CUDA_VISIBLE_DEVICES = "-1"

Write-Host "=== Meshy pipeline ==="
Write-Host "1) Ensure MESHY_API_KEY is set OR Meshy MCP toggled on in Cursor"
Write-Host "2) Generate GLB/OBJ/FBX/STL for all scenes"
Write-Host "3) Import to Blender preview (master safe unless AFRICA_MESHY_APPLY_MASTER=1)"
Write-Host ""

if (-not $env:MESHY_API_KEY) {
  $env:MESHY_API_KEY = [Environment]::GetEnvironmentVariable("MESHY_API_KEY", "User")
}
if (-not $env:MESHY_API_KEY) {
  Write-Host "SKIP Meshy API: no MESHY_API_KEY — use Cursor MCP or setx MESHY_API_KEY msy_..."
  python "$root\scripts\meshy_generate_all_scenes.py" --dry-run
} else {
  python "$root\scripts\meshy_generate_all_scenes.py" @args
}

$anyGlb = Get-ChildItem "$root\assets\meshy\scenes" -Recurse -Filter "*.glb" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($anyGlb) {
  Write-Host "GLB found — running Blender motion setup (preview mode unless AFRICA_MESHY_APPLY_MASTER=1)"
  & $blender -b "$root\blend\africa_s1_master_v01.blend" -P "$root\setup_meshy_scene_motion.py"
} else {
  Write-Host "No GLBs yet — run generation first, then re-run this script."
}
