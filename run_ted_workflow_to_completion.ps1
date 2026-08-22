# Wait for Sasa 1080p render → assemble 7-min master into project folder
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "workflow_log.txt"
$RenderLogs = @(
    (Join-Path $Project "sasa_render_log.txt"),
    (Join-Path $Project "render_log.txt")
)
$ClipsDir = Join-Path $Project "renders\video_clips"
$Scenes = @(
    "01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone",
    "05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity",
    "09_Closer","10_EndCard"
)
$MinBytes = @{
    "01_ColdOpen"=3000000; "02_Context2007"=3000000; "03_Beat1_Hubs"=2500000
    "04_Beat1_Phone"=1500000; "05_Beat2_Money"=2500000; "06_Beat2_Solar"=2500000
    "07_Beat3_Gap"=3000000; "08_Beat3_SecondaryCity"=2500000
    "09_Closer"=4000000; "10_EndCard"=800000
}

function Log($msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $Log -Value $line -ErrorAction SilentlyContinue
    Write-Host $line
}

function ClipsReady {
    foreach ($s in $Scenes) {
        $p = Join-Path $ClipsDir "$s.mp4"
        if (-not (Test-Path $p)) { return $false }
        if ((Get-Item $p).Length -lt $MinBytes[$s]) { return $false }
    }
    return $true
}

Log "=== Waiting for Sasa 1080p batch; will save 7min master to project folder ==="
while (-not (ClipsReady)) {
    $n = 0
    foreach ($s in $Scenes) {
        $p = Join-Path $ClipsDir "$s.mp4"
        if ((Test-Path $p) -and ((Get-Item $p).Length -ge $MinBytes[$s])) { $n++ }
    }
    foreach ($rl in $RenderLogs) {
        if (Test-Path $rl) {
            $t = Get-Content $rl -Tail 8 -Raw -ErrorAction SilentlyContinue
            if ($t -match "ALL_SCENES_RENDERED") { break }
        }
    }
    Log "  Clips ready: $n/10"
    # Abort wait if blender died and incomplete
    if (-not (Get-Process blender -ErrorAction SilentlyContinue)) {
        Log "WARNING: Blender not running — will keep waiting for clips or ALL_SCENES flag"
    }
    Start-Sleep -Seconds 120
}

Log "Assembling 7-min master..."
python (Join-Path $Project "assemble_final_video.py")
if ($LASTEXITCODE -ne 0) { Log "ERROR assembly"; exit 1 }

$out = Join-Path $Project "Africa_S1_Silicon_Savannah_7min.mp4"
$master = Join-Path $Project "Africa_S1_Silicon_Savannah_7min_MASTER.mp4"
if (Test-Path $out) {
    $mb = [math]::Round((Get-Item $out).Length / 1MB, 1)
    Log "SAVED: $out ($mb MB)"
}
if (Test-Path $master) {
    Log "SAVED: $master"
}
"COMPLETE=1`npath=$out`nresolution=1920x1080" | Set-Content (Join-Path $Project "READY_FOR_RESOLVE_HQ.txt")
Log "=== 7-MIN VIDEO SAVED TO PROJECT FOLDER ==="
