param([int]$IntervalMin = 60)
# Hourly completion report for Africa Season 1 render. Run as a scheduled task or
# in a background window. Writes one line per report to hourly_reports.log.
$proj = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$M = Join-Path $proj "renders\video_clips\masters"
$Report = Join-Path $proj "hourly_reports.log"
$frames = @{ "05_Beat2_Money"=1080; "06_Beat2_Solar"=960; "07_Beat3_Gap"=1200; "08_Beat3_SecondaryCity"=840; "09_Closer"=1680; "10_EndCard"=360 }

function Get-State {
  $rem = 0; $parts = @()
  foreach ($k in $frames.Keys) {
    $n = @(Get-ChildItem (Join-Path $M $k) -Filter "frame_*.png" -EA SilentlyContinue).Count
    $rem += ($frames[$k] - $n)
    $parts += "$($frames[$k]-$n)"
  }
  $bs = Get-CimInstance -Namespace root\wmi -ClassName BatteryStatus -EA SilentlyContinue
  $bat = Get-CimInstance Win32_Battery -EA SilentlyContinue
  $gpu = ((nvidia-smi --query-gpu=utilization.gpu,power.draw,temperature.gpu --format=csv,noheader,nounits 2>$null) | Select-Object -First 1)
  $proc = @(Get-Process blender -EA SilentlyContinue).Count
  return @{
    rem = $rem; parts = ($parts -join ",")
    ac = $bs.PowerOnline; pct = $bat.EstimatedChargeRemaining; gpu = $gpu; blender = $proc
  }
}

while ($true) {
  $s = Get-State
  $etaH = [math]::Round($s.rem * 10 / 3600, 1)
  $totH = [math]::Round($s.rem * 10 / 3600 + 4.5, 1)
  $done = (Get-Date).AddHours($totH).ToString("MM/dd HH:mm")
  $line = ("[{0}] AC={1} Btry={2}% blender={3} remaining={4} (S05-S10: {5}) ETA_render={6}h ETA_total={7}h done~{8} GPU={9}" -f `
    (Get-Date).ToString("MM/dd HH:mm"), $s.ac, $s.pct, $s.blender, $s.rem, $s.parts, $etaH, $totH, $done, $s.gpu)
  Write-Output $line
  Add-Content -Path $Report -Value $line -Encoding UTF8
  Start-Sleep -Seconds ($IntervalMin * 60)
}