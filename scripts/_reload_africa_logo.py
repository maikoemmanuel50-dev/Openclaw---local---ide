import bpy
NEW = r'C:\Users\HP\OneDrive\The Vault\Africa Season 1\assets\canva\s10_africa_logo.png'
updated = []
img = bpy.data.images.load(NEW, check_existing=True)
img.filepath = NEW
img.filepath_raw = NEW
img.reload()
for i in bpy.data.images:
    key = (i.name + ' ' + (i.filepath or '')).lower()
    if 'africa' in key and ('logo' in key or 's10' in key):
        i.filepath = NEW
        i.filepath_raw = NEW
        i.reload()
        updated.append(i.name)
sc = bpy.data.scenes.get('10_EndCard')
if sc:
    for o in sc.objects:
        if o.type == 'MESH' and 'Background' in o.name:
            for s in o.material_slots:
                m = s.material
                if not m or not m.use_nodes: continue
                for n in m.node_tree.nodes:
                    if n.type == 'TEX_IMAGE':
                        n.image = img
                        updated.append(f'{o.name}:{m.name}')
bpy.ops.wm.save_mainfile()
print('UPDATED', updated)
print('SIZE', list(img.size))
