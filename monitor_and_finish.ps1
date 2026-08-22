# Monitor Blender render → assemble → rebuild silent video → log for Resolve
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "render_log.txt"
$MonitorLog = Join-Path $Project "monitor_log.txt"
$ClipsDir = Join-Path $Project "renders\video_clips"
$Scenes = @(
    "01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone",
    "05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity",
    "09_Closer","10_EndCard"
)

function Write-Monitor($msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $MonitorLog -Value $line
    Write-Host $line
}

function Get-ClipCount {
    $done = 0
    foreach ($s in $Scenes) {
        $p = Join-Path $ClipsDir "$s.mp4"
        if ((Test-Path $p) -and ((Get-Item $p).Length -gt 500KB)) { $done++ }
    }
    return $done
}

function Test-RenderStuck {
    param([int]$StaleMinutes = 15)
    if (-not (Test-Path $Log)) { return $false }
    $lastWrite = (Get-Item $Log).LastWriteTime
    return ((Get-Date) - $lastWrite).TotalMinutes -gt $StaleMinutes
}

Write-Monitor "Monitor started."

# Phase 1: Build immediate silent video from heroes/stock (don't wait for Blender)
Write-Monitor "Building silent video from heroes + stock..."
python (Join-Path $Project "build_complete_silent_video.py") 2>&1 | ForEach-Object { Write-Monitor $_ }

# Phase 2: Monitor Blender render
$lastClipCount = Get-ClipCount
$stuckChecks = 0
while ($true) {
    $clipCount = Get-ClipCount
    Write-Monitor "Blender clips ready: $clipCount/10"

    if (Test-Path $Log) {
        $tail = Get-Content $Log -Tail 3 -ErrorAction SilentlyContinue -Raw
        if ($tail -match "ALL_SCENES_RENDERED") {
            Write-Monitor "Blender render COMPLETE."
            break
        }
    }

    if ($clipCount -eq 10) {
        Write-Monitor "All 10 Blender clips detected."
        break
    }

    if (Test-RenderStuck -StaleMinutes 20) {
        $stuckChecks++
        Write-Monitor "WARNING: Render log stale >20min (stuck check #$stuckChecks)"
        if ($stuckChecks -ge 2) {
            Write-Monitor "Render appears stuck. Using hero/stock build as primary deliverable."
            break
        }
    }

    if ($clipCount -gt $lastClipCount) {
        Write-Monitor "New clip detected — rebuilding with Blender clips..."
        python (Join-Path $Project "build_complete_silent_video.py") 2>&1 | ForEach-Object { Write-Monitor $_ }
        $lastClipCount = $clipCount
    }

    Start-Sleep -Seconds 180
}

# Phase 3: Final assembly if all blender clips exist
if ((Get-ClipCount) -eq 10) {
    Write-Monitor "Running ffmpeg assembly from Blender clips..."
    python (Join-Path $Project "assemble_final_video.py") 2>&1 | ForEach-Object { Write-Monitor $_ }
    Write-Monitor "Rebuilding unified silent master with Blender clips..."
    python (Join-Path $Project "build_complete_silent_video.py") 2>&1 | ForEach-Object { Write-Monitor $_ }
}

$final = Join-Path $Project "Africa_S1_Silicon_Savannah_7min_silent.mp4"
$canonical = Join-Path $Project "Africa_S1_Silicon_Savannah_7min.mp4"
if (Test-Path $final) {
    $mb = [math]::Round((Get-Item $final).Length / 1MB, 1)
    Write-Monitor "FINAL SILENT VIDEO: $final ($mb MB)"
}
if (Test-Path $canonical) {
    $mb = [math]::Round((Get-Item $canonical).Length / 1MB, 1)
    Write-Monitor "CANONICAL OUTPUT: $canonical ($mb MB)"
}

Write-Monitor "Monitor complete. Resolve assembly can proceed via MCP."
Write-Monitor "READY_FOR_RESOLVE=1"
