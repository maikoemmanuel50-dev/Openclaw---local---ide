# Post-batch Cycles + delivery encode + S02 Resolve preview.
# Does NOT interrupt the active EEVEE HQ batch — waits for GPU free, then runs.
#
# Phases:
#   1) S02 Cycles re-render + 2-pass ffmpeg (when GPU free, S02 plate locked)
#   2) Resolve S02 kinetic preview (CPU — can overlap next GPU job if Resolve only)
#   3) Remaining scenes S01,S03–S10 Cycles re-render (AFRICA_ONLY_SCENES skip done optional)
#
# Invoked automatically from merge_motion_after_hq.ps1 before motion re-render.
# Manual:
#   powershell -File scripts/post_batch_cycles_fix.ps1 -Phase s02
#   powershell -File scripts/post_batch_cycles_fix.ps1 -Phase all
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Bl = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$Master = Join-Path $Project "blend\africa_s1_master_v01.blend"
$Log = Join-Path $Project "post_batch_cycles_fix_log.txt"
$Phase = if ($args -contains "-Phase") { $args[[array]::IndexOf($args, "-Phase") + 1] } else { "all" }

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
    W ("Waiting for GPU batch ({0} blender -b)" -f $batch.Count)
    Start-Sleep 60
  }
}

function Invoke-CyclesRender([string[]]$Scenes) {
  $only = ($Scenes -join ",")
  $env:AFRICA_RENDER_ENGINE = "CYCLES"
  $env:AFRICA_MASTER_FRAMES = "1"
  $env:AFRICA_FORCE_RERENDER = "1"
  $env:AFRICA_DELIVERY_BITRATE = "10M"
  $env:AFRICA_NO_YELLOW_BALL = "1"
  if ($only) { $env:AFRICA_ONLY_SCENES = $only }
  else { Remove-Item Env:AFRICA_ONLY_SCENES -ErrorAction SilentlyContinue }
  W ("CYCLES render scenes=[{0}]" -f $only)
  & $Bl -b $Master -P (Join-Path $Project "render_scenes_mp4.py") 2>&1 |
    Tee-Object -FilePath (Join-Path $Project "post_batch_cycles_render_log.txt")
  W ("cycles render exit={0}" -f $LASTEXITCODE)
  return $LASTEXITCODE
}

W "=== post_batch_cycles_fix START phase=$Phase ==="

if ($Phase -eq "watch") {
  Wait-NoBlenderBatch
  $Phase = "s02-first"
}

$Dof = Join-Path $Project "setup_tighten_dof_parallax.py"
if ((Test-Path $Bl) -and (Test-Path $Master) -and (Test-Path $Dof)) {
  W "Tightening DOF on parallax plates..."
  & $Bl -b $Master -P $Dof 2>&1 | Tee-Object -FilePath (Join-Path $Project "dof_tighten_log.txt")
  W ("dof tighten exit={0}" -f $LASTEXITCODE)
}

if ($Phase -eq "s02" -or $Phase -eq "s02-first") {
  Wait-NoBlenderBatch
  Invoke-CyclesRender @("02_Context2007")
  W "Resolve S02 kinetic preview (V1 + V3/V4)..."
  python (Join-Path $Project "scripts\resolve_s02_kinetic_preview.py") 2>&1 |
    Tee-Object -FilePath (Join-Path $Project "s02_kinetic_preview_log.txt")
  W ("s02 preview exit={0}" -f $LASTEXITCODE)
  if ($Phase -eq "s02") {
    W "=== post_batch_cycles_fix DONE (s02 only) ==="
    exit 0
  }
}

if ($Phase -eq "all" -or $Phase -eq "s02-first") {
  Wait-NoBlenderBatch
  # Re-render all plates Cycles + delivery (supersedes EEVEE S01–S10)
  Invoke-CyclesRender @()
}

W "=== post_batch_cycles_fix DONE ==="
