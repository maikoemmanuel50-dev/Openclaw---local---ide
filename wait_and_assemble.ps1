$ErrorActionPreference = "Stop"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "render_log.txt"
$ClipsDir = Join-Path $Project "renders\video_clips"
$Scenes = @(
    "01_ColdOpen","02_Context2007","03_Beat1_Hubs","04_Beat1_Phone",
    "05_Beat2_Money","06_Beat2_Solar","07_Beat3_Gap","08_Beat3_SecondaryCity",
    "09_Closer","10_EndCard"
)

Write-Host "Waiting for Blender render to finish..."
while ($true) {
    if (Test-Path $Log) {
        $tail = Get-Content $Log -Tail 5 -ErrorAction SilentlyContinue
        if ($tail -match "ALL_SCENES_RENDERED") { break }
    }
    $done = 0
    foreach ($s in $Scenes) {
        $p = Join-Path $ClipsDir "$s.mp4"
        if ((Test-Path $p) -and ((Get-Item $p).Length -gt 100KB)) { $done++ }
    }
    Write-Host ("[{0}] Clips ready: {1}/10" -f (Get-Date -Format "HH:mm:ss"), $done)
    Start-Sleep -Seconds 120
}

Write-Host "Render complete. Running assembly..."
python (Join-Path $Project "assemble_final_video.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$out = Join-Path $Project "Africa_S1_Silicon_Savannah_7min.mp4"
if (Test-Path $out) {
    $mb = [math]::Round((Get-Item $out).Length / 1MB, 1)
    Write-Host "SUCCESS: $out ($mb MB)"
} else {
    Write-Host "ERROR: Final video not found"
    exit 1
}
