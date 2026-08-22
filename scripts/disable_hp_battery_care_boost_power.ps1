# Disable HP Battery Care when exposed; force High Performance for HQ renders.
# Run elevated if possible: Right-click PowerShell → Run as administrator
$ErrorActionPreference = "Continue"
$Project = "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
$Log = Join-Path $Project "renders\quality\battery_care_boost_log.txt"
function L($m) {
  $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m
  Add-Content -Path $Log -Value $line -EA SilentlyContinue
  Write-Host $line
}

New-Item -ItemType Directory -Force -Path (Split-Path $Log) | Out-Null
L "=== battery care / power boost ==="

# --- HP BIOS WMI (business / some OMEN; often missing on Victus) ---
$disabled = $false
try {
  $iface = Get-CimInstance -Namespace root\HP\InstrumentedBIOS -ClassName HP_BIOSSettingInterface -EA Stop
  $settings = Get-CimInstance -Namespace root\HP\InstrumentedBIOS -ClassName HP_BIOSSetting -EA SilentlyContinue
  foreach ($s in $settings) {
    if ($s.Name -match 'Battery Care|BatteryCare|Adaptive Battery|Battery Health|Charge Limit') {
      L ("Found BIOS setting: {0} = {1}" -f $s.Name, $s.Value)
      foreach ($want in @("100%", "Disabled", "Off", "Maximize my battery's lifespan - Off", "Let HP manage my battery charging - Off")) {
        try {
          $r = Invoke-CimMethod -InputObject $iface -MethodName SetBIOSSetting -Arguments @{ Name = $s.Name; Value = $want }
          L ("SetBIOSSetting {0} -> {1} ret={2}" -f $s.Name, $want, $r.Return)
          if ($r.Return -eq 0) { $disabled = $true; break }
        } catch {}
      }
    }
  }
} catch {
  L "HP InstrumentedBIOS not available (common on Victus): $($_.Exception.Message)"
}

# Registry heuristics
$regHits = @()
foreach ($root in @(
  "HKLM:\SOFTWARE\HP",
  "HKLM:\SOFTWARE\WOW6432Node\HP",
  "HKCU:\SOFTWARE\HP",
  "HKLM:\SOFTWARE\Hewlett-Packard",
  "HKLM:\SOFTWARE\WOW6432Node\Hewlett-Packard"
)) {
  if (-not (Test-Path $root)) { continue }
  Get-ChildItem $root -Recurse -EA SilentlyContinue | ForEach-Object {
    try {
      $p = Get-ItemProperty $_.PSPath -EA SilentlyContinue
      foreach ($prop in $p.PSObject.Properties) {
        if ($prop.Name -match 'BatteryCare|Battery Care|ChargeThreshold|ChargeLimit|AdaptiveBattery|MaxCharge') {
          $regHits += "{0}\{1}={2}" -f $_.PSPath, $prop.Name, $prop.Value
          try {
            Set-ItemProperty -Path $_.PSPath -Name $prop.Name -Value 0 -EA Stop
            L "Registry cleared $($prop.Name) at $($_.PSPath)"
            $disabled = $true
          } catch {
            L "Registry write denied $($prop.Name): $($_.Exception.Message)"
          }
        }
      }
    } catch {}
  }
}
if (-not $regHits) { L "No HP Battery Care registry values found to clear" }
else { $regHits | ForEach-Object { L "HIT $_" } }

# --- Windows power: High Performance ---
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>$null
$dup = powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 2>&1 | Out-String
if ($dup -match '([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})') {
  powercfg /setactive $Matches[1] 2>$null
  L "Ultimate Performance activated $($Matches[1])"
}
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 100
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100
powercfg /setdcvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 100
powercfg /setdcvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100
powercfg /setacvalueindex SCHEME_CURRENT SUB_PCIEXPRESS ASPM 0
powercfg /setdcvalueindex SCHEME_CURRENT SUB_PCIEXPRESS ASPM 0
powercfg /setacvalueindex SCHEME_CURRENT SUB_ENERGYSAVER ESBATTTHRESHOLD 100
powercfg /setdcvalueindex SCHEME_CURRENT SUB_ENERGYSAVER ESBATTTHRESHOLD 100
powercfg /setactive SCHEME_CURRENT
L ("Active scheme: " + (powercfg /getactivescheme))

# Raise Blender HQ priority
Get-CimInstance Win32_Process -Filter "Name='blender.exe'" | Where-Object { $_.CommandLine -match '-b ' } | ForEach-Object {
  try {
    $proc = Get-Process -Id $_.ProcessId
    $proc.PriorityClass = "High"
    L "Blender $($_.ProcessId) Priority=High"
  } catch { L "Blender priority fail: $_" }
}

# Status
$bs = Get-CimInstance -Namespace root\wmi -ClassName BatteryStatus -EA SilentlyContinue
if ($bs) {
  L ("AC PowerOnline={0} Charging={1} Discharging={2}" -f $bs.PowerOnline, $bs.Charging, $bs.Discharging)
}
$bat = Get-CimInstance Win32_Battery -EA SilentlyContinue
if ($bat) { L ("BatteryStatus={0} Charge%={1}" -f $bat.BatteryStatus, $bat.EstimatedChargeRemaining) }
if (Get-Command nvidia-smi -EA SilentlyContinue) {
  L (nvidia-smi --query-gpu=pstate,power.draw,clocks.sm,utilization.gpu --format=csv,noheader)
}

if (-not $bs.PowerOnline) {
  L "ACTION REQUIRED: Plug in AC adapter. OS power boost cannot unlock full RTX clocks on battery."
}
if (-not $disabled) {
  L "Battery Care not exposed via Windows WMI/registry on this SKU. Use BIOS F10 if Battery Care Function exists; otherwise plug in."
}
L "=== done ==="
L "See docs/HP_BATTERY_CARE.md"
