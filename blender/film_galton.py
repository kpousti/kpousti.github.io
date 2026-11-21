# Run with:  Blender -b blender/galton.blend --python blender/film_galton.py -- <set> [frames] [samples] [shot]
#   <set>     d (computers: 1920 x 1080, 120 frames) or p (phones: 720 x 1280, 80 frames). Smaller pictures looked soft on high-resolution screens.
#   [frames]  "all" (default) or a list such as 1,40,75 for a few test frames
#   [samples] Cycles samples per pixel (default 64)
#   [shot]    "open" (default): the opening film, described below, to film/<set>/.  "balls": the closing film, to film/balls/<set>/ (see SHOTS further down)
# Renders the opening film: one continuous camera move over the Galton board, as numbered pictures the page plays by scroll (film/<set>/0001.webp ...).
# The pictures have no background (the page's own sky shows through), so the board sits in the page exactly as the live one does.
#
# The shot, by share of the film:
#   0.00  the whole board from the front, a little from the left and above: the same view the live board has as the film takes over
#   0.16  in close on the hopper's throat as the first balls come out
#   0.30 to 0.48  down the pegs with the balls, very close, in slow motion: each ball makes one random left-or-right bounce per row
#   0.58  low along the bins, time running fast, as the pile fills into the bell curve
#   0.62 to 0.90  pulling back and up the other side while the tree is priced: each row of pegs and paths lights gold, from the bins up to the first peg
#   1.00  the whole board from the front again, where the live board takes back over
# The balls follow the page's own rule (index.html, "The Galton board's balls"): the same peg spacing, timing and stacking, with their own seeded random stream.
import bpy, math, os, random, sys
from mathutils import Vector

ROOT = "/Users/kiapousti/Documents/kpousti.github.io"
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SET = argv[0] if argv else "d"
ONLY = None if len(argv) < 2 or argv[1] == "all" else [int(x) for x in argv[1].split(",")]
SAMPLES = int(argv[2]) if len(argv) > 2 else 64
SHOT = argv[3] if len(argv) > 3 else "open"
PERCENT = int(argv[4]) if len(argv) > 4 else 100   # a fifth argument below 100 makes a quick small draft on the processor, in film/draft-<shot>-<set>/
N = 120 if SET == "d" else 80
W, H = (1920, 1080) if SET == "d" else (720, 1280)
sc = bpy.context.scene

# ---------- the balls: the page's constants and rule ----------
GN, GDX, GDY, GY0, GRB, GFLOOR, GTOP, GTHROAT = 13, 0.094, 0.082, 0.52, 0.0095, -0.93, -0.55, 0.6
GNB, GREL, GROW, GDROP = 320, 55.0, 95.0, 460.0
if SHOT == "balls": GREL = 28.0   # the closing film lets the balls go twice as often, nearly touching: seen this close, the page's own pace looks sparse
GFALL = (GN + 1) * GROW + GDROP
rnd = random.Random(1009)
slots = []
j = 0
while len(slots) < GNB:   # where the waiting balls sit in the hopper, lowest first
    y = GTHROAT + 0.03 + j * GRB * 1.74; w = 0.02 + (y - GTHROAT) / 0.7 - GRB * 1.2; m = math.ceil(w / (GRB * 2.04))
    for c in range(-m, m + 1):
        x = c * GRB * 2.04 + (GRB * 1.02 if j % 2 else 0)
        if abs(x) <= w: slots.append((x, y))
    j += 1
bits, bins, slot, cnt = [], [], [], {}
for i in range(GNB):
    b = [rnd.random() < 0.5 for _ in range(GN)]; k = sum(b); bits.append(b); bins.append(k); slot.append(cnt.get(k, 0)); cnt[k] = cnt.get(k, 0) + 1
def smooth(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def mix(a, b, t): return a + (b - a) * t
def way(i, m): x = sum(0.5 if bits[i][q] else -0.5 for q in range(m)); return (x * GDX, GTOP if m == GN else GY0 - m * GDY + 0.021)
def rest(i):
    k = bins[i]; pr = slot[i] % 7; L = 2 * (slot[i] // 7) + (1 if pr >= 4 else 0)
    return ((k - GN / 2) * GDX + ((pr - 5) if pr >= 4 else (pr - 1.5)) * GRB * 2.06, GFLOOR + GRB + L * GRB * 1.74)
def ball(i, tau):   # where ball i is, tau ms after its release: (across, up)
    s = slots[GNB - 1 - i]
    if tau < -300: return s
    if tau < 0: f0 = smooth(1 + tau / 300); return (mix(s[0], 0, f0), mix(s[1], GTHROAT, f0))
    seg = tau / GROW; m = int(seg); f = seg - m
    if m == 0: return (0, mix(GTHROAT, GY0 + 0.021, f * f))
    if m <= GN: a = way(i, m - 1); b = way(i, m); return (mix(a[0], b[0], f), mix(a[1], b[1], f * f) + 0.016 * math.sin(math.pi * f))
    f3 = max(0.0, min(1.0, (tau - (GN + 1) * GROW) / GDROP)); a = way(i, GN); b = rest(i); return (mix(a[0], b[0], f3), mix(a[1], b[1], f3 * f3))
def clock(p):   # the run's clock (ms) at share p of the film: slow motion down the pegs, then fast while the bins fill
    if SHOT == "balls":   # the closing film starts mid-run, with a steady stream already coming down: very slow at the top, quicker on the way down, fast while the pile fills to the finished bell curve
        return mix(2000.0, 3800.0, p / 0.3) if p < 0.3 else mix(3800.0, 6600.0, (p - 0.3) / 0.4) if p < 0.7 else mix(6600.0, GNB * GREL + GFALL, smooth((p - 0.7) / 0.27))
    if p < 0.08: return -350.0
    if p < 0.48: return -350.0 + (p - 0.08) / 0.40 * 3700.0
    return 3350.0 + smooth((p - 0.48) / 0.14) * (GNB * GREL + GFALL - 3350.0)

steel = bpy.data.materials.new("ball"); steel.use_nodes = True
bs = next(n for n in steel.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); bs.inputs["Base Color"].default_value = (0.8, 0.83, 0.87, 1); bs.inputs["Metallic"].default_value = 1; bs.inputs["Roughness"].default_value = 0.12
bpy.ops.mesh.primitive_uv_sphere_add(segments=64 if SHOT == "balls" else 24, ring_count=32 if SHOT == "balls" else 12, radius=GRB); proto = bpy.context.object; bpy.ops.object.shade_smooth(); proto.data.materials.append(steel)   # the closing film is close enough to see a ball's outline, so its balls are rounder
balls = [proto]
for i in range(1, GNB): o = proto.copy(); sc.collection.objects.link(o); balls.append(o)

# ---------- for film: no glass pane (close in, its reflections lay a haze over everything), and one brass per row so a row can light on its own ----------
for o in bpy.data.objects:
    if o.name.startswith("case.glass"): o.hide_render = True
GOLD = (1.0, 0.62, 0.16, 1)
rowmat = {}
def row_material(src, r):
    key = (src.name, r)
    if key not in rowmat:
        m = src.copy(); m.name = f"{src.name}.row{r}"; b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Emission Color" if "Emission Color" in b.inputs else "Emission"].default_value = GOLD; rowmat[key] = (m, b)
    return rowmat[key][0]
for o in list(bpy.data.objects):
    nm = o.name.split(".")
    if o.type == "MESH" and len(nm) >= 3 and (o.name.startswith("can.peg.") or o.name.startswith("blade.edge.")):
        r = int(nm[2]); o.data = o.data.copy(); o.data.materials[0] = row_material(o.data.materials[0], r)

# ---------- light: a studio sky for the reflections, a warm key and a cool rim for the glints; no background ----------
world = bpy.data.worlds.new("film"); sc.world = world; world.use_nodes = True; nt = world.node_tree
env = nt.nodes.new("ShaderNodeTexEnvironment")
hdr = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.join(os.path.dirname(bpy.app.binary_path), "..", "Resources")) for f in fn if f == "sunset.exr"]
env.image = bpy.data.images.load(hdr[0]); bg = next(n for n in nt.nodes if n.type == "BACKGROUND"); nt.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.55
mp = nt.nodes.new("ShaderNodeMapping"); tc = nt.nodes.new("ShaderNodeTexCoord"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(200)); nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])   # the low sun behind and to the left: warm edges, like the page's own dusk
def lamp(name, loc, energy, color, size):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.color = color; d.size = size; o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0.1)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o
lamp("key", (-2.2, -3.0, 2.4), 300, (1.0, 0.84, 0.64), 2.0); lamp("rim", (2.6, -1.0, 1.6), 220, (0.6, 0.76, 1.0), 1.5); lamp("low", (0.4, -2.0, -1.6), 60, (1.0, 0.66, 0.4), 2.5)

# ---------- the camera: where it is and what it looks at, at shares of the film ----------
cam_d = bpy.data.cameras.new("film"); cam = bpy.data.objects.new("film", cam_d); sc.collection.objects.link(cam); sc.camera = cam
aim = bpy.data.objects.new("aim", None); sc.collection.objects.link(aim)
tr = cam.constraints.new("TRACK_TO"); tr.target = aim; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
cam_d.sensor_fit = "VERTICAL" if SET == "p" else "AUTO"; cam_d.dof.use_dof = True; cam_d.dof.focus_object = aim; cam_d.clip_start = 0.01
WIDE = (-2.37, -7.75, 0.92) if SET == "d" else (-2.25, -7.35, 0.9)   # 17 degrees to the left and a little above, and far enough that the board is about 0.7 of the picture's height: as the live board is seen when the film takes over
AIM0 = (0.0, 0.0, 0.12)
SHOTS = [  # share, camera, aim, lens (mm), f-stop
    (0.00, WIDE, AIM0, 50, 5.6),
    (0.16, (-0.16, -0.62, 0.80), (0.0, -0.03, 0.60), 50, 2.0),
    (0.30, (0.20, -0.44, 0.34), (0.02, -0.03, 0.22), 55, 1.6),
    (0.48, (-0.17, -0.42, -0.22), (0.0, -0.03, -0.34), 55, 1.6),
    (0.58, (0.34, -0.60, -0.80), (-0.06, -0.03, -0.76), 50, 2.0),
    (0.76, (1.15, -2.6, 0.25), (0.0, 0.0, 0.0), 50, 3.2),
    (1.00, WIDE, AIM0, 50, 5.6)]
if SHOT == "balls":   # the closing film: steel balls through brass pegs, as close as a macro lens gets. In at the first pegs, down through the rows with the stream, ending on the finished pile in the middle bins
    SHOTS = [
        (0.00, (0.16, -0.42, 0.56), (0.0, -0.03, 0.44), 60, 2.8),
        (0.30, (-0.14, -0.38, 0.26), (0.02, -0.03, 0.15), 58, 2.8),
        (0.52, (0.16, -0.38, -0.12), (-0.01, -0.03, -0.24), 58, 2.8),
        (0.72, (-0.14, -0.38, -0.56), (0.0, -0.03, -0.64), 62, 2.8),
        (1.00, (0.06, -0.27, -0.79), (-0.01, -0.03, -0.845), 80, 4.0)]
    if SET == "p": SHOTS = [(p_, c, a, lens * 0.62, fs) for (p_, c, a, lens, fs) in SHOTS]   # phones: a tall picture sees a narrower strip, so a wider lens keeps several balls in view
def frame_of(p): return 1 + p * (N - 1)
for (p, c, a, lens, fs) in SHOTS:
    f = frame_of(p); cam.location = c; aim.location = a; cam_d.lens = lens; cam_d.dof.aperture_fstop = fs
    cam.keyframe_insert("location", frame=f); aim.keyframe_insert("location", frame=f); cam_d.keyframe_insert("lens", frame=f); cam_d.dof.keyframe_insert("aperture_fstop", frame=f)

# ---------- every frame: put the balls where the run has them, and light the rows the pricing has reached ----------
def pose(scene, *a):
    p = (scene.frame_current - 1) / (N - 1); T = clock(p)
    for i, o in enumerate(balls): x, y = ball(i, T - i * GREL); o.location = (x, -0.03, y)
    q = 0 if SHOT == "balls" else smooth((p - 0.62) / 0.26); out = 1 - smooth((p - 0.9) / 0.08)   # the pricing goes back up from the bins, a row at a time, to the one number at the top (the opening film only)
    for (name, r), (m, b) in rowmat.items():
        lit = smooth((q * (GN + 1.5) - (GN - 1 - r)) / 1.5) * out
        b.inputs["Emission Strength"].default_value = 2.4 * lit
bpy.app.handlers.frame_change_pre.append(pose)

# ---------- render ----------
sc.frame_start, sc.frame_end = 1, N
r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y, r.resolution_percentage = W, H, PERCENT; r.film_transparent = True
r.image_settings.file_format = "WEBP"; r.image_settings.color_mode = "RGBA"; r.image_settings.quality = 72 if SET == "d" else 68
cy = sc.cycles; cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.03; cy.use_denoising = True; cy.max_bounces = 6; cy.glossy_bounces = 4; cy.transmission_bounces = 6; cy.caustics_reflective = False; cy.caustics_refractive = False
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()
    for d in prefs.devices: d.use = True
    cy.device = "GPU" if PERCENT == 100 else "CPU"
except Exception as e: print("no GPU:", e)
try: sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - High Contrast"; sc.view_settings.exposure = -0.25
except Exception as e: print("view:", e)
out = os.path.join(ROOT, "film", SET) if SHOT == "open" else os.path.join(ROOT, "film", SHOT, SET)
if PERCENT < 100: out = os.path.join(ROOT, "film", f"draft-{SHOT}-{SET}")
os.makedirs(out, exist_ok=True)
import time
for f in (ONLY or range(1, N + 1)):
    t0 = time.time(); sc.frame_set(f); r.filepath = os.path.join(out, f"{f:04d}.webp"); bpy.ops.render.render(write_still=True)
    print(f"frame {f}/{N}: {time.time() - t0:.1f}s, {os.path.getsize(r.filepath) // 1024} KB", flush=True)
