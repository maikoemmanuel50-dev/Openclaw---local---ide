import bpy
sc = bpy.data.scenes['10_EndCard']
bpy.context.window.scene = sc
sc.render.filepath = r'C:\Users\HP\OneDrive\The Vault\Africa Season 1\renders\softpop_heroes\10_EndCard_logo_v2'
sc.render.image_settings.file_format = 'PNG'
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.frame_set((sc.frame_start + sc.frame_end)//2)
# Faster verify samples
if hasattr(sc.eevee, 'taa_render_samples'):
    sc.eevee.taa_render_samples = 32
bpy.ops.render.render(write_still=True)
print('WROTE', sc.render.filepath)
