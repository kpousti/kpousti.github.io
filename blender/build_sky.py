# Run inside Blender after importing the Poly Haven sky "the_sky_is_on_fire" (8k hdr, CC0, by Greg Zaal and Rico Cilliers).
# Writes the page backdrop: textures/sky.jpg (1600 x 800, phones) and textures/sky-wide.jpg (2880 x 1440, wide screens).
# The picture is a 130-degree stretch of the real sky above the open-sea horizon, looking at where the sun has just gone down.
# Everything under the horizon in the photo (rocks, a promenade) is thrown away: the page draws the sea itself, live (see "The backdrop" in index.html).
# For visitors without WebGL, with reduced motion or with scripts off, the sea in the file is one still frame of that same live water,
# captured from the page (shots/sea-still.png, see NOTES.md); until that capture exists a soft mirror of the sky stands in.
import bpy, numpy as np, os

HERE = os.path.dirname(bpy.data.filepath)
OUT = os.path.normpath(os.path.join(HERE, "..", "textures"))
STILL = os.path.normpath(os.path.join(HERE, "..", "shots", "sea-still.png"))
AZ, SUN, HORIZON = 130.0, 0.664, 0.66    # degrees across; where the glow sits in the panorama (0 to 1); how far down the picture the horizon is

img = next(i for i in bpy.data.images if "sky_is_on_fire" in i.name.lower())
W, H = img.size
a = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(a)
a = a.reshape(H, W, 4)[::-1, :, :3]                       # row 0 = top
lum = np.array([0.2126, 0.7152, 0.0722], np.float32)
# the horizon: the row where the open sea meets the sky (largest jump in brightness going down, right of the glow)
band = (a[int(0.47 * H):int(0.52 * H), int(0.70 * W):int(0.90 * W)] @ lum).mean(1)
hz = int(0.47 * H) + int(np.argmax(band[:-3] - band[3:])) + 1
cw = int(round(AZ / 360 * W)); ch = cw // 2
x0 = int(round(SUN * W - 0.68 * cw)); top = hz - int(round(HORIZON * ch))
sky = a[top:hz, x0:x0 + cw] * 0.3                         # exposure well down: the photo is bright twilight, the page wants the last of the light
L = sky @ lum
sky = sky / (1 + L[:, :, None]) * 1.5                      # Reinhard on brightness, so the colours keep their hue
L = (sky @ lum)[:, :, None]
sky = L + (sky - L) * 1.22                                 # richer colour: the oranges and magentas of the real sky, not pastel
sky = np.clip(sky, 0, None); m = sky.max(2, keepdims=True); sky = sky / np.maximum(1, m) ** 0.85   # anything too bright rolls off toward its own hue instead of clipping to flat yellow
g = np.linspace(0, 1, sky.shape[0], dtype=np.float32)[:, None, None]             # 0 at the top, 1 at the horizon
sky = sky * (0.42 + 0.58 * g ** 1.3) * (np.array([0.82, 0.9, 1.12], np.float32) * (1 - g) + g)   # deeper and cooler higher up: night coming down from the top
sky = np.clip(sky, 0, 1) ** (1 / 2.2)
sky = np.clip(sky * sky * (3 - 2 * sky) * 0.55 + sky * 0.45, 0, 1)               # a gentle S-curve for contrast

def resize(p, w, h):                                       # plain linear resampling, each way in turn
    def axis(q, n, ax):
        m = q.shape[ax]; f = (np.arange(n) + 0.5) * m / n - 0.5; i = np.clip(np.floor(f).astype(int), 0, m - 2); t = (f - i).astype(np.float32)
        lo, hi = np.take(q, i, ax), np.take(q, i + 1, ax); t = t.reshape([-1 if d == ax else 1 for d in range(q.ndim)])
        return lo * (1 - t) + hi * t
    if p.shape[1] > 1.6 * w:                               # shrinking a lot: average blocks first, so nothing shimmers
        k = p.shape[1] // w; p = p[:p.shape[0] // k * k, :p.shape[1] // k * k].reshape(p.shape[0] // k, k, p.shape[1] // k, k, 3).mean((1, 3))
    return axis(axis(p, h, 0), w, 1)

def load(path):
    im = bpy.data.images.load(path); im.colorspace_settings.name = "Non-Color"; w, h = im.size   # read the file's own values, not Blender's linear-light version of them
    b = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(b); bpy.data.images.remove(im)
    return b.reshape(h, w, 4)[::-1, :, :3]

sea_rows = ch - sky.shape[0]
if os.path.exists(STILL):
    sea = resize(load(STILL), cw, sea_rows); sea[0] = sea[1]   # the capture's first row is half transparent
    for _ in range(2):                                     # smeared sideways a little, like a long exposure: it is only the stand-in for the moving sea, and soft water makes a much smaller file
        c = np.cumsum(np.pad(sea, ((0, 0), (8, 8), (0, 0)), mode="edge"), 1, dtype=np.float64); sea = ((c[:, 16:] - c[:, :-16]) / 16).astype(np.float32)
else:                                                      # stand-in: the sky upside down, squashed and softened
    sea = sky[np.linspace(sky.shape[0] - 1, sky.shape[0] * 0.3, sea_rows).astype(int)].copy()
    for _ in range(3):
        c = np.cumsum(np.pad(sea, ((0, 0), (12, 12), (0, 0)), mode="edge"), 1); sea = (c[:, 24:] - c[:, :-24]) / 24
    sea *= np.linspace(0.8, 0.35, sea_rows, dtype=np.float32)[:, None, None]
full = np.clip(np.vstack([sky, sea]), 0, 1)

s = bpy.context.scene; keep = (s.view_settings.view_transform, s.render.image_settings.file_format, s.render.image_settings.quality)
s.view_settings.view_transform = "Standard"; s.render.image_settings.file_format = "JPEG"
for name, w, q in (("sky.jpg", 1600, 72), ("sky-wide.jpg", 2880, 80)):
    out = resize(full, w, w // 2); h = w // 2
    res = bpy.data.images.new("kp_sky_out", w, h, alpha=False)
    res.pixels.foreach_set(np.dstack([out[::-1], np.ones((h, w, 1), np.float32)]).ravel())
    s.render.image_settings.quality = q; res.save_render(os.path.join(OUT, name), scene=s); bpy.data.images.remove(res)
    print("wrote", name, w, h, os.path.getsize(os.path.join(OUT, name)) // 1024, "KB")
s.view_settings.view_transform, s.render.image_settings.file_format, s.render.image_settings.quality = keep
print("horizon row", hz, "of", H, "crop", x0, top, cw, ch, "still sea" if os.path.exists(STILL) else "stand-in sea")
