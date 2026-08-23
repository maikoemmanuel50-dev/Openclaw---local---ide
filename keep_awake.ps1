# Keep system awake by simulating activity every 30 seconds
while ($true) {
    # Move mouse slightly to prevent sleep
    $wshell = New-Object -ComObject WScript.Shell
    $wshell.SendKeys("{SCROLLLOCK}")
    Start-Sleep -Seconds 30
}