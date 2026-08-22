# Redeploy after outage: S03–S10 Cycles PNG masters; skip playable S01/S02.
# Does NOT set AFRICA_FORCE_RERENDER (would wipe S01/S02).
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Bl = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$Master = Join-Path $Project "blend\africa_s1_master_v01.blend"
$RenderPy = Join-Path $Project "render_scenes_mp4.py"
$Log = Join-Path $Project "sasa_hq_rerender_log.txt"
$Err = Join-Path $Project "sasa_hq_rerender_err.txt"
$Clips = Join-Path $Project "renders\video_clips"

$corrupt = Join-Path $Clips "03_Beat1_Hubs.mp4"
$bak = Join-Path $Clips "03_Beat1_Hubs_CORRUPT_outage.mp4"
if ((Test-Path $corrupt) -and -not (Test-Path $bak)) {
  Rename-Item $corrupt $bak -Force
  Add-Content $Log "[$(Get-Date -Format o)] renamed corrupt S03 -> CORRUPT_outage"
}

$sidecar = Join-Path $Project "renders\paced_overlays\s01_teded_open30_blender51.mp4"
if (Test-Path $sidecar) {
  Rename-Item $sidecar ($sidecar -replace '\.mp4$','_CORRUPT_outage.mp4') -Force -ErrorAction SilentlyContinue
}

$env:AFRICA_ONLY_SCENES = "03_Beat1_Hubs,04_Beat1_Phone,05_Beat2_Money,06_Beat2_Solar,07_Beat3_Gap,08_Beat3_SecondaryCity,09_Closer,10_EndCard"
$env:AFRICA_RENDER_ENGINE = "CYCLES"
$env:AFRICA_MASTER_FRAMES = "1"
$env:AFRICA_DELIVERY_BITRATE = "10M"
$env:AFRICA_NO_YELLOW_BALL = "1"
# Completion-viable HQ: 64 samples (PNG resume). Raise to 128 when on AC if desired.
# Floor in render_scenes_mp4.py is 64. Do not set AFRICA_FORCE_RERENDER.
$env:AFRICA_CYCLES_SAMPLES = "64"
Remove-Item Env:AFRICA_FORCE_RERENDER -ErrorAction SilentlyContinue

# Quarantine any leftover CORRUPT mp4s out of video_clips so watcher cannot restore them
$qdir = Join-Path $Project "renders\quality\corrupt_outage"
New-Item -ItemType Directory -Force -Path $qdir | Out-Null
Get-ChildItem $Clips -Filter "*CORRUPT*" -ErrorAction SilentlyContinue | ForEach-Object {
  Move-Item $_.FullName (Join-Path $qdir $_.Name) -Force
}

Set-Location -LiteralPath $Project
Add-Content $Log "[$(Get-Date -Format o)] REDEPLOY S03-S10 Cycles PNG @64 samples (resume PNG; S01/S02 skipped)"
& $Bl -b $Master -P $RenderPy *>> $Log 2>> $Err
