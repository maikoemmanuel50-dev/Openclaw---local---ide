# After HQ 10/10: merge object motion into master + re-render scenes with motion bake.
# Runs BEFORE finish_after_hq.ps1 (invoked from wait_hq_assemble.ps1).
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "merge_motion_after_hq_log.txt"
$Bl = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$Master = Join-Path $Project "blend\africa_s1_master_v01.blend"
$Preview = Join-Path $Project "blend\africa_s1_object_motion_preview.blend"
$MotionScript = Join-Path $Project "setup_object_motion_all_scenes.py"
$RenderScript = Join-Path $Project "render_scenes_mp4.py"
$Clips = Join-Path $Project "renders\video_clips"
$Scenes = @("01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone","05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity","09_Closer","10_EndCard")

function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $Log -Value $l
  Write-Host $l
}

function Wait-NoBlenderBatch {
  while ($true) {
    $batch = @(Get-CimInstance Win32_Process -Filter "Name='blender.exe'" -ErrorAction SilentlyContinue |
      Where-Object { $_.CommandLine -match '-b ' })
    if ($batch.Count -eq 0) { return }
    W ("Waiting for HQ batch to exit ({0} blender -b)" -f $batch.Count)
    Start-Sleep 60
  }
}

W "=== merge_motion_after_hq START ==="
Wait-NoBlenderBatch

# Backup master before motion merge
$bak = Join-Path $Project ("blend\africa_s1_master_v01_pre_motion_{0}.blend" -f (Get-Date -Format "yyyyMMdd_HHmm"))
if (Test-Path $Master) {
  Copy-Item $Master $bak -Force
  W ("Backed up master -> {0}" -f $bak.Name)
}

# Prefer re-applying motion script on master (idempotent) over blind copy from preview
if ((Test-Path $Bl) -and (Test-Path $Master) -and (Test-Path $MotionScript)) {
  W "Applying object motion to master (AFRICA_OUT_BLEND=master)..."
  $env:AFRICA_OUT_BLEND = $Master
  $env:CUDA_VISIBLE_DEVICES = "-1"
  & $Bl -b $Master -P $MotionScript 2>&1 | Tee-Object -FilePath (Join-Path $Project "merge_motion_apply_log.txt")
  W ("motion apply exit={0}" -f $LASTEXITCODE)
  Remove-Item Env:AFRICA_OUT_BLEND -ErrorAction SilentlyContinue
} elseif (Test-Path $Preview) {
  W "Fallback: copy preview blend over master"
  Copy-Item $Preview $Master -Force
} else {
  W "ERROR: no preview blend and motion script failed — skipping motion merge"
}

$AfrAlpha = Join-Path $Project "setup_fix_s01_africa_alpha.py"
$MeshyG = Join-Path $Project "setup_meshy_s07_giraffe.py"
if ((Test-Path $Bl) -and (Test-Path $Master)) {
  if (Test-Path $AfrAlpha) {
    W "Applying S01 Africa alpha whip fix..."
    $env:CUDA_VISIBLE_DEVICES = "-1"
    & $Bl -b $Master -P $AfrAlpha 2>&1 | Tee-Object -FilePath (Join-Path $Project "s01_africa_alpha_merge_log.txt")
    W ("s01 africa alpha exit={0}" -f $LASTEXITCODE)
  }
  $glbDir = Join-Path $Project "assets\meshy\scenes\S07"
  $hasGlb = @(Get-ChildItem $glbDir -Filter "*.glb" -ErrorAction SilentlyContinue).Count -gt 0
  if ($hasGlb -and (Test-Path $MeshyG)) {
    W "Importing Meshy S07 giraffe GLB..."
    & $Bl -b $Master -P $MeshyG 2>&1 | Tee-Object -FilePath (Join-Path $Project "meshy_s07_giraffe_log.txt")
    W ("meshy giraffe exit={0}" -f $LASTEXITCODE)
  } else {
    W "Meshy S07: no GLB yet — skip (drop assets/meshy/scenes/S07/*.glb before merge to include)"
  }
}

# Re-render all scenes with motion (one GPU job) — Cycles + 2-pass delivery
if ((Test-Path $Bl) -and (Test-Path $Master) -and (Test-Path $RenderScript)) {
  W "Tightening DOF before Cycles motion re-render..."
  $Dof = Join-Path $Project "setup_tighten_dof_parallax.py"
  if (Test-Path $Dof) {
    $env:CUDA_VISIBLE_DEVICES = "-1"
    & $Bl -b $Master -P $Dof 2>&1 | Tee-Object -FilePath (Join-Path $Project "dof_tighten_merge_log.txt")
    W ("dof tighten exit={0}" -f $LASTEXITCODE)
  }
  W "Re-rendering 10 scenes: Cycles + OptiX masters + 10M 2-pass delivery..."
  foreach ($s in $Scenes) {
    $dest = Join-Path $Clips ($s + ".mp4")
    if (Test-Path $dest) {
      Copy-Item $dest ($dest + ".pre_motion_bak") -Force -ErrorAction SilentlyContinue
    }
  }
  $env:AFRICA_RENDER_ENGINE = "CYCLES"
  $env:AFRICA_MASTER_FRAMES = "1"
  $env:AFRICA_FORCE_RERENDER = "1"
  $env:AFRICA_DELIVERY_BITRATE = "10M"
  $env:AFRICA_NO_YELLOW_BALL = "1"
  Remove-Item Env:AFRICA_ONLY_SCENES -ErrorAction SilentlyContinue
  Remove-Item Env:CUDA_VISIBLE_DEVICES -ErrorAction SilentlyContinue
  & $Bl -b $Master -P $RenderScript 2>&1 | Tee-Object -FilePath (Join-Path $Project "motion_rerender_log.txt")
  W ("motion rerender exit={0}" -f $LASTEXITCODE)
  W "Resolve S02 kinetic preview (post Cycles S02)..."
  python (Join-Path $Project "scripts\resolve_s02_kinetic_preview.py") 2>&1 |
    Tee-Object -FilePath (Join-Path $Project "s02_kinetic_preview_log.txt")
  W ("s02 kinetic preview exit={0}" -f $LASTEXITCODE)
} else {
  W "Skip motion re-render — blender/master/render script missing"
}

W "=== merge_motion_after_hq DONE ==="
