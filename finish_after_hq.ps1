# Post-HQ finish: normalize clips -> copy to built_clips -> assemble -> Resolve place -> status
# Invoked by wait_hq_assemble.ps1 when 10/10 ready.
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Clips = Join-Path $Project "renders\video_clips"
$Built = Join-Path $Project "renders\built_clips"
$Log = Join-Path $Project "finish_after_hq_log.txt"
$Scenes = @("01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone","05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity","09_Closer","10_EndCard")

function W([string]$m) {
  $l = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $Log -Value $l
  Write-Host $l
}

W "=== finish_after_hq START ==="

$bl = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$blend = Join-Path $Project "blend\africa_s1_master_v01.blend"
$prelocks = Join-Path $Project "STATUS_REFORM_PRELOCKS_DONE.txt"
$skipBlendLocks = Test-Path $prelocks
if ($skipBlendLocks) {
  W "STATUS_REFORM_PRELOCKS_DONE present — locks already baked into HQ plates; skip re-mutating blend before assemble"
} else {
  # Quality lock: camera ease + frustum framing + texture Smart filter (GPU free after batch)
  $camLock = Join-Path $Project "setup_camera_framing_textures_lock.py"
  if ((Test-Path $bl) -and (Test-Path $camLock)) {
    W "Running camera/framing/texture lock (Blender 5.1)..."
    & $bl -b $blend -P $camLock 2>&1 | Tee-Object -FilePath (Join-Path $Project "camera_framing_lock_log.txt")
    W ("camera_framing_lock exit={0}" -f $LASTEXITCODE)
  }
}

# Normalize Blender 5.1 names Scene0001-N.mp4 -> Scene.mp4
foreach ($s in $Scenes) {
  $dest = Join-Path $Clips ($s + ".mp4")
  if ((Test-Path $dest) -and ((Get-Item $dest).Length -gt 200KB)) { continue }
  $cands = Get-ChildItem $Clips -Filter ($s + "*.mp4") -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 200KB } | Sort-Object Length -Descending
  if ($cands) {
    $best = $cands[0]
    if ($best.FullName -ne $dest) {
      if (Test-Path $dest) { Remove-Item $dest -Force -ErrorAction SilentlyContinue }
      Move-Item $best.FullName $dest -Force
      W ("Renamed {0} -> {1}" -f $best.Name, ($s + ".mp4"))
    }
  }
}

# Mirror into built_clips for Resolve V1 (current timeline paths)
New-Item -ItemType Directory -Force -Path $Built | Out-Null

W "Inject stock B-roll into TED-Ed 30s open..."
python (Join-Path $Project "scripts\inject_open30_stock_footage.py")
W ("inject_open30_stock exit={0}" -f $LASTEXITCODE)

W "Merging TED-Ed 30s open into S01 stem (0-720f)..."
python (Join-Path $Project "scripts\merge_open30_into_s01.py")
W ("merge_open30 exit={0}" -f $LASTEXITCODE)

foreach ($s in $Scenes) {
  if ($s -eq "01_ColdOpen") {
    $integrated = Join-Path $Clips "01_ColdOpen_with_open30.mp4"
    $dst = Join-Path $Built ($s + ".mp4")
    if ((Test-Path $integrated) -and ((Get-Item $integrated).Length -gt 200KB)) {
      Copy-Item $integrated $dst -Force
      W "built_clips S01: integrated open30 stem"
      continue
    }
  }
  $src = Join-Path $Clips ($s + ".mp4")
  $dst = Join-Path $Built ($s + ".mp4")
  if ((Test-Path $src) -and ((Get-Item $src).Length -gt 200KB)) {
    Copy-Item $src $dst -Force
    W ("Copied to built_clips: {0}" -f ($s + ".mp4"))
  }
}

$out = Join-Path $Project "Africa_S1_Silicon_Savannah_7min.mp4"
$master = Join-Path $Project "Africa_S1_Silicon_Savannah_7min_MASTER.mp4"
W "Assembling silent master..."
python (Join-Path $Project "assemble_final_video.py") --dir $Clips --output $out --master $master
W ("assemble_final_video exit={0}" -f $LASTEXITCODE)

W "Assembling with audio (active VO stem: episode_01_vo.wav)..."
python (Join-Path $Project "assemble_with_audio.py")
W ("assemble_with_audio exit={0}" -f $LASTEXITCODE)

if (-not $skipBlendLocks) {
  # Yellow ball / YB / rig / doc — only if plates were rendered without prelocks
  $ybBall = Join-Path $Project "setup_yellow_ball_teded_physics.py"
  if ((Test-Path $ybBall) -and (Test-Path $bl)) {
    W "Running Yellow Ball TED-Ed physics/rig (Blender 5.1)..."
    & $bl -b $blend -P $ybBall 2>&1 | Tee-Object -FilePath (Join-Path $Project "yellow_ball_teded_log.txt")
    W ("yellow_ball_teded exit={0}" -f $LASTEXITCODE)
  }
  $yb = Join-Path $Project "setup_yb_body_humanoid.py"
  if ((Test-Path $yb) -and (Test-Path $bl)) {
    W "Running YB-Body humanoid setup (Blender 5.1)..."
    & $bl -b $blend -P $yb 2>&1 | Tee-Object -FilePath (Join-Path $Project "yb_body_setup_log.txt")
    W ("yb_body exit={0}" -f $LASTEXITCODE)
  }
  $rigLock = Join-Path $Project "setup_blender_rig_animation_lock.py"
  if ((Test-Path $rigLock) -and (Test-Path $bl)) {
    W "Running Blender rig+animation lock (tutorial pack)..."
    & $bl -b $blend -P $rigLock 2>&1 | Tee-Object -FilePath (Join-Path $Project "rig_animation_lock_log.txt")
    W ("rig_anim_lock exit={0}" -f $LASTEXITCODE)
  }
  $docLock = Join-Path $Project "setup_documentary_aesthetic_lock.py"
  if ((Test-Path $docLock) -and (Test-Path $bl)) {
    W "Running documentary aesthetic lock (Fern/Imperial/Lucas/tinynocky)..."
    & $bl -b $blend -P $docLock 2>&1 | Tee-Object -FilePath (Join-Path $Project "documentary_aesthetic_log.txt")
    W ("doc_aesthetic exit={0}" -f $LASTEXITCODE)
  }
  $archLock = Join-Path $Project "setup_arch_comm_iv_lock.py"
  if ((Test-Path $archLock) -and (Test-Path $bl)) {
    W "Running Arch Comm IV lock (JKUAT Blender Class 01-16)..."
    & $bl -b $blend -P $archLock 2>&1 | Tee-Object -FilePath (Join-Path $Project "arch_comm_iv_lock_log.txt")
    W ("arch_comm_iv exit={0}" -f $LASTEXITCODE)
  }
} else {
  W "Skipped post-render blend locks (prelocks already in rendered V1)"
}

# Resolve V1: built_clips + kinetic; YB overlays skipped (AFRICA_NO_YELLOW_BALL)
W "Import open30 + unique kinetic assets to Media Pool..."
python (Join-Path $Project "scripts\import_open30_resolve.py")
W ("import_open30 exit={0}" -f $LASTEXITCODE)
python (Join-Path $Project "scripts\resolve_open30_timeline.py")
W ("resolve_open30_timeline exit={0}" -f $LASTEXITCODE)
python (Join-Path $Project "scripts\import_unique_kinetic_assets.py")
W ("import_unique exit={0}" -f $LASTEXITCODE)

W "Pacing Resolve kinetic (YB overlays OFF)..."
$env:AFRICA_NO_YELLOW_BALL = "1"
python (Join-Path $Project "scripts\resolve_pace_kinetic_yb.py")
W ("resolve_pace exit={0}" -f $LASTEXITCODE)

W "Fairlight stems + A1–A5 place (active VO stem)..."
python (Join-Path $Project "scripts\resolve_fairlight_overnight.py")
W ("fairlight exit={0}" -f $LASTEXITCODE)

# Status stamp
$status = Join-Path $Project "PRODUCTION_STATUS.md"
$voActive = Test-Path (Join-Path $Project "assets\audio\vo\episode_01_vo.wav")
$note = @"

---
## Auto finish stamp ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))
- HQ clips: mirrored to built_clips + assembled 7min / MASTER / FINAL
- Active VO stem (episode_01_vo.wav): $voActive — swap later via scripts/swap_vo_stem.py
- Yellow ball REMOVED from V1 plates (scenes 02–10 redo) + Resolve V2 YB overlays skipped
- Kinetic V3/V4 + Fairlight executed
- 4K still HOLD until PRE_4K_GATE #2–7 clear
"@
Add-Content -Path $status -Value $note -ErrorAction SilentlyContinue
W "=== finish_after_hq DONE ==="
