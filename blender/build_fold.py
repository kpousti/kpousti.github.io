# Run with:  Blender -b --python blender/build_fold.py
# Builds the Experience chapter's model, "the pop-up plant", saves it as fold.blend, rounds its edges and bakes soft shadows (finish_turbine.py),
# and writes models/fold.bin (export_parts.py). One run does all of it.
#
# The model is the San Diego model's base plate, cut into 34 square tiles and 8 strips on a chassis. Every tile has two faces: the city on top
# (dark enamel with a few roof blocks, a brass rim) and the factory underneath (steel, belt, walnut, hazard stripes or a control panel).
# Each has two poses: lying in the plate, and standing or lying as its piece of an approval line:
#   a workbench where a job is stamped by hand (columns 0 and 1), a control cabinet behind the gap (column 2),
#   and a conveyor with two stamping gantries (columns 3 to 5). The tiles that are not needed turn over where they lie and become the shop floor.
# The page moves each tile between its two poses as one rigid body about one fixed axis, in stages. The press heads, hand stamps, ink pads,
# beacon and job cards have one pose: the page telescopes them out once the line is standing.
# Blender is Z-up: X runs along the line, +Y is the back of the plate, Z is up. Grid: column c at x = -1 + 0.4 c, row r at y = 1 - 0.4 r (row 0 at the back).
import bpy, math, os
from mathutils import Vector, Matrix

ROOT = "/Users/kiapousti/Documents/kpousti.github.io"
T = 0.034                      # a tile's thickness
ZT = -0.003                    # a tile's middle when it lies in the plate: its top is then level with the city plate's top (0.014)
FLOOR = ZT - T / 2 - 0.0055    # the chassis top the tiles lie on (their inlays stand up to 0.005 proud)
STAND = FLOOR + 0.196          # the middle of a tile standing on the chassis
LID = FLOOR + 0.392 + T / 2    # the middle of a tile lying on top of standing ones (conveyor bed, bench top, cabinet top)
POST = FLOOR + 0.392 + 0.196   # the middle of a strip standing on top of a standing tile
BEAM = FLOOR + 0.784 + T / 2   # the middle of a strip lying across two posts
bpy.ops.wm.read_homefile(use_empty=True)
sc = bpy.context.scene

def lin(h): return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in [((h >> s) & 255) / 255 for s in (16, 8, 0)])
M = {}
def mat(name, rgb, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*lin(rgb), 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough; M[name] = m
for a in [("enamel", 0x12151d, 0.55, 0.42), ("roof", 0x27304a, 0.55, 0.42), ("brass", 0xd9ab4e, 0.92, 0.26), ("steel", 0x5d6778, 0.9, 0.34), ("plate", 0x8d98ab, 0.9, 0.4), ("rubber", 0x14161b, 0.0, 0.8),
          ("slat", 0x4a5263, 0.5, 0.5), ("walnut", 0x6b4630, 0.0, 0.5), ("walnut2", 0x4d3120, 0.0, 0.55), ("yellow", 0xe2b23c, 0.1, 0.5), ("black", 0x101216, 0.2, 0.6), ("glass", 0x0e1524, 0.6, 0.2),
          ("amber", 0xf2b56b, 0.1, 0.5), ("paper", 0xe9edf5, 0.0, 0.8), ("ink", 0x25407a, 0.0, 0.8), ("dark", 0x12151d, 0.6, 0.5), ("deck", 0x2b3242, 0.7, 0.45)]: mat(*a)

def g_box(s, m):
    x, y, z = s[0] / 2, s[1] / 2, s[2] / 2
    return [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], [m] * 6
def g_lathe(prof, m, seg=20):
    rs = [[(r * math.cos(math.tau * k / seg), r * math.sin(math.tau * k / seg), z) for k in range(seg)] for (r, z) in prof]
    n = seg; v = [p for r in rs for p in r]; f = []
    for i in range(len(rs) - 1):
        for k in range(n): f.append((i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k))
    f.append(tuple(range(n - 1, -1, -1))); f.append(tuple((len(rs) - 1) * n + k for k in range(n)))
    return v, f, [m] * len(f)
def at(g, loc=(0, 0, 0)): return [(p[0] + loc[0], p[1] + loc[1], p[2] + loc[2]) for p in g[0]], g[1], g[2]
def build(name, geos, smooth=False):
    """several pieces as one mesh, which is one part on the page; the first piece's material sets how shiny the part is"""
    v, f, names = [], [], []
    for (gv, gf, gm) in geos: b = len(v); v.extend(gv); f.extend(tuple(b + i for i in q) for q in gf); names.extend(gm)
    order = list(dict.fromkeys(names)); me = bpy.data.meshes.new(name); me.from_pydata(v, [], f)
    for m in order: me.materials.append(M[m])
    me.polygons.foreach_set("material_index", [order.index(m) for m in names]); me.polygons.foreach_set("use_smooth", [smooth] * len(f)); me.update(); return me
def frame(loc, x, y):
    """a pose from where its middle is and where its own x and y point; its own z (the city face) follows"""
    x = Vector(x); y = Vector(y); z = x.cross(y); m = Matrix((x, y, z)).transposed().to_4x4(); m.translation = Vector(loc); return m
PARTS = []   # (object, its pose in the plate, its pose in the line or None). Not called objs: the two scripts run at the end use that name
def put(name, me, plate, line=None):
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o["keep"] = 1; PARTS.append((o, plate, line)); return o

# ---------- the tiles: one body, five undersides ----------
def body(w, h):   # brass core with a rim showing, the city face on top with a few roofs standing a hair proud
    g = [g_box((w - 0.003, h - 0.003, T - 0.008), "enamel"), at(g_box((w, h, 0.012), "brass"), (0, 0, 0)), at(g_box((w - 0.014, h - 0.014, 0.004), "enamel"), (0, 0, T / 2 - 0.002))]
    for (x, y, sx, sy) in [(-0.1, 0.09, 0.11, 0.1), (0.07, 0.1, 0.13, 0.08), (-0.11, -0.07, 0.08, 0.13), (0.03, -0.05, 0.07, 0.07), (0.12, -0.1, 0.07, 0.1)]:
        if abs(x) + sx / 2 < w / 2 - 0.012: g.append(at(g_box((sx, sy, 0.003), "roof"), (x, y, T / 2 + 0.0015)))
    return g
def under(w, h, m): return at(g_box((w - 0.014, h - 0.014, 0.004), m), (0, 0, -T / 2 + 0.002))
ZU = -T / 2 - 0.0015   # where an inlay on the underside sits
W = 0.392
steel = body(W, W) + [under(W, W, "steel")] + [at(g_box(s, "plate"), p) for (s, p) in [((0.3, 0.02, 0.003), (0, 0.14, ZU)), ((0.3, 0.02, 0.003), (0, -0.14, ZU)), ((0.02, 0.26, 0.003), (0.14, 0, ZU)), ((0.02, 0.26, 0.003), (-0.14, 0, ZU))]] \
    + [at(g_lathe([(0.005, -0.0045), (0.009, -0.003), (0.009, 0)], "brass", 10), (sx * 0.14, sy * 0.14, -T / 2)) for sx in (-1, 1) for sy in (-1, 1)]
belt = body(W, W) + [under(W, W, "rubber")] + [at(g_box((0.018, 0.34, 0.003), "slat"), (x, 0, ZU)) for x in (-0.15, -0.075, 0, 0.075, 0.15)]
wood = body(W, W) + [under(W, W, "walnut")] + [at(g_box((0.36, 0.004, 0.002), "walnut2"), (0, y, ZU + 0.0005)) for y in (-0.09, 0.0, 0.09)]
haz = body(W, W) + [under(W, W, "steel")] + [at(g_box((0.052, 0.05, 0.003), "yellow" if k % 2 == 0 else "black"), (-0.156 + 0.052 * k, -0.14, ZU)) for k in range(7)] \
    + [at(g_box((0.3, 0.012, 0.003), "plate"), (0, 0.08, ZU)), at(g_box((0.3, 0.012, 0.003), "plate"), (0, 0.02, ZU))]
panel = body(W, W) + [under(W, W, "steel"), at(g_box((0.24, 0.15, 0.003), "glass"), (0, 0.07, ZU)), at(g_box((0.2, 0.006, 0.0015), "amber"), (0, 0.085, ZU - 0.002)), at(g_box((0.12, 0.006, 0.0015), "amber"), (-0.04, 0.05, ZU - 0.002))] \
    + [at(g_lathe([(0.011, -0.005), (0.016, -0.003), (0.016, 0)], c, 14), (x, -0.08, -T / 2)) for (x, c) in [(-0.08, "amber"), (0, "yellow"), (0.08, "brass")]]
SW = 0.092
strip = body(SW, W) + [under(SW, W, "steel"), at(g_box((0.05, 0.05, 0.003), "yellow"), (0, 0.15, ZU)), at(g_box((0.05, 0.05, 0.003), "black"), (0, 0.1, ZU)), at(g_box((0.03, 0.2, 0.003), "plate"), (0, -0.06, ZU))]
MESH = {k: build("tile-" + k, g) for k, g in [("steel", steel), ("belt", belt), ("wood", wood), ("haz", haz), ("panel", panel)]}
MESH["strip"] = build("strip", strip)

def X(c): return -1.0 + 0.4 * c
def Y(r): return 1.0 - 0.4 * r
def flat(x, y, z=ZT): return frame((x, y, z), (1, 0, 0), (0, 1, 0))                      # city face up
def over(x, y, z, about="x"): return frame((x, y, z), (1, 0, 0), (0, -1, 0)) if about == "x" else frame((x, y, z), (-1, 0, 0), (0, 1, 0))   # turned over: factory face up
def back(x, y, z=STAND): return frame((x, y, z), (1, 0, 0), (0, 0, 1))                    # standing, hinged up about its front edge: factory face to the back
def front(x, y, z=STAND): return frame((x, y, z), (1, 0, 0), (0, 0, -1))                  # standing, hinged up about its back edge: factory face to the front
def left(x, y, z=STAND): return frame((x, y, z), (0, 0, -1), (0, 1, 0))                   # standing, hinged up about its right edge: factory face to the left
def right(x, y, z=STAND): return frame((x, y, z), (0, 0, 1), (0, 1, 0))                   # standing, hinged up about its left edge: factory face to the right

# what each cell of the plate becomes: (mesh, pose in the line, group for the page's stages)
ROLE = {}
for c in (3, 4, 5):
    ROLE[(3, c)] = ("belt", over(X(c), -0.2, LID), "bed"); ROLE[(2, c)] = ("steel", back(X(c), 0.0), "skirt"); ROLE[(4, c)] = ("steel", front(X(c), -0.4), "skirt")
for c in (0, 1):
    ROLE[(3, c)] = ("wood", over(X(c), -0.2, LID), "top"); ROLE[(2, c)] = ("steel", back(X(c), 0.0), "bench"); ROLE[(4, c)] = ("steel", front(X(c), -0.4), "bench")
ROLE[(3, 2)] = ("steel", right(-0.4, -0.2), "bench")
ROLE[(0, 2)] = ("steel", back(-0.2, 0.8), "cab"); ROLE[(2, 2)] = ("panel", front(-0.2, 0.4), "cab"); ROLE[(1, 1)] = ("steel", left(-0.4, 0.6), "cab"); ROLE[(1, 3)] = ("steel", right(0.0, 0.6), "cab")
ROLE[(1, 2)] = ("haz", over(-0.2, 0.6, LID), "captop")
n_floor = 0
for r in range(6):
    for c in range(6):
        if (r, c) in ((0, 4), (0, 5)): continue          # these two cells are the strips
        kind, line, grp = ROLE.get((r, c), ("haz", None, "floor"))
        if line is None: line = over(X(c), Y(r), ZT, "x" if (r + c) % 2 else "y"); n_floor += 1
        put(f"fold.{grp}.{r}.{c}", MESH[kind], flat(X(c), Y(r)), line)
# the eight strips: two gantries of two posts and a beam, and two legs for the open end of the bench
GX = (X(3), X(5))
jobs = [frame((GX[0], 0.0, POST), (1, 0, 0), (0, 0, 1)), frame((GX[0], -0.4, POST), (-1, 0, 0), (0, 0, 1)), frame((GX[0], -0.2, BEAM), (-1, 0, 0), (0, 1, 0)), frame((-1.2, -0.08, STAND), (0, 1, 0), (0, 0, 1)),
        frame((-1.2, -0.32, STAND), (0, 1, 0), (0, 0, 1)), frame((GX[1], 0.0, POST), (1, 0, 0), (0, 0, 1)), frame((GX[1], -0.4, POST), (-1, 0, 0), (0, 0, 1)), frame((GX[1], -0.2, BEAM), (-1, 0, 0), (0, 1, 0))]
names = ["post.0", "post.1", "beam.0", "leg.0", "leg.1", "post.2", "post.3", "beam.1"]
for k in range(8):
    c = 4 + k // 4; put("fold." + names[k], MESH["strip"], flat(X(c) + (k % 4 - 1.5) * 0.1, Y(0)), jobs[k])

# ---------- the chassis the tiles lie on, and the small things that come out once the line stands ----------
ch = [at(g_box((2.4, 2.4, FLOOR + 0.11 - 0.004), "dark"), (0, 0, (FLOOR - 0.004 - 0.11) / 2)), at(g_box((2.37, 2.37, 0.004), "deck"), (0, 0, FLOOR - 0.002))]
for k in range(1, 6): ch += [at(g_box((2.37, 0.004, 0.001), "dark"), (0, -1.2 + 0.4 * k, FLOOR + 0.0005)), at(g_box((0.004, 2.37, 0.001), "dark"), (-1.2 + 0.4 * k, 0, FLOOR + 0.0005))]   # the lines the tiles lay along
put("fold.chassis", build("chassis", ch), Matrix.Identity(4))
LT = LID + T / 2   # the top of the bed, the bench and the cabinet
head = build("head", [g_lathe([(0.044, -0.294), (0.05, -0.29), (0.05, -0.268), (0.014, -0.265), (0.014, -0.182), (0.036, -0.18), (0.046, -0.17), (0.046, -0.006), (0.03, 0)], "steel", 20),
                      g_lathe([(0.049, -0.05), (0.049, -0.03)], "yellow", 20)], smooth=True)   # hangs from the beam: its own origin is where it is fixed, so it can telescope down from there
for k in (0, 1): put(f"fold.head.{k}", head, Matrix.Translation((GX[k], -0.2, BEAM - T / 2)))
stamp = build("stamp", [g_lathe([(0.04, 0), (0.04, 0.016), (0.03, 0.02)], "rubber", 18), g_lathe([(0.013, 0.02), (0.013, 0.085)], "walnut", 12),
                        g_lathe([(0.016, 0.085), (0.03, 0.095), (0.033, 0.115), (0.026, 0.135), (0.012, 0.142)], "walnut", 18)], smooth=True)
for k in (0, 1): put(f"fold.stamp.{k}", stamp, Matrix.Translation((X(k), -0.27, LT)))
pad = build("pad", [at(g_box((0.13, 0.085, 0.014), "black"), (0, 0, 0.007)), at(g_box((0.11, 0.065, 0.003), "ink"), (0, 0, 0.0155))])
for k in (0, 1): put(f"fold.pad.{k}", pad, Matrix.Translation((X(k), -0.09, LT)))
card = build("card", [at(g_box((0.15, 0.1, 0.003), "paper"), (0, 0, 0.0015)), at(g_box((0.09, 0.008, 0.001), "ink"), (-0.015, 0.02, 0.0035)), at(g_box((0.06, 0.008, 0.001), "ink"), (-0.03, 0.0, 0.0035))])
put("fold.card.0", card, Matrix.Translation((X(0), -0.27, LT)))
for k in range(1, 6): put(f"fold.card.{k}", card, Matrix.Translation((0.0, -0.2, LT)))
put("fold.beacon", build("beacon", [g_lathe([(0.026, 0), (0.026, 0.008), (0.011, 0.012), (0.011, 0.25), (0.02, 0.254)], "steel", 14), g_lathe([(0.028, 0.254), (0.028, 0.3), (0.02, 0.312)], "amber", 16)], smooth=True), Matrix.Translation((-0.2, 0.6, LT)))

# ---------- shadows are baked with every part on its own, far from the rest: lying in the plate, the factory faces would bake black ----------
for i, (o, plate, line) in enumerate(PARTS): o.matrix_world = Matrix.Translation((6.0 * i, 40.0, 0))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "fold.blend"))
here = os.path.join(ROOT, "blender")
exec(compile(open(os.path.join(here, "finish_turbine.py")).read(), "finish_turbine.py", "exec"))
for (o, plate, line) in PARTS:
    o.matrix_world = plate
    if line is not None: o["poses"] = [v for row in line for v in row]
bpy.context.view_layer.update()
tiles = sum(1 for (o, p, l) in PARTS if l is not None)
print("fold:", len(PARTS), "parts,", tiles, "with a second pose,", n_floor, "floor tiles")
assert tiles == 42 and len(PARTS) == 56, (tiles, len(PARTS))
bpy.ops.wm.save_mainfile()
exec(compile(open(os.path.join(here, "export_parts.py")).read(), "export_parts.py", "exec"))
