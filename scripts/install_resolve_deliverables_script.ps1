# Install in-Resolve deliverables runner (Utility menu)
$ErrorActionPreference = "Stop"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$DestDir = Join-Path $env:APPDATA "Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"
$Dest = Join-Path $DestDir "AfricaS1_RunDeliverables.py"
$Src = Join-Path $Project "scripts\resolve_run_deliverables.py"
New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
Copy-Item $Src $Dest -Force
Write-Host "Installed: $Dest"
Write-Host "In Resolve: Workspace -> Scripts -> Utility -> AfricaS1_RunDeliverables"
