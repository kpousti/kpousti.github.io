# Run inside Blender: builds the kit for the "graphs" and "routes" scenes into an empty file and saves it as city.blend.
# The city is downtown San Diego: besides the generic kit there are the landmarks (kit.oap One America Plaza, kit.hyatt, kit.emerald Emerald Plaza,
# kit.harbor Harbor Club, kit.library Central Library, kit.petco Petco Park, kit.conv Convention Center, kit.midway USS Midway, kit.bridge Coronado Bridge,
# kit.caltower California Tower) and the bay (kit.bay, kit.boat, kit.palm). Shapes only, drawn from memory of the skyline: no logos or signs.
# Every kit piece is one mesh in a unit box (footprint -0.5..0.5, height 0..1); the site places and scales copies of them.
#   kit.t1-t3  towers          kit.m1-m3  mid-rise blocks      kit.l1-l4  low buildings      kit.park  a park block
#   kit.hub / kit.ferrule / kit.ring   the space-frame fittings of the network (node, strut end, cost collar)
#   kit.plate  the base plate, with rim, ruler ticks, scale bar and north arrow       kit.pin  the route marker
import bpy, math, os

bpy.ops.wm.read_homefile(use_empty=True)

def lin(h): return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in [((h >> s) & 255) / 255 for s in (16, 8, 0)])
def mat(name, rgb, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*lin(rgb), 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*lin(rgb), 1); return m

WALL, WALL2, ROOF, TRIM, GLASS, LIT, GREEN, LEAF, STEEL, BRASS, DARK, SAND, BRICK, WATER, WHITE, GIRDER, EMER, GREY = range(18)
MATS = [mat("wall", 0x33415f, 0.25, 0.6), mat("wall2", 0x46546f, 0.25, 0.6), mat("roof", 0x1b2130, 0.25, 0.6), mat("trim", 0x9aa8c2, 0.25, 0.6),
        mat("glass", 0x0e1524, 0.25, 0.6), mat("lit", 0xf2b56b, 0.25, 0.6), mat("green", 0x24443c, 0.25, 0.6), mat("leaf", 0x3d6f5d, 0.25, 0.6),
        mat("steel", 0xaab6cc, 0.9, 0.32), mat("brass", 0xf2b56b, 0.9, 0.3), mat("dark", 0x12151d, 0.6, 0.5),
        mat("sand", 0xb9a585, 0.25, 0.6), mat("brick", 0x7c4a39, 0.25, 0.6), mat("water", 0x10294a, 0.7, 0.22), mat("white", 0xe9edf5, 0.25, 0.6),
        mat("girder", 0x3f78c2, 0.25, 0.6), mat("emerald", 0x35c58d, 0.25, 0.6), mat("grey", 0x77839a, 0.25, 0.6)]

V, F, M = [], [], []
def box(x0, x1, y0, y1, z0, z1, m, bottom=False):
    i = len(V)
    V.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
    for f in [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)] + ([(3, 2, 1, 0)] if bottom else []):
        F.append(tuple(i + k for k in f)); M.append(m)
def cyl(cx, cy, r0, r1, z0, z1, m, seg=8, top=True, phase=0.0):
    """a cylinder or cone frustum standing on z0; r1 = 0 makes a point"""
    i = len(V)
    for k in range(seg):
        a = phase + math.tau * k / seg; V.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0))
    if r1 > 0:
        for k in range(seg):
            a = phase + math.tau * k / seg; V.append((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1))
        for k in range(seg): F.append((i + k, i + (k + 1) % seg, i + seg + (k + 1) % seg, i + seg + k)); M.append(m)
        if top: F.append(tuple(i + seg + k for k in range(seg))); M.append(m)
    else:
        V.append((cx, cy, z1))
        for k in range(seg): F.append((i + k, i + (k + 1) % seg, i + seg)); M.append(m)
def gable(x0, x1, y0, y1, z0, z1, m, wall):
    """a pitched roof with its ridge along x, and the two end triangles in the wall colour"""
    i = len(V); ym = (y0 + y1) / 2
    V.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, ym, z1), (x1, ym, z1)])
    for f, mm in [((0, 1, 5, 4), m), ((2, 3, 4, 5), m), ((3, 0, 4), wall), ((1, 2, 5), wall)]: F.append(tuple(i + k for k in f)); M.append(mm)
def shed(x0, x1, y0, y1, z0, z1, m, glass):
    """one tooth of a sawtooth roof: slopes up along +x to a vertical glazed face"""
    i = len(V)
    V.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x1, y0, z1), (x1, y1, z1)])
    for f, mm in [((0, 4, 5, 3), m), ((1, 2, 5, 4), glass), ((0, 1, 4), m), ((2, 3, 5), m)]: F.append(tuple(i + k for k in f)); M.append(mm)
def sphere(cx, cy, cz, r, m, seg=10, rings=6):
    i = len(V); V.append((cx, cy, cz - r))
    for j in range(1, rings):
        t = math.pi * j / rings
        for k in range(seg):
            a = math.tau * k / seg; V.append((cx + r * math.sin(t) * math.cos(a), cy + r * math.sin(t) * math.sin(a), cz - r * math.cos(t)))
    V.append((cx, cy, cz + r)); top = len(V) - 1
    for k in range(seg): F.append((i, i + 1 + (k + 1) % seg, i + 1 + k)); M.append(m)
    for j in range(rings - 2):
        for k in range(seg):
            a = i + 1 + j * seg + k; b = i + 1 + j * seg + (k + 1) % seg; F.append((a, b, b + seg, a + seg)); M.append(m)
    base = i + 1 + (rings - 2) * seg
    for k in range(seg): F.append((base + k, base + (k + 1) % seg, top)); M.append(m)

X = [0.0]
def finish(name, smooth=0.0):
    """make the mesh from what was drawn, park it in a row for looking at, and start the next one"""
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    for m in MATS: me.materials.append(m)
    me.polygons.foreach_set("material_index", M)
    # the export takes shininess from slot 0, so metal parts lead with a metal
    if M and M[0] in (STEEL, BRASS, DARK, WATER):
        lead = M[0]; order = [lead] + [k for k in range(len(MATS)) if k != lead]
        me.materials.clear()
        for k in order: me.materials.append(MATS[k])
        me.polygons.foreach_set("material_index", [order.index(k) for k in M])
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        try: me.set_sharp_from_angle(angle=smooth)
        except Exception as e: print(e)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = (X[0], 0, 0); X[0] += 1.6
    tris = sum(len(p) - 2 for p in F); V.clear(); F.clear(); M.clear(); return tris

def slabs(hw, hd, z0, z1, floors, over=0.02, t=0.008, m=TRIM):
    for k in range(floors + 1):
        z = z0 + (z1 - z0) * k / floors; box(-hw - over, hw + over, -hd - over, hd + over, z - t, z + t, m)
def piers(hw, hd, z0, z1, w=0.03, m=WALL):
    for sx in (-1, 1):
        for sy in (-1, 1): box(sx * hw - w, sx * hw + w, sy * hd - w, sy * hd + w, z0, z1, m)
def parapet(hw, hd, z, h=0.05, w=0.025, m=TRIM):
    box(-hw, hw, -hd, -hd + w, z, z + h, m); box(-hw, hw, hd - w, hd, z, z + h, m); box(-hw, -hw + w, -hd + w, hd - w, z, z + h, m); box(hw - w, hw, -hd + w, hd - w, z, z + h, m)

report = {}
# ---- towers ----
for hw, z0, z1, fl in [(0.48, 0.0, 0.52, 6), (0.36, 0.52, 0.82, 4), (0.22, 0.82, 0.94, 2)]:
    box(-hw, hw, -hw, hw, z0, z1, GLASS); slabs(hw, hw, z0, z1, fl); piers(hw, hw, z0, z1)
box(-0.015, 0.015, -0.015, 0.015, 0.94, 1.0, TRIM)
for (x, z) in [(-0.2, 0.2), (0.25, 0.36), (0.05, 0.62)]: box(x, x + 0.14, -0.486, -0.48, z, z + 0.05, LIT)
report["kit.t1"] = finish("kit.t1")

box(-0.5, 0.5, -0.5, 0.5, 0, 0.1, WALL); box(-0.46, 0.46, -0.3, 0.3, 0.1, 0.95, GLASS)
for k in range(8):
    x = -0.46 + 0.92 * k / 7
    box(x - 0.012, x + 0.012, 0.3, 0.36, 0.1, 0.95, TRIM); box(x - 0.012, x + 0.012, -0.36, -0.3, 0.1, 0.95, TRIM)
box(-0.48, 0.48, -0.32, 0.32, 0.95, 0.965, TRIM); box(-0.2, 0.2, -0.14, 0.14, 0.965, 1.0, ROOF)
for (x, z) in [(-0.3, 0.3), (0.1, 0.55), (0.22, 0.75)]: box(x, x + 0.1, -0.304, -0.3, z, z + 0.035, LIT)
report["kit.t2"] = finish("kit.t2")

cyl(0, 0, 0.5, 0.5, 0, 0.86, GLASS, 8, True, math.pi / 8)
for k in range(7): cyl(0, 0, 0.525, 0.525, 0.86 * k / 6 - 0.007 if k else 0.0, 0.86 * k / 6 + 0.007, TRIM, 8, True, math.pi / 8)
cyl(0, 0, 0.4, 0.4, 0.86, 0.91, WALL, 8, True, math.pi / 8); cyl(0, 0, 0.3, 0.3, 0.91, 0.935, TRIM, 8, True, math.pi / 8); cyl(0, 0, 0.1, 0, 0.935, 1.0, TRIM, 6)
report["kit.t3"] = finish("kit.t3")

# ---- mid-rise ----
box(-0.5, 0.5, -0.5, 0.5, 0, 0.84, WALL2)
for k in range(4): box(-0.504, 0.504, -0.504, 0.504, 0.1 + 0.19 * k, 0.2 + 0.19 * k, GLASS)
piers(0.5, 0.5, 0, 0.84, 0.035, WALL2); parapet(0.5, 0.5, 0.84)
box(-0.3, -0.1, -0.25, -0.05, 0.84, 0.93, ROOF); box(0.05, 0.3, 0.1, 0.3, 0.84, 0.91, ROOF); box(-0.1, 0.12, 0.3, 0.46, 0.84, 1.0, WALL2)
box(-0.2, -0.06, -0.508, -0.504, 0.3, 0.38, LIT)
report["kit.m1"] = finish("kit.m1")

for (x0, x1, y0, y1) in [(-0.5, -0.18, -0.5, 0.5), (0.18, 0.5, -0.5, 0.5), (-0.18, 0.18, 0.12, 0.5)]:
    box(x0, x1, y0, y1, 0, 0.78, WALL)
    for k in range(1, 4): box(x0 - 0.012, x1 + 0.012, y0 - 0.012, y1 + 0.012, 0.78 * k / 4 - 0.008, 0.78 * k / 4 + 0.008, TRIM)
    box(x0, x1, y0, y1, 0.78, 0.8, ROOF)
box(-0.18, 0.18, -0.5, 0.12, 0, 0.03, GREEN); box(-0.03, 0.03, -0.5, 0.12, 0.03, 0.036, TRIM)
for (x, y) in [(-0.41, 0.26), (-0.29, 0.26), (-0.41, 0.38), (-0.29, 0.38)]: box(x - 0.01, x + 0.01, y - 0.01, y + 0.01, 0.8, 0.86, TRIM)
cyl(-0.35, 0.32, 0.085, 0.085, 0.86, 0.97, TRIM, 8); cyl(-0.35, 0.32, 0.095, 0, 0.97, 1.0, ROOF, 8)
report["kit.m2"] = finish("kit.m2")

box(-0.5, 0.08, -0.5, 0.5, 0, 0.95, WALL); box(0.08, 0.5, -0.5, 0.5, 0, 0.52, WALL2)
for k in range(4): box(-0.504, 0.084, -0.504, 0.504, 0.12 + 0.2 * k, 0.24 + 0.2 * k, GLASS)
box(-0.5, 0.08, -0.5, 0.5, 0.95, 0.97, TRIM); box(-0.3, -0.1, -0.2, 0.1, 0.97, 1.0, ROOF)
box(0.12, 0.46, -0.46, 0.46, 0.52, 0.54, GREEN)
for y in (-0.3, 0.0, 0.3): box(0.14, 0.44, y - 0.008, y + 0.008, 0.62, 0.635, TRIM)
for (x, y) in [(0.14, -0.3), (0.44, -0.3), (0.14, 0.3), (0.44, 0.3)]: box(x - 0.008, x + 0.008, y - 0.008, y + 0.008, 0.54, 0.62, TRIM)
box(0.504, 0.508, -0.2, 0.0, 0.2, 0.3, LIT)
report["kit.m3"] = finish("kit.m3")

# ---- low buildings ----
box(-0.5, 0.5, -0.5, 0.5, 0, 0.62, WALL2); parapet(0.5, 0.5, 0.62, 0.07)
box(-0.42, 0.42, -0.508, -0.5, 0.05, 0.3, GLASS); box(-0.5, 0.5, -0.62, -0.5, 0.33, 0.37, LIT)
box(-0.3, -0.08, 0.05, 0.3, 0.62, 0.8, ROOF); box(0.1, 0.34, -0.3, -0.1, 0.62, 0.74, ROOF); box(-0.36, 0.36, -0.51, -0.5, 0.42, 0.54, TRIM)
report["kit.l1"] = finish("kit.l1")

box(-0.5, 0.5, -0.5, 0.5, 0, 0.5, WALL2); gable(-0.54, 0.54, -0.56, 0.56, 0.5, 0.94, ROOF, WALL2)
box(0.2, 0.32, 0.12, 0.26, 0.6, 1.0, TRIM); box(-0.12, 0.12, -0.506, -0.5, 0.0, 0.3, GLASS); box(-0.4, -0.22, -0.506, -0.5, 0.2, 0.36, LIT); box(0.22, 0.4, -0.506, -0.5, 0.2, 0.36, GLASS)
report["kit.l2"] = finish("kit.l2")

box(-0.5, 0.5, -0.5, 0.5, 0, 0.56, WALL)
for k in range(4): shed(-0.5 + 0.25 * k, -0.25 + 0.25 * k, -0.5, 0.5, 0.56, 0.96, ROOF, GLASS)
box(-0.5, 0.5, -0.506, -0.5, 0.3, 0.33, TRIM); box(-0.3, 0.3, -0.6, -0.5, 0.36, 0.385, TRIM)
for x in (-0.25, 0.0, 0.25): box(x - 0.09, x + 0.09, -0.506, -0.5, 0.02, 0.28, GLASS)
report["kit.l3"] = finish("kit.l3")

box(-0.5, 0.5, -0.5, 0.5, 0, 0.42, WALL2)
i = len(V); seg = 8
for k in range(seg + 1):
    a = math.pi * k / seg; y = -0.5 * math.cos(a); z = 0.42 + 0.56 * math.sin(a)
    V.extend([(-0.5, y, z), (0.5, y, z)])
for k in range(seg): F.append((i + 2 * k, i + 2 * k + 1, i + 2 * k + 3, i + 2 * k + 2)); M.append(ROOF)
F.append(tuple(i + 2 * k for k in range(seg + 1))); M.append(WALL2); F.append(tuple(i + 2 * k + 1 for k in range(seg, -1, -1))); M.append(WALL2)
for x in (-0.3, 0.0, 0.3): box(x - 0.012, x + 0.012, -0.52, 0.52, 0.42, 0.44, TRIM)
box(-0.14, 0.14, -0.506, -0.5, 0.0, 0.3, GLASS)
report["kit.l4"] = finish("kit.l4")

# ---- park: lawn, crossing paths, a fountain, trees ----
box(-0.5, 0.5, -0.5, 0.5, 0, 0.08, GREEN); box(-0.5, 0.5, -0.03, 0.03, 0.08, 0.1, TRIM); box(-0.03, 0.03, -0.5, 0.5, 0.08, 0.1, TRIM)
cyl(0, 0, 0.12, 0.12, 0.08, 0.2, TRIM, 10); cyl(0, 0, 0.095, 0.095, 0.2, 0.21, GLASS, 10); cyl(0, 0, 0.02, 0.02, 0.2, 0.36, TRIM, 6)
for (x, y, s) in [(-0.32, -0.3, 1.0), (-0.18, 0.3, 0.8), (0.3, -0.22, 0.9), (0.34, 0.3, 1.0), (-0.36, 0.08, 0.7), (0.14, -0.38, 0.75), (0.2, 0.16, 0.6)]:
    cyl(x, y, 0.012, 0.012, 0.08, 0.3, WALL, 5, False); cyl(x, y, 0.09 * s, 0, 0.26, 0.26 + 0.7 * s, LEAF, 7); cyl(x, y, 0.07 * s, 0, 0.5, 0.5 + 0.5 * s, LEAF, 7)
report["kit.park"] = finish("kit.park")

# ---- network fittings (radius 1 = the strut's radius, or the node's) ----
sphere(0, 0, 0, 1.0, STEEL, 10, 6)
for ax in range(3):
    for sgn in (-1, 1):
        i = len(V); seg = 6
        for (r, d) in [(0.44, 0.86), (0.44, 1.2)]:
            for k in range(seg):
                a = math.tau * k / seg; p = [r * math.cos(a), r * math.sin(a), d * sgn]
                if sgn < 0: p[0] = -p[0]
                V.append((p[0], p[1], p[2]) if ax == 2 else (p[2], p[0], p[1]) if ax == 0 else (p[1], p[2], p[0]))
        for k in range(seg): F.append((i + k, i + (k + 1) % seg, i + seg + (k + 1) % seg, i + seg + k)); M.append(STEEL)
        F.append(tuple(i + seg + k for k in range(seg))); M.append(STEEL)
report["kit.hub"] = finish("kit.hub", 0.6)

cyl(0, 0, 1.5, 1.5, 0, 0.55, STEEL, 6); cyl(0, 0, 1.2, 0.62, 0.55, 2.6, STEEL, 8, True)
report["kit.ferrule"] = finish("kit.ferrule", 0.5)
cyl(0, 0, 1.75, 1.75, -0.4, 0.4, BRASS, 10);
i = len(V)
for k in range(10): a = math.tau * k / 10; V.append((1.75 * math.cos(a), 1.75 * math.sin(a), -0.4))
F.append(tuple(i + k for k in range(9, -1, -1))); M.append(BRASS)
report["kit.ring"] = finish("kit.ring", 0.5)

# ---- the route marker: a map pin, point down at the origin ----
cyl(0, 0, 0.001, 0.3, 0, 1.15, BRASS, 10, False); sphere(0, 0, 1.5, 0.5, BRASS, 12, 8); cyl(0, 0, 0.55, 0.55, -0.02, 0.02, BRASS, 12)
report["kit.pin"] = finish("kit.pin", 0.7)

# ---- the base plate: top face at z = 0, streets sit on it. Rim, ruler ticks on two edges, a scale bar, a north arrow, corner bolts, feet ----
E = 1.2
box(-E, E, -E, E, -0.07, 0, DARK, True)
for (x0, x1, y0, y1) in [(-E, E, -E, -E + 0.02), (-E, E, E - 0.02, E), (-E, -E + 0.02, -E + 0.02, E - 0.02), (E - 0.02, E, -E + 0.02, E - 0.02)]: box(x0, x1, y0, y1, 0, 0.012, STEEL)
for k in range(21):
    t = -1 + 0.1 * k; L = 0.05 if k % 5 == 0 else 0.028
    box(t - 0.003, t + 0.003, -E + 0.03, -E + 0.03 + L, 0, 0.004, STEEL); box(-E + 0.03, -E + 0.03 + L, t - 0.003, t + 0.003, 0, 0.004, STEEL)
for k in range(5): box(0.5 + 0.1 * k, 0.6 + 0.1 * k, E - 0.075, E - 0.055, 0, 0.005, STEEL if k % 2 == 0 else BRASS)
i = len(V); V.extend([(E - 0.1, 0.72, 0.006), (E - 0.07, 0.6, 0.006), (E - 0.1, 0.63, 0.006), (E - 0.13, 0.6, 0.006)]); F.append((i, i + 3, i + 2)); M.append(BRASS); F.append((i, i + 2, i + 1)); M.append(STEEL)
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl(sx * (E - 0.07), sy * (E - 0.07), 0.022, 0.022, 0, 0.014, STEEL, 6); cyl(sx * (E - 0.16), sy * (E - 0.16), 0.07, 0.06, -0.11, -0.07, DARK, 10, False)
report["kit.plate"] = finish("kit.plate")


# ================= San Diego =================
def prism(pts, z0, z1, m, topm=None, slant=0.0, sdir=(1, 0)):
    """a polygon (counter-clockwise) pulled up from z0 to z1; slant tilts the top face along sdir"""
    i = len(V); n = len(pts)
    for (x, y) in pts: V.append((x, y, z0))
    for (x, y) in pts: V.append((x, y, z1 + slant * (x * sdir[0] + y * sdir[1])))
    for k in range(n): F.append((i + k, i + (k + 1) % n, i + n + (k + 1) % n, i + n + k)); M.append(m)
    F.append(tuple(i + n + k for k in range(n))); M.append(m if topm is None else topm)
def ngon(cx, cy, rx, ry, n, phase=0.0): return [(cx + rx * math.cos(phase + math.tau * k / n), cy + ry * math.sin(phase + math.tau * k / n)) for k in range(n)]
def pyramid(x0, x1, y0, y1, z0, z1, m, ax=None, ay=None):
    i = len(V); ax = (x0 + x1) / 2 if ax is None else ax; ay = (y0 + y1) / 2 if ay is None else ay
    V.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (ax, ay, z1)])
    for f in [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]: F.append(tuple(i + k for k in f)); M.append(m)

# One America Plaza: the tallest, a cross-shaped glass shaft under the pointed crown people call the screwdriver
box(-0.38, 0.38, -0.38, 0.38, 0, 0.76, WALL)
for (x0, x1, y0, y1) in [(-0.2, 0.2, 0.38, 0.5), (-0.2, 0.2, -0.5, -0.38), (0.38, 0.5, -0.2, 0.2), (-0.5, -0.38, -0.2, 0.2)]: box(x0, x1, y0, y1, 0, 0.7, GLASS)
for k in range(1, 12):
    z = 0.7 * k / 12
    box(-0.392, 0.392, -0.392, 0.392, z - 0.005, z + 0.005, TRIM); box(-0.21, 0.21, -0.51, 0.51, z - 0.005, z + 0.005, TRIM); box(-0.51, 0.51, -0.21, 0.21, z - 0.005, z + 0.005, TRIM)
piers(0.38, 0.38, 0, 0.76, 0.025, TRIM)
pyramid(-0.38, 0.38, -0.38, 0.38, 0.76, 0.97, GIRDER)
pyramid(-0.2, 0.2, 0.38, 0.5, 0.7, 0.9, GIRDER, 0, 0.38); pyramid(-0.2, 0.2, -0.5, -0.38, 0.7, 0.9, GIRDER, 0, -0.38); pyramid(0.38, 0.5, -0.2, 0.2, 0.7, 0.9, GIRDER, 0.38, 0); pyramid(-0.5, -0.38, -0.2, 0.2, 0.7, 0.9, GIRDER, -0.38, 0)
box(-0.39, 0.39, -0.39, 0.39, 0.755, 0.77, LIT); box(-0.008, 0.008, -0.008, 0.008, 0.96, 1.0, TRIM)
report["kit.oap"] = finish("kit.oap")

# Manchester Grand Hyatt: twin slabs with stepped tops on one podium
box(-0.5, 0.5, -0.5, 0.5, 0, 0.1, WALL2)
for (cx, top) in [(-0.25, 1.0), (0.25, 0.9)]:
    for (hw, hd, a, b) in [(0.2, 0.42, 0.1, 0.8), (0.16, 0.33, 0.8, 0.88), (0.11, 0.23, 0.88, 0.95), (0.06, 0.12, 0.95, 1.0)]:
        box(cx - hw, cx + hw, -hd, hd, a * top, b * top, WALL2); box(cx - hw - 0.01, cx + hw + 0.01, -hd - 0.01, hd + 0.01, b * top - 0.008, b * top, TRIM)
    for k in range(6): box(cx - 0.204, cx + 0.204, -0.424, 0.424, (0.14 + 0.105 * k) * top, (0.2 + 0.105 * k) * top, GLASS)
report["kit.hyatt"] = finish("kit.hyatt")

# Emerald Plaza: a cluster of hexagonal towers, each cut at a slant and lit green on top
for k, (cx, cy, hh) in enumerate([(0, 0, 0.94), (0.3, 0.1, 0.8), (-0.3, 0.12, 0.74), (0.15, -0.3, 0.84), (-0.17, -0.28, 0.66), (0.02, 0.32, 0.58), (-0.36, -0.1, 0.52), (0.38, -0.18, 0.6)]):
    d = (math.cos(k * 1.3), math.sin(k * 1.3))
    prism(ngon(cx, cy, 0.19, 0.19, 6, math.pi / 6), 0, hh, GLASS, EMER, 0.3, d)
    for j in range(1, 4): prism(ngon(cx, cy, 0.2, 0.2, 6, math.pi / 6), hh * j / 4 - 0.006, hh * j / 4 + 0.006, TRIM)
report["kit.emerald"] = finish("kit.emerald")

# Harbor Club: two oval towers side by side, ringed with balconies
box(-0.5, 0.5, -0.5, 0.5, 0, 0.08, WALL2)
for (cx, top) in [(-0.25, 1.0), (0.25, 0.96)]:
    prism(ngon(cx, 0, 0.2, 0.38, 12), 0.08, 0.93 * top, GLASS)
    for k in range(1, 8): prism(ngon(cx, 0, 0.215, 0.395, 12), 0.93 * top * k / 8, 0.93 * top * k / 8 + 0.012, TRIM)
    prism(ngon(cx, 0, 0.14, 0.27, 12), 0.93 * top, top, TRIM)
report["kit.harbor"] = finish("kit.harbor", 0.5)

# Central Library: a nine-storey block under the steel lattice dome
box(-0.5, 0.5, -0.5, 0.5, 0, 0.56, WALL2)
for k in range(3): box(-0.504, 0.504, -0.504, 0.504, 0.1 + 0.16 * k, 0.19 + 0.16 * k, GLASS)
piers(0.5, 0.5, 0, 0.56, 0.035, TRIM); box(-0.4, 0.4, -0.4, 0.4, 0.56, 0.66, TRIM)
i0 = len(V); seg = 10
for j in range(4):
    t = (math.pi / 2) * j / 4
    for k in range(seg): a = math.tau * k / seg; V.append((0.36 * math.cos(t) * math.cos(a), 0.36 * math.cos(t) * math.sin(a), 0.66 + 0.34 * math.sin(t)))
V.append((0, 0, 1.0)); apex = len(V) - 1
for j in range(3):
    for k in range(seg): a = i0 + j * seg + k; b = i0 + j * seg + (k + 1) % seg; F.append((a, b, b + seg, a + seg)); M.append(TRIM if (j + k) % 2 else GLASS)
for k in range(seg): F.append((i0 + 3 * seg + k, i0 + 3 * seg + (k + 1) % seg, apex)); M.append(TRIM if k % 2 else GLASS)
report["kit.library"] = finish("kit.library")

# Petco Park: a sandstone bowl open to the outfield, dark blue seats, the field, light towers, and the brick warehouse built into the left-field corner
seg = 16; i0 = len(V)
def wall_h(k): return 0.3 if 2 <= k <= 5 else 0.55
for k in range(seg):
    a = math.tau * k / seg; c, sn = math.cos(a), math.sin(a); hk = wall_h(k)
    V.extend([(0.5 * c, 0.46 * sn, 0), (0.5 * c, 0.46 * sn, hk), (0.43 * c, 0.4 * sn, hk), (0.2 * c, 0.19 * sn, 0.08)])
for k in range(seg):
    a = i0 + 4 * k; b = i0 + 4 * ((k + 1) % seg)
    F.append((a, b, b + 1, a + 1)); M.append(SAND); F.append((a + 1, b + 1, b + 2, a + 2)); M.append(TRIM); F.append((a + 2, b + 2, b + 3, a + 3)); M.append(WALL)
F.append(tuple(i0 + 4 * k + 3 for k in range(seg))); M.append(GREEN)
i = len(V); V.extend([(0.0, -0.13, 0.082), (0.09, -0.04, 0.082), (0.0, 0.05, 0.082), (-0.09, -0.04, 0.082)]); F.append((i, i + 1, i + 2, i + 3)); M.append(SAND)
box(-0.5, -0.3, 0.22, 0.44, 0, 0.5, BRICK); box(-0.504, -0.296, 0.216, 0.444, 0.2, 0.22, TRIM); box(-0.504, -0.296, 0.216, 0.444, 0.36, 0.38, TRIM)
for (x, y) in [(0.44, 0.3), (0.44, -0.3), (-0.2, -0.44), (0.1, 0.45)]: box(x - 0.008, x + 0.008, y - 0.008, y + 0.008, 0, 0.92, TRIM); box(x - 0.045, x + 0.045, y - 0.012, y + 0.012, 0.92, 1.0, WHITE)
box(-0.06, 0.1, 0.4, 0.43, 0.3, 0.52, ROOF)
report["kit.petco"] = finish("kit.petco")

# Convention Center: long and low on the bay, a glass barrel vault down the middle, concrete fins along the water side, and the white sails on the roof
box(-0.5, 0.5, -0.5, 0.5, 0, 0.4, TRIM)
i0 = len(V); seg = 6
for k in range(seg + 1):
    a = math.pi * k / seg; V.extend([(-0.5, -0.22 * math.cos(a), 0.4 + 0.3 * math.sin(a)), (0.16, -0.22 * math.cos(a), 0.4 + 0.3 * math.sin(a))])
for k in range(seg): F.append((i0 + 2 * k, i0 + 2 * k + 1, i0 + 2 * k + 3, i0 + 2 * k + 2)); M.append(GLASS)
F.append(tuple(i0 + 2 * k for k in range(seg + 1))); M.append(GLASS); F.append(tuple(i0 + 2 * k + 1 for k in range(seg, -1, -1))); M.append(GLASS)
for k in range(15):
    x = -0.47 + 0.94 * k / 14; i = len(V)
    for xx in (x - 0.008, x + 0.008): V.extend([(xx, -0.5, 0), (xx, -0.66, 0), (xx, -0.5, 0.4)])
    F.append((i, i + 1, i + 2)); M.append(TRIM); F.append((i + 3, i + 5, i + 4)); M.append(TRIM); F.append((i + 1, i + 4, i + 5, i + 2)); M.append(TRIM)
for a in range(5):
    for b in range(2): pyramid(0.18 + 0.064 * a, 0.18 + 0.064 * (a + 1), -0.3 + 0.3 * b, 0.3 * b, 0.4, 0.9, WHITE)
box(-0.5, 0.5, 0.5, 0.505, 0.12, 0.3, GLASS)
report["kit.conv"] = finish("kit.conv")

# USS Midway: the carrier museum at the pier. Hull, angled flight deck, island with its mast, a few aircraft on deck
prism([(-0.5, -0.07), (0.36, -0.07), (0.5, 0.0), (0.36, 0.07), (-0.5, 0.07)], 0, 0.35, GREY)
prism([(-0.5, -0.11), (0.3, -0.11), (0.48, -0.02), (0.48, 0.04), (0.38, 0.1), (0.1, 0.13), (-0.2, 0.13), (-0.5, 0.09)], 0.35, 0.41, GREY, ROOF)
box(0.04, 0.2, -0.108, -0.05, 0.41, 0.64, GREY); box(0.07, 0.17, -0.1, -0.058, 0.64, 0.76, GREY); box(0.115, 0.125, -0.084, -0.074, 0.76, 1.0, TRIM); box(0.09, 0.15, -0.082, -0.076, 0.86, 0.87, TRIM)
box(-0.45, 0.2, 0.03, 0.036, 0.411, 0.413, LIT)
for (x, y, r) in [(-0.38, -0.05, 0.3), (-0.3, -0.06, 0.2), (-0.2, -0.055, 0.4), (0.3, 0.02, 2.6), (-0.42, 0.06, 1.2), (-0.1, 0.09, 1.9)]:
    i = len(V); c, sn = math.cos(r), math.sin(r)
    for (px, py) in [(0.03, 0), (-0.02, 0.022), (-0.012, 0), (-0.02, -0.022)]: V.append((x + px * c - py * sn, y + px * sn + py * c, 0.416))
    F.append((i, i + 1, i + 2, i + 3)); M.append(TRIM)
report["kit.midway"] = finish("kit.midway")

# Coronado Bridge: a long blue girder deck on slender paired piers, curving out over the bay and rising high enough for ships
N = 18; st = []
for k in range(N + 1):
    u = k / N; x = -0.5 + u; y = -0.36 * u * u; z = max(0.0, math.sin(math.pi * u)) ** 0.8
    dx, dy = 1.0, -0.72 * u; L = math.hypot(dx, dy); st.append((x, y, z, -dy / L, dx / L))
i0 = len(V)
for (x, y, z, nx_, ny_) in st:
    for (off, dz) in [(0.03, 0.0), (-0.03, 0.0), (-0.024, -0.05), (0.024, -0.05)]: V.append((x + nx_ * off, y + ny_ * off, z + 0.03 + dz))
for k in range(N):
    a = i0 + 4 * k; b = a + 4
    F.append((a + 1, a, b, b + 1)); M.append(WHITE); F.append((a, a + 3, b + 3, b)); M.append(GIRDER); F.append((a + 2, a + 1, b + 1, b + 2)); M.append(GIRDER); F.append((a + 3, a + 2, b + 2, b + 3)); M.append(GIRDER)
for k in range(1, N):
    x, y, z, nx_, ny_ = st[k]
    if z < 0.06: continue
    for off in (0.018, -0.018): box(x + nx_ * off - 0.006, x + nx_ * off + 0.006, y + ny_ * off - 0.006, y + ny_ * off + 0.006, 0, z - 0.02, TRIM)
    box(x - 0.03, x + 0.03, y - 0.03, y + 0.03, z - 0.035, z - 0.02, TRIM)
report["kit.bridge"] = finish("kit.bridge")

# California Tower in Balboa Park: a low museum front and a slender tower in three diminishing stages under a tiled dome
box(-0.5, 0.5, -0.3, 0.3, 0, 0.14, SAND); box(-0.5, 0.5, -0.31, 0.31, 0.13, 0.15, TRIM); cyl(0.3, 0, 0.14, 0.02, 0.15, 0.26, GIRDER, 8, True)
box(-0.17, 0.17, -0.17, 0.17, 0, 0.5, SAND)
for z in (0.3, 0.4, 0.5): box(-0.185, 0.185, -0.185, 0.185, z - 0.008, z + 0.004, TRIM)
prism(ngon(0, 0, 0.16, 0.16, 8, math.pi / 8), 0.5, 0.68, SAND); prism(ngon(0, 0, 0.175, 0.175, 8, math.pi / 8), 0.67, 0.69, TRIM)
prism(ngon(0, 0, 0.12, 0.12, 8, math.pi / 8), 0.69, 0.8, SAND); prism(ngon(0, 0, 0.13, 0.13, 8, math.pi / 8), 0.79, 0.81, TRIM)
cyl(0, 0, 0.09, 0.09, 0.81, 0.86, TRIM, 8); cyl(0, 0, 0.09, 0.025, 0.86, 0.95, GIRDER, 8, True); cyl(0, 0, 0.012, 0.012, 0.95, 1.0, BRASS, 5)
report["kit.caltower"] = finish("kit.caltower")

# The bay: water, sailboats, and the palms along the Embarcadero
box(-0.5, 0.5, -0.5, 0.5, 0, 1, WATER)
report["kit.bay"] = finish("kit.bay")
prism([(-0.5, -0.12), (0.3, -0.12), (0.5, 0.0), (0.3, 0.12), (-0.5, 0.12)], 0, 0.14, TRIM); box(-0.012, 0.012, -0.012, 0.012, 0.14, 1.0, TRIM)
i = len(V); V.extend([(-0.36, 0, 0.2), (-0.02, 0, 0.2), (-0.02, 0, 0.96), (0.02, 0, 0.2), (0.34, 0, 0.2), (0.02, 0, 0.8)])
for f in [(0, 1, 2), (2, 1, 0), (3, 4, 5), (5, 4, 3)]: F.append(tuple(i + k for k in f)); M.append(WHITE)
report["kit.boat"] = finish("kit.boat")
cyl(0, 0, 0.03, 0.02, 0, 0.8, SAND, 5, False)
for k in range(7):
    a = math.tau * k / 7; c, sn = math.cos(a), math.sin(a); i = len(V)
    V.extend([(0, 0, 0.82), (0.24 * c - 0.07 * sn, 0.24 * sn + 0.07 * c, 0.8), (0.5 * c, 0.5 * sn, 0.6), (0.24 * c + 0.07 * sn, 0.24 * sn - 0.07 * c, 0.8)])
    F.append((i, i + 3, i + 2, i + 1)); M.append(LEAF); F.append((i, i + 1, i + 2, i + 3)); M.append(LEAF)
report["kit.palm"] = finish("kit.palm")

path = os.path.join("/Users/kiapousti/Documents/kpousti.github.io/blender", "city.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print(report, "total", sum(report.values()))
