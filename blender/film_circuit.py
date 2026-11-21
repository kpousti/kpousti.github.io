# Run with:  Blender -b --python blender/film_circuit.py -- <set> [frames] [samples] [percent]     (arguments: see filmkit.py)
# The film that opens Projects: a circuit board seen as a city at night. Chips are the blocks, capacitors the towers, and the copper traces are streets:
# pulses of light run along them the way traffic does. The whole board is built here from a seeded random layout; there is no .blend file.
#
# The shot, by share of the film:
#   0.00  the whole board from above and to one side, floating in the page's sky
#   0.30  coming down toward it
#   0.60  low between the parts, along a clear street
#   1.00  very close on the edge of the main chip, the pulses arriving at its pins
import bpy, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filmkit import *

sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
rnd = random.Random(163)

# ---------- materials ----------
mask = metal("mask", (0.008, 0.02, 0.04), 0.42, 0.08, 30); bsdf(mask).inputs["Metallic"].default_value = 0.0   # the board's dark coating
epoxy = metal("epoxy", (0.016, 0.017, 0.02), 0.42, 0.06, 300); bsdf(epoxy).inputs["Metallic"].default_value = 0.0
tin = metal("tin", (0.78, 0.8, 0.82), 0.22, 0.06, 200); lid = metal("lid", (0.42, 0.44, 0.48), 0.38, 0.1, 160); gold = metal("gold", (0.9, 0.66, 0.26), 0.2, 0.05, 100)
alu = metal("alu", (0.8, 0.82, 0.85), 0.34, 0.08, 120); sleeve = metal("sleeve", (0.02, 0.03, 0.06), 0.3, 0.05, 40); bsdf(sleeve).inputs["Metallic"].default_value = 0.2
tan = metal("tan", (0.42, 0.3, 0.17), 0.45); bsdf(tan).inputs["Metallic"].default_value = 0.0
ferrite = metal("ferrite", (0.05, 0.05, 0.055), 0.6); bsdf(ferrite).inputs["Metallic"].default_value = 0.0
led_a = glow("led.amber", (1.0, 0.55, 0.15), 14); led_b = glow("led.blue", (0.38, 0.6, 1.0), 12)
trace, clockv = pulse_metal()   # the traces: gold, with pulses of light running along them

# ---------- parts ----------
taken = []   # (x, y, radius) of every part, so nothing overlaps
def free(x, y, r, pad=0.02): return abs(x) + r < 1.52 and abs(y) + r < 1.52 and all(math.hypot(x - a, y - b) > r + c + pad for a, b, c in taken)
def chip(x, y, w, l, h, n, rot=0.0, four=True):
    box(epoxy, x, y, 0.004, w, l, h, rot); pins(tin, x, y, w, l, n, rot, (0, 1, 2, 3) if four else (0, 2)); taken.append((x, y, math.hypot(w, l) / 2 + 0.02))
def mlcc(x, y, rot=0.0, body=tan, k=1.0, z=0.001): chip2(body, tin, x, y, rot, k, z)
def tower(x, y, r, h):   # an electrolytic capacitor: the skyline
    box(epoxy, x, y, 0.001, 2 * r + 0.02, 2 * r + 0.02, 0.012); cyl(sleeve, x, y, 0.013, r, h * 0.93); cyl(alu, x, y, 0.013 + h * 0.93, r * 0.94, h * 0.07); taken.append((x, y, r + 0.03))
def coil(x, y, s_): box(ferrite, x, y, 0.001, s_, s_, s_ * 0.55); cyl(tan, x, y, 0.001 + s_ * 0.55, s_ * 0.36, 0.004); taken.append((x, y, s_ * 0.75))
def header(x, y, n, rot):
    c, s = math.cos(rot), math.sin(rot); box(epoxy, x, y, 0.001, n * 0.05, 0.05, 0.026, rot)
    for i in range(n): t = (i - (n - 1) / 2) * 0.05; box(gold, x + t * c, y + t * s, 0.001, 0.012, 0.012, 0.12, rot)
    taken.append((x, y, n * 0.025 + 0.03))

HERO = (0.55, 0.35)   # the main chip: a board of its own with a metal lid and a ring of small capacitors
box(mask, *HERO, 0.003, 0.62, 0.62, 0.016); box(lid, *HERO, 0.019, 0.5, 0.5, 0.024); box(lid, *HERO, 0.043, 0.38, 0.38, 0.008); taken.append((*HERO, 0.5))
box(gold, HERO[0] - 0.285, HERO[1] - 0.285, 0.019, 0.022, 0.022, 0.0012, math.pi / 4)   # the corner mark that shows which way round the chip goes
for side in range(4):
    for i in range(9):
        t = (i - 4) * 0.062; e = 0.282; lx, ly = ((t, -e), (e, t), (t, e), (-e, t))[side]; mlcc(HERO[0] + lx, HERO[1] + ly, 0 if side % 2 == 0 else math.pi / 2, tan, 0.8, 0.019)
# a clear street for the camera: from the near corner in to the main chip. Only low parts may stand in it
def street(x, y):
    ax, ay, bx, by = -1.5, -1.75, HERO[0] - 0.3, HERO[1] - 0.3; t = max(0, min(1, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
    return math.hypot(x - ax - t * (bx - ax), y - ay - t * (by - ay))
def place(n, r, make, tall=True, tries=4000):
    done = 0
    for _ in range(tries):
        if done >= n: break
        x, y = rnd.uniform(-1.45, 1.45), rnd.uniform(-1.45, 1.45)
        if free(x, y, r) and (not tall or street(x, y) > r + 0.2): make(x, y); done += 1
for (x, y, n) in ((-1.1, 1.42, 12), (1.42, -0.6, 10)): header(x, y, n, 0 if abs(y) > abs(x) else math.pi / 2)
place(7, 0.21, lambda x, y: chip(x, y, 0.3, 0.3, 0.034, 12, rnd.choice((0, math.pi / 2))))
place(9, 0.11, lambda x, y: tower(x, y, rnd.uniform(0.05, 0.075), rnd.uniform(0.13, 0.24)))
place(12, 0.14, lambda x, y: chip(x, y, 0.2, 0.11, 0.03, 7, rnd.choice((0, math.pi / 2)), False))
place(8, 0.09, lambda x, y: coil(x, y, rnd.uniform(0.09, 0.13)))
def row(x, y):   # a short row of small capacitors or resistors
    rot = rnd.choice((0, math.pi / 2)); n = rnd.randint(2, 6); body = rnd.choice((tan, tan, epoxy)); c, s = math.cos(rot + math.pi / 2), math.sin(rot + math.pi / 2)
    for i in range(n): mlcc(x + (i - (n - 1) / 2) * 0.03 * c, y + (i - (n - 1) / 2) * 0.03 * s, rot, body)
    taken.append((x, y, n * 0.016 + 0.02))
place(70, 0.1, row, tall=False)
def lamp_(x, y): box(rnd.choice((led_a, led_a, led_b)), x, y, 0.001, 0.02, 0.012, 0.008, rnd.choice((0, math.pi / 2))); taken.append((x, y, 0.02))
place(26, 0.03, lamp_, tall=False)

# ---------- traces: buses of parallel lanes with 45 degree bends, each lane ending in a via ----------
nbus = 0
for _ in range(400):
    if nbus >= 46: break
    x, y = rnd.uniform(-1.4, 1.4), rnd.uniform(-1.4, 1.4); ang = rnd.randrange(8) * math.pi / 4; pts = [(x, y)]
    for _s in range(rnd.randint(2, 5)):
        L = rnd.uniform(0.18, 0.8); x, y = x + L * math.cos(ang), y + L * math.sin(ang); pts.append((x, y)); ang += rnd.choice((-1, 1)) * math.pi / 4
    lanes = rnd.randint(2, 7); pitch = 0.014
    if any(abs(px) > 1.5 - lanes * pitch or abs(py) > 1.5 - lanes * pitch for px, py in pts): continue
    hue = 1.0 if rnd.random() < 0.22 else 0.0; nbus += 1
    for e in bus(trace, pts, lanes, pitch, 0.0012 + (nbus - 1) * 0.00004, hue, rnd): cyl(gold, e[0], e[1], 0.0005, 0.0085, 0.0026, 16); cyl(mask, e[0], e[1], 0.0005, 0.0036, 0.003, 12)
box(mask, 0, 0, -0.034, 3.12, 3.12, 0.034)   # the board itself
box(tan, 0, 0, -0.03, 3.124, 3.124, 0.026)     # its bare edge, showing just outside the coating

build(sc, smooth=("sleeve", "alu", "tan", "gold"), sharp=("trace", "mask"))   # cylinders are smooth; boxes keep flat faces with rounded edges; the board and its traces stay sharp

def pose(scene, *a): clockv.default_value = share(scene) * 2.6   # the pulses move as the film does: scrolling drives the traffic
bpy.app.handlers.frame_change_pre.append(pose)

# ---------- light and camera ----------
studio(sc, 0.14, 200)   # night: the sky is dim, and the board is lit mostly by its own traces
lamp(sc, "key", (-3.0, -2.2, 1.6), 110, (1.0, 0.8, 0.6), 2.0); lamp(sc, "rim", (2.6, 2.8, 1.4), 150, (0.55, 0.72, 1.0), 1.8)
far = 1.0 if SET == "d" else 2.1   # phones: farther back, so the board clears both sides of a tall picture
hx, hy = HERO
camera(sc, [  # share, camera, aim, lens (mm), f-stop
    (0.00, (-2.5 * far, -3.5 * far, 2.7 * far), (0.0, 0.0, 0.0), 50, 5.6),
    (0.30, (-1.75, -2.1, 0.95), (0.0, -0.1, 0.0), 50, 3.2),
    (0.60, (-0.95, -1.15, 0.26), (0.12, 0.0, 0.02), 45, 2.4),
    (0.85, (-0.3, -0.42, 0.15), (hx - 0.22, hy - 0.22, 0.03), 55, 2.4),
    (1.00, (hx - 0.6, hy - 0.58, 0.17), (hx - 0.27, hy - 0.25, 0.02), 60, 4.0)])
render(sc, "circuit", exposure=-0.1)
