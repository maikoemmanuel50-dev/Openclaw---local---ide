# Phase A: Finish 1080p -> save 7min master
# Phase B: On completion, start 4K render -> save 7min 4K master
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Blender = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$Blend = Join-Path $Project "blend\africa_s1_master_v01.blend"
$Log = Join-Path $Project "workflow_1080_then_4k_log.txt"
$Scenes = @(
    "01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone",
    "05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity",
    "09_Closer","10_EndCard"
)

function Write-Log([string]$msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $Log -Value $line -ErrorAction SilentlyContinue
    Write-Host $line
}

function Wait-Clips([string]$dir, [int]$minKB, [string]$doneFlag, [string]$label) {
    Write-Log ("Waiting for {0} clips in {1} ..." -f $label, $dir)
    while ($true) {
        $n = 0
        foreach ($s in $Scenes) {
            $p = Join-Path $dir ($s + ".mp4")
            if ((Test-Path $p) -and ((Get-Item $p).Length -ge ($minKB * 1KB))) { $n++ }
        }
        $flagHit = $false
        foreach ($f in @("sasa_render_log.txt","render_log.txt","sasa_4k_render_log.txt")) {
            $rl = Join-Path $Project $f
            if (Test-Path $rl) {
                $t = Get-Content $rl -Tail 10 -Raw -ErrorAction SilentlyContinue
                if ($t -and ($t -match $doneFlag)) { $flagHit = $true }
            }
        }
        Write-Log ("  {0} clips: {1}/10" -f $label, $n)
        # Require all 10 clips on disk (ignore stale ALL_SCENES flags in old logs)
        if ($n -eq 10) { break }
        if ($flagHit -and $n -ge 9) { break }
        if (-not (Get-Process blender -ErrorAction SilentlyContinue)) {
            Write-Log "  (Blender not running - still waiting for all clips)"
        }
        Start-Sleep -Seconds 120
    }
    Write-Log ("{0} clips ready." -f $label)
}

# -- PHASE A: 1080p --
Write-Log "=== PHASE A: 1080p pipeline ==="
$Clips1080 = Join-Path $Project "renders\video_clips"
Wait-Clips $Clips1080 800 "ALL_SCENES_RENDERED" "1080p"

Write-Log "Assembling 1080p 7-min master..."
$out1080 = Join-Path $Project "Africa_S1_Silicon_Savannah_7min.mp4"
$master1080 = Join-Path $Project "Africa_S1_Silicon_Savannah_7min_MASTER.mp4"
python (Join-Path $Project "assemble_final_video.py") --dir $Clips1080 --output $out1080 --master $master1080
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: 1080p assembly failed"; exit 1 }

if (Test-Path $out1080) {
    $mb = [math]::Round((Get-Item $out1080).Length / 1MB, 1)
    Write-Log ("1080p SAVED: {0} ({1} MB)" -f $out1080, $mb)
}
"1080p_complete=1`npath=$out1080" | Set-Content (Join-Path $Project "STATUS_1080P_COMPLETE.txt")
Write-Log "=== PHASE A COMPLETE ==="

# -- PHASE B: 4K (gated) --
$hold = Join-Path $Project "STATUS_4K_HOLD.txt"
$cleared = Join-Path $Project "STATUS_PRE4K_GATE_CLEARED.txt"
if ((Test-Path $hold) -and (-not (Test-Path $cleared))) {
    Write-Log "PHASE B SKIPPED: PRE_4K_GATE still open (see docs/PRE_4K_GATE.md). 4K will not auto-start."
    Write-Log "Complete creative remaining steps, then create STATUS_PRE4K_GATE_CLEARED.txt or remove STATUS_4K_HOLD.txt"
    exit 0
}

Write-Log "=== PHASE B: initiating 4K render with Blender 5.1 ==="
if (-not (Test-Path $Blender)) {
    Write-Log "ERROR: Blender 5.1 not found at $Blender"
    exit 1
}
$Clips4K = Join-Path $Project "renders\video_clips_4k"
New-Item -ItemType Directory -Force -Path $Clips4K | Out-Null

Get-Process blender -ErrorAction SilentlyContinue | Where-Object { $_.WorkingSet64 -gt 100MB } | ForEach-Object {
    Write-Log ("Stopping leftover Blender PID {0} before 4K..." -f $_.Id)
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 3

$Log4K = Join-Path $Project "sasa_4k_render_log.txt"
$Err4K = Join-Path $Project "sasa_4k_render_err.txt"
("=== 4K START Blender 5.1 {0} ===" -f (Get-Date)) | Out-File $Log4K
$script4k = Join-Path $Project "render_scenes_4k.py"
Start-Process -FilePath $Blender `
    -ArgumentList "-b `"$Blend`" -P `"$script4k`"" `
    -WorkingDirectory $Project `
    -RedirectStandardOutput $Log4K `
    -RedirectStandardError $Err4K `
    -WindowStyle Hidden
Write-Log ("4K Blender 5.1 batch started. Monitor: {0}" -f $Log4K)

Wait-Clips $Clips4K 1500 "ALL_SCENES_RENDERED_4K" "4K"

Write-Log "Assembling 4K 7-min master..."
$out4k = Join-Path $Project "Africa_S1_Silicon_Savannah_7min_4K.mp4"
$master4k = Join-Path $Project "Africa_S1_Silicon_Savannah_7min_4K_MASTER.mp4"
python (Join-Path $Project "assemble_final_video.py") --dir $Clips4K --output $out4k --master $master4k
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: 4K assembly failed"; exit 1 }

if (Test-Path $out4k) {
    $mb = [math]::Round((Get-Item $out4k).Length / 1MB, 1)
    Write-Log ("4K SAVED: {0} ({1} MB)" -f $out4k, $mb)
}
@"
1080p=Africa_S1_Silicon_Savannah_7min.mp4
4k=Africa_S1_Silicon_Savannah_7min_4K.mp4
folder=$Project
"@ | Set-Content (Join-Path $Project "STATUS_BOTH_COMPLETE.txt")
Write-Log "=== PHASE B COMPLETE - 1080p + 4K masters in project folder ==="
