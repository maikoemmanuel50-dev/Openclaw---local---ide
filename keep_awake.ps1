# Keep system awake using Win32 SetThreadExecutionState API
# This is more robust than simulating keypresses

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class PowerState {
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern uint SetThreadExecutionState(uint esFlags);
    
    public const uint ES_CONTINUOUS = 0x80000000;
    public const uint ES_SYSTEM_REQUIRED = 0x00000001;
    public const uint ES_DISPLAY_REQUIRED = 0x00000002;
}
"@

# Prevent system sleep and display timeout indefinitely
$result = [PowerState]::SetThreadExecutionState([PowerState]::ES_CONTINUOUS -bor [PowerState]::ES_SYSTEM_REQUIRED -bor [PowerState]::ES_DISPLAY_REQUIRED)

if ($result -eq 0) {
    Write-Host "Warning: SetThreadExecutionState failed. System may still sleep." -ForegroundColor Yellow
} else {
    Write-Host "System sleep prevention active. Press Ctrl+C to stop." -ForegroundColor Green
}

# Keep script running to maintain the state
try {
    while ($true) {
        Start-Sleep -Seconds 60
    }
} finally {
    # Reset to allow sleep when script exits
    [PowerState]::SetThreadExecutionState([PowerState]::ES_CONTINUOUS)
    Write-Host "Sleep prevention disabled." -ForegroundColor Yellow
}
