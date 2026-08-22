"""
Configure Blender for RTX 4060 OptiX / CUDA production quality.
Run: blender -b blend/africa_s1_master_v01.blend -P setup_nvidia_gpu.py

Sets Cycles device to OPTIX (preferred) or CUDA, Eevee samples for preview quality.
"""
import bpy

def prefer_optix():
    prefs = bpy.context.preferences.addons["cycles"].preferences
    # Try OPTIX first (RTX), then CUDA
    for backend in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            enabled = 0
            for d in prefs.devices:
                # Enable NVIDIA only; disable CPU for pure GPU renders if desired
                is_nvidia = "NVIDIA" in d.name.upper() or "GEFORCE" in d.name.upper() or "RTX" in d.name.upper()
                if d.type in ("OPTIX", "CUDA") and is_nvidia:
                    d.use = True
                    enabled += 1
                    print(f"  ENABLE {backend}: {d.name}")
                elif d.type == "CPU":
                    d.use = True  # keep CPU as fallback for hybrid
                    print(f"  CPU fallback: {d.name}")
                else:
                    d.use = False
            if enabled:
                return backend
        except Exception as e:
            print(f"  {backend} failed: {e}")
    return None


def configure_scenes():
    backend = prefer_optix()
    for sc in bpy.data.scenes:
        # Prefer Eevee Next for motion-graphics speed (already used in pipeline)
        # When Cycles is needed (chart DOF / glass), use GPU
        sc.cycles.device = "GPU"
        if hasattr(sc.cycles, "use_denoising"):
            sc.cycles.use_denoising = True
        if hasattr(sc.cycles, "denoiser"):
            try:
                sc.cycles.denoiser = "OPTIX"
            except Exception:
                pass
        # Eevee quality for final looks
        if hasattr(sc.eevee, "taa_render_samples"):
            sc.eevee.taa_render_samples = max(sc.eevee.taa_render_samples, 64)
        print(f"  Scene {sc.name}: cycles.device=GPU, eevee samples ok")
    return backend


def main():
    print("=== NVIDIA GPU Blender Setup (RTX 4060) ===")
    backend = configure_scenes()
    blend = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print(f"Backend: {backend or 'NONE'}")
    print(f"Saved: {blend}")
    print("=== DONE ===")


if __name__ == "__main__":
    main()
