$ErrorActionPreference = "Continue"
$script = "C:\Users\HP\OneDrive\The Vault\Africa Season 1\scripts\hourly_status_report.ps1"
while ($true) {
  Start-Sleep -Seconds 3600
  try { & powershell -NoProfile -ExecutionPolicy Bypass -File $script } catch { $_ | Out-String | Write-Host }
}
