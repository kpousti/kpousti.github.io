# Run inside Blender: builds the models for the page's scenes into an empty file and saves it as scenes.blend.
# Every object is one part, named <model>.<part>[.more]. The site flies each model's parts together as its scene arrives, and moves named parts.
#   line   Experience: an approval line. By hand on the left (two hand stamps, one job), automated on the right (conveyor, two stamping gantries)
#   rec    Industrial AI Notebook: a strip-chart recorder wired to a vibration sensor on a bearing; the pen draws the live signal
#   gears  TheAlgorithms/C++ (Tarjan): gear trains on a plate; each strongly connected component is one train that turns together
#   surf   Surf Alert: a weather buoy and a surfboard on a rolling swell
#   mm     Mini Maps (Dijkstra): a pin-and-string board; pins are settled in order of distance
#   ac     Agent City: a hub pavilion and six huts on stilts over water, joined by boardwalks, with agents walking in to report
#   kb     Kia-bot: a small desk robot with a ring of level bars for its voice, wired to three tools it calls (a card drawer, a clock, a magnifier)
#   qb     Quant Backtest Lab: an equity curve as a row of bars on a bed, with a brass window that steps forward along a rail (train, then test)
#   la     Lead Autoresponder: a mail sorter. Envelopes drop through a hopper and a flipper sends each to one of three trays
#   md     Market Debrief: a split-flap board whose flaps turn to draw the day's bars
#   mg     Math 163 Study Game: flash cards on two rings, flipping over, with a pencil, a set square and a compass
#   tools  Skills: a dark pegboard wall of real tools, each one doing its job in turn
#   tk     Contact: a brass telegraph key and its sounder, tapping out a message
import bpy, math, os
from mathutils import Vector

bpy.ops.wm.read_homefile(use_empty=True)

def lin(h): return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in [((h >> s) & 255) / 255 for s in (16, 8, 0)])
def mat(name, rgb, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*lin(rgb), 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*lin(rgb), 1); return m

STEEL, DARK, BRASS, WOOD, RUBBER, PAPER, AMBER, BLUE, GREY, BRICK, YELLOW, GLASS, WATER, INK = range(14)
MATS = [mat("steel", 0xaab6cc, 0.9, 0.32), mat("dark", 0x1a1e29, 0.6, 0.5), mat("brass", 0xd9a54a, 0.9, 0.3), mat("wood", 0x8b6a47, 0.0, 0.7), mat("rubber", 0x14161b, 0.0, 0.8),
        mat("paper", 0xe9edf5, 0.0, 0.8), mat("amber", 0xf2b56b, 0.1, 0.5), mat("blue", 0x3f78c2, 0.1, 0.5), mat("grey", 0x6b7790, 0.5, 0.45), mat("brick", 0xa2493a, 0.1, 0.5),
        mat("yellow", 0xe2b23c, 0.1, 0.5), mat("glass", 0x0e1524, 0.6, 0.2), mat("water", 0x123560, 0.7, 0.2), mat("ink", 0x25407a, 0.0, 0.8)]

V, F, M = [], [], []
def tr(p, axis): return p if axis == 'z' else (p[2], p[0], p[1]) if axis == 'x' else (p[1], p[2], p[0])
def box(x0, x1, y0, y1, z0, z1, m, bottom=False):
    i = len(V)
    V.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
    for f in [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)] + ([(3, 2, 1, 0)] if bottom else []):
        F.append(tuple(i + k for k in f)); M.append(m)
def cyl(c, r0, r1, length, m, seg=10, axis='z'):
    """a cylinder or cone frustum from point c along +axis, capped at both ends"""
    i = len(V)
    for (r, t) in ((r0, 0.0), (r1, length)):
        for k in range(seg):
            a = math.tau * k / seg; p = tr((r * math.cos(a), r * math.sin(a), t), axis); V.append((c[0] + p[0], c[1] + p[1], c[2] + p[2]))
    for k in range(seg): F.append((i + k, i + (k + 1) % seg, i + seg + (k + 1) % seg, i + seg + k)); M.append(m)
    F.append(tuple(i + seg + k for k in range(seg))); M.append(m); F.append(tuple(i + k for k in range(seg - 1, -1, -1))); M.append(m)
def rod(p0, p1, r, m, seg=6):
    """a thin bar between two points"""
    a = Vector(p0); b = Vector(p1); d = (b - a).normalized(); u = d.orthogonal().normalized(); v = d.cross(u); i = len(V)
    for c in (a, b):
        for k in range(seg): ang = math.tau * k / seg; V.append(tuple(c + (u * math.cos(ang) + v * math.sin(ang)) * r))
    for k in range(seg): F.append((i + k, i + (k + 1) % seg, i + seg + (k + 1) % seg, i + seg + k)); M.append(m)
    F.append(tuple(i + seg + k for k in range(seg))); M.append(m); F.append(tuple(i + k for k in range(seg - 1, -1, -1))); M.append(m)
def sphere(cx, cy, cz, r, m, seg=10, rings=6):
    i = len(V); V.append((cx, cy, cz - r))
    for j in range(1, rings):
        t = math.pi * j / rings
        for k in range(seg): a = math.tau * k / seg; V.append((cx + r * math.sin(t) * math.cos(a), cy + r * math.sin(t) * math.sin(a), cz - r * math.cos(t)))
    V.append((cx, cy, cz + r)); top = len(V) - 1
    for k in range(seg): F.append((i, i + 1 + (k + 1) % seg, i + 1 + k)); M.append(m)
    for j in range(rings - 2):
        for k in range(seg): a = i + 1 + j * seg + k; b = i + 1 + j * seg + (k + 1) % seg; F.append((a, b, b + seg, a + seg)); M.append(m)
    base = i + 1 + (rings - 2) * seg
    for k in range(seg): F.append((base + k, base + (k + 1) % seg, top)); M.append(m)
def prism(pts, z0, z1, m, topm=None):
    i = len(V); n = len(pts)
    for (x, y) in pts: V.append((x, y, z0))
    for (x, y) in pts: V.append((x, y, z1))
    for k in range(n): F.append((i + k, i + (k + 1) % n, i + n + (k + 1) % n, i + n + k)); M.append(m)
    F.append(tuple(i + n + k for k in range(n))); M.append(m if topm is None else topm); F.append(tuple(i + k for k in range(n - 1, -1, -1))); M.append(m)
def xprism(pts, x0, x1, m):
    """a side profile in (y, z), counter-clockwise seen from +x, pulled along x"""
    i = len(V); n = len(pts)
    for (y, z) in pts: V.append((x0, y, z))
    for (y, z) in pts: V.append((x1, y, z))
    for k in range(n): F.append((i + k, i + (k + 1) % n, i + n + (k + 1) % n, i + n + k)); M.append(m)
    F.append(tuple(i + n + k for k in range(n))); M.append(m); F.append(tuple(i + k for k in range(n - 1, -1, -1))); M.append(m)
def quad(a, b, c, d, m): i = len(V); V.extend([a, b, c, d]); F.append((i, i + 1, i + 2, i + 3)); M.append(m)

count = {}
def part(name, loc=(0, 0, 0), rot=(0, 0, 0), smooth=0.0, mesh=None, scale=None):
    """turn what was drawn into one part (or reuse a mesh already made), standing at loc"""
    if mesh is None:
        me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
        order = [M[0]] + [k for k in range(len(MATS)) if k != M[0]]  # the export takes shininess from the first material
        for k in order: me.materials.append(MATS[k])
        me.polygons.foreach_set("material_index", [order.index(k) for k in M])
        if smooth:
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
            try: me.set_sharp_from_angle(angle=smooth)
            except Exception as e: print(e)
        count[name.split(".")[0]] = count.get(name.split(".")[0], 0) + sum(len(p) - 2 for p in F)
        V.clear(); F.clear(); M.clear()
    else: me = mesh
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; o["keep"] = 1
    if scale: o.scale = scale
    return me

# ================= line: the approval line =================
box(-1.05, 1.05, -0.3, 0.3, 0, 0.05, DARK, True)
for y in (-0.24, 0.24): box(-1.0, 1.0, y - 0.014, y + 0.014, 0.05, 0.062, STEEL)
for k in range(21): box(-1.0 + 0.1 * k - 0.002, -1.0 + 0.1 * k + 0.002, -0.29, -0.262, 0.05, 0.053, STEEL)  # a ruler along the front edge
part("line.base")
cyl((0, 0, 0), 0.02, 0.02, 0.016, STEEL, 6); bolt = part("line.bolt.0", (-1.0, -0.275, 0.05))
for k, (x, y) in enumerate([(1.0, -0.275), (-1.0, 0.275), (1.0, 0.275), (0.0, -0.275), (0.0, 0.275)]): part(f"line.bolt.{k + 1}", (x, y, 0.05), mesh=bolt)
# the bench where the work is done by hand
box(-0.98, -0.08, -0.22, 0.22, 0.3, 0.335, WOOD, True)
for (x, y) in [(-0.94, -0.18), (-0.12, -0.18), (-0.94, 0.18), (-0.12, 0.18)]: box(x - 0.018, x + 0.018, y - 0.018, y + 0.018, 0.05, 0.3, STEEL)
box(-0.94, -0.12, -0.19, -0.17, 0.12, 0.14, STEEL); box(-0.94, -0.12, 0.17, 0.19, 0.12, 0.14, STEEL); box(-0.96, -0.1, -0.2, 0.2, 0.13, 0.142, DARK)
for k in range(7): box(-0.6 - 0.004 * k, -0.44 - 0.004 * k, 0.04 + 0.002 * k, 0.17 + 0.002 * k, 0.335 + 0.004 * k, 0.338 + 0.004 * k, PAPER)  # the pile waiting its turn
box(-0.565, -0.475, 0.05, 0.16, 0.142, 0.2, PAPER)
part("line.bench")
box(-0.07, 0.07, -0.05, 0.05, 0, 0.018, STEEL); box(-0.06, 0.06, -0.04, 0.04, 0.018, 0.024, INK)
pad = part("line.pad.0", (-0.8, -0.13, 0.335)); part("line.pad.1", (-0.3, -0.13, 0.335), mesh=pad)
box(-0.085, 0.085, -0.06, 0.06, 0, 0.005, PAPER); box(-0.085, 0.085, 0.036, 0.06, 0.005, 0.0065, AMBER)
for k in range(3): box(-0.07, 0.04 - 0.02 * k, 0.012 - 0.02 * k, 0.018 - 0.02 * k, 0.005, 0.006, INK)
card = part("line.card.0", (-0.8, 0.07, 0.335))
for k in range(1, 6): part(f"line.card.{k}", (0.1 + 0.17 * k, 0.0, 0.388), mesh=card)
box(-0.047, 0.047, -0.032, 0.032, 0, 0.006, RUBBER); box(-0.045, 0.045, -0.03, 0.03, 0.006, 0.04, WOOD); cyl((0, 0, 0.04), 0.014, 0.011, 0.055, WOOD, 8); sphere(0, 0, 0.118, 0.027, WOOD, 8, 5)
stamp = part("line.stamp.0", (-0.8, 0.07, 0.341), smooth=0.7); part("line.stamp.1", (-0.38, 0.07, 0.341), mesh=stamp)
# the conveyor
for y in (-0.21, 0.19): box(0.0, 1.0, y, y + 0.02, 0.3, 0.38, STEEL)
for (x, y) in [(0.06, -0.2), (0.94, -0.2), (0.06, 0.2), (0.94, 0.2)]: box(x - 0.016, x + 0.016, y - 0.016, y + 0.016, 0.05, 0.3, STEEL)
box(0.06, 0.94, -0.21, -0.19, 0.14, 0.16, STEEL); box(0.06, 0.94, 0.19, 0.21, 0.14, 0.16, STEEL)
box(0.03, 0.97, -0.18, 0.18, 0.372, 0.384, RUBBER); box(0.03, 0.97, -0.18, 0.18, 0.31, 0.318, RUBBER)
for x in (0.03, 0.97): cyl((x, -0.19, 0.347), 0.037, 0.037, 0.38, STEEL, 12, 'y')
for k in range(7): cyl((0.14 + 0.12 * k, -0.19, 0.352), 0.016, 0.016, 0.38, GREY, 8, 'y')
cyl((1.0, 0.21, 0.26), 0.05, 0.05, 0.09, GREY, 12, 'y'); box(0.95, 1.05, 0.21, 0.3, 0.2, 0.22, STEEL)  # the drive motor
part("line.conveyor", smooth=0.6)
box(-0.02, 0.02, -0.25, -0.21, 0.05, 0.74, STEEL); box(-0.02, 0.02, 0.21, 0.25, 0.05, 0.74, STEEL); box(-0.03, 0.03, -0.25, 0.25, 0.74, 0.79, STEEL)
cyl((0, 0, 0.6), 0.042, 0.042, 0.14, GREY, 12); cyl((0, 0, 0.585), 0.05, 0.05, 0.015, STEEL, 12); cyl((0.042, 0, 0.7), 0.01, 0.01, 0.03, BRASS, 6, 'x'); rod((0.07, 0, 0.7), (0.07, 0.2, 0.76), 0.005, AMBER)
gan = part("line.gantry.0", (0.36, 0, 0), smooth=0.6); part("line.gantry.1", (0.72, 0, 0), mesh=gan)
cyl((0, 0, -0.17), 0.012, 0.012, 0.17, STEEL, 8); box(-0.05, 0.05, -0.035, 0.035, -0.2, -0.17, GREY); box(-0.052, 0.052, -0.037, 0.037, -0.206, -0.2, RUBBER)
head = part("line.head.0", (0.36, 0, 0.6)); part("line.head.1", (0.72, 0, 0.6), mesh=head)
# the control box and the stack light
box(-0.07, 0.07, -0.03, 0.03, 0.42, 0.6, GREY); rod((0, 0, 0.05), (0, 0, 0.42), 0.012, STEEL)
cyl((-0.03, -0.03, 0.55), 0.014, 0.014, 0.012, BRICK, 10, 'y'); cyl((0.025, -0.03, 0.55), 0.01, 0.01, 0.008, AMBER, 8, 'y'); cyl((0.025, -0.03, 0.5), 0.01, 0.01, 0.008, STEEL, 8, 'y'); box(-0.05, 0.0, -0.034, -0.03, 0.44, 0.5, GLASS)
part("line.panel", (0.54, -0.42, 0), smooth=0.6)
rod((0, 0, 0.05), (0, 0, 0.62), 0.01, STEEL)
for k, m in enumerate((BRICK, AMBER, BLUE)): cyl((0, 0, 0.62 + 0.05 * k), 0.026, 0.026, 0.044, m, 10)
cyl((0, 0, 0.77), 0.028, 0.02, 0.012, STEEL, 10)
part("line.beacon", (1.0, -0.22, 0), smooth=0.6)

# ================= rec: the strip-chart recorder =================
S0, S1 = (-0.28, 0.2), (0.28, 0.44)   # the sloping top, front edge to back edge, in (y, z)
def on_slope(s, lift=0.0): return (S0[0] + (S1[0] - S0[0]) * s, S0[1] + (S1[1] - S0[1]) * s + lift)
PHI = math.atan2(S1[1] - S0[1], S1[0] - S0[0])
xprism([(-0.28, 0.04), (0.28, 0.04), S1, S0], -0.45, 0.45, GREY)
box(-0.43, 0.43, -0.286, -0.28, 0.055, 0.185, DARK)
for (x, y) in [(-0.4, -0.23), (0.4, -0.23), (-0.4, 0.23), (0.4, 0.23)]: cyl((x, y, 0), 0.03, 0.036, 0.04, RUBBER, 8)
for k in range(9): box(0.452, 0.458, -0.2 + 0.045 * k, -0.18 + 0.045 * k, 0.1, 0.3, DARK)  # cooling slots
rod((0.47, -0.12, 0.16), (0.52, -0.12, 0.2), 0.008, STEEL); rod((0.52, -0.12, 0.2), (0.52, 0.12, 0.2), 0.008, STEEL); rod((0.52, 0.12, 0.2), (0.47, 0.12, 0.16), 0.008, STEEL)
part("rec.body")
a, b = on_slope(0.05, 0.004), on_slope(0.95, 0.004)
quad((-0.3, a[0], a[1]), (0.3, a[0], a[1]), (0.3, b[0], b[1]), (-0.3, b[0], b[1]), PAPER)
for k in range(1, 12):
    p, q = on_slope(0.05, 0.005), on_slope(0.95, 0.005); x = -0.3 + 0.05 * k
    quad((x - 0.0012, p[0], p[1]), (x + 0.0012, p[0], p[1]), (x + 0.0012, q[0], q[1]), (x - 0.0012, q[0], q[1]), GREY)
for k in range(1, 9):
    p, q = on_slope(0.05 + 0.1 * k - 0.002, 0.005), on_slope(0.05 + 0.1 * k + 0.002, 0.005)
    quad((-0.3, p[0], p[1]), (0.3, p[0], p[1]), (0.3, q[0], q[1]), (-0.3, q[0], q[1]), GREY)
part("rec.paper")
cyl((-0.31, 0.3, 0.52), 0.075, 0.075, 0.62, PAPER, 14, 'x'); cyl((-0.33, 0.3, 0.52), 0.09, 0.09, 0.02, STEEL, 14, 'x'); cyl((0.31, 0.3, 0.52), 0.09, 0.09, 0.02, STEEL, 14, 'x')
for x in (-0.345, 0.345): box(x - 0.012, x + 0.012, 0.27, 0.33, 0.42, 0.52, STEEL)
part("rec.roll", smooth=0.6)
r0 = on_slope(0.86, 0.06)
rod((-0.38, r0[0], r0[1]), (0.38, r0[0], r0[1]), 0.008, STEEL)
for x in (-0.38, 0.38): g = on_slope(0.86, 0.0); rod((x, g[0], g[1]), (x, r0[0], r0[1]), 0.01, STEEL)
part("rec.rail")
box(-0.03, 0.03, -0.02, 0.02, -0.014, 0.014, DARK); rod((0, 0, -0.014), (0, 0, -0.05), 0.006, AMBER); cyl((0, 0, -0.056), 0.0015, 0.006, 0.006, INK, 6)
part("rec.pen", (0, r0[0], r0[1]), (PHI, 0, 0))
box(-0.008, 0.008, -0.006, 0.006, 0, 0.002, INK)
dot = None
for j in range(34):
    p = on_slope(0.84 - 0.02 * j, 0.006); dot = part(f"rec.dot.{j}", (0, p[0], p[1]), (PHI, 0, 0), mesh=dot)
cyl((0, -0.31, 0), 0.028, 0.024, 0.03, DARK, 12, 'y'); box(-0.003, 0.003, -0.312, -0.31, 0.008, 0.026, PAPER)
knob = part("rec.knob.0", (-0.3, 0, 0.12), smooth=0.6)
for k, x in enumerate((-0.18, -0.06)): part(f"rec.knob.{k + 1}", (x, 0, 0.12), mesh=knob)
box(0.1, 0.3, -0.29, -0.286, 0.08, 0.16, GLASS); cyl((0.36, -0.295, 0.12), 0.012, 0.012, 0.015, BRICK, 8, 'y')
part("rec.display")
g = on_slope(0.3, 0.004)
cyl((0, 0, 0), 0.062, 0.062, 0.012, STEEL, 16); cyl((0, 0, 0.012), 0.054, 0.054, 0.002, PAPER, 16)
for k in range(9): a2 = math.radians(-60 + 15 * k); box(0.044 * math.sin(a2) - 0.0015, 0.044 * math.sin(a2) + 0.0015, 0.044 * math.cos(a2) - 0.004, 0.044 * math.cos(a2) + 0.004, 0.014, 0.0155, DARK)
part("rec.gauge", (0.375, g[0], g[1]), (PHI, 0, 0), smooth=0.6)
box(-0.003, 0.003, -0.008, 0.045, 0, 0.003, BRICK); cyl((0, 0, 0), 0.008, 0.008, 0.005, DARK, 8)
part("rec.needle", (0.375, g[0] - 0.0155 * math.sin(PHI), g[1] + 0.0155 * math.cos(PHI)), (PHI, 0, 0))
# the sensor on its bearing, and the cable back to the recorder
box(-0.14, 0.14, -0.1, 0.1, 0, 0.022, STEEL); box(-0.1, 0.1, -0.05, 0.05, 0.022, 0.06, GREY); cyl((0, -0.05, 0.11), 0.082, 0.082, 0.1, GREY, 14, 'y'); cyl((0, -0.2, 0.11), 0.03, 0.03, 0.4, STEEL, 10, 'y')
for (x, y) in [(-0.115, -0.07), (0.115, -0.07), (-0.115, 0.07), (0.115, 0.07)]: cyl((x, y, 0.022), 0.012, 0.012, 0.012, STEEL, 6)
cyl((0, 0.2, 0.11), 0.07, 0.07, 0.03, DARK, 14, 'y')
part("rec.rig", (-0.8, 0, 0), smooth=0.6)
cyl((0, 0, 0), 0.024, 0.024, 0.034, BRASS, 10); cyl((0, 0, 0.034), 0.012, 0.012, 0.012, DARK, 8)
part("rec.sensor", (-0.8, 0, 0.192), smooth=0.6)
pts = [(-0.8, 0, 0.24), (-0.76, 0.02, 0.33), (-0.66, 0.0, 0.37), (-0.56, -0.04, 0.33), (-0.5, -0.06, 0.26), (-0.452, -0.06, 0.22)]
for k in range(len(pts) - 1): rod(pts[k], pts[k + 1], 0.006, RUBBER)
part("rec.cable")

# ================= gears: Tarjan's strongly connected components as gear trains =================
MOD = 0.02
def gear(n, thick=0.03):
    R = MOD * n / 2; p = math.tau / n; pts = []
    for k in range(n):
        a0 = k * p
        for (r, da) in [(R - 1.25 * MOD, -0.25), (R + MOD, -0.1), (R + MOD, 0.1), (R - 1.25 * MOD, 0.25)]: pts.append((r * math.cos(a0 + da * p), r * math.sin(a0 + da * p)))
    prism(pts, 0, thick, STEEL)
    cyl((0, 0, thick), R * 0.36, R * 0.36, 0.012, STEEL, 12); cyl((0, 0, thick + 0.012), R * 0.14, R * 0.14, 0.012, BRASS, 6)
    holes = 5 if n >= 16 else 4 if n >= 12 else 0
    for k in range(holes): a = math.tau * k / holes + 0.3; cyl((R * 0.62 * math.cos(a), R * 0.62 * math.sin(a), thick), R * 0.17, R * 0.17, 0.0015, DARK, 8)
    box(-R * 0.03, R * 0.03, R * 0.14, R * 0.22, thick + 0.012, thick + 0.016, DARK)  # the key in the shaft
# back plate, standing up
box(-0.95, 1.0, 0.0, 0.03, 0.04, 1.12, DARK, True); box(-0.97, 1.02, -0.01, 0.04, 0.0, 0.05, STEEL, True)
for (x, z) in [(-0.9, 0.1), (0.95, 0.1), (-0.9, 1.06), (0.95, 1.06)]: cyl((x, -0.012, z), 0.018, 0.018, 0.012, STEEL, 6, 'y')
for x in (-0.6, 0.65): box(x - 0.03, x + 0.03, 0.03, 0.3, 0.0, 0.03, STEEL); box(x - 0.012, x + 0.012, 0.03, 0.26, 0.03, 0.5, STEEL)
part("gears.plate")
LAY = [  # component, teeth, centre (x, z), and which gear it meshes with (index) or None
    (0, 24, (-0.55, 0.74), None), (0, 12, None, 0, 0.0), (0, 16, None, 0, -math.pi / 2), (0, 12, None, 2, 0.0),
    (1, 16, (0.2, 0.8), None), (1, 12, None, 4, 0.0), (1, 10, None, 5, -math.pi / 2),
    (2, 24, (0.68, 0.24), None), (2, 12, None, 7, math.pi),
    (3, 12, (0.03, 0.3), None), (3, 10, None, 9, math.pi / 2)]
pos, ang, sign, meshes = [], [], [], {}
for k, g in enumerate(LAY):
    n = g[1]
    if g[2] is not None: pos.append(g[2]); ang.append(0.1 * k); sign.append(1)
    else:
        j, phi = g[3], g[4]; d = MOD * (n + LAY[j][1]) / 2
        pos.append((pos[j][0] + d * math.cos(phi), pos[j][1] + d * math.sin(phi)))
        ang.append(phi + math.pi - math.pi / n - (ang[j] - phi) * LAY[j][1] / n); sign.append(-sign[j])   # a tooth of one sits in a gap of the other
    if n not in meshes: gear(n); meshes[n] = None
    # the gear is drawn lying flat; stood up, its axis points at the viewer. Its own turn goes in first, so the site can keep turning it about that axis.
    from mathutils import Euler, Matrix
    rotm = Matrix.Rotation(math.pi / 2, 4, 'X') @ Matrix.Rotation(ang[k], 4, 'Z')
    me = part(f"gears.gear.{g[0]}.{n}.{sign[k]}.{k}", (pos[k][0], -0.012, pos[k][1]), rotm.to_euler(), mesh=meshes[n]); meshes[n] = me
# one-way links between the components, engraved on the plate: brass arrows
def arrow(p, q):
    a = Vector((p[0], -0.003, p[1])); b = Vector((q[0], -0.003, q[1])); d = (b - a).normalized(); s = Vector((-d.z, 0, d.x)) * 0.012
    rod(tuple(a), tuple(b - d * 0.04), 0.004, BRASS, 4); i = len(V); V.extend([tuple(b), tuple(b - d * 0.05 + s), tuple(b - d * 0.05 - s)]); F.append((i, i + 1, i + 2)); M.append(BRASS); F.append((i, i + 2, i + 1)); M.append(BRASS)
arrow((-0.16, 0.5), (-0.06, 0.4)); arrow((0.3, 0.6), (0.14, 0.42)); arrow((0.18, 0.28), (0.34, 0.25))
part("gears.links")

# ================= surf: the weather buoy and the board =================
box(-0.062, 0.062, -0.062, 0.062, -0.012, 0, WATER)
tile = None; k = 0
for iy in range(9):
    for ix in range(14): tile = part(f"surf.w.{k}", (-0.845 + 0.13 * ix, -0.52 + 0.13 * iy, 0), mesh=tile); k += 1
# the buoy: a discus hull, a tripod mast, solar panels, the instruments
cyl((0, 0, -0.06), 0.2, 0.28, 0.06, YELLOW, 16); cyl((0, 0, 0), 0.28, 0.28, 0.05, YELLOW, 16); cyl((0, 0, 0.05), 0.285, 0.285, 0.012, STEEL, 16); cyl((0, 0, 0.062), 0.12, 0.12, 0.06, GREY, 12)
for k in range(3):
    a = math.tau * k / 3 + 0.5; rod((0.2 * math.cos(a), 0.2 * math.sin(a), 0.06), (0.03 * math.cos(a), 0.03 * math.sin(a), 0.56), 0.009, STEEL)
    a2 = a + math.pi / 3; c, s = math.cos(a2), math.sin(a2); n = Vector((c, s, 0)); t = Vector((-s, c, 0))
    p0 = n * 0.21 + Vector((0, 0, 0.1)); p1 = n * 0.12 + Vector((0, 0, 0.3))
    quad(tuple(p0 - t * 0.09), tuple(p0 + t * 0.09), tuple(p1 + t * 0.09), tuple(p1 - t * 0.09), GLASS); quad(tuple(p0 + t * 0.09), tuple(p0 - t * 0.09), tuple(p1 - t * 0.09), tuple(p1 + t * 0.09), STEEL)
for z in (0.28, 0.42): cyl((0, 0, z), 0.075 if z < 0.4 else 0.05, 0.075 if z < 0.4 else 0.05, 0.008, STEEL, 10)
cyl((0, 0, 0.56), 0.05, 0.05, 0.02, STEEL, 10); box(-0.035, 0.035, -0.03, 0.03, 0.58, 0.64, GREY); rod((0.03, 0, 0.64), (0.03, 0, 0.9), 0.004, STEEL); sphere(-0.02, 0, 0.665, 0.018, AMBER, 8, 5)
rod((-0.03, 0.02, 0.64), (-0.03, 0.02, 0.72), 0.005, STEEL)
part("surf.buoy", (-0.4, 0.1, 0), smooth=0.6)
for k in range(3):
    a = math.tau * k / 3; rod((0, 0, 0), (0.05 * math.cos(a), 0.05 * math.sin(a), 0), 0.003, STEEL, 4); sphere(0.05 * math.cos(a), 0.05 * math.sin(a), 0, 0.014, DARK, 6, 4)
part("surf.cups", (-0.43, 0.12, 0.725))
# the board: a thruster shortboard, nose to +x
ST = [(0.0, 0.045), (0.08, 0.082), (0.2, 0.112), (0.35, 0.128), (0.5, 0.13), (0.65, 0.12), (0.8, 0.092), (0.9, 0.06), (0.96, 0.032), (1.0, 0.003)]
i0 = len(V)
for (u, w) in ST:
    x = -0.5 + u; z = 0.012 * (1 - 2 * u) ** 2 + 0.28 * max(0.0, u - 0.6) ** 2
    for (yy, dz) in [(-1, 0), (-0.6, 0.012), (0, 0.016), (0.6, 0.012), (1, 0), (0.6, -0.01), (0, -0.013), (-0.6, -0.01)]: V.append((x, yy * w, z + dz))
for s in range(len(ST) - 1):
    for k in range(8):
        a = i0 + s * 8 + k; b = i0 + s * 8 + (k + 1) % 8
        F.append((a, a + 8, b + 8, b)); M.append(AMBER if k in (1, 2) and 2 <= s <= 6 and False else (BLUE if k in (0, 3, 4, 7) else PAPER))
F.append(tuple(i0 + k for k in range(8))); M.append(PAPER)
box(-0.34, 0.3, -0.004, 0.004, 0.0165, 0.018, AMBER)  # the stringer
cyl((-0.44, 0, 0.012), 0.012, 0.012, 0.004, DARK, 8)   # the leash plug
for (x, y, lean) in [(-0.42, 0, 0), (-0.33, 0.075, 0.25), (-0.33, -0.075, -0.25)]:
    i = len(V)
    for dy in (-0.003, 0.003): V.extend([(x + 0.06, y + dy, -0.012), (x - 0.04, y + dy, -0.012), (x - 0.07, y + dy + lean * 0.08, -0.095)])
    F.append((i, i + 1, i + 2)); M.append(BLUE); F.append((i + 3, i + 5, i + 4)); M.append(BLUE); F.append((i, i + 2, i + 5, i + 3)); M.append(BLUE); F.append((i + 1, i + 4, i + 5, i + 2)); M.append(BLUE)
part("surf.board", (0.3, -0.12, 0.02), (0, 0, 0.35), smooth=0.8)


from mathutils import Matrix
def ngon(cx, cy, r, n, phase=0.0): return [(cx + r * math.cos(phase + math.tau * k / n), cy + r * math.sin(phase + math.tau * k / n)) for k in range(n)]
def flat(angle=0.0): return (Matrix.Rotation(math.pi / 2, 4, 'X') @ Matrix.Rotation(angle, 4, 'Z')).to_euler()  # drawn lying flat, hung on an upright board facing the viewer

# ================= mm: the pin-and-string board (Dijkstra) =================
box(-0.92, 0.92, 0.0, 0.035, 0.06, 1.1, WOOD, True)
for (x0, x1, z0, z1) in [(-0.95, 0.95, 0.03, 0.06), (-0.95, 0.95, 1.1, 1.13), (-0.95, -0.92, 0.06, 1.1), (0.92, 0.95, 0.06, 1.1)]: box(x0, x1, -0.012, 0.045, z0, z1, DARK, True)
for k in range(13): box(-0.9 + 0.15 * k - 0.001, -0.9 + 0.15 * k + 0.001, -0.002, 0.0, 0.06, 1.1, DARK)
for k in range(7): box(-0.92, 0.92, -0.002, 0.0, 0.08 + 0.16 * k - 0.001, 0.08 + 0.16 * k + 0.001, DARK)
for x in (-0.6, 0.6): box(x - 0.03, x + 0.03, 0.035, 0.36, 0.0, 0.03, STEEL, True); rod((x, 0.33, 0.03), (x, 0.04, 0.7), 0.012, STEEL)
part("mm.board")
cyl((0, -0.05, 0), 0.008, 0.008, 0.05, BRASS, 8, 'y'); sphere(0, -0.058, 0, 0.02, BRASS, 10, 6)
pin = None; PINS = []
for j in range(3):
    for i in range(6):
        k = j * 6 + i; x = -0.74 + 0.296 * i + 0.07 * math.sin(k * 2.3); z = 0.27 + 0.31 * j + 0.06 * math.cos(k * 1.7)
        PINS.append((x, z)); pin = part(f"mm.pin.{k}", (x, 0, z), smooth=0.7, mesh=pin)
cyl((0, 0, 0), 0.0045, 0.0045, 1.0, PAPER, 6)
string = None; EDGES = []
for j in range(3):
    for i in range(6):
        k = j * 6 + i
        if i < 5: EDGES.append((k, k + 1))
        if j < 2: EDGES.append((k, k + 6))
        if i < 5 and j < 2 and (k % 4 == 1): EDGES.append((k, k + 7))
for (a, b) in EDGES:
    dx, dz = PINS[b][0] - PINS[a][0], PINS[b][1] - PINS[a][1]
    string = part(f"mm.str.{a}.{b}", (PINS[a][0], -0.036, PINS[a][1]), (0, math.atan2(dx, dz), 0), mesh=string, scale=(1, 1, math.hypot(dx, dz)))

# ================= ac: Agent City, huts over the water =================
box(-0.068, 0.068, -0.068, 0.068, -0.012, 0, WATER)
tile = None; k = 0
for iy in range(10):
    for ix in range(13): tile = part(f"ac.w.{k}", (-0.84 + 0.14 * ix, -0.63 + 0.14 * iy, 0), mesh=tile); k += 1
# the hub: an eight-sided deck and an open pavilion under a two-tier thatched roof
for k in range(8): a = math.tau * k / 8; rod((0.2 * math.cos(a), 0.2 * math.sin(a), -0.05), (0.2 * math.cos(a), 0.2 * math.sin(a), 0.13), 0.012, WOOD)
prism(ngon(0, 0, 0.27, 8, math.pi / 8), 0.13, 0.15, WOOD)
for k in range(8): a = math.tau * k / 8 + math.pi / 8; rod((0.2 * math.cos(a), 0.2 * math.sin(a), 0.15), (0.2 * math.cos(a), 0.2 * math.sin(a), 0.32), 0.008, WOOD)
cyl((0, 0, 0.32), 0.3, 0.12, 0.12, YELLOW, 12); cyl((0, 0, 0.42), 0.16, 0.0, 0.14, YELLOW, 12); cyl((0, 0, 0.15), 0.06, 0.06, 0.1, DARK, 10); sphere(0, 0, 0.275, 0.022, AMBER, 8, 5)
part("ac.hub", smooth=0.5)
# a hut: four stilts, a deck with a rail, walls with a doorway, a thatched roof, a ladder
for (x, y) in [(-0.07, -0.06), (0.07, -0.06), (-0.07, 0.06), (0.07, 0.06)]: rod((x, y, -0.05), (x, y, 0.11), 0.007, WOOD)
box(-0.1, 0.1, -0.09, 0.09, 0.11, 0.122, WOOD, True); box(-0.075, 0.075, -0.06, 0.06, 0.122, 0.21, PAPER); box(-0.02, 0.02, -0.062, -0.06, 0.122, 0.19, DARK)
cyl((0, 0, 0.2), 0.14, 0.05, 0.07, YELLOW, 8); cyl((0, 0, 0.26), 0.07, 0.0, 0.08, YELLOW, 8)
for x in (-0.03, 0.03): rod((x, -0.09, 0.122), (x, -0.15, -0.04), 0.004, WOOD, 4)
for z in (0.0, 0.04, 0.08): rod((-0.03, -0.11 - (0.08 - z) * 0.4, z), (0.03, -0.11 - (0.08 - z) * 0.4, z), 0.003, WOOD, 4)
hut = None; HUTS = []
for k in range(6):
    a = math.tau * k / 6 + 0.3; hx, hy = 0.68 * math.cos(a), 0.5 * math.sin(a); HUTS.append((hx, hy))
    hut = part(f"ac.hut.{k}", (hx, hy, 0), (0, 0, math.atan2(-hy, -hx) + math.pi / 2), smooth=0.5, mesh=hut)
# boardwalks: a unit length of planks, stretched from each hut to the hub
box(-0.03, 0.03, 0, 1, 0, 0.008, WOOD, True)
for k in range(10): box(-0.036, 0.036, 0.04 + 0.1 * k, 0.07 + 0.1 * k, 0.008, 0.011, WOOD)
walk = None
for k, (hx, hy) in enumerate(HUTS):
    d = math.hypot(hx, hy); ux, uy = hx / d, hy / d; L2 = d - 0.27 - 0.1
    walk = part(f"ac.walk.{k}", (ux * 0.27, uy * 0.27, 0.118), (0, 0, math.atan2(hy, hx) - math.pi / 2), mesh=walk, scale=(1, L2, 1))
cyl((0, 0, 0), 0.016, 0.006, 0.04, BLUE, 8); sphere(0, 0, 0.05, 0.013, AMBER, 8, 5)
agent = None
for k in range(6): agent = part(f"ac.agent.{k}", (HUTS[k][0] * 0.8, HUTS[k][1] * 0.8, 0.13), smooth=0.6, mesh=agent)

# ================= kb: Kia-bot =================
# A small desk robot. Its head turns to the tool it is calling, its eyes blink and light, the ring of bars round it is its voice.
def rrect(hx, hy, r, n=5):
    """a rounded rectangle outline, counter-clockwise"""
    pts = []
    for q, (cx, cy) in enumerate(((hx - r, hy - r), (-hx + r, hy - r), (-hx + r, -hy + r), (hx - r, -hy + r))):
        for k in range(n + 1): a = math.pi / 2 * (q + k / n); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts
cyl((0, 0, 0), 0.4, 0.4, 0.03, DARK, 28); cyl((0, 0, 0.03), 0.37, 0.37, 0.006, STEEL, 28)
part("kb.base", smooth=0.5)
# the body: a tapered torso with a speaker grille, a chest light, a brass collar, a neck and two short arms
cyl((0, 0, 0.036), 0.2, 0.17, 0.3, GREY, 28); cyl((0, 0, 0.336), 0.185, 0.185, 0.02, BRASS, 28); cyl((0, 0, 0.356), 0.07, 0.07, 0.05, STEEL, 16)
for k in range(5): z = 0.07 + 0.035 * k; r = 0.2 - 0.03 * (z - 0.036) / 0.3 + 0.004; cyl((0, 0, z), r, r - 0.001, 0.012, DARK, 28)
box(-0.05, 0.05, -0.186, -0.17, 0.25, 0.29, AMBER)
for sx in (-1, 1):
    sphere(sx * 0.2, 0, 0.3, 0.036, STEEL, 10, 6); rod((sx * 0.2, 0, 0.3), (sx * 0.265, -0.07, 0.15), 0.018, GREY, 8); sphere(sx * 0.265, -0.07, 0.15, 0.03, BRASS, 10, 6)
part("kb.body", smooth=0.5)
HEAD = 0.406  # the height of the neck joint the head turns on
prism(rrect(0.19, 0.14, 0.05), 0, 0.2, PAPER); box(-0.14, 0.14, -0.146, -0.14, 0.05, 0.15, GLASS); rod((0, 0, 0.2), (0, 0, 0.29), 0.008, STEEL)
for k in range(5): box(-0.05 + 0.022 * k, -0.038 + 0.022 * k, -0.143, -0.14, 0.018, 0.034, DARK)
for sx in (-1, 1): cyl((0.19 if sx > 0 else -0.215, 0, 0.1), 0.045, 0.045, 0.025, BRASS, 14, 'x')
part("kb.head", (0, 0, HEAD), smooth=0.5)
box(-0.024, 0.024, -0.004, 0, -0.032, 0.032, AMBER)
eye = part("kb.eye.0", (-0.062, -0.147, HEAD + 0.1)); part("kb.eye.1", (0.062, -0.147, HEAD + 0.1), mesh=eye)
sphere(0, 0, 0, 0.024, AMBER, 10, 6)
part("kb.tip", (0, 0, HEAD + 0.305), smooth=0.5)
box(-0.013, 0.013, -0.008, 0.008, 0, 0.1, AMBER)
bar = None
for k in range(24): a = math.tau * k / 24; bar = part(f"kb.bar.{k}", (0.29 * math.cos(a), 0.29 * math.sin(a), 0.036), (0, 0, a + math.pi / 2), mesh=bar)
# tool one: a card drawer (what it looks things up in)
box(-0.1, 0.1, -0.12, 0.12, 0, 0.16, WOOD, True); box(-0.104, 0.104, -0.124, 0.124, 0.16, 0.17, WOOD); box(-0.085, 0.085, -0.122, -0.12, 0.02, 0.07, DARK)
part("kb.tool.0", (-0.6, -0.1, 0), (0, 0, 0.5))
box(-0.085, 0.085, -0.02, 0.18, 0, 0.055, WOOD, True); box(-0.085, 0.085, -0.03, -0.02, -0.005, 0.06, WOOD, True); cyl((0, -0.045, 0.028), 0.012, 0.012, 0.015, BRASS, 8, 'y'); box(-0.04, 0.04, -0.032, -0.03, 0.036, 0.052, PAPER)
for k in range(8): box(-0.07, 0.07, 0.0 + 0.02 * k, 0.003 + 0.02 * k, 0.055, 0.075 + 0.006 * (k % 3), PAPER)
part("kb.drawer", (-0.6, -0.1, 0.085), (0, 0, 0.5))
# tool two: a clock (what day it is)
box(-0.08, 0.08, -0.03, 0.03, 0, 0.03, DARK, True); cyl((0, -0.02, 0.15), 0.11, 0.11, 0.04, STEEL, 20, 'y'); cyl((0, -0.024, 0.15), 0.098, 0.098, 0.004, PAPER, 20, 'y'); box(-0.012, 0.012, -0.012, 0.012, 0.03, 0.05, DARK)
for k in range(12): a = math.tau * k / 12; box(0.084 * math.sin(a) - 0.003, 0.084 * math.sin(a) + 0.003, -0.0262, -0.024, 0.15 + 0.084 * math.cos(a) - 0.008, 0.15 + 0.084 * math.cos(a) + 0.008, DARK)
part("kb.tool.1", (0.0, 0.62, 0), (0, 0, math.pi), smooth=0.5)
box(-0.004, 0.004, -0.004, 0, -0.01, 0.075, DARK); cyl((0, -0.006, 0), 0.008, 0.008, 0.006, BRASS, 8, 'y')
part("kb.hand", (0.0, 0.6475, 0.15), (0, 0, math.pi))
# tool three: a magnifier on a stand (what it searches with)
box(-0.07, 0.07, -0.05, 0.05, 0, 0.025, DARK, True); rod((0, 0, 0.025), (0, 0, 0.16), 0.008, STEEL)
part("kb.tool.2", (0.6, -0.1, 0), (0, 0, -0.5))
for k in range(16): a0, a1 = math.tau * k / 16, math.tau * (k + 1) / 16; rod((0.085 * math.cos(a0), 0, 0.085 * math.sin(a0) + 0.1), (0.085 * math.cos(a1), 0, 0.085 * math.sin(a1) + 0.1), 0.009, BRASS, 6)
cyl((0, -0.003, 0.1), 0.08, 0.08, 0.006, GLASS, 16, 'y'); rod((0, 0, 0.015), (0, 0, -0.08), 0.011, WOOD)
part("kb.lens", (0.6, -0.1, 0.16), (0, 0, -0.5))
for k, (tx, ty) in enumerate([(-0.6, -0.1), (0.0, 0.62), (0.6, -0.1)]):
    d = math.hypot(tx, ty); ux, uy = tx / d, ty / d
    wire_pts = [(ux * 0.2, uy * 0.2, 0.05), (ux * 0.3, uy * 0.3, 0.012), (ux * (d - 0.14), uy * (d - 0.14), 0.012), (ux * (d - 0.09), uy * (d - 0.09), 0.03)]
    for q in range(3): rod(wire_pts[q], wire_pts[q + 1], 0.007, PAPER)
    part(f"kb.cable.{k}")

# ================= qb: the walk-forward bed =================
box(-1.02, 1.02, -0.26, 0.26, 0, 0.04, DARK, True); box(-0.98, 0.98, -0.235, -0.215, 0.04, 0.062, STEEL); box(-0.98, 0.98, 0.215, 0.235, 0.04, 0.062, STEEL)
for k in range(50): box(-0.94 + 0.0384 * k - 0.0015, -0.94 + 0.0384 * k + 0.0015, -0.2, -0.18 if k % 6 else -0.16, 0.04, 0.043, STEEL)
for x in (-0.99, 0.99): box(x - 0.02, x + 0.02, -0.25, 0.25, 0.04, 0.1, STEEL)
cyl((1.01, 0.0, 0.07), 0.05, 0.05, 0.02, STEEL, 14, 'x'); rod((1.03, 0.0, 0.07), (1.03, 0.04, 0.07), 0.006, STEEL); rod((1.03, 0.04, 0.07), (1.08, 0.04, 0.07), 0.008, WOOD)
part("qb.base", smooth=0.5)
box(-0.016, 0.016, -0.12, 0.12, 0, 1.0, GREY, True)
qbar = None
for k in range(48):
    hh = 0.1 + 0.42 * (k / 47) ** 0.85 + 0.07 * math.sin(k * 0.55) + 0.045 * math.sin(k * 1.37 + 1) - (0.12 if 26 <= k <= 31 else 0)
    qbar = part(f"qb.bar.{k}", (-0.9 + 0.0383 * k, 0.0, 0.04), mesh=qbar, scale=(1, 1, max(0.05, hh)))
for x in (-0.235, 0.235): box(x - 0.012, x + 0.012, -0.24, -0.21, 0.022, 0.8, BRASS); box(x - 0.012, x + 0.012, 0.21, 0.24, 0.022, 0.8, BRASS); box(x - 0.012, x + 0.012, -0.24, 0.24, 0.78, 0.8, BRASS)
box(-0.235, 0.235, -0.24, -0.225, 0.76, 0.8, BRASS); box(-0.235, 0.235, 0.225, 0.24, 0.76, 0.8, BRASS)
box(0.112, 0.118, -0.24, 0.24, 0.03, 0.8, AMBER)   # the line between training and testing
for (x, y) in [(-0.235, -0.225), (0.235, -0.225), (-0.235, 0.225), (0.235, 0.225)]: box(x - 0.03, x + 0.03, y - 0.022, y + 0.022, 0.0, 0.03, STEEL, True)
box(0.118, 0.235, -0.26, -0.24, 0.6, 0.66, AMBER)
part("qb.win", (-0.66, 0, 0.062))

# ================= la: the mail sorter =================
for (x, y) in [(-0.62, -0.2), (0.62, -0.2), (-0.62, 0.2), (0.62, 0.2)]: box(x - 0.015, x + 0.015, y - 0.015, y + 0.015, 0, 1.0, STEEL)
box(-0.64, 0.64, -0.215, 0.215, 0, 0.03, DARK, True); box(-0.64, 0.64, -0.215, -0.185, 0.96, 1.0, STEEL); box(-0.64, 0.64, 0.185, 0.215, 0.96, 1.0, STEEL)
for x in (-0.21, 0.21): box(x - 0.008, x + 0.008, -0.18, 0.18, 0.03, 0.3, STEEL)
for k, x in enumerate((-0.42, 0.0, 0.42)):
    m = AMBER if k == 2 else GREY
    box(x - 0.19, x + 0.19, -0.18, 0.18, 0.03, 0.045, m, True); box(x - 0.19, x + 0.19, -0.18, -0.17, 0.045, 0.22, m); box(x - 0.19, x + 0.19, 0.17, 0.18, 0.045, 0.22, m)
    box(x - 0.06, x + 0.06, -0.184, -0.18, 0.1, 0.16, PAPER)
part("la.frame")
cyl((0, 0, 0.76), 0.1, 0.34, 0.2, GREY, 20); cyl((0, 0, 0.955), 0.345, 0.345, 0.012, STEEL, 20); cyl((0, 0, 0.66), 0.1, 0.1, 0.1, GREY, 20)
for k in range(3): a = math.tau * k / 3 + 0.4; rod((0.3 * math.cos(a), 0.3 * math.sin(a), 0.9), (0.6 * (1 if math.cos(a) > 0 else -1), 0.2 * (1 if math.sin(a) > 0 else -1), 0.97), 0.008, STEEL)
part("la.hopper", smooth=0.5)
box(-0.16, 0.16, -0.14, 0.14, -0.006, 0.006, STEEL, True); cyl((0, -0.16, 0), 0.014, 0.014, 0.32, DARK, 8, 'y')
part("la.flipper", (0, 0, 0.52))
box(-0.075, 0.075, -0.05, 0.05, 0, 0.006, PAPER, True)
i = len(V); V.extend([(-0.075, 0.05, 0.0065), (0.075, 0.05, 0.0065), (0, -0.005, 0.0065)]); F.append((i, i + 2, i + 1)); M.append(GREY); box(0.035, 0.06, -0.04, -0.012, 0.006, 0.0068, AMBER)
env = None
for k in range(9): env = part(f"la.env.{k}", (0, 0, 1.1), mesh=env)

# ================= md: the split-flap board =================
box(-0.86, 0.86, 0.0, 0.14, 0.2, 1.06, DARK, True)
for (x0, x1, z0, z1) in [(-0.88, 0.88, 0.17, 0.2), (-0.88, 0.88, 1.06, 1.09), (-0.88, -0.86, 0.2, 1.06), (0.86, 0.88, 0.2, 1.06)]: box(x0, x1, -0.015, 0.15, z0, z1, STEEL, True)
for x in (-0.6, 0.6): box(x - 0.02, x + 0.02, 0.04, 0.1, 0.0, 0.2, STEEL); box(x - 0.14, x + 0.14, -0.08, 0.22, 0.0, 0.02, STEEL, True)
for r in range(3):
    for c in range(12):
        x = -0.737 + 0.134 * c; z = 0.26 + 0.27 * r
        box(x - 0.058, x + 0.058, -0.004, 0.0, z, z + 0.105, GLASS)                      # the lower half of the cell
        cyl((x - 0.062, -0.008, z + 0.11), 0.005, 0.005, 0.124, STEEL, 6, 'x')            # its spindle
part("md.board")
i = len(V); V.extend([(-0.058, -0.004, 0.003), (0.058, -0.004, 0.003), (0.058, -0.004, 0.105), (-0.058, -0.004, 0.105), (-0.058, 0.0, 0.003), (0.058, 0.0, 0.003), (0.058, 0.0, 0.105), (-0.058, 0.0, 0.105)])
for f, m in [((0, 1, 2, 3), PAPER), ((5, 4, 7, 6), AMBER), ((3, 2, 6, 7), DARK), ((0, 3, 7, 4), DARK), ((1, 5, 6, 2), DARK), ((0, 4, 5, 1), DARK)]: F.append(tuple(i + k for k in f)); M.append(m)
flap = None
for r in range(3):
    for c in range(12): flap = part(f"md.flap.{r}.{c}", (-0.737 + 0.134 * c, -0.006, 0.26 + 0.27 * r + 0.11), mesh=flap)

# ================= mg: the flash cards =================
box(-0.55, 0.55, -0.34, 0.34, 0, 0.04, WOOD, True)
for x in (-0.2, 0.2):
    box(x - 0.02, x + 0.02, -0.03, 0.03, 0.04, 0.1, STEEL)
    for k in range(14): a0, a1 = math.tau * k / 14, math.tau * (k + 1) / 14; rod((x, 0.11 * math.sin(a0), 0.2 + 0.11 * math.cos(a0)), (x, 0.11 * math.sin(a1), 0.2 + 0.11 * math.cos(a1)), 0.008, STEEL, 6)
# pencil, set square and compass on the base
rod((0.4, -0.25, 0.052), (0.48, 0.2, 0.052), 0.011, YELLOW, 6); rod((0.48, 0.2, 0.052), (0.487, 0.24, 0.052), 0.008, WOOD, 6)
i = len(V); V.extend([(-0.5, -0.3, 0.042), (-0.3, -0.3, 0.042), (-0.5, 0.05, 0.042), (-0.5, -0.3, 0.05), (-0.3, -0.3, 0.05), (-0.5, 0.05, 0.05)])
for f in [(3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]: F.append(tuple(i + k for k in f)); M.append(BLUE)
rod((-0.42, 0.14, 0.05), (-0.34, 0.3, 0.05), 0.006, STEEL); rod((-0.42, 0.14, 0.05), (-0.48, 0.3, 0.05), 0.006, STEEL); cyl((-0.42, 0.14, 0.042), 0.014, 0.014, 0.02, BRASS, 8)
part("mg.base", smooth=0.5)
box(-0.17, 0.17, -0.002, 0.002, 0.09, 0.48, PAPER, True)
for k in range(4): box(-0.13, 0.1 - 0.05 * (k % 2), -0.0035, -0.002, 0.4 - 0.06 * k, 0.408 - 0.06 * k, INK)
box(-0.17, 0.17, 0.002, 0.0035, 0.09, 0.16, AMBER); box(-0.1, 0.1, 0.002, 0.0035, 0.26, 0.3, INK)
card2 = None
for k in range(7): card2 = part(f"mg.card.{k}", (0, 0, 0.2), (math.radians(108 + 2.2 * k), 0, 0), mesh=card2)
for k in range(7, 12): card2 = part(f"mg.card.{k}", (0, 0, 0.2), (math.radians(-108 - 2.2 * (k - 7)), 0, 0), mesh=card2)
part("mg.flip.0", (0, 0, 0.2), (math.radians(106), 0, 0), mesh=card2)

# ================= tools: the pegboard wall =================
# A dark shadow board. Each tool is a part the page moves: the wrench turns a bolt, the caliper's jaw slides, the screwdriver spins, the pliers open,
# the hex key turns, the meter's needle sweeps and the iron's tip heats.
box(-0.95, 0.95, 0.0, 0.03, 0.08, 1.12, DARK, True)
for (x0, x1, z0, z1) in [(-0.98, 0.98, 0.05, 0.08), (-0.98, 0.98, 1.12, 1.15), (-0.98, -0.95, 0.08, 1.12), (0.95, 0.98, 0.08, 1.12)]: box(x0, x1, -0.012, 0.04, z0, z1, WOOD, True)
for ix in range(30):
    for iz in range(16): x = -0.9 + 0.062 * ix; z = 0.12 + 0.064 * iz; quad((x - 0.007, -0.0006, z - 0.007), (x + 0.007, -0.0006, z - 0.007), (x + 0.007, -0.0006, z + 0.007), (x - 0.007, -0.0006, z + 0.007), GREY)
for x in (-0.6, 0.6): box(x - 0.03, x + 0.03, 0.03, 0.34, 0.0, 0.03, STEEL, True); rod((x, 0.31, 0.03), (x, 0.035, 0.7), 0.012, STEEL)
cyl((-0.77, -0.03, 0.87), 0.03, 0.03, 0.03, BRASS, 6, 'y')  # the bolt the wrench turns
part("tools.board")
T = 0.014
# 0 wrench: drawn with its open jaw at the origin, so it turns about the bolt
box(-0.022, 0.022, -0.51, -0.07, 0, T, STEEL, True); prism([(-0.06, -0.07), (0.06, -0.07), (0.072, 0.03), (0.034, 0.03), (0.03, -0.025), (-0.03, -0.025), (-0.034, 0.03), (-0.072, 0.03)], 0, T, STEEL)
prism(ngon(0, -0.555, 0.052, 12), 0, T, STEEL); prism(ngon(0, -0.555, 0.028, 6), T, T + 0.001, DARK)
part("tools.t.0", (-0.77, -0.012, 0.87), flat(0.08))
# 1 calipers: the beam with its fixed jaw, and the sliding jaw as its own part
box(-0.013, 0.013, -0.3, 0.3, 0, 0.01, STEEL, True)
for k in range(24): box(-0.013, -0.003 if k % 4 else 0.004, -0.27 + 0.022 * k, -0.268 + 0.022 * k, 0.01, 0.0108, DARK)
box(-0.11, 0.013, 0.27, 0.3, 0, 0.01, STEEL, True); prism([(-0.11, 0.27), (-0.085, 0.27), (-0.1, 0.2)], 0, 0.01, STEEL)
part("tools.t.1", (-0.52, -0.012, 0.6), flat(0.0))
box(-0.11, 0.035, 0.06, 0.1, 0, 0.014, GREY, True); prism([(-0.11, 0.1), (-0.1, 0.17), (-0.085, 0.1)], 0, 0.01, GREY); cyl((0.03, 0.045, 0.004), 0.014, 0.014, 0.01, BRASS, 10)
part("tools.jaw", (-0.52, -0.012, 0.6), flat(0.0))
# 2 screwdriver: drawn about its own long axis, so it can spin
box(-0.034, 0.034, -0.3, -0.07, -0.015, 0.015, AMBER, True)
for k in range(5): box(-0.036, 0.036, -0.28 + 0.045 * k, -0.27 + 0.045 * k, -0.0155, 0.0155, DARK, True)
box(-0.02, 0.02, -0.07, -0.04, -0.011, 0.011, STEEL, True); box(-0.008, 0.008, -0.04, 0.26, -0.005, 0.005, STEEL, True); prism([(-0.008, 0.26), (0.008, 0.26), (0.013, 0.3), (-0.013, 0.3)], -0.002, 0.002, STEEL)
part("tools.t.2", (-0.3, -0.03, 0.6), flat(-0.05))
# 3 pliers: two halves on one pivot at the origin
prism([(-0.05, -0.33), (-0.02, -0.33), (0.012, -0.01), (-0.014, -0.01)], 0, T, BLUE); prism([(0.0, -0.01), (0.03, -0.01), (0.02, 0.15), (0.004, 0.17)], 0, T, STEEL); cyl((0, 0, T), 0.016, 0.016, T + 0.006, DARK, 10)
part("tools.pl.0", (-0.08, -0.012, 0.63), flat(0.06))
prism([(0.02, -0.33), (0.05, -0.33), (0.014, -0.01), (-0.012, -0.01)], T, 2 * T, BLUE); prism([(-0.03, -0.01), (0.0, -0.01), (-0.004, 0.17), (-0.02, 0.15)], T, 2 * T, STEEL)
part("tools.pl.1", (-0.08, -0.012, 0.63), flat(0.06))
# 4 steel rule
box(-0.022, 0.022, -0.34, 0.34, 0, 0.004, STEEL, True)
for k in range(33): box(-0.022, -0.008 if k % 4 else 0.0, -0.32 + 0.02 * k, -0.3185 + 0.02 * k, 0.004, 0.0046, DARK)
cyl((0, 0.31, 0.004), 0.007, 0.007, 0.001, DARK, 8)
part("tools.t.4", (0.12, -0.012, 0.6), flat(0.0))
# 5 hex key: drawn about its long leg, so it can turn
prism([(-0.01, -0.26), (0.01, -0.26), (0.01, 0.18), (0.13, 0.18), (0.13, 0.2), (-0.01, 0.2)], -0.009, 0.009, STEEL)
part("tools.t.5", (0.3, -0.021, 0.58), flat(-0.1))
# 6 multimeter: an analog face, with the needle as its own part
box(-0.1, 0.1, -0.17, 0.17, 0, 0.04, AMBER, True); box(-0.085, 0.085, -0.155, 0.155, 0.04, 0.046, DARK); box(-0.07, 0.07, 0.06, 0.14, 0.046, 0.049, PAPER)
for k in range(9): a = math.radians(-48 + 12 * k); box(0.058 * math.sin(a) - 0.0015, 0.058 * math.sin(a) + 0.0015, 0.072 + 0.058 * math.cos(a) - 0.004, 0.072 + 0.058 * math.cos(a) + 0.004, 0.049, 0.0496, DARK)
cyl((0, -0.05, 0.046), 0.045, 0.045, 0.012, GREY, 16); box(-0.004, 0.004, -0.05, -0.008, 0.058, 0.061, PAPER)
for k, m in enumerate((BRICK, DARK, BRICK)): cyl((-0.05 + 0.05 * k, -0.135, 0.046), 0.011, 0.011, 0.006, m, 8)
part("tools.t.6", (0.54, -0.012, 0.62), flat(0.0), smooth=0.5)
box(-0.0025, 0.0025, 0, 0.056, 0, 0.002, BRICK, True); cyl((0, 0, 0), 0.006, 0.006, 0.003, DARK, 8)
part("tools.needle", (0.54, -0.0625, 0.692), flat(0.0))
# 7 soldering iron, with the tip as its own part
box(-0.022, 0.022, -0.3, -0.06, 0, 0.034, BLUE, True); box(-0.026, 0.026, -0.07, -0.05, 0, 0.036, DARK, True); box(-0.014, 0.014, -0.05, 0.02, 0.006, 0.028, STEEL, True); box(-0.007, 0.007, 0.02, 0.24, 0.011, 0.023, STEEL, True)
rod((0, -0.3, 0.017), (0.03, -0.36, 0.017), 0.007, RUBBER)
part("tools.t.7", (0.79, -0.012, 0.6), flat(0.04))
prism([(-0.007, 0.24), (0.007, 0.24), (0.0, 0.3)], 0.013, 0.021, BRASS)
part("tools.tip", (0.79, -0.012, 0.6), flat(0.04))

# ================= tk: the telegraph key =================
box(-0.62, 0.62, -0.32, 0.32, 0, 0.06, WOOD, True); box(-0.62, 0.62, -0.32, 0.32, 0.06, 0.066, WOOD); box(-0.5, 0.36, -0.14, 0.14, 0.066, 0.078, BRASS, True)
for y in (-0.08, 0.08): box(0.03, 0.09, y - 0.012, y + 0.012, 0.078, 0.2, BRASS, True)
cyl((0.06, -0.1, 0.18), 0.008, 0.008, 0.2, STEEL, 8, 'y')
cyl((-0.34, 0, 0.078), 0.022, 0.018, 0.03, BRASS, 10); cyl((-0.34, 0, 0.108), 0.008, 0.008, 0.008, STEEL, 8)        # the anvil the lever strikes
for (x, y) in [(0.5, -0.2), (0.5, 0.2)]: cyl((x, y, 0.066), 0.03, 0.03, 0.012, BRASS, 12); cyl((x, y, 0.078), 0.012, 0.012, 0.05, BRASS, 8); cyl((x, y, 0.1), 0.026, 0.026, 0.018, BRASS, 12)
rod((0.5, -0.2, 0.09), (0.36, -0.12, 0.085), 0.006, AMBER); rod((0.5, 0.2, 0.09), (0.58, 0.3, 0.075), 0.006, RUBBER); rod((0.58, 0.3, 0.075), (0.64, 0.4, 0.02), 0.006, RUBBER)
for (x, y) in [(-0.58, -0.28), (0.58, -0.28), (-0.58, 0.28), (0.58, 0.28)]: cyl((x, y, 0.066), 0.014, 0.014, 0.008, BRASS, 6)
# the sounder at the back: two coils, and the armature they pull
for y in (-0.05, 0.05): cyl((0.26, y + 0.2, 0.066), 0.045, 0.045, 0.13, BRICK, 14); cyl((0.26, y + 0.2, 0.196), 0.05, 0.05, 0.01, BRASS, 14); cyl((0.26, y + 0.2, 0.06), 0.05, 0.05, 0.01, BRASS, 14)
box(0.2, 0.32, 0.1, 0.3, 0.215, 0.228, STEEL, True)
part("tk.base", smooth=0.5)
box(-0.46, 0.26, -0.022, 0.022, -0.012, 0.012, BRASS, True); cyl((-0.4, 0, 0.012), 0.012, 0.012, 0.05, BRASS, 8); cyl((-0.4, 0, 0.062), 0.07, 0.07, 0.012, DARK, 18); cyl((-0.4, 0, 0.074), 0.05, 0.03, 0.03, DARK, 18)
cyl((-0.4, 0, -0.03), 0.008, 0.008, 0.018, STEEL, 8); cyl((0.2, 0, 0.012), 0.012, 0.012, 0.05, BRASS, 8); cyl((0.2, 0, 0.05), 0.024, 0.024, 0.014, BRASS, 12)
for k in range(5): cyl((0.2, 0, -0.07 + 0.011 * k), 0.016, 0.016, 0.004, STEEL, 10)
part("tk.lever", (0.06, 0, 0.18), smooth=0.5)
sphere(0, 0, 0, 0.014, AMBER, 8, 5)
part("tk.spark", (-0.34, 0, 0.122))

path = os.path.join("/Users/kiapousti/Documents/kpousti.github.io/blender", "scenes.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print(count, "total", sum(count.values()))
