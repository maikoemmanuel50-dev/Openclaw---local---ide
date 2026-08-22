# Wait for HQ re-render then normalize + assemble (playbook B→F)
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Clips = Join-Path $Project "renders\video_clips"
$Log = Join-Path $Project "wait_hq_assemble_log.txt"
$Scenes = @("01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone","05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity","09_Closer","10_EndCard")
function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m
  Add-Content -Path $Log -Value $l -ErrorAction SilentlyContinue
  Write-Host $l
}
function Test-ClipReady([string]$path, [double]$minSec) {
  if (-not (Test-Path $path)) { return $false }
  if ((Get-Item $path).Length -lt 200KB) { return $false }
  if ($path -match 'CORRUPT|DEAD_moov') { return $false }
  $dur = & ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 $path 2>$null
  try { return ([double]$dur -ge ($minSec - 0.5)) } catch { return $false }
}
$ExpectedSec = @{
  "01_ColdOpen"=50; "02_Context2007"=45; "03_Beat1_Hubs"=45; "04_Beat1_Phone"=25
  "05_Beat2_Money"=45; "06_Beat2_Solar"=40; "07_Beat3_Gap"=50
  "08_Beat3_SecondaryCity"=35; "09_Closer"=70; "10_EndCard"=15
}
function Normalize-Clips {
  foreach ($s in $Scenes) {
    $dest = Join-Path $Clips ($s + ".mp4")
    if (Test-ClipReady $dest $ExpectedSec[$s]) { continue }
    $cands = Get-ChildItem $Clips -Filter ($s + "*.mp4") -ErrorAction SilentlyContinue |
      Where-Object { $_.Length -gt 200KB -and $_.Name -notmatch 'CORRUPT|DEAD_moov' }
    if ($cands) {
      $best = $cands | Sort-Object Length -Descending | Select-Object -First 1
      if ($best.FullName -ne $dest) {
        if (Test-Path $dest) { Remove-Item $dest -Force -ErrorAction SilentlyContinue }
        Move-Item $best.FullName $dest -Force
        W ("Renamed {0} -> {1}" -f $best.Name, ($s + ".mp4"))
      }
    }
  }
}
W "Watcher started (playbook B/F)"
while ($true) {
  Normalize-Clips
  $n = 0
  foreach ($s in $Scenes) {
    $p = Join-Path $Clips ($s + ".mp4")
    if (Test-ClipReady $p $ExpectedSec[$s]) { $n++ }
  }
  $rl = Join-Path $Project "sasa_hq_rerender_log.txt"
  $tail = ""
  if (Test-Path $rl) { $tail = ((Get-Content $rl -Tail 2) -join " | ") }
  W ("clips={0}/10 | {1}" -f $n, $tail)
  if ($n -eq 10 -or ($tail -match "ALL_SCENES_RENDERED")) { Normalize-Clips; break }
  $bl = @(Get-Process blender -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match '-b' -or $_.WorkingSet64 -gt 800MB })
  # simpler: any blender with high RAM is render
  $render = @(Get-CimInstance Win32_Process -Filter "Name='blender.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match '-b ' })
  if ($render.Count -eq 0) {
    Start-Sleep 45
    Normalize-Clips
    $n2 = 0
    foreach ($s in $Scenes) {
      $p = Join-Path $Clips ($s + ".mp4")
      if (Test-ClipReady $p $ExpectedSec[$s]) { $n2++ }
    }
    $render2 = @(Get-CimInstance Win32_Process -Filter "Name='blender.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match '-b ' })
    if ($render2.Count -eq 0 -and $n2 -lt 10) { W ("Blender batch stopped early at {0}/10" -f $n2); break }
  }
  Start-Sleep 120
}
Normalize-Clips
$ready = 0
foreach ($s in $Scenes) {
  $p = Join-Path $Clips ($s + ".mp4")
  if (Test-ClipReady $p $ExpectedSec[$s]) { $ready++ }
}
W ("Ready {0}/10" -f $ready)
if ($ready -ge 10) {
  $motion = Join-Path $Project "merge_motion_after_hq.ps1"
  if (Test-Path $motion) {
    W "Handing off to merge_motion_after_hq.ps1 (motion bake before assemble)"
    & powershell -NoProfile -ExecutionPolicy Bypass -File $motion
    W ("merge_motion exit={0}" -f $LASTEXITCODE)
  }
  $finish = Join-Path $Project "finish_after_hq.ps1"
  if (Test-Path $finish) {
    W "Handing off to finish_after_hq.ps1"
    & powershell -NoProfile -ExecutionPolicy Bypass -File $finish
    W ("finish_after_hq exit={0}" -f $LASTEXITCODE)
  } else {
    $out = Join-Path $Project "Africa_S1_Silicon_Savannah_7min.mp4"
    $master = Join-Path $Project "Africa_S1_Silicon_Savannah_7min_MASTER.mp4"
    python (Join-Path $Project "assemble_final_video.py") --dir $Clips --output $out --master $master
    W ("assemble exit={0}" -f $LASTEXITCODE)
    if (Test-Path (Join-Path $Project "assemble_with_audio.py")) {
      python (Join-Path $Project "assemble_with_audio.py")
      W ("audio assemble exit={0}" -f $LASTEXITCODE)
    }
  }
} else {
  W "Incomplete — not assembling FINAL"
}
W "Watcher exit"
