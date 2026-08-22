# When the active blender -b HQ batch exits, run S02 Cycles + Resolve preview once.
# Full all-scene Cycles re-render still runs via merge_motion_after_hq.ps1 at 10/10.
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "watch_s02_cycles_when_free_log.txt"
$Flag = Join-Path $Project "renders\quality\s02_cycles_preview_done.flag"
$Fix = Join-Path $Project "scripts\post_batch_cycles_fix.ps1"

function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m
  Add-Content -Path $Log -Value $l
}

if (Test-Path $Flag) { exit 0 }
W "watch_s02_cycles_when_free armed"

while ($true) {
  $batch = @(Get-CimInstance Win32_Process -Filter "Name='blender.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match '-b ' })
  if ($batch.Count -eq 0) {
    $s02 = Join-Path $Project "renders\video_clips\02_Context2007.mp4"
    $clips = 0
    foreach ($s in @("01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone","05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity","09_Closer","10_EndCard")) {
      $p = Join-Path $Project "renders\video_clips\$s.mp4"
      if ((Test-Path $p) -and ((Get-Item $p).Length -gt 500KB)) { $clips++ }
    }
    if ($clips -ge 10) {
      W "10/10 on disk — merge_motion_after_hq owns Cycles pass; skip early s02"
      New-Item -ItemType File -Path $Flag -Force | Out-Null
      break
    }
    if ((Test-Path $s02) -and ((Get-Item $s02).Length -gt 500KB)) {
      W "GPU free + S02 locked — running post_batch_cycles_fix -Phase s02"
      & powershell -NoProfile -ExecutionPolicy Bypass -File $Fix -Phase s02
      New-Item -ItemType File -Path $Flag -Force | Out-Null
      W "done"
    }
    break
  }
  Start-Sleep 120
}
