# Run inside Blender with turbine.blend open (after finish_turbine.py), then run export_parts.py.
# For the close fly-through on computers:
# 1. Blades keep most of their width out to the tip (they tapered to under half, which read as spikes up close). Vertex count and order are untouched, so the rod shape still works.
# 2. textures/wear-wide.jpg: the same scanned steel plate as wear.jpg (Poly Haven metal_plate_02, CC0; roughness in red, height in green) at 1024 px instead of 256.
import bpy, numpy as np, os

TIP = 0.8  # tip width as a share of the root width
for me in {o.data for o in bpy.data.objects if o.name.startswith("blade")}:
    if me.get("tip"): continue  # already done
    v = me.vertices; rows = len(v) // 6; assert len(v) % 6 == 0
    wide = lambda r: max(v[r * 6 + i].co.x for i in range(6)) - min(v[r * 6 + i].co.x for i in range(6))
    was = wide(rows - 1) / wide(0)
    for r in range(rows):
        f = r / (rows - 1); k = (1 + (TIP - 1) * f) / (1 + (was - 1) * f)
        for i in range(6): c = v[r * 6 + i].co; c.x *= k; c.y *= k
    me["tip"] = TIP; me.update()

def grey(name):
    im = bpy.data.images[name]; n = im.size[0]; assert tuple(im.size) == (1024, 1024)
    a = np.empty(n * n * 4, np.float32); im.pixels.foreach_get(a); return a.reshape(n, n, 4)[..., 0]
def fit(a, mean, std): return np.clip((a - a.mean()) / a.std() * std + mean, mean - 0.7 * std, 1)  # same levels as wear.jpg, so the page's shader needs no retuning; the floor fills in the plate's seams, which read as brickwork on the blades at this sharpness
out = np.zeros((1024, 1024, 4), np.float32); out[..., 3] = 1
out[..., 0] = fit(grey("metal_plate_02_Rough"), 0.69, 0.135); out[..., 1] = fit(grey("metal_plate_02_Displacement"), 0.579, 0.108)
im = bpy.data.images.new("wear-wide", 1024, 1024); im.colorspace_settings.name = "Non-Color"; im.pixels.foreach_set(out.ravel())
im.filepath_raw = os.path.join(os.path.dirname(bpy.data.filepath), "..", "textures", "wear-wide.jpg"); im.file_format = "JPEG"; im.save(quality=80)
print("wrote", os.path.getsize(im.filepath_raw), "bytes"); bpy.data.images.remove(im)
