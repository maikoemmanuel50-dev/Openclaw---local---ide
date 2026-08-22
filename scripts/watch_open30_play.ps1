# Open 30s open in default media player when Blender51 render verifies.
param(
  [string]$Mp4 = "C:\Users\HP\OneDrive\The Vault\Africa Season 1\renders\paced_overlays\s01_teded_open30_blender51.mp4",
  [string]$Log = "C:\Users\HP\OneDrive\The Vault\Africa Season 1\renders\quality\teded_open30_render_log.txt",
  [int]$PollSec = 60
)
$ErrorActionPreference = "Continue"
$WatchLog = "C:\Users\HP\OneDrive\The Vault\Africa Season 1\renders\quality\watch_open30_play_log.txt"
function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $WatchLog -Value $l -Encoding UTF8
  Write-Host $l
}
W "watch_open30_play START target=$Mp4"
while ($true) {
  if (Test-Path $Log) {
    $tail = Get-Content $Log -Tail 20 -ErrorAction SilentlyContinue
    if ($tail -match "RENDER_DONE open30_blender51") {
      if (Test-Path $Mp4) {
        $probe = & ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames,duration -of default=noprint_wrappers=1 $Mp4 2>$null
        W "verified: $probe"
        Start-Process $Mp4
        W "OPENED media player"
        break
      }
    }
  }
  Start-Sleep -Seconds $PollSec
}
W "watch_open30_play END"
