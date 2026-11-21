# Run with:  Blender -b --python blender/film_from_video.py -- <clip> <name> [sets] [frames-d] [frames-p]
#   <clip>   a video file (for example film/src/wave.mp4)
#   <name>   the film's name: pictures go to film/<name>/d/0001.webp ... and film/<name>/p/0001.webp ...
#   [sets]   "dp" (default), "d" or "p"
#   [frames-d] [frames-p]   how many pictures to take, evenly spaced over the whole clip (default 120 and 80)
# Turns a video clip into the numbered pictures the page plays by scroll. There is no ffmpeg on this Mac, so Blender's own video editor reads the clip.
#   d: 1920 x 1080 for computers, the clip scaled to cover.   p: 720 x 1280 for phones, a crop from the middle of the clip: keep the subject centred when the clip is made.
import bpy, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
assert len(argv) >= 2, "usage: -- <clip> <name> [dp|d|p] [frames-d] [frames-p]"
clip, name = os.path.abspath(argv[0]), argv[1]
sets = argv[2] if len(argv) > 2 else "dp"
count = {"d": int(argv[3]) if len(argv) > 3 else 120, "p": int(argv[4]) if len(argv) > 4 else 80}
assert os.path.isfile(clip), "no such clip: " + clip

sc = bpy.context.scene
ed = sc.sequence_editor_create()
strip = ed.strips.new_movie("clip", clip, 1, 1)
length = strip.frame_final_duration; ow, oh = strip.elements[0].orig_width, strip.elements[0].orig_height
print(f"clip: {ow} x {oh}, {length} frames", flush=True)
assert length >= 2 and ow and oh, "could not read the clip"
r = sc.render; r.use_sequencer = True; r.resolution_percentage = 100
r.image_settings.file_format = "WEBP"; r.image_settings.color_mode = "RGB"
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"   # the clip's own colours, untouched
for s in sets:
    W, H = (1920, 1080) if s == "d" else (720, 1280)
    r.resolution_x, r.resolution_y = W, H; r.image_settings.quality = 72 if s == "d" else 68
    k = max(W / ow, H / oh); strip.transform.scale_x = strip.transform.scale_y = k; strip.transform.offset_x = strip.transform.offset_y = 0   # cover the picture, cropping from the middle
    out = os.path.join(ROOT, "film", name, s); os.makedirs(out, exist_ok=True); n = count[s]; total = 0
    for i in range(n):
        sc.frame_set(1 + round(i * (length - 1) / (n - 1))); r.filepath = os.path.join(out, f"{i + 1:04d}.webp"); bpy.ops.render.render(write_still=True); total += os.path.getsize(r.filepath)
    print(f"{name}/{s}: {n} pictures, {W} x {H}, {total / 1e6:.1f} MB", flush=True)
