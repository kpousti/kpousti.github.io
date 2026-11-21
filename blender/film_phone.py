# Run with:  Blender -b --python blender/film_phone.py -- <set> [frames] [samples] [percent]     (arguments: see filmkit.py)
# The film that opens Side builds (the app mock-ups): a phone comes apart into its layers. A generic slab of a phone with no maker's marks, built here; there is no .blend file.
# Front to back: glass, the lit display (the page's own dusk colours, no words on it), the metal frame, the cameras, the logic board, the battery, the back.
#
# The shot, by share of the film:
#   0.00  the phone whole, upright, seen from the front
#   0.08 to 0.50  it opens: the layers drift apart along the line of sight while the camera comes round to the side
#   0.75  beside the stack, level with the gap in front of the logic board
#   1.00  very close on the main chip, pulses running into it along the board's traces
import bpy, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filmkit import *
from mathutils import Vector

sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
rnd = random.Random(7)
PW, PH, PR = 0.72, 1.5, 0.11   # the phone: wide, tall, corner radius

# ---------- materials ----------
ti = metal("ti", (0.56, 0.56, 0.58), 0.3, 0.08, 300); plate = metal("plate", (0.16, 0.17, 0.19), 0.4, 0.08, 200); tin = metal("tin", (0.78, 0.8, 0.82), 0.22, 0.06, 200)
gold = metal("gold", (0.9, 0.66, 0.26), 0.2, 0.05, 100); lidm = metal("lid", (0.42, 0.44, 0.48), 0.38, 0.1, 160); steel = metal("steel", (0.8, 0.83, 0.87), 0.12)
def plain(name, color, rough, grain=0.0, scale=40): m = metal(name, color, rough, grain, scale); bsdf(m).inputs["Metallic"].default_value = 0.0; return m
mask = plain("mask", (0.008, 0.02, 0.04), 0.42, 0.08, 30); epoxy = plain("epoxy", (0.016, 0.017, 0.02), 0.42, 0.06, 300); tan = plain("tan", (0.42, 0.3, 0.17), 0.45)
pouch = plain("pouch", (0.02, 0.02, 0.024), 0.5, 0.1, 14); back = plain("back", (0.016, 0.026, 0.05), 0.3, 0.05, 20); ink = plain("ink", (0.004, 0.004, 0.005), 0.2)
lens = metal("lens", (0.05, 0.06, 0.16), 0.03)   # coated glass over the cameras: dark, with a blue sheen
glass = bpy.data.materials.new("glass"); glass.use_nodes = True; gb = bsdf(glass); gb.inputs["Roughness"].default_value = 0.0; gb.inputs["IOR"].default_value = 1.5
gb.inputs["Transmission Weight" if "Transmission Weight" in gb.inputs else "Transmission"].default_value = 1.0; gb.inputs["Base Color"].default_value = (0.9, 0.93, 1.0, 1)
# the display: lit, showing the page's dusk sky from top to bottom. No words, no icons
screen = bpy.data.materials.new("screen"); screen.use_nodes = True; nt = screen.node_tree; sb = bsdf(screen); sb.inputs["Base Color"].default_value = (0, 0, 0, 1); sb.inputs["Roughness"].default_value = 0.15
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); ramp = nt.nodes.new("ShaderNodeValToRGB"); mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value = -PH / 2; mr.inputs["From Max"].default_value = PH / 2
nt.links.new(tc.outputs["Object"], sep.inputs["Vector"]); nt.links.new(sep.outputs["Y"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
els = ramp.color_ramp.elements; els[0].position = 0.0; els[0].color = (0.9, 0.36, 0.08, 1); els[1].position = 1.0; els[1].color = (0.02, 0.04, 0.12, 1)
for pos, col in ((0.22, (0.75, 0.2, 0.16, 1)), (0.5, (0.22, 0.1, 0.3, 1)), (0.78, (0.05, 0.08, 0.24, 1))): e = els.new(pos); e.color = col
nt.links.new(ramp.outputs["Color"], sb.inputs["Emission Color" if "Emission Color" in sb.inputs else "Emission"]); sb.inputs["Emission Strength"].default_value = 2.2
trace, clockv = pulse_metal(); led = glow("led", (1.0, 0.55, 0.15), 10)
flex = plain("flex", (0.75, 0.33, 0.06), 0.35); copper = metal("copper", (0.9, 0.45, 0.25), 0.25, 0.06, 80)
def ring(r, n=96): return [(r * math.cos(math.tau * i / n), r * math.sin(math.tau * i / n)) for i in range(n)]

# ---------- the layers. Each is built flat (thickness along Z, front toward +Z) under its own handle, and has a place along Z when the phone is open ----------
root = bpy.data.objects.new("phone", None); sc.collection.objects.link(root); root.rotation_euler = (math.radians(90), 0, 0)   # upright, its front toward the camera
layers = []
def layer(name, z_shut, z_open, smooth=(), sharp=(), edge=0.0012):
    h = bpy.data.objects.new(name, None); sc.collection.objects.link(h); h.parent = root; h.location = (0, 0, z_shut)
    build(sc, smooth=smooth, sharp=sharp, parent=h, edge=edge); layers.append((h, z_shut, z_open)); return h
outer = rrect(PW, PH, PR)
slab(glass, outer, 0, 0.006); slab(ink, outer, -0.0012, 0.001, rrect(PW - 0.05, PH - 0.05, PR - 0.025)); layer("glass", 0.036, 0.72, sharp=("glass", "ink"))
slab(screen, rrect(PW - 0.04, PH - 0.04, PR - 0.02), 0, 0.004); slab(plate, rrect(PW - 0.03, PH - 0.03, PR - 0.015), -0.004, 0.004); layer("display", 0.03, 0.46, sharp=("screen",))
slab(ti, outer, -0.03, 0.06, rrect(PW - 0.06, PH - 0.06, PR - 0.03)); slab(plate, rrect(PW - 0.06, PH - 0.06, PR - 0.03), -0.003, 0.006)   # the frame, and the plate across its middle
for x, y, l in ((PW / 2, 0.28, 0.2), (-PW / 2, 0.36, 0.11), (-PW / 2, 0.2, 0.11)): box(ti, x, y, -0.012, 0.014, l, 0.024)   # the buttons on its sides
for x, y in ((-0.29, 0.66), (0.29, 0.66), (-0.29, -0.66), (0.29, -0.66), (-0.29, 0.0), (0.29, 0.0)): cyl(steel, x, y, -0.006, 0.014, 0.003, 20)   # screws through the plate, on its back
for x, y, w, l in ((-0.1, 0.1, 0.05, 0.5), (0.02, -0.3, 0.3, 0.04)): box(flex, x, y, -0.0045, w, l, 0.0015)   # two flat cables across the back of the plate
layer("frame", 0.0, 0.0, smooth=("ti",), edge=0.002)
for cx, cy in ((-0.2, 0.56), (-0.2, 0.36), (-0.04, 0.46)):   # three cameras
    cyl(steel, cx, cy, -0.02, 0.07, 0.034, 64); cyl(ink, cx, cy, 0.0142, 0.058, 0.0005, 64); cyl(lens, cx, cy, 0.0148, 0.04, 0.0006, 64); box(epoxy, cx, cy, -0.024, 0.15, 0.15, 0.006)
layer("cameras", -0.008, -0.2, smooth=("steel", "lens", "ink"))
# the logic board: an L down the right side and across the top, with the main chip part way down
SOC = (0.19, 0.12)
box(mask, 0.19, 0.2, 0, 0.24, 1.0, 0.008); box(mask, 0.19, -0.5, 0, 0.24, 0.3, 0.008)
box(mask, SOC[0], SOC[1], 0.008, 0.19, 0.19, 0.01); box(lidm, SOC[0], SOC[1], 0.018, 0.15, 0.15, 0.014); box(lidm, SOC[0], SOC[1], 0.032, 0.11, 0.11, 0.005)
box(gold, SOC[0] - 0.085, SOC[1] - 0.085, 0.018, 0.012, 0.012, 0.001, math.pi / 4)   # the corner mark that shows which way round the chip goes
for side in range(4):
    for i in range(5): t = (i - 2) * 0.034; e = 0.085; lx, ly = ((t, -e), (e, t), (t, e), (-e, t))[side]; chip2(tan, tin, SOC[0] + lx, SOC[1] + ly, 0 if side % 2 == 0 else math.pi / 2, 0.55, 0.018)
for (x, y, w, l) in ((0.19, 0.4, 0.16, 0.2), (0.19, 0.62, 0.18, 0.1), (0.2, -0.5, 0.14, 0.18)): box(tin, x, y, 0.008, w, l, 0.016)   # shield cans
box(epoxy, 0.14, -0.16, 0.012, 0.09, 0.09, 0.012); pins(tin, 0.14, -0.16, 0.09, 0.09, 6, 0, (0, 1, 2, 3), 0.009)
box(epoxy, 0.26, -0.2, 0.012, 0.05, 0.12, 0.01); pins(tin, 0.26, -0.2, 0.05, 0.12, 5, math.pi / 2, (0, 2), 0.009)
for _ in range(34):
    x, y = rnd.uniform(0.09, 0.29), rnd.uniform(-0.62, 0.68)
    if abs(x - SOC[0]) < 0.13 and abs(y - SOC[1]) < 0.13 or 0.28 < y < 0.68 or -0.6 < y < -0.4 or (abs(y + 0.18) < 0.09): continue
    chip2(rnd.choice((tan, tan, epoxy)), tin, x, y, rnd.choice((0, math.pi / 2)), 0.6, 0.008)
for (x, y) in ((0.1, -0.02), (0.28, 0.26), (0.1, -0.32)): box(led, x, y, 0.008, 0.012, 0.008, 0.005)
for pts, n, hue in (([(0.19, -0.3), (0.19, -0.08), (0.19, 0.02)], 6, 0.0), ([(0.28, -0.05), (0.28, 0.06), (0.25, 0.09)], 3, 1.0), ([(0.1, 0.3), (0.1, 0.24), (0.14, 0.2)], 4, 0.0), ([(0.26, 0.3), (0.26, 0.24), (0.23, 0.21)], 3, 0.0), ([(0.09, -0.3), (0.09, 0.0), (0.105, 0.03)], 2, 1.0)):
    for e in bus(trace, pts, n, 0.009, 0.0086, hue, rnd, 0.004): cyl(gold, e[0], e[1], 0.0082, 0.005, 0.001, 12)
for (x, y) in ((0.09, 0.68), (0.29, 0.68), (0.09, -0.63), (0.29, -0.63)): cyl(steel, x, y, 0.008, 0.012, 0.004, 20)   # screws
layer("board", -0.018, -0.42, smooth=("steel", "gold"), sharp=("trace", "mask"), edge=0.0008)
slab(pouch, rrect(0.36, 0.9, 0.03), 0, 0.03); box(tan, -0.14, 0.25, 0.03, 0.1, 0.03, 0.002); box(tin, -0.14, -0.6, 0, 0.3, 0.1, 0.028); box(epoxy, -0.14, 0.33, 0, 0.36, 0.05, 0.03)
layer("battery", -0.03, -0.6, edge=0.003).location.x = 0.0
for o in list(layers[-1][0].children): o.location.x = -0.14 if o.name.startswith("pouch") else 0.0; o.location.y = -0.18 if o.name.startswith("pouch") else 0.0
slab(back, outer, 0, 0.006); slab(back, rrect(0.36, 0.42, 0.08), -0.006, 0.006)
for k in range(9): slab(copper, ring(0.2 - k * 0.013), 0.006, 0.002, ring(0.2 - k * 0.013 - 0.009))   # the charging coil on the inside of the back
slab(ink, ring(0.23), 0.006, 0.0008, ring(0.07)); box(flex, 0.0, -0.36, 0.006, 0.04, 0.3, 0.0012)
layer("back", -0.042, -0.86, smooth=("copper",), sharp=("back", "ink"), edge=0.0006)

def pose(scene, *a):
    p = share(scene); e = smooth((p - 0.08) / 0.42); clockv.default_value = p * 2.2
    for h, z0, z1 in layers: h.location.z = mix(z0, z1, e)
bpy.app.handlers.frame_change_pre.append(pose)

# ---------- light and camera. Places are given in the phone's own frame (x across, y up, z out of the front) and turned into the scene's ----------
def W_(x, y, z): return (x, -z, y)
studio(sc, 0.5, 200)
lamp(sc, "key", (-2.6, -3.2, 2.4), 420, (1.0, 0.84, 0.64), 2.2); lamp(sc, "rim", (2.8, 1.8, 1.6), 380, (0.6, 0.76, 1.0), 1.6)
bz = -0.42   # where the logic board ends up
lamp(sc, "gap", W_(SOC[0] + 0.5, SOC[1] - 0.25, bz + 0.2), 6, (1.0, 0.86, 0.7), 0.3, W_(SOC[0], SOC[1], bz))   # a small lamp in the gap, so the chip is not left in the frame's shadow
near = 1.0 if SET == "d" else 1.5
camera(sc, [  # share, camera, aim, lens (mm), f-stop
    (0.00, W_(0.5 * near, 0.25, 4.7 * near), W_(0, 0, 0), 50, 5.6),
    (0.48, W_(3.3, 0.55, 2.3) if SET == "d" else W_(2.6, 0.6, 5.6), W_(0, 0, -0.08), 50, 4.0),   # phones: more from the front and farther off, so the open stack fits a tall picture
    (0.75, W_(1.5, 0.2, 0.0), W_(SOC[0], SOC[1], bz), 50, 2.8),
    (1.00, W_(SOC[0] + 0.24, SOC[1] - 0.2, bz + 0.3), W_(SOC[0], SOC[1], bz + 0.02), 60, 4.0)])
render(sc, "phone")
