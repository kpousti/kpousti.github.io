# Run with:  Blender -b --python blender/build_galton.py
# Builds the page's opening model, a Galton board, saves it as galton.blend, rounds its edges and bakes soft shadows (finish_turbine.py),
# then adds the glass and writes models/galton.bin (export_parts.py). One run does all of it.
#
# The board: a walnut frame and plinth, an enamel back with the lattice of paths inlaid in brass, 13 rows of brass pegs (91), a brass hopper and gate,
# 14 bins between brass dividers, brass feet, and a glass front. The steel balls are not in this file: the page drops them, one real random bounce per row.
#
# The page turns this model into a street network, part for part, so the counts matter: exactly 100 parts that can round into a ball (the 91 pegs and 9 others),
# and at least one rod-like part for every street (the 182 inlaid lattice lines, 13 dividers and 3 frame rails). Rods are named blade.* or vane.* and are drawn
# as stacked rings of 12 points with their root at the origin. Peg and lattice names carry their row, which the page uses to light the pricing tree.
# Numbers the page's ball run relies on (keep them in step with the G* constants in index.html): DX, DY, Z0, bins from BIN_TOP down to FLOOR, the throat.
import bpy, math, os
from mathutils import Vector, Matrix

ROOT = "/Users/kiapousti/Documents/kpousti.github.io"
N, DX, DY, Z0, BIN_TOP, FLOOR, THROAT = 13, 0.094, 0.082, 0.52, -0.55, -0.93, 0.6
bpy.ops.wm.read_homefile(use_empty=True)
sc = bpy.context.scene; sc["ring"] = 12

def lin(h): return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in [((h >> s) & 255) / 255 for s in (16, 8, 0)])
M = {}
def mat(name, rgb, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*lin(rgb), 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough; M[name] = m
for a in [("brass", 0xd9ab4e, 0.92, 0.26), ("inlay", 0xc99a45, 0.9, 0.34), ("walnut", 0x5a3a25, 0.0, 0.55), ("walnut2", 0x6b4630, 0.0, 0.5), ("enamel", 0x10141c, 0.15, 0.5), ("glass", 0xd6e8ff, 0.0, 0.05)]: mat(*a)

count = {"ball": 0, "rod": 0}
def put(name, me, loc=(0, 0, 0), rot=None, scale=(1, 1, 1)):
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = loc; o.scale = scale
    if rot is not None: o.rotation_euler = rot.to_euler() if isinstance(rot, Matrix) else rot
    count["rod" if name.startswith(("blade", "vane")) else "ball"] += 1; return o
def g_rings(rs, m, caps=True):
    """one skin over a stack of rings: (verts, faces, material name per face)"""
    n = len(rs[0]); v = [tuple(p) for r in rs for p in r]; f = []
    for i in range(len(rs) - 1):
        for k in range(n): f.append((i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k))
    if caps: f.append(tuple(range(n - 1, -1, -1))); f.append(tuple((len(rs) - 1) * n + k for k in range(n)))
    return v, f, [m] * len(f)
def g_lathe(prof, m, seg=24): return g_rings([[(r * math.cos(math.tau * k / seg), r * math.sin(math.tau * k / seg), z) for k in range(seg)] for (r, z) in prof], m)
def g_box(s, m):
    x, y, z = s[0] / 2, s[1] / 2, s[2] / 2
    return [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], [m] * 6
def at(g, loc=(0, 0, 0), rot=None):
    T = Matrix.Translation(loc) @ (rot.to_4x4() if rot is not None else Matrix.Identity(4)); return [tuple(T @ Vector(p)) for p in g[0]], g[1], g[2]
def build(name, geos, smooth=True):
    """several pieces as one mesh, which is one part on the page; the first piece's material sets how shiny the part is"""
    v, f, names = [], [], []
    for (gv, gf, gm) in geos: b = len(v); v.extend(gv); f.extend(tuple(b + i for i in q) for q in gf); names.extend(gm)
    order = list(dict.fromkeys(names)); me = bpy.data.meshes.new(name); me.from_pydata(v, [], f)
    for m in order: me.materials.append(M[m])
    me.polygons.foreach_set("material_index", [order.index(m) for m in names]); me.polygons.foreach_set("use_smooth", [smooth] * len(f)); me.update(); return me
def r12(r): return [(r * math.cos(math.tau * k / 12), r * math.sin(math.tau * k / 12)) for k in range(12)]
def rect12(w, t): a, b = w / 2, t / 2; return [(-a, -b), (-a / 2, -b), (0, -b), (a / 2, -b), (a, -b), (a, 0), (a, b), (a / 2, b), (0, b), (-a / 2, b), (-a, b), (-a, 0)]
def cham12(w, d, c): a, b = w / 2, d / 2; return [(-a + c, -b), (0, -b), (a - c, -b), (a, -b + c), (a, 0), (a, b - c), (a - c, b), (0, b), (-a + c, b), (-a, b - c), (-a, 0), (-a, -b + c)]
def strip(name, secs, m, smooth=False): return build(name, [g_rings([[(x, y, z) for (x, y) in pts] for (z, pts) in secs], m)], smooth)
def frame(zdir, xdir):
    z = Vector(zdir).normalized(); x = Vector(xdir); x = (x - z * x.dot(z)).normalized(); return Matrix((x, z.cross(x), z)).transposed()
FRONT = Matrix.Rotation(math.pi / 2, 3, 'X')    # a part's own z pointing out of the board, toward the viewer
def peg_xz(r, i): return ((i - r / 2) * DX, Z0 - r * DY)
def bin_x(k): return (k - N / 2) * DX

# ---------- the back: enamel panel, bin floor, and a shallow engraved scale under the bins ----------
back = [at(g_box((1.336, 0.02, 2.02), "enamel"), (0, 0.01, 0.065)), at(g_box((1.316, 0.062, 0.022), "enamel"), (0, -0.03, FLOOR - 0.011))]
for k in range(N + 2): back.append(at(g_box((0.004, 0.003, 0.03 if k % 7 == 0 else 0.016), "enamel"), ((k - (N + 1) / 2) * DX, -0.0625, FLOOR - 0.03)))
put("disc.back", build("back", back, smooth=False))

# ---------- 13 rows of pegs, and the lattice of every path a ball can take, inlaid in brass on the back ----------
peg = build("peg", [g_lathe([(0.0085, 0), (0.0085, 0.033), (0.0115, 0.036), (0.0115, 0.045), (0.0095, 0.049), (0.005, 0.051)], "brass", 16)])
line = strip("line", [(0, rect12(0.0075, 0.0016)), (1, rect12(0.0075, 0.0016))], "inlay")
for r in range(N):
    for i in range(r + 1):
        x, z = peg_xz(r, i); put(f"can.peg.{r}.{i}", peg, (x, 0, z), FRONT)
        for s in (0, 1):   # left and right: to the next row's pegs, or from the last row down into the bins
            x2, z2 = peg_xz(r + 1, i + s) if r < N - 1 else (bin_x(i + s), BIN_TOP)
            d = Vector((x2 - x, 0, z2 - z)); put(f"blade.edge.{r}.{i}.{s}", line, (x, -0.0008, z), frame(d, (d.z, 0, -d.x)), (1, 1, d.length))

# ---------- bins, frame, plinth, crown and feet ----------
div = strip("div", [(0, rect12(0.008, 0.05)), (BIN_TOP - FLOOR - 0.012, rect12(0.008, 0.05)), (BIN_TOP - FLOOR, rect12(0.003, 0.05))], "brass")
for k in range(1, N + 1): put(f"vane.div.{k}", div, ((k - (N + 1) / 2) * DX, -0.03, FLOOR))
rail = strip("rail", [(0, cham12(0.07, 0.13, 0.012)), (1, cham12(0.07, 0.13, 0.012))], "walnut")
for sx in (-1, 1): put("vane.frame.side", rail, (sx * 0.693, -0.025, -1.0), None, (1, 1, 2.1))
put("vane.frame.top", rail, (-0.728, -0.025, 1.065), Matrix.Rotation(math.pi / 2, 3, 'Y'), (1, 1, 1.456))
put("core.base", build("base", [at(g_box((1.62, 0.26, 0.08), "walnut"), (0, -0.025, -1.045)), at(g_box((1.5, 0.2, 0.03), "walnut2"), (0, -0.025, -0.99)), at(g_box((0.36, 0.006, 0.04), "walnut2"), (0, -0.157, -1.045))], smooth=False))
put("core.crown", build("crown", [at(g_box((1.54, 0.18, 0.036), "walnut"), (0, -0.025, 1.118)), at(g_box((1.42, 0.15, 0.02), "walnut2"), (0, -0.025, 1.146))], smooth=False))
foot = build("foot", [g_lathe([(0.05, 0), (0.062, 0.012), (0.062, 0.03), (0.042, 0.04)], "brass", 28)])
for sx in (-1, 1): put("bolt.foot", foot, (sx * 0.64, -0.025, -1.125))

# ---------- the hopper: two brass walls down to the throat, and the gate that lets the balls out ----------
hi = Vector((0.658, 0, THROAT + (0.658 - 0.02) * math.tan(math.radians(35))))
for sx in (-1, 1):
    a = Vector((sx * 0.02, 0, THROAT)); b = Vector((sx * hi.x, 0, hi.z)); d = b - a
    wall = build("hop", [g_box((0.009, 0.05, d.length), "brass"), at(g_box((0.02, 0.05, 0.012), "brass"), (0.006, 0, -d.length / 2 + 0.006))], smooth=False)
    put("nozzle.hop", wall, (a + b) / 2 + Vector((0, -0.03, 0)), frame(d, (d.z, 0, -d.x)))
put("nozzle.gate", build("gate", [at(g_box((0.11, 0.022, 0.01), "brass"), (0.062, 0, 0)), at(g_lathe([(0.012, 0), (0.016, 0.006), (0.016, 0.02), (0.01, 0.026)], "brass", 16), (0.11, -0.011, 0), FRONT)], smooth=True), (0, -0.03, THROAT - 0.018))

assert count["ball"] == 99, count   # the glass makes 100
path = os.path.join(ROOT, "blender", "galton.blend"); bpy.ops.wm.save_as_mainfile(filepath=path)
here = os.path.join(ROOT, "blender")
exec(compile(open(os.path.join(here, "finish_turbine.py")).read(), "finish_turbine.py", "exec"))   # rounded edges and baked shadows, worked out before the glass is in the way

put("case.glass", build("glass", [g_box((1.316, 0.005, 2.0), "glass")], smooth=False), (0, -0.0605, 0.055))
print("galton:", count); assert count["ball"] == 100 and count["rod"] >= 185, count
bpy.ops.wm.save_mainfile()
exec(compile(open(os.path.join(here, "export_parts.py")).read(), "export_parts.py", "exec"))
