# Full Episode 01 reformulation: apply ALL locks/resources THEN force HQ re-render all 10 scenes.
# Blender 5.1 only. Does NOT start 4K. ASCII-only (avoid smart punctuation).
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Bl = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$Blend = Join-Path $Project "blend\africa_s1_master_v01.blend"
$RenderPy = Join-Path $Project "render_scenes_mp4.py"
$Log = Join-Path $Project "reformulation_full_log.txt"
$Clips = Join-Path $Project "renders\video_clips"
$Marker = Join-Path $Project "STATUS_REFORM_PRELOCKS_DONE.txt"

function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $Log -Value $l
  Write-Host $l
}

function Run-Blend([string]$script, [string]$tag) {
  $path = Join-Path $Project $script
  if (-not (Test-Path $path)) { W "SKIP missing $script"; return 0 }
  W "=== LOCK $tag : $script ==="
  $outLog = Join-Path $Project ("reform_" + $tag + "_log.txt")
  & $Bl -b $Blend -P $path 2>&1 | Tee-Object -FilePath $outLog
  $code = $LASTEXITCODE
  W ("exit $tag = {0}" -f $code)
  return $code
}

Set-Content -Path $Log -Value ("[{0}] reformulation boot" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
W "=== FULL REFORMULATION START ==="
W "GPU must be free; one Blender job at a time"

Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -eq "blender.exe" -and $_.CommandLine -match "-b " } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; W ("killed blender {0}" -f $_.ProcessId) }
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
  Where-Object { $_.CommandLine -match "wait_hq_assemble" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; W ("killed watcher {0}" -f $_.ProcessId) }

New-Item -ItemType Directory -Force -Path $Clips | Out-Null
Get-ChildItem $Clips -Filter "*.mp4" -ErrorAction SilentlyContinue | ForEach-Object {
  Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
  W ("cleared {0}" -f $_.Name)
}

$steps = @(
  @{ s = "setup_photoreal_stack_51.py"; t = "01_photoreal_stack" },
  @{ s = "setup_softpop_photoreal.py"; t = "02_softpop" },
  @{ s = "setup_camera_framing_textures_lock.py"; t = "03_framing" },
  @{ s = "setup_yellow_ball_teded_physics.py"; t = "04_yellow_ball" },
  @{ s = "setup_yb_body_humanoid.py"; t = "05_yb_body" },
  @{ s = "setup_blender_rig_animation_lock.py"; t = "06_rig_anim" },
  @{ s = "setup_documentary_aesthetic_lock.py"; t = "07_doc_aesthetic" },
  @{ s = "setup_arch_comm_iv_lock.py"; t = "08_arch_comm" }
)
$fail = 0
foreach ($st in $steps) {
  $c = Run-Blend $st.s $st.t
  if ($c -ne 0) { $fail++ }
}

$stamp = Get-Date -Format o
@(
  "REFORM_PRELOCKS=$stamp",
  "photoreal+softpop+framing+teded_ball+yb_body+rig_lock+doc_aesthetic+arch_comm_iv",
  "polyhaven=assets/textures/polyhaven + assets/hdri",
  "vo=assets/audio/vo/episode_01_vo.wav",
  "force_rerender=AFRICA_FORCE_RERENDER=1",
  "4k=HOLD",
  "fail_count=$fail"
) | Set-Content -Encoding utf8 $Marker
W ("Wrote {0} (fail_count={1})" -f $Marker, $fail)

W "=== FORCE HQ RE-RENDER ALL 10 SCENES ==="
$env:AFRICA_FORCE_RERENDER = "1"
$renderLog = Join-Path $Project "sasa_hq_rerender_log.txt"
$errLog = Join-Path $Project "sasa_hq_rerender_err.txt"
Set-Content -Path $renderLog -Value ("=== REFORM FORCE RENDER {0} AFRICA_FORCE_RERENDER=1 ===" -f $stamp)

$cmdLines = @(
  "`$env:AFRICA_FORCE_RERENDER = '1'",
  "Set-Location -LiteralPath '$Project'",
  "& '$Bl' -b '$Blend' -P '$RenderPy' *>> '$renderLog' 2>> '$errLog'"
)
$cmdPath = Join-Path $Project "scripts\_launch_force_render.ps1"
Set-Content -Path $cmdPath -Value ($cmdLines -join "`r`n") -Encoding utf8
$p = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File",$cmdPath) -PassThru -WindowStyle Hidden
W ("render wrapper pid={0}" -f $p.Id)
Start-Sleep -Seconds 10
$b = Get-CimInstance Win32_Process -Filter "Name='blender.exe'" | Where-Object { $_.CommandLine -match "render_scenes_mp4" } | Select-Object -First 1
if ($b) {
  try {
    $gp = Get-Process -Id $b.ProcessId
    $gp.PriorityClass = "High"
    W ("blender pid={0} priority=High" -f $b.ProcessId)
  } catch {
    W ("priority skip: {0}" -f $_)
  }
} else {
  W "WARN: blender render not detected yet - check sasa_hq_rerender_log.txt"
}

Start-Process powershell -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File",(Join-Path $Project "wait_hq_assemble.ps1")) -WindowStyle Minimized
W "watcher started"
W "=== FULL REFORMULATION ARMED - ETA ~20h for 10/10 HQ ==="
W "AGENT_LOOP_TICK_hourly_report"
