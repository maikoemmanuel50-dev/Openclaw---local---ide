# Poll Composio PENDING + remind: chat_id must come from getUpdates after /start to @Manu_Tgbot
param([int]$MaxMinutes = 180)
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Pending = Join-Path $Project "renders\quality\TELEGRAM_S01_PENDING.txt"
$ChatFile = Join-Path $Project "renders\quality\TELEGRAM_CHAT_ID.txt"
$Log = Join-Path $Project "renders\quality\poll_telegram_chat_id_log.txt"
function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $Log -Value $l
  Write-Host $l
}
W "poll_telegram_chat_id START"
$deadline = (Get-Date).AddMinutes($MaxMinutes)
while ((Get-Date) -lt $deadline) {
  if (Test-Path $ChatFile) {
    $cid = (Get-Content $ChatFile -Raw).Trim()
    if ($cid) {
      W "chat_id file present: $cid"
      [Environment]::SetEnvironmentVariable("AFRICA_TELEGRAM_CHAT_ID", $cid, "User")
      $env:AFRICA_TELEGRAM_CHAT_ID = $cid
      if (Test-Path $Pending) {
        W "PENDING exists - agent should Composio TELEGRAM_SEND_MESSAGE now"
        Write-Host "AGENT_SEND_TELEGRAM_PENDING"
      }
      break
    }
  }
  Start-Sleep -Seconds 30
}
W "poll_telegram_chat_id END"
