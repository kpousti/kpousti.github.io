# Run inside Blender: builds the models for the page's scenes into an empty file and saves it as scenes.blend.
# Every object is one part, named <model>.<part>[.more]. The site flies each model's parts together as its scene arrives, and moves named parts.
#   line   Experience: an approval line. By hand on the left (two hand stamps, one job), automated on the right (conveyor, two stamping gantries)
#   rec    Industrial AI Notebook: a strip-chart recorder wired to a vibration sensor on a bearing; the pen draws the live signal
#   gears  TheAlgorithms/C++ (Tarjan): gear trains on a plate; each strongly connected component is one train that turns together
#   surf   Surf Alert: a weather buoy and a surfboard on a rolling swell
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
def part(name, loc=(0, 0, 0), rot=(0, 0, 0), smooth=0.0, mesh=None):
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

path = os.path.join("/Users/kiapousti/Documents/kpousti.github.io/blender", "scenes.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print(count, "total", sum(count.values()))
