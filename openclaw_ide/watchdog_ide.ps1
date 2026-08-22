# Watchdog for the OpenClaw Local IDE server.
# Polls http://127.0.0.1:8765 every 10s; if the server is dark, relaunches it.
# Run detached so it survives console closes:
#   powershell -NoProfile -ExecutionPolicy Bypass -File watchdog_ide.ps1
param(
    [int]$Port = 8765,
    [int]$PollSeconds = 10,
    [int]$StartupGraceSeconds = 8
)

$ErrorActionPreference = "SilentlyContinue"
$ideDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Python314\python.exe"
if (-not (Test-Path -LiteralPath $python)) { $python = "python" }
$outLog = Join-Path $ideDir "server_detached.log"
$errLog = Join-Path $ideDir "server_detached.log.err"
$watchdogLog = Join-Path $ideDir "watchdog.log"

function Test-ServerUp {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/api/status" -UseBasicParsing -TimeoutSec 4
        return $resp.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-IdeServer {
    $serverPy = Join-Path $ideDir "server.py"
    $argLine = "`"$serverPy`" --port $Port"
    Start-Process -FilePath $python -ArgumentList $argLine `
        -WorkingDirectory (Split-Path -Parent $ideDir) `
        -RedirectStandardOutput $outLog -RedirectStandardError $errLog `
        -WindowStyle Hidden | Out-Null
}

# Initial start if the server is not already running.
if (-not (Test-ServerUp)) {
    Start-IdeServer
    Start-Sleep -Seconds $StartupGraceSeconds
}

$restarts = 0
while ($true) {
    Start-Sleep -Seconds $PollSeconds
    if (-not (Test-ServerUp)) {
        $restarts++
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $watchdogLog -Value "[watchdog] $stamp server down (restart #$restarts) - relaunching"
        Start-IdeServer
        Start-Sleep -Seconds $StartupGraceSeconds
    }
}