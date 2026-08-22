# Canonical Blender path for Africa S1 — ALWAYS 5.1.2
$script:AfricaBlender = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
if (-not (Test-Path $script:AfricaBlender)) {
    throw "Blender 5.1 not found at $script:AfricaBlender — do not fall back to 4.4 (blend file is 5.1-only)."
}
