# Build Blender 5.1 sidecar open (save .blend only) — no GPU render yet.
$ErrorActionPreference = "Stop"
$root = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$blender = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$script = Join-Path $root "setup_teded_open30_blender51.py"
$log = Join-Path $root "renders\quality\teded_open30_build_log.txt"
$env:CUDA_VISIBLE_DEVICES = "-1"
$env:AFRICA_SKIP_OPEN30_RENDER = "1"
& $blender -b -P $script 2>&1 | Tee-Object -FilePath $log
"exit=$LASTEXITCODE"
