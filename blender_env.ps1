# Canonical Blender for Africa Season 1 — ALWAYS use 5.1 (blend file is 5.x)
# Dot-source: . .\blender_env.ps1
$script:BLENDER_EXE = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$script:BLENDER_VERSION = "5.1.2"
if (-not (Test-Path $script:BLENDER_EXE)) {
    throw "Blender 5.1 not found at $script:BLENDER_EXE — install Blender 5.1.2 and retry."
}
