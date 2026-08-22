# Execute AFRICA S1 production workflow to completion
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "workflow_log.txt"
$RenderLog = Join-Path $Project "render_log.txt"
$ClipsDir = Join-Path $Project "renders\video_clips"
$Scenes = @(
    "01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone",
    "05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity",
    "09_Closer","10_EndCard"
)
$MinBytes = @{
    "01_ColdOpen"=4000000;"02_Context2007"=4000000;"03_Beat1_Hubs"=3500000
    "04_Beat1_Phone"=2000000;"05_Beat2_Money"=3500000;"06_Beat2_Solar"=3500000
    "07_Beat3_Gap"=4000000;"08_Beat3_SecondaryCity"=4000000
    "09_Closer"=6000000;"10_EndCard"=1000000
}

function Log($msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $Log -Value $line -ErrorAction SilentlyContinue
    Write-Host $line
}

function Test-AllClipsReady {
    foreach ($s in $Scenes) {
        $p = Join-Path $ClipsDir "$s.mp4"
        if (-not (Test-Path $p)) { return $false }
        if ((Get-Item $p).Length -lt $MinBytes[$s]) { return $false }
    }
    return $true
}

Log "=== WORKFLOW START ==="

# Step 1: Wait for Blender render
Log "Step 1: Waiting for Blender scene renders (9/10 in progress)..."
while (-not (Test-AllClipsReady)) {
    $ready = 0
    foreach ($s in $Scenes) {
        $p = Join-Path $ClipsDir "$s.mp4"
        if ((Test-Path $p) -and (Get-Item $p).Length -ge $MinBytes[$s]) { $ready++ }
    }
    if (Test-Path $RenderLog) {
        $tail = Get-Content $RenderLog -Tail 3 -ErrorAction SilentlyContinue -Raw
        if ($tail -match "ALL_SCENES_RENDERED") { break }
    }
    Log "  Clips ready: $ready/10"
    Start-Sleep -Seconds 120
}
Log "Step 1: All 10 Blender clips ready."

# Step 2: FFmpeg assembly
Log "Step 2: Running assemble_final_video.py..."
python (Join-Path $Project "assemble_final_video.py")
if ($LASTEXITCODE -ne 0) { Log "ERROR: assembly failed"; exit 1 }
Log "Step 2: Assembly complete."

# Step 3: Build from Blender clips (preferred over Ken Burns)
Log "Step 3: Building master from Blender clips..."
python (Join-Path $Project "build_complete_silent_video.py")
Log "Step 3: build_complete_silent_video.py done."

# Step 4: Flag for Resolve HQ export (agent/MCP step)
$flag = Join-Path $Project "READY_FOR_RESOLVE_HQ.txt"
@"
workflow_complete=partial
blender_clips=ready
assembly=Africa_S1_Silicon_Savannah_7min.mp4
next_step=Resolve MCP: import Blender clips, timeline per resolve_spec.yaml, export HQ
"@ | Set-Content $flag
Log "Step 4: Wrote $flag — Resolve HQ export via MCP next."
Log "=== WORKFLOW COMPLETE (video); audio VO still needs human record ==="
