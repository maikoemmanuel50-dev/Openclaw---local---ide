# Hourly status reporter for Africa S1 finish pipeline (ASCII-safe)
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Report = Join-Path $Project "docs\HOURLY_PROGRESS.md"
$Latest = Join-Path $Project "STATUS_HOURLY_LATEST.txt"
$Log = Join-Path $Project "sasa_hq_rerender_log.txt"
$Clips = Join-Path $Project "renders\video_clips"
$Scenes = @("01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone","05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity","09_Closer","10_EndCard")

function Get-Frame {
  if (-not (Test-Path $Log)) { return @{ scene="?"; frame=0; total=0 } }
  $start = Select-String -Path $Log -Pattern "RENDER_START (\S+) frames=(\d+)" | Select-Object -Last 1
  $fr = Select-String -Path $Log -Pattern "Video append frame (\d+)" | Select-Object -Last 1
  $scene = if ($start -and $start.Line -match "RENDER_START (\S+)") { $Matches[1] } else { "?" }
  $frame = if ($fr -and $fr.Line -match "frame (\d+)") { [int]$Matches[1] } else { 0 }
  $total = if ($start -and $start.Line -match "frames=(\d+)") { [int]$Matches[1] } else { 0 }
  return @{ scene=$scene; frame=$frame; total=$total }
}

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$f = Get-Frame
$doneLog = @(Select-String -Path $Log -Pattern "RENDER_DONE" -ErrorAction SilentlyContinue).Count
$clipsReady = 0
foreach ($s in $Scenes) {
  $p = Join-Path $Clips ($s + ".mp4")
  if ((Test-Path $p) -and ((Get-Item $p).Length -gt 500KB)) { $clipsReady++ }
}
# Prefer real on-disk clips; historical RENDER_DONE lines inflate counts across batches
$clips = $clipsReady
$batch = @(Get-CimInstance Win32_Process -Filter "Name='blender.exe'" | Where-Object { $_.CommandLine -match "-b " }).Count
$vo = Test-Path (Join-Path $Project "assets\audio\vo\episode_01_vo.wav")
# Trust on-disk clips only (log can print ALL_SCENES after AFRICA_ONLY_SCENES skip stubs)
$allDone = ($clipsReady -ge 10)

$sceneSecs = @{
  "01_ColdOpen"=50; "02_Context2007"=45; "03_Beat1_Hubs"=45; "04_Beat1_Phone"=25
  "05_Beat2_Money"=45; "06_Beat2_Solar"=40; "07_Beat3_Gap"=50
  "08_Beat3_SecondaryCity"=35; "09_Closer"=70; "10_EndCard"=15
}
$idx = [array]::IndexOf($Scenes, $f.scene)
if ($idx -lt 0) { $idx = 0 }
$remainF = 0
if ($f.total -gt 0) { $remainF += [Math]::Max(0, $f.total - $f.frame) }
for ($i = $idx + 1; $i -lt $Scenes.Count; $i++) {
  $remainF += [int]($sceneSecs[$Scenes[$i]] * 24)
}
$spf = 8.1
$etaH = [math]::Round(($remainF * $spf) / 3600, 1)

$n = 1
if (Test-Path $Report) {
  $n = (@(Select-String -Path $Report -Pattern "^## Report #" ).Count) + 1
}

$batchLabel = if ($batch -gt 0) { "YES" } else { "NO" }
$allLabel = if ($allDone) { "YES" } else { "no" }
$spfLabel = ("{0}s/frame" -f $spf)

$block = @"

---

## Report #$n - $stamp EAT

### Snapshot
- HQ batch alive: $batchLabel | ALL_SCENES_RENDERED: $allLabel
- Current: **$($f.scene)** frame **$($f.frame)/$($f.total)**
- Finished scene MP4s: **$clips / 10**
- Remaining frames ~**$remainF** -> ETA **~${etaH}h** at $spfLabel
- Active VO stem (episode_01_vo.wav): **$vo** (placeholder bytes OK; swap later)

### Done (cumulative machine path)
- Soft-pop / photoreal / framing / AFRICA logo v2 / Arch Comm IV baked into blend
- HQ 1080p FORCE batch (Blender 5.1) — fidelity: high samples, OptiX denoise, AgX
- Resolve V2-V5 + kinetic/YB placed; A2 music ducked stem on timeline
- Audio excellence pack: docs/AUDIO_EXCELLENCE_PACK.md + FAIRLIGHT_A2_SIDECHAIN.md
- Overnight finish armed (wait_hq_assemble.ps1 -> finish_after_hq.ps1)

### Remaining
1. Finish HQ 10/10 clips (~${etaH}h) — industry-grade frames, no 4K until gate
2. Auto-assemble 7min + MASTER + FINAL (locked VO stem)
3. Resolve V1 refresh + morning picture/audio QA
4. Fairlight loudness check (~-16 LUFS VO); optional UI Ducker polish
5. 4K only after PRE_4K_GATE #2-7 clear

### Needs from you
- Keep machine awake; one GPU job only (Blender HQ)
- Optional later: final VO + swap_vo_stem.py; morning spot-check V1
"@

if (-not (Test-Path (Split-Path $Report))) {
  New-Item -ItemType Directory -Force -Path (Split-Path $Report) | Out-Null
}
if (-not (Test-Path $Report)) {
  Set-Content -Path $Report -Value "# Africa S1 - Hourly Progress Report`r`n"
}
Add-Content -Path $Report -Value $block
$open30Log = Join-Path $Project "renders\quality\teded_open30_render_log.txt"
$open30Fr = 0
if (Test-Path $open30Log) {
  $ofr = Select-String -Path $open30Log -Pattern "Video append frame (\d+)" | Select-Object -Last 1
  if ($ofr -and $ofr.Line -match "frame (\d+)") { $open30Fr = [int]$Matches[1] }
}
$morphOk = Test-Path (Join-Path $Project "renders\paced_overlays\episode_morph_pack_preview.mp4")
$qcLine = "QC: 5.1.2 only | 4K HOLD | YB waived | morph=$morphOk | open30_blender51=f$open30Fr/720"
$latestLine = "Africa S1 hourly - $stamp | scene=$($f.scene) frame=$($f.frame)/$($f.total) clips=$clips/10 eta_h=$etaH batch=$batch vo=$vo`r`n$qcLine"
Set-Content -Path $Latest -Value $latestLine -Encoding UTF8
Write-Host $block
Write-Host "AGENT_LOOP_TICK_hourly_report"

# Telegram copy via @Manu_Tgbot (User env TELEGRAM_BOT_TOKEN + chat_id file)
function Send-TelegramHourly([string]$text) {
  $tok = [Environment]::GetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "User")
  if (-not $tok) { $tok = $env:TELEGRAM_BOT_TOKEN }
  $cidPath = Join-Path $Project "renders\quality\TELEGRAM_CHAT_ID.txt"
  $cid = $null
  if (Test-Path $cidPath) { $cid = (Get-Content $cidPath -Raw).Trim() }
  if (-not $cid) { $cid = [Environment]::GetEnvironmentVariable("AFRICA_TELEGRAM_CHAT_ID", "User") }
  if (-not $tok -or -not $cid) {
    Write-Host "TELEGRAM_SKIP missing token or chat_id"
    return
  }
  # Telegram hard limit ~4096; keep under 3500
  if ($text.Length -gt 3500) { $text = $text.Substring(0, 3490) + "`n...(truncated)" }
  try {
    $uri = "https://api.telegram.org/bot$tok/sendMessage"
    $payload = @{ chat_id = $cid; text = $text } | ConvertTo-Json -Compress
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
    Invoke-RestMethod -Uri $uri -Method Post -Body $bytes -ContentType "application/json; charset=utf-8" | Out-Null
    Write-Host "TELEGRAM_SENT hourly to $cid"
    Add-Content -Path (Join-Path $Project "renders\quality\telegram_hourly_send_log.txt") -Value ("[{0}] sent {1} chars" -f (Get-Date -Format "s"), $text.Length)
  } catch {
    Write-Host ("TELEGRAM_FAIL " + $_.Exception.Message)
  }
}

$tgText = @"
Africa S1 hourly #$n — $stamp EAT
HQ: $($f.scene) $($f.frame)/$($f.total) | clips $clips/10 | ETA ~${etaH}h | batch=$batchLabel
ALL_SCENES=$allLabel | VO=$vo
$qcLine
Remaining: finish HQ 10/10 → assemble → Resolve V1 → Fairlight (−14 LUFS) → 4K HOLD until gate.
"@
Send-TelegramHourly $tgText
