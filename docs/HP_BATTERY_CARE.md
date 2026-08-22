# Disable HP Battery Care / charge limit (Victus) + prefer plug-in performance

**Machine:** HP Victus-class (Battery Care is often BIOS-only or absent from Windows.)

## What we can do from Windows (done by script)

```powershell
powershell -ExecutionPolicy Bypass -File "scripts\disable_hp_battery_care_boost_power.ps1"
```

- Activates **High performance** / Ultimate Performance if available  
- Max CPU min/max states on AC **and** DC  
- Disables PCIe ASPM + USB selective suspend (less GPU idle throttle)  
- Raises HQ Blender process priority  
- Searches HP registry / WMI for Battery Care and sets to 100% when exposed  

## What you must do (hardware)

1. **Plug in the stock AC adapter** — OS still saw `PowerOnline=False` / discharging when last checked. Battery Care cannot fix a machine that is not on AC.
2. If still **“Plugged in, not charging”**:
   - Cool the chassis (Battery Care / SMART charge often pauses when hot)
   - Reseat barrel plug; avoid weak USB-C PD bricks
3. **BIOS Battery Care** (if present on your SKU):
   - Restart → mash **F10** → look under **System Configuration** / **Advanced Battery**  
   - **Battery Care Function** → **100%** (or Disabled)  
   - **Adaptive Battery Optimizer** → **Disabled**  
   - Save & Exit (F10)

Many Victus SKUs **do not expose** Battery Care in Windows or BIOS; then the only fix for GPU P4 / ~12 W throttle is **AC power + High performance**.

## Verify after plugging in

```powershell
nvidia-smi --query-gpu=pstate,power.draw,clocks.sm,utilization.gpu --format=csv
# Want: P0–P2, tens of watts, SM clocks >> 885 MHz
```
