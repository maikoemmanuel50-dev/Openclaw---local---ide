# Watch CURRENT S01 HQ complete (ignore older RENDER_DONE in log) -> Telegram pending
param(
  [string]$ChatId = $env:AFRICA_TELEGRAM_CHAT_ID,
  [int]$PollSec = 45
)
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "sasa_hq_rerender_log.txt"
$Flag = Join-Path $Project "renders\quality\S01_COMPLETE_FLAG.txt"
$Pending = Join-Path $Project "renders\quality\TELEGRAM_S01_PENDING.txt"
$WatchLog = Join-Path $Project "renders\quality\watch_s01_telegram_log.txt"
$SessionMarker = "S01 full then remaining NO-YB"
New-Item -ItemType Directory -Force -Path (Join-Path $Project "renders\quality") | Out-Null

function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $WatchLog -Value $l
  Write-Host $l
}

function CurrentBatchDone {
  if (-not (Test-Path $Log)) { return $false }
  $lines = Get-Content $Log
  $startIdx = -1
  for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match [regex]::Escape($SessionMarker)) { $startIdx = $i }
    if ($lines[$i] -match "RENDER_START 01_ColdOpen") { $startIdx = $i }
  }
  # Prefer latest RENDER_START 01
  for ($i = $lines.Count - 1; $i -ge 0; $i--) {
    if ($lines[$i] -match "RENDER_START 01_ColdOpen") { $startIdx = $i; break }
  }
  if ($startIdx -lt 0) { return $false }
  for ($i = $startIdx + 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match "RENDER_DONE 01_ColdOpen") { return $true }
  }
  return $false
}

function BlenderStillOnS01 {
  $p = Get-CimInstance Win32_Process -EA SilentlyContinue | Where-Object {
    $_.Name -eq "blender.exe" -and $_.CommandLine -match "render_scenes"
  }
  return [bool]$p
}

# Clear false-positive flags from partial-file detection
if (Test-Path $Flag) {
  $t = Get-Content $Flag -Raw -EA SilentlyContinue
  if ($t -and -not (CurrentBatchDone)) {
    Remove-Item $Flag -Force -EA SilentlyContinue
    Remove-Item $Pending -Force -EA SilentlyContinue
    W "cleared false-positive S01 complete flags"
  }
}

$cidLabel = "UNSET"
if ($ChatId) { $cidLabel = "$ChatId" }
W ("watch_s01_telegram START chat_id=" + $cidLabel)

while ($true) {
  if (Test-Path $Flag) {
    $flagText = Get-Content $Flag -Raw -EA SilentlyContinue
    if ($flagText -match "TELEGRAM_SENT=1") {
      W "already notified - exit"
      break
    }
  }

  if (CurrentBatchDone) {
    # Extra safety: if blender still writing this batch, wait until process exits or log shows next scene
    if (BlenderStillOnS01) {
      $tail = Get-Content $Log -Tail 5 -EA SilentlyContinue
      $movedOn = ($tail -join "`n") -match "RENDER_START 02_|SKIP 02_|ALL_SCENES"
      if (-not $movedOn) {
        W "log has DONE but blender still on render_scenes - wait confirm"
        Start-Sleep -Seconds $PollSec
        continue
      }
    }

    W "S01 COMPLETE detected (current batch)"
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    $msg = "Africa S1 - Scene 01 Cold Open COMPLETE. File: renders/video_clips/01_ColdOpen.mp4 Time: $stamp Next: S02-S10 HQ (no YB) then assemble / Resolve pace."
    $flagBody = "S01_COMPLETE=$stamp`r`nTELEGRAM_SENT=0`r`n$msg"
    Set-Content -Path $Flag -Value $flagBody -Encoding UTF8
    Set-Content -Path $Pending -Value $msg -Encoding UTF8
    W "Wrote TELEGRAM_S01_PENDING.txt for Composio ping"

    $token = $env:TELEGRAM_BOT_TOKEN
    if ($ChatId -and $token) {
      try {
        $uri = "https://api.telegram.org/bot$token/sendMessage"
        $body = (@{ chat_id = $ChatId; text = $msg } | ConvertTo-Json -Compress)
        Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json; charset=utf-8" | Out-Null
        (Get-Content $Flag) -replace "TELEGRAM_SENT=0", "TELEGRAM_SENT=1" | Set-Content $Flag -Encoding UTF8
        W ("Telegram sent via Bot API to " + $ChatId)
      } catch {
        W ("Bot API send failed: " + $_.Exception.Message)
      }
    } else {
      W "DM @Manu_Tgbot then set AFRICA_TELEGRAM_CHAT_ID - agent Composio-sends from PENDING"
    }
    Write-Host "AGENT_S01_COMPLETE_TELEGRAM_PENDING"
    break
  }
  Start-Sleep -Seconds $PollSec
}
W "watch_s01_telegram END"
