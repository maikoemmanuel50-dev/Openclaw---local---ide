# PASTE INTO POWERSHELL AND RUN (Africa S1 — arm resume + continue HQ)
# Path has spaces — keep the quotes exactly as written.

$ErrorActionPreference = 'Continue'
$Project = 'C:\Users\HP\OneDrive\The Vault\Africa Season 1'
$StartupDir = [Environment]::GetFolderPath('Startup')
$StartupCmd = Join-Path $StartupDir 'AfricaS1_AutoResume.cmd'
$AutoResume = Join-Path $Project 'scripts\power_outage_auto_resume.ps1'
$ResumeHq = Join-Path $Project 'scripts\resume_hq_s03_s10.ps1'
$Watcher = Join-Path $Project 'wait_hq_assemble.ps1'
$Checkpoint = Join-Path $Project 'STATUS_POWER_CHECKPOINT.txt'
$BootLog = Join-Path $Project 'renders\quality\power_auto_resume_log.txt'

New-Item -ItemType Directory -Force -Path (Split-Path $BootLog) | Out-Null
Set-Location -LiteralPath $Project

function W([string]$m) {
  $l = '[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
  Add-Content $BootLog $l -EA SilentlyContinue
  Write-Host $l
}

# --- 1) Startup launcher (runs at every Windows logon after power returns) ---
@'
@echo off
cd /d "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\power_outage_auto_resume.ps1"
'@ | Set-Content -Path $StartupCmd -Encoding ASCII
W "Startup armed: $StartupCmd"

# --- 2) Scheduled task (best-effort; may need Admin) ---
$tr = 'cmd.exe /c "C:\Users\HP\OneDrive\THEVAU~1\AFRICA~1\STARTUP_AUTO_RESUME.cmd"'
cmd /c "schtasks /Create /TN AfricaS1_PowerAutoResume /TR `"$tr`" /SC ONLOGON /RL LIMITED /F" 2>&1 | ForEach-Object { W "schtasks: $_" }

# --- 3) Reduce sleep while rendering (best-effort) ---
powercfg /change standby-timeout-ac 0 | Out-Null
powercfg /change hibernate-timeout-ac 0 | Out-Null
powercfg /change standby-timeout-dc 0 | Out-Null
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>$null
W 'Power: High performance + sleep timeouts cleared (best-effort)'

# --- 4) Ensure auto-resume orchestrator exists ---
if (-not (Test-Path $AutoResume)) {
  W "MISSING $AutoResume — project scripts not found"
  return
}

# --- 5) Run orchestrator now (quarantine bad MP4s, checkpoint, start HQ+watcher if needed) ---
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $AutoResume

# --- 6) Hard ensure HQ + watcher (idempotent) ---
$hq = Get-CimInstance Win32_Process -Filter "Name='blender.exe'" -EA SilentlyContinue |
  Where-Object { $_.CommandLine -match 'render_scenes_mp4|-b .+africa_s1_master' }
if (-not $hq) {
  Start-Process cmd.exe -ArgumentList "/c powershell -NoProfile -ExecutionPolicy Bypass -File `"$ResumeHq`"" -WorkingDirectory $Project -WindowStyle Minimized
  W 'Started HQ resume_hq_s03_s10.ps1'
} else {
  W ("HQ already running PID={0}" -f $hq.ProcessId)
}

$w = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -EA SilentlyContinue |
  Where-Object { $_.CommandLine -match 'wait_hq_assemble' }
if (-not $w) {
  Start-Process cmd.exe -ArgumentList "/c powershell -NoProfile -ExecutionPolicy Bypass -File `"$Watcher`"" -WorkingDirectory $Project -WindowStyle Minimized
  W 'Started wait_hq_assemble.ps1'
} else {
  W ("Watcher already running PID={0}" -f $w.ProcessId)
}

# --- 7) Raise Blender priority ---
Get-Process blender -EA SilentlyContinue | ForEach-Object {
  try { $_.PriorityClass = 'High'; W ("Blender priority High PID={0}" -f $_.Id) } catch {}
}

# --- 8) Status ---
$png = @(Get-ChildItem (Join-Path $Project 'renders\video_clips\masters\03_Beat1_Hubs\frame_*.png') -EA SilentlyContinue).Count
$bs = Get-CimInstance -Namespace root\wmi -ClassName BatteryStatus -EA SilentlyContinue
W ("S03_PNG={0}  Startup={1}" -f $png, (Test-Path $StartupCmd))
if ($bs) {
  W ("AC PowerOnline={0} Charging={1} Discharging={2}" -f $bs.PowerOnline, $bs.Charging, $bs.Discharging)
  if (-not $bs.PowerOnline) { W 'WARN: Plug into AC now — battery kills GPU speed and risks shutdown mid-frame' }
}
W 'DONE — after power returns, sign in; Startup will resume PNG HQ then watcher to FINAL.'
W 'Manual: powershell -File scripts\power_outage_auto_resume.ps1'
if (Test-Path $Checkpoint) { Get-Content $Checkpoint }
