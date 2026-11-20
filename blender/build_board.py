# Run with:  Blender -b --python blender/build_board.py
# Then:      Blender -b blender/board.blend --python blender/finish_turbine.py --python blender/export_parts.py   (rounds edges, bakes soft shadows, writes models/board.bin)
#
# The page's opening model: an electric skateboard lying deck-down on the bench, so everything that was built is on show: trucks and wheels, the belt drive and its motor,
# the battery (60 cells under a ribbed lid, with their nickel strips, balance leads and BMS), the finned speed controller and its wiring.
#
# The page turns this model into a street network, part for part, so the counts matter: exactly 100 parts that can round into a ball (one per street corner), and at
# least as many rod-like parts as the street graph has edges. Rods are named blade.* or vane.* (cells, wheel spokes, belt links, cooling fins, wire runs); they are drawn
# as stacked rings of 12 points with their root at the origin, which is what lets the page straighten them into rods.
# Names also say how a part leaves in the exploded view: disc = the deck, can = on an axle, nozzle = truck and motor, bolt, case, core = electronics.
import bpy, math, os
from mathutils import Vector, Matrix

ROOT = "/Users/kiapousti/Documents/kpousti.github.io"
bpy.ops.wm.read_homefile(use_empty=True)
sc = bpy.context.scene; sc["ring"] = 12
rotor = bpy.data.collections.new("rotor"); sc.collection.children.link(rotor)  # what turns: the wheels

def lin(h): return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in [((h >> s) & 255) / 255 for s in (16, 8, 0)])
M = {}
def mat(name, rgb, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*lin(rgb), 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough; M[name] = m
for a in [("steel", 0xb4bdcc, 0.9, 0.3), ("alu", 0x8d95a3, 0.85, 0.4), ("dark", 0x16181d, 0.5, 0.5), ("black", 0x0c0d10, 0.2, 0.6), ("rubber", 0x111214, 0.0, 0.85), ("grip", 0x0b0b0d, 0.0, 0.95),
          ("maple", 0xc49a66, 0.0, 0.5), ("art", 0x1b3358, 0.1, 0.35), ("amber", 0xf2b56b, 0.1, 0.4), ("ure", 0xe9a348, 0.0, 0.3), ("cell", 0x2f8f8a, 0.2, 0.35), ("white", 0xe8ebf0, 0.0, 0.6),
          ("nickel", 0xcfd3d8, 0.9, 0.35), ("pcb", 0x1f6b3f, 0.1, 0.5), ("red", 0xc8362b, 0.0, 0.5), ("blue", 0x2d62c4, 0.0, 0.5), ("yellow", 0xe2b23c, 0.0, 0.5), ("brass", 0xd9a54a, 0.9, 0.3)]: mat(*a)

count = {"ball": 0, "rod": 0}
def mesh(name, verts, faces, mats, fm=None, smooth=True):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for m in mats: me.materials.append(M[m])
    if fm: me.polygons.foreach_set("material_index", fm)
    me.polygons.foreach_set("use_smooth", [smooth] * len(me.polygons)); me.update(); return me
def put(name, me, loc=(0, 0, 0), rot=None, scale=(1, 1, 1), spin=False):
    o = bpy.data.objects.new(name, me); (rotor if spin else sc.collection).objects.link(o); o.location = loc; o.scale = scale
    if rot is not None: o.rotation_euler = rot.to_euler() if isinstance(rot, Matrix) else rot
    count["rod" if name.startswith(("blade", "vane")) else "ball"] += 1; return o
def rings(name, rs, mats, band=None, caps=True, smooth=True):
    """a skin over a stack of rings (lists of points, all the same length, counter-clockwise seen from where the stack is heading)"""
    n = len(rs[0]); v = [p for r in rs for p in r]; f = []; fm = []
    for i in range(len(rs) - 1):
        for k in range(n): f.append((i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k)); fm.append(band(i, k) if band else 0)
    if caps: f.append(tuple(range(n - 1, -1, -1))); fm.append(band(0, -1) if band else 0); f.append(tuple((len(rs) - 1) * n + k for k in range(n))); fm.append(band(len(rs) - 2, -1) if band else 0)
    return mesh(name, v, f, mats, fm, smooth)
def lathe(name, prof, mats, seg=28, band=None, caps=True):
    """a profile of (radius, height) turned round the part's own z axis"""
    return rings(name, [[(r * math.cos(math.tau * k / seg), r * math.sin(math.tau * k / seg), z) for k in range(seg)] for (r, z) in prof], mats, band, caps)
def box(name, s, m):
    x, y, z = s[0] / 2, s[1] / 2, s[2] / 2
    return mesh(name, [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], [m], smooth=False)
def hexnut(name, r, h, m): return lathe(name, [(r, 0), (r, h)], [m], 6)
def r12(r): return [(r * math.cos(math.tau * k / 12), r * math.sin(math.tau * k / 12)) for k in range(12)]
def rect12(w, t): a, b = w / 2, t / 2; return [(-a, -b), (-a / 2, -b), (0, -b), (a / 2, -b), (a, -b), (a, 0), (a, b), (a / 2, b), (0, b), (-a / 2, b), (-a, b), (-a, 0)]
def strip(name, secs, mats, band=None, smooth=True):
    """a rod-like part: 12-point sections stacked up its own z from the root"""
    return rings(name, [[(x, y, z) for (x, y) in pts] for (z, pts) in secs], mats, band, True, smooth)
ALONG_Y = (-math.pi / 2, 0, 0); ALONG_X = (0, math.pi / 2, 0)   # turn a part's own z to the board's width, or its length
def frame(zdir, xdir):
    """a turn that points a part's z along zdir and its x as near xdir as it can"""
    z = Vector(zdir).normalized(); x = Vector(xdir); x = (x - z * x.dot(z)).normalized(); y = z.cross(x)
    return Matrix((x, y, z)).transposed()

# ---------- the deck: seven-ply maple, grip tape underneath (it lies face down), a stained belly with one amber stripe ----------
def deck_ring(x):
    e = max(0.0, (abs(x) / 1.1 - 0.72) / 0.28); w = 0.3 * math.sqrt(max(0.03, 1 - (e * 0.98) ** 2)); zc = -0.1 * e * e; pts = []
    for j in range(8): u = 1 - 2 * j / 7; pts.append((x, w * u, zc + 0.036 - 0.012 * u * u))
    for j in range(8): u = -1 + 2 * j / 7; pts.append((x, w * u, zc - 0.012 * u * u))
    return pts
put("disc.deck", rings("deck", [deck_ring(-1.1 + 2.2 * i / 33) for i in range(34)], ["art", "amber", "maple", "grip"], lambda i, k: 2 if k in (-1, 7, 15) else 3 if k > 7 else 1 if k == 3 else 0))

# ---------- trucks and wheels ----------
AX = 0.17   # axle height above the bench
tire = lathe("tire", [(0.062, -0.058), (0.098, -0.06), (0.11, -0.045), (0.112, 0), (0.11, 0.045), (0.098, 0.06), (0.062, 0.058), (0.062, -0.058)], ["ure"], 36, caps=False)
hub = lathe("hub", [(0.03, -0.05), (0.03, 0.05)], ["black"], 24); bearing = lathe("bearing", [(0.024, -0.008), (0.024, 0.008)], ["steel", "dark"], 20, lambda i, k: 1 if k == -1 else 0)
spoke = strip("spoke", [(0, rect12(0.016, 0.085)), (0.034, rect12(0.012, 0.075))], ["black"], smooth=False)
riser = box("riser", (0.21, 0.17, 0.012), "black"); base = box("base", (0.19, 0.15, 0.022), "alu"); nut = hexnut("nut", 0.011, 0.012, "steel")
bush = lathe("bush", [(0.03, 0), (0.04, 0.008), (0.04, 0.042), (0.03, 0.05)], ["ure"], 24); bush2 = lathe("bush2", [(0.03, 0), (0.036, 0.006), (0.036, 0.024), (0.03, 0.03)], ["ure"], 24)
king = lathe("king", [(0.011, 0), (0.011, 0.2)], ["steel"], 12); kingnut = hexnut("kingnut", 0.02, 0.014, "steel"); axlenut = hexnut("axlenut", 0.017, 0.014, "steel")
hanger = lathe("hanger", [(0.014, -0.45), (0.016, -0.17), (0.03, -0.15), (0.045, -0.07), (0.05, 0), (0.045, 0.07), (0.03, 0.15), (0.016, 0.17), (0.014, 0.45)], ["alu"], 24)
for sx in (-1, 1):
    X = 0.66 * sx
    put("nozzle.riser", riser, (X, 0, 0.042)); put("nozzle.base", base, (X, 0, 0.059))
    for (dx, dy) in ((-0.07, -0.05), (0.07, -0.05), (-0.07, 0.05), (0.07, 0.05)): put("bolt.deck", nut, (X + dx, dy, 0.07))
    put("nozzle.bush", bush, (X, 0, 0.07)); put("nozzle.bush", bush2, (X, 0, 0.22)); put("nozzle.kingpin", king, (X, 0, 0.066)); put("bolt.king", kingnut, (X, 0, 0.252))
    put("nozzle.hanger", hanger, (X, 0, AX), ALONG_Y)
    for sy in (-1, 1):
        c = Vector((X, 0.37 * sy, AX))
        put("can.tire", tire, c, ALONG_Y, spin=True); put("can.hub", hub, c, ALONG_Y, spin=True)
        for d in (-0.045, 0.045): put("can.bearing", bearing, c + Vector((0, d, 0)), ALONG_Y, spin=True)
        for k in range(6): a = math.tau * k / 6; z = (math.cos(a), 0, math.sin(a)); put("vane.spoke", spoke, c + Vector(z) * 0.029, frame(z, (0, 1, 0)).to_4x4() @ Matrix.Rotation(math.pi / 2, 4, 'Z'), spin=True)
        put("bolt.axle", axlenut, c + Vector((0, sy * 0.066, 0)), ALONG_Y if sy > 0 else (math.pi / 2, 0, 0))

# ---------- the drive: motor on the rear hanger, a toothed belt to the wheel's pulley ----------
MX = -0.44
put("can.wpulley", lathe("wpulley", [(0.03, 0.255), (0.075, 0.255), (0.075, 0.29), (0.03, 0.29)], ["alu"], 40), (-0.66, 0, AX), ALONG_Y, spin=True)
put("nozzle.motor", lathe("motor", [(0.02, 0.03), (0.066, 0.035), (0.07, 0.05), (0.07, 0.09), (0.07, 0.11), (0.07, 0.2), (0.06, 0.215), (0.02, 0.215)], ["dark", "amber"], 36, lambda i, k: 1 if i == 3 else 0), (MX, 0, AX), ALONG_Y)
put("can.mpulley", lathe("mpulley", [(0.012, 0.25), (0.03, 0.25), (0.03, 0.295), (0.012, 0.295)], ["steel"], 24), (MX, 0, AX), ALONG_Y)
put("nozzle.mount", box("mount", (0.32, 0.012, 0.11), "alu"), (-0.55, 0.233, AX))
for k in range(4): a = math.tau * (k + 0.5) / 4; put("bolt.motor", hexnut("mbolt", 0.009, 0.008, "steel"), (MX + 0.046 * math.cos(a), 0.239, AX + 0.046 * math.sin(a)), ALONG_Y)
r1, r2, dd = 0.079, 0.034, 0.22; phi = math.acos((r1 - r2) / dd); path = []
for k in range(16): a = phi + (math.tau - 2 * phi) * k / 15; path.append(Vector((-0.66 + r1 * math.cos(a), 0.2725, AX + r1 * math.sin(a))))
for k in range(8): a = -phi + 2 * phi * k / 7; path.append(Vector((MX + r2 * math.cos(a), 0.2725, AX + r2 * math.sin(a))))
link = strip("link", [(0, rect12(0.03, 0.008)), (1, rect12(0.03, 0.008))], ["rubber"], smooth=False)
for k in range(len(path)):
    p, q = path[k], path[(k + 1) % len(path)]; put("vane.belt", link, p, frame(q - p, (0, 1, 0)), (1, 1, (q - p).length))

# ---------- the battery: 60 cells standing in a tray, nickel strips across their tops, a BMS, and a ribbed lid they show through ----------
put("case.floor", box("floor", (0.68, 0.30, 0.012), "dark"), (-0.02, 0, 0.042))
for y in (-0.144, 0.144): put("case.wall", box("wall", (0.68, 0.012, 0.17), "dark"), (-0.02, y, 0.133))
for x in (-0.354, 0.314): put("case.end", box("end", (0.012, 0.276, 0.17), "dark"), (x, 0, 0.133))
cell = strip("cell", [(0, r12(0.019)), (0.004, r12(0.0215)), (0.144, r12(0.0215)), (0.15, r12(0.0205)), (0.154, r12(0.013)), (0.157, r12(0.012))], ["cell", "white", "steel"], lambda i, k: 2 if (k == -1 and i > 0) or i == 4 else 1 if i in (2, 3) else 0)
cols = [-0.32 + 0.046 * (i + 0.5) for i in range(12)]
for x in cols:
    for j in range(5): put("blade.cell", cell, (x, -0.092 + 0.046 * j, 0.048))
    put("core.nickel", box("nickel", (0.02, 0.204, 0.004), "nickel"), (x, 0, 0.2075))
put("core.bms", box("bms", (0.05, 0.24, 0.006), "pcb"), (0.275, 0, 0.19))
for y in (-0.06, 0.05): put("core.chip", box("chip", (0.03, 0.05, 0.008), "black"), (0.275, y, 0.197))
put("core.conn", box("conn", (0.018, 0.1, 0.014), "white"), (0.262, -0.005, 0.2))
for y in (-0.135, 0.135): put("case.rail", box("rail", (0.68, 0.03, 0.012), "alu"), (-0.02, y, 0.224))
for k in range(5): put("case.rib", box("rib", (0.024, 0.24, 0.012), "alu"), (-0.348 + 0.656 * k / 4, 0, 0.224))
for (x, y) in ((-0.348, -0.135), (0.308, -0.135), (-0.348, 0.135), (0.308, 0.135)): put("bolt.lid", hexnut("lbolt", 0.009, 0.008, "steel"), (x, y, 0.23))

# ---------- the speed controller: a finned case, its capacitors, the battery plug, a power button and a charge port ----------
put("case.esc", box("esc", (0.17, 0.2, 0.05), "alu"), (0.47, 0, 0.061))
fin = strip("fin", [(0, rect12(0.19, 0.005)), (0.03, rect12(0.19, 0.004))], ["dark"], smooth=False)
for k in range(14): put("vane.fin", fin, (0.395 + 0.15 * k / 13, 0, 0.086), (0, 0, math.pi / 2))
for (x, y) in ((0.395, -0.09), (0.545, -0.09), (0.395, 0.09), (0.545, 0.09)): put("bolt.esc", hexnut("ebolt", 0.007, 0.006, "steel"), (x, y, 0.086))
for k in range(3): put("core.cap", lathe("cap", [(0.018, 0), (0.018, 0.052)], ["dark", "nickel"], 20, lambda i, k: 1 if k == -1 else 0), (0.41 + 0.045 * k, 0.135, 0.058), ALONG_X)
put("core.xt", box("xt", (0.03, 0.05, 0.03), "yellow"), (0.35, 0, 0.07))
put("core.button", lathe("button", [(0.02, 0), (0.02, 0.01), (0.014, 0.012), (0.014, 0.018)], ["amber", "black"], 24, lambda i, k: 1 if i > 0 or k == -1 else 0), (0.47, -0.2, 0.034))
put("core.port", lathe("port", [(0.016, 0), (0.016, 0.014), (0.009, 0.014)], ["steel", "black"], 20, lambda i, k: 1 if k == -1 else 0), (0.47, 0.2, 0.034))

# ---------- wiring: every run is a chain of straight pieces ----------
unit = {}
def wire(pts, r, m):
    if m not in unit: unit[m] = strip("wire." + m, [(0, r12(1)), (1, r12(1))], [m])
    for a, b in zip(pts, pts[1:]): a = Vector(a); b = Vector(b); put("vane.wire", unit[m], a, frame(b - a, (0, 0, 1) if abs((b - a).normalized().z) < 0.9 else (1, 0, 0)), (r, r, (b - a).length))
bullet = lathe("bullet", [(0.009, -0.02), (0.009, 0.02)], ["brass"], 14)
for k, m in enumerate(("amber", "blue", "black")):   # three phase wires from the controller round the battery to the motor
    y = -0.185 - 0.024 * k
    wire([(0.385, -0.05 + 0.05 * k, 0.065), (0.36, y, 0.05), (0.1, y, 0.05), (-0.2, y, 0.05), (-0.4, y, 0.05), (-0.46, -0.1 + 0.03 * k, 0.1), (MX + 0.03 * (k - 1), 0.03, AX - 0.01)], 0.008, m)
    put("core.bullet", bullet, (0.1, y, 0.05), ALONG_X); put("core.bullet", bullet, (-0.2, y, 0.05), ALONG_X)
for sy, m in ((-1, "red"), (1, "black")): wire([(0.314, 0.03 * sy, 0.1), (0.335, 0.02 * sy, 0.085), (0.35, 0.012 * sy, 0.075)], 0.009, m)   # battery leads into the plug
for i, x in enumerate(cols): wire([(x, 0.1, 0.21), (x, 0.126, 0.218), (0.245, 0.126 - 0.002 * i, 0.218), (0.262, 0.04 - 0.008 * i, 0.207)], 0.0032, "white" if i % 2 else "red")   # one balance lead per cell group, to the BMS
wire([(0.385, 0.08, 0.06), (0.34, 0.19, 0.05), (0.0, 0.19, 0.05), (-0.3, 0.19, 0.05), (-0.38, 0.17, 0.08), (-0.42, 0.1, 0.12)], 0.005, "dark")   # the motor's sensor cable

print("board:", count)
assert count["ball"] == 100, "the street network has 100 corners: the board needs exactly 100 ball parts"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "board.blend"))
