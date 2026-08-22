# Power-outage auto-resume - Africa Season 1
# Safe at Windows logon or after power returns.
# Rules: one GPU Blender job; never wipe PNG masters; never AFRICA_FORCE_RERENDER;
# quarantine corrupt MP4s; skip playable S01/S02.
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Bl = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$Master = Join-Path $Project "blend\africa_s1_master_v01.blend"
$RenderPy = Join-Path $Project "render_scenes_mp4.py"
$Log = Join-Path $Project "sasa_hq_rerender_log.txt"
$Err = Join-Path $Project "sasa_hq_rerender_err.txt"
$Clips = Join-Path $Project "renders\video_clips"
$Masters = Join-Path $Clips "masters"
$Checkpoint = Join-Path $Project "STATUS_POWER_CHECKPOINT.txt"
$BootLog = Join-Path $Project "renders\quality\power_auto_resume_log.txt"
$Watch = Join-Path $Project "wait_hq_assemble.ps1"
$ResumeHq = Join-Path $Project "scripts\resume_hq_s03_s10.ps1"
$CorruptDir = Join-Path $Project "renders\quality\corrupt_outage"

$Scenes = @(
  @{ n = "01_ColdOpen"; sec = 50 },
  @{ n = "02_Context2007"; sec = 45 },
  @{ n = "03_Beat1_Hubs"; sec = 45 },
  @{ n = "04_Beat1_Phone"; sec = 25 },
  @{ n = "05_Beat2_Money"; sec = 45 },
  @{ n = "06_Beat2_Solar"; sec = 40 },
  @{ n = "07_Beat3_Gap"; sec = 50 },
  @{ n = "08_Beat3_SecondaryCity"; sec = 35 },
  @{ n = "09_Closer"; sec = 70 },
  @{ n = "10_EndCard"; sec = 15 }
)

function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $BootLog -Value $l -EA SilentlyContinue
  Add-Content -Path $Log -Value $l -EA SilentlyContinue
  Write-Host $l
}

function Test-ClipReady([string]$path, [double]$minSec) {
  if (-not (Test-Path $path)) { return $false }
  if ((Get-Item $path).Length -lt 200KB) { return $false }
  if ($path -match "CORRUPT|DEAD_moov") { return $false }
  $dur = & ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 $path 2>$null
  try { return ([double]$dur -ge ($minSec - 0.5)) } catch { return $false }
}

function Get-PngCount([string]$scene) {
  $d = Join-Path $Masters $scene
  if (-not (Test-Path $d)) { return 0 }
  return @(Get-ChildItem $d -Filter "frame_*.png" -EA SilentlyContinue).Count
}

function Test-BlenderHqRunning {
  $procs = Get-CimInstance Win32_Process -Filter "Name='blender.exe'" -EA SilentlyContinue |
    Where-Object { $_.CommandLine -match "-b " -and $_.CommandLine -match "render_scenes_mp4" }
  return @($procs).Count -gt 0
}

function Test-WatcherRunning {
  $procs = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -EA SilentlyContinue |
    Where-Object { $_.CommandLine -match "wait_hq_assemble" }
  return @($procs).Count -gt 0
}

New-Item -ItemType Directory -Force -Path (Split-Path $BootLog), $CorruptDir, $Masters | Out-Null
Set-Location -LiteralPath $Project
W "=== power auto-resume start ==="

# 1) Quarantine known-bad / tiny / unplayable spine MP4s only
Get-ChildItem $Clips -Filter "*CORRUPT*" -EA SilentlyContinue | ForEach-Object {
  Move-Item $_.FullName (Join-Path $CorruptDir $_.Name) -Force -EA SilentlyContinue
  W ("quarantined " + $_.Name)
}
Get-ChildItem $Clips -Filter "*DEAD_moov*" -EA SilentlyContinue | ForEach-Object {
  Move-Item $_.FullName (Join-Path $CorruptDir $_.Name) -Force -EA SilentlyContinue
  W ("quarantined " + $_.Name)
}
foreach ($s in $Scenes) {
  $mp4 = Join-Path $Clips ($s.n + ".mp4")
  if (-not (Test-Path $mp4)) { continue }
  $fi = Get-Item $mp4
  if ($fi.Length -lt 100KB) {
    Move-Item $mp4 (Join-Path $CorruptDir ($s.n + "_CORRUPT_outage.mp4")) -Force -EA SilentlyContinue
    W ("quarantined tiny " + $s.n + ".mp4")
    continue
  }
  $probe = & ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 $mp4 2>$null
  if (-not $probe) {
    Move-Item $mp4 (Join-Path $CorruptDir ($s.n + "_CORRUPT_outage.mp4")) -Force -EA SilentlyContinue
    W ("quarantined unplayable " + $s.n + ".mp4")
  }
}

# 2) Checkpoint inventory
$ready = 0
$lines = @()
$lines += "AFRICA S1 POWER CHECKPOINT"
$lines += ("Updated: " + (Get-Date -Format o))
$lines += "Rule: PNG masters under renders/video_clips/masters/<scene>/ survive outages; resume from next missing frame."
$lines += ""
foreach ($s in $Scenes) {
  $mp4 = Join-Path $Clips ($s.n + ".mp4")
  $ok = Test-ClipReady $mp4 $s.sec
  if ($ok) { $ready++ }
  $png = Get-PngCount $s.n
  $st = if ($ok) { "READY" } else { "MISSING" }
  $lines += ("{0}: mp4={1} png_frames={2}" -f $s.n, $st, $png)
}
$lines += ""
$lines += ("READY_CLIPS={0}/10" -f $ready)
$lines += "AUTO_RESUME=scripts/power_outage_auto_resume.ps1"
$lines += "HQ_RESUME=scripts/resume_hq_s03_s10.ps1"
$lines += "WATCHER=wait_hq_assemble.ps1"
$lines += "SAMPLES_ENV=AFRICA_CYCLES_SAMPLES (64 on battery; 128 on AC)"
$lines += "4K=HOLD"
$lines | Set-Content -Path $Checkpoint -Encoding UTF8
W ("checkpoint written READY={0}/10" -f $ready)

# 3) Power tip
$bs = Get-CimInstance -Namespace root\wmi -ClassName BatteryStatus -EA SilentlyContinue
if ($bs -and -not $bs.PowerOnline) {
  W "WARN: on battery (PowerOnline=False) - plug in ASAP; GPU will throttle"
}

# 4) If 10/10, only ensure watcher/finish path
if ($ready -ge 10) {
  W "10/10 clips ready - ensure watcher/finish"
  if (-not (Test-WatcherRunning)) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c powershell -NoProfile -ExecutionPolicy Bypass -File `"$Watch`"" -WorkingDirectory $Project -WindowStyle Minimized
    W "watcher started"
  }
  W "=== power auto-resume done (complete) ==="
  exit 0
}

# 5) Ensure HQ Blender running (PNG resume inside render_scenes_mp4.py)
if (Test-BlenderHqRunning) {
  W "HQ Blender already running - leave it"
} else {
  if (Test-Path $ResumeHq) {
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c powershell -NoProfile -ExecutionPolicy Bypass -File `"$ResumeHq`"" -WorkingDirectory $Project -WindowStyle Minimized
    W "started resume_hq_s03_s10.ps1"
  } else {
    $env:AFRICA_ONLY_SCENES = "03_Beat1_Hubs,04_Beat1_Phone,05_Beat2_Money,06_Beat2_Solar,07_Beat3_Gap,08_Beat3_SecondaryCity,09_Closer,10_EndCard"
    $env:AFRICA_RENDER_ENGINE = "CYCLES"
    $env:AFRICA_MASTER_FRAMES = "1"
    $env:AFRICA_DELIVERY_BITRATE = "10M"
    $env:AFRICA_NO_YELLOW_BALL = "1"
    $env:AFRICA_CYCLES_SAMPLES = "64"
    Remove-Item Env:AFRICA_FORCE_RERENDER -EA SilentlyContinue
    Start-Process -FilePath $Bl -ArgumentList @("-b", "`"$Master`"", "-P", "`"$RenderPy`"") -WorkingDirectory $Project -WindowStyle Minimized
    W "started blender HQ directly @64"
  }
}

# 6) Watcher
if (-not (Test-WatcherRunning)) {
  Start-Process -FilePath "cmd.exe" -ArgumentList "/c powershell -NoProfile -ExecutionPolicy Bypass -File `"$Watch`"" -WorkingDirectory $Project -WindowStyle Minimized
  W "watcher started"
} else {
  W "watcher already running"
}

W "=== power auto-resume done ==="
