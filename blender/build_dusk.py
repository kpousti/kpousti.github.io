# Run inside Blender after importing the Poly Haven sky "umhlanga_sunrise" (4k hdr, CC0, by Greg Zaal).
# Writes textures/dusk.jpg, the page backdrop: the sky above the open-sea horizon, graded down to last light, with a still sea mirrored under it.
import bpy, numpy as np, os

OUT = os.path.join(os.path.dirname(bpy.data.filepath), "..", "textures", "dusk.jpg")
img = next(i for i in bpy.data.images if "umhlanga" in i.name.lower())
W, H = img.size
a = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(a)
a = a.reshape(H, W, 4)[::-1, :, :3]            # row 0 = top
x0, x1 = int(0.43 * W), int(0.935 * W)          # the stretch of horizon that is open sea, sun a little right of centre
top, hz = int(0.17 * H), int(0.497 * H)        # from well up in the sky down to the horizon line
sky = a[top:hz, x0:x1] * 0.5                   # exposure down: sunrise becomes last light
L = sky @ np.array([0.2126, 0.7152, 0.0722], np.float32)
sky = sky / (1 + L[:, :, None])                # Reinhard on brightness, so colours keep their hue
t = np.clip((L - 2.5) / 10, 0, 1)[:, :, None]  # the sun's disc itself: a warm white, not a clipped yellow
sky = np.clip(sky * (1 - t) + np.array([1.0, 0.84, 0.62], np.float32) * t, 0, 1) ** (1 / 2.2)
ink = np.array([14, 21, 30], np.float32) / 255  # the page colour
g = np.linspace(0, 1, sky.shape[0], dtype=np.float32)[:, None, None]   # 0 at the top, 1 at the horizon
sky = sky * (0.5 + 0.5 * g ** 1.5) * np.array([0.9, 0.95, 1.08], np.float32)   # darker and cooler higher up
k = 0.6 * (1 - g) ** 2; sky = sky * (1 - k) + ink * k                          # the top melts into the page colour

rows = np.linspace(sky.shape[0] - 1, 0, int(sky.shape[0] * 0.55)).astype(int)  # the sea: the sky upside down and squashed
sea = sky[rows].copy()
for _ in range(3):                             # three box blurs sideways and down make a soft, glassy reflection
    c = np.cumsum(np.pad(sea, ((0, 0), (9, 9), (0, 0)), mode="edge"), 1); sea = (c[:, 18:] - c[:, :-18]) / 18
    c = np.cumsum(np.pad(sea, ((3, 3), (0, 0), (0, 0)), mode="edge"), 0); sea = (c[6:] - c[:-6]) / 6
d = np.linspace(0, 1, sea.shape[0], dtype=np.float32)[:, None, None]
k = 0.78 * (1 - d) ** 1.5; sea = sea * k + ink * (1 - k)                       # the reflection dies away into the page colour

out = np.clip(np.vstack([sky, sea]), 0, 1)[::-1, ::-1]   # mirrored left to right, so the sun sits on the right, under the model
h, w, _ = out.shape
res = bpy.data.images.new("dusk", w, h, alpha=False)
res.pixels.foreach_set(np.dstack([out, np.ones((h, w, 1), np.float32)]).ravel())
s = bpy.context.scene; s.view_settings.view_transform = "Standard"; s.render.image_settings.file_format = "JPEG"; s.render.image_settings.quality = 74
res.save_render(os.path.normpath(OUT), scene=s)
print("wrote", os.path.normpath(OUT), w, h, "horizon at", round(sky.shape[0] / h, 3))
