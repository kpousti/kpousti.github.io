# Run with:  Blender -b --python blender/film_flatten.py -- <name> <set> [quality]
#   <name> <set>   the film and set to treat, for example  turbine d   (film/turbine/d)
#   [quality]      WebP quality of the finished pictures (default 64 for d, 62 for p)
# Lays a section film's see-through pictures over a dark studio backdrop and saves them again as plain pictures.
# Why: a see-through picture has to store exactly how clear every soft, out-of-focus edge is, and that alone was half of each file (170 KB against 80 KB for one armillary frame).
# The untouched renders are kept in film/src/<name>-<set>/ (not in git), so the backdrop or the quality can be changed later without rendering again; running this twice is safe.
import bpy, os, sys, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index("--") + 1:]
name, SET = argv[0], argv[1]; quality = int(argv[2]) if len(argv) > 2 else (64 if SET == "d" else 62)
live = os.path.join(ROOT, "film", name, SET); keep = os.path.join(ROOT, "film", "src", f"{name}-{SET}"); os.makedirs(keep, exist_ok=True)
bg = None; total = 0; n = 0
for f in sorted(x for x in os.listdir(live) if x.endswith(".webp")):
    src = os.path.join(keep, f)
    if not os.path.exists(src): os.replace(os.path.join(live, f), src)   # first time: the render moves to film/src
    img = bpy.data.images.load(src); w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    if bg is None:   # the backdrop: the page's dark blue, a little lighter behind the middle, a trace of dusk low down. Rows run from the bottom up
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); yy = yy / (h - 1) * 2 - 1; xx = (xx / (w - 1) * 2 - 1) * (w / h if w > h else 1.0); glow = np.exp(-(xx * xx * 0.55 + yy * yy) * 1.5)[:, :, None]; low = np.clip(-yy, 0, 1)[:, :, None] ** 2
        bg = np.array([0.028, 0.034, 0.054], np.float32) + np.array([0.04, 0.052, 0.078], np.float32) * glow + np.array([0.034, 0.014, 0.004], np.float32) * low
    a = px[:, :, 3:4]; px[:, :, :3] = px[:, :, :3] * a + bg * (1 - a); px[:, :, 3] = 1   # the same sum a browser does when it lays a see-through picture over a page
    out = bpy.data.images.new("flat", w, h, alpha=False); out.pixels.foreach_set(px.ravel()); out.file_format = "WEBP"; dst = os.path.join(live, f); out.save(filepath=dst, quality=quality)
    total += os.path.getsize(dst); n += 1; bpy.data.images.remove(img); bpy.data.images.remove(out)
print(f"{name}/{SET}: {n} pictures at quality {quality}, {total / 1e6:.2f} MB, {total // max(n, 1) // 1024} KB each on average", flush=True)
