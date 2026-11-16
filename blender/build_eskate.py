# Run inside Blender: models an electric skateboard (deck, trucks, wheels, belt-driven rear motor, battery enclosure, speed controller with its wiring),
# saves it as eskate.blend and renders the picture used in the "Mechanically inclined" tile to renders/eskate.jpg.
import bpy, math, os
from mathutils import Vector, Euler

ROOT = "/Users/kiapousti/Documents/kpousti.github.io"
bpy.ops.wm.read_homefile(use_empty=True)

def lin(h): return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in [((h >> s) & 255) / 255 for s in (16, 8, 0)])
def mat(name, rgb, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*lin(rgb), 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    return m
GRIP, WOOD, PAINT, STEEL, ALU, URETHANE, CORE, RUBBER, CASE, FIN, AMBER, BLUE, BRICK, DARK = range(14)
MATS = [mat("grip", 0x101114, 0.0, 0.95), mat("wood", 0xb08a5e, 0.0, 0.55), mat("paint", 0x1b2740, 0.0, 0.35), mat("steel", 0xb9c2d2, 1.0, 0.28), mat("alu", 0x8d97a8, 1.0, 0.4),
        mat("urethane", 0xf2b56b, 0.0, 0.3), mat("core", 0x20242c, 0.2, 0.4), mat("rubber", 0x0c0d10, 0.0, 0.7), mat("case", 0x191c24, 0.3, 0.45), mat("fin", 0x3a4152, 0.9, 0.4),
        mat("amber", 0xf2b56b, 0.0, 0.4), mat("blue", 0x3f78c2, 0.0, 0.4), mat("brick", 0xb04a3a, 0.0, 0.4), mat("dark", 0x0d0f14, 0.0, 0.6)]

V, F, M = [], [], []
def tr(p, axis): return p if axis == 'z' else (p[2], p[0], p[1]) if axis == 'x' else (p[1], p[2], p[0])
def box(x0, x1, y0, y1, z0, z1, m):
    i = len(V); V.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
    for f in [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (3, 2, 1, 0)]: F.append(tuple(i + k for k in f)); M.append(m)
def lathe(c, prof, m, seg=24, axis='z'):
    """turn a profile of (radius, height) pairs round an axis starting at c"""
    i = len(V); n = len(prof)
    for (r, t) in prof:
        for k in range(seg):
            a = math.tau * k / seg; p = tr((r * math.cos(a), r * math.sin(a), t), axis); V.append((c[0] + p[0], c[1] + p[1], c[2] + p[2]))
    for j in range(n - 1):
        for k in range(seg): a = i + j * seg + k; b = i + j * seg + (k + 1) % seg; F.append((a, b, b + seg, a + seg)); M.append(m[j] if isinstance(m, (list, tuple)) else m)
    F.append(tuple(i + (n - 1) * seg + k for k in range(seg))); M.append(m[-1] if isinstance(m, (list, tuple)) else m)
    F.append(tuple(i + k for k in range(seg - 1, -1, -1))); M.append(m[0] if isinstance(m, (list, tuple)) else m)
def rod(p0, p1, r, m, seg=8):
    a = Vector(p0); b = Vector(p1); d = (b - a).normalized(); u = d.orthogonal().normalized(); v = d.cross(u); i = len(V)
    for c in (a, b):
        for k in range(seg): ang = math.tau * k / seg; V.append(tuple(c + (u * math.cos(ang) + v * math.sin(ang)) * r))
    for k in range(seg): F.append((i + k, i + (k + 1) % seg, i + seg + (k + 1) % seg, i + seg + k)); M.append(m)
    F.append(tuple(i + seg + k for k in range(seg))); M.append(m); F.append(tuple(i + k for k in range(seg - 1, -1, -1))); M.append(m)
def wire(pts, r, m):
    for k in range(len(pts) - 1): rod(pts[k], pts[k + 1], r, m, 6)

objs = []
def part(name, smooth=0.6):
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    for m in MATS: me.materials.append(m)
    me.polygons.foreach_set("material_index", M)
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        try: me.set_sharp_from_angle(angle=smooth)
        except Exception as e: print(e)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); objs.append(o); V.clear(); F.clear(); M.clear(); return o

# ---- deck: seven plies of maple under grip tape, a little concave, with a kicked tail. Drawn upside up; z = 0 is the underside ----
L, W = 0.92, 0.23
def half_width(u):  # rounded nose and tail
    e = min(u, 1 - u) / 0.14; return W / 2 * (1.0 if e >= 1 else math.sqrt(max(0.0, 1 - (1 - e) ** 2.4)) * 0.92 + 0.08 * e)
def lift(u): return 0.085 * max(0.0, (0.13 - u) / 0.13) ** 2 + 0.03 * max(0.0, (u - 0.9) / 0.1) ** 2  # tail kicks up, nose a little
NS = 40; i0 = len(V); CS = [-1, -0.7, -0.35, 0, 0.35, 0.7, 1]
for s in range(NS + 1):
    u = s / NS; x = -L / 2 + L * u; w = half_width(u); zl = lift(u)
    for c in CS: V.append((x, c * w, zl + 0.006 * c * c + 0.014))       # top: grip tape
    for c in reversed(CS): V.append((x, c * w, zl + 0.006 * c * c))     # underside
for s in range(NS):
    for k in range(14):
        a = i0 + s * 14 + k; b = i0 + s * 14 + (k + 1) % 14
        F.append((a, a + 14, b + 14, b)); M.append(GRIP if k < 6 else WOOD if k in (6, 13) else PAINT)
F.append(tuple(i0 + k for k in range(14))); M.append(WOOD); F.append(tuple(i0 + NS * 14 + k for k in range(13, -1, -1))); M.append(WOOD)
part("deck", 0.9)
box(-0.26, 0.3, -0.006, 0.006, -0.0006, 0.0002, AMBER)  # a pinstripe down the underside
part("stripe", 0)

# ---- trucks: baseplate, hanger, axle, kingpin and bushings; and the wheels ----
def truck(x, flip):
    s = -1 if flip else 1
    box(x - 0.04, x + 0.04, -0.03, 0.03, -0.012, 0.0, ALU)                                   # baseplate (with a riser pad)
    box(x - 0.042, x + 0.042, -0.032, 0.032, -0.004, 0.0, RUBBER)
    for (dx, dy) in [(-0.028, -0.02), (0.028, -0.02), (-0.028, 0.02), (0.028, 0.02)]: lathe((x + dx, dy, -0.018), [(0.005, 0), (0.005, 0.006)], STEEL, 6)
    rod((x + s * 0.012, 0, -0.012), (x - s * 0.02, 0, -0.058), 0.006, STEEL)                # kingpin
    lathe((x + s * 0.004, 0, -0.03), [(0.016, 0), (0.017, 0.008), (0.014, 0.014)], URETHANE, 14); lathe((x - s * 0.008, 0, -0.046), [(0.014, 0), (0.016, 0.008), (0.016, 0.012)], URETHANE, 14)  # bushings
    i = len(V)                                                                               # hanger: a wedge that carries the axle
    for yy in (-0.085, 0.085): V.extend([(x - s * 0.03, yy, -0.07), (x + s * 0.004, yy * 0.35, -0.03), (x - s * 0.006, yy, -0.052), (x - s * 0.018, yy * 0.35, -0.04)])
    for f in [(0, 2, 6, 4), (2, 1, 5, 6), (1, 3, 7, 5), (3, 0, 4, 7), (0, 3, 1, 2), (4, 6, 5, 7)]: F.append(tuple(i + k for k in f)); M.append(ALU)
    rod((x - s * 0.022, -0.14, -0.062), (x - s * 0.022, 0.14, -0.062), 0.0045, STEEL)        # axle
    for yy in (-0.118, 0.118):
        lathe((x - s * 0.022, yy - 0.026, -0.062), [(0.017, 0), (0.04, 0.003), (0.045, 0.012), (0.045, 0.04), (0.04, 0.049), (0.017, 0.052)], [CORE, URETHANE, URETHANE, URETHANE, CORE, CORE], 28, 'y')   # wheel
        lathe((x - s * 0.022, yy - 0.029, -0.062), [(0.011, 0), (0.011, 0.058)], STEEL, 12, 'y')   # bearings and spacer
        lathe((x - s * 0.022, yy + (0.03 if yy > 0 else -0.036), -0.062), [(0.007, 0), (0.007, 0.006)], STEEL, 6, 'y')  # axle nut
    return x - s * 0.022
truck(0.3, False); part("truck.front")
ax = truck(-0.3, True)
# ---- drive: motor on a mount off the rear hanger, pulleys and a toothed belt to the wheel ----
mx, mz = ax + 0.085, -0.066
box(ax - 0.004, mx + 0.03, 0.062, 0.068, -0.09, -0.04, ALU)                                   # motor mount plate
lathe((mx, -0.01, mz), [(0.012, 0), (0.028, 0.002), (0.03, 0.01), (0.03, 0.06), (0.026, 0.066), (0.008, 0.068)], [DARK, DARK, FIN, DARK, DARK, DARK], 20, 'y')   # motor can
for k in range(10): a = math.tau * k / 10; box(mx + 0.0305 * math.cos(a) - 0.002, mx + 0.0305 * math.cos(a) + 0.002, 0.002, 0.046, mz + 0.0305 * math.sin(a) - 0.002, mz + 0.0305 * math.sin(a) + 0.002, AMBER)  # magnets seen through the can's slots
lathe((mx, 0.068, mz), [(0.012, 0), (0.012, 0.018)], STEEL, 14, 'y')                           # motor pulley
lathe((ax, 0.07, -0.062), [(0.034, 0), (0.034, 0.016)], STEEL, 22, 'y')                        # wheel pulley
i = len(V); seg = 12                                                                           # belt: round each pulley and straight between
ring = []
for k in range(seg + 1): a = math.pi / 2 + math.pi * k / seg; ring.append((ax + 0.036 * math.cos(a), -0.062 + 0.036 * math.sin(a)))
for k in range(seg + 1): a = -math.pi / 2 + math.pi * k / seg; ring.append((mx + 0.014 * math.cos(a), mz + 0.014 * math.sin(a)))
n = len(ring)
for (px, pz) in ring: V.extend([(px, 0.071, pz), (px, 0.085, pz)])
for k in range(n): a = i + 2 * k; b = i + 2 * ((k + 1) % n); F.append((a, a + 1, b + 1, b)); M.append(RUBBER); F.append((b, b + 1, a + 1, a)); M.append(RUBBER)
part("truck.rear")

# ---- battery enclosure: a long ribbed case bolted under the deck ----
box(-0.1, 0.27, -0.085, 0.085, -0.04, 0.0, CASE)
for k in range(9): box(-0.085 + 0.042 * k, -0.07 + 0.042 * k, -0.088, 0.088, -0.043, -0.004, CASE)
for (x, y) in [(-0.09, -0.075), (0.26, -0.075), (-0.09, 0.075), (0.26, 0.075), (0.085, -0.075), (0.085, 0.075)]: lathe((x, y, -0.046), [(0.005, 0), (0.005, 0.004)], STEEL, 6)
lathe((0.272, 0.04, -0.02), [(0.008, 0), (0.008, 0.006)], STEEL, 10, 'x'); lathe((0.272, -0.03, -0.02), [(0.006, 0), (0.006, 0.004)], AMBER, 10, 'x')   # charge port and power button
part("battery")
# ---- the ESC: a finned aluminium case at the tail, with phase wires to the motor and leads to the battery ----
box(-0.25, -0.13, -0.06, 0.06, -0.03, 0.0, CASE)
for k in range(11): box(-0.246 + 0.0112 * k, -0.241 + 0.0112 * k, -0.055, 0.055, -0.042, -0.03, FIN)
for (x, y) in [(-0.244, -0.054), (-0.136, -0.054), (-0.244, 0.054), (-0.136, 0.054)]: lathe((x, y, -0.034), [(0.004, 0), (0.004, 0.004)], STEEL, 6)
part("esc")
for k, m in enumerate((AMBER, BLUE, DARK)): wire([(-0.25, 0.02 - 0.012 * k, -0.018), (-0.262, 0.03 - 0.008 * k, -0.03), (mx + 0.01, 0.01 - 0.008 * k, mz + 0.034), (mx, 0.012 - 0.006 * k, mz + 0.028)], 0.0028, m)
wire([(-0.13, 0.02, -0.016), (-0.115, 0.022, -0.02), (-0.1, 0.02, -0.018)], 0.004, BRICK); wire([(-0.13, -0.02, -0.016), (-0.115, -0.022, -0.02), (-0.1, -0.02, -0.018)], 0.004, DARK)
part("wires")

# ---- the picture: the board rolled toward the camera so its underside shows, lit warm from one side and cool from behind ----
board = bpy.data.objects.new("board", None); bpy.context.scene.collection.objects.link(board)
for o in objs: o.parent = board
board.rotation_euler = Euler((math.radians(-112), 0, math.radians(-5)))
sc = bpy.context.scene
w = bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
next(nd for nd in w.node_tree.nodes if nd.type == "BACKGROUND").inputs[0].default_value = (*lin(0x0b0d14), 1)
def light(name, loc, energy, color, size):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = energy; d.color = color; d.size = size
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
light("key", (-0.9, -1.1, 0.9), 55, (1.0, 0.82, 0.62), 1.2); light("rim", (0.9, 0.8, 0.5), 40, (0.45, 0.62, 1.0), 1.0); light("fill", (0.2, -1.4, -0.3), 10, (1, 1, 1), 1.5)
cam = bpy.data.cameras.new("cam"); cam.lens = 85; co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
co.location = (0.05, -2.9, 0.12); co.rotation_euler = (Vector((0.0, 0, 0.0)) - Vector(co.location)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
sc.render.resolution_x, sc.render.resolution_y = 1680, 400
try: sc.view_settings.view_transform = 'Standard'
except Exception as e: print(e)
try: sc.eevee.taa_render_samples = 64
except Exception as e: print(e)
fmts = [i.identifier for i in bpy.types.ImageFormatSettings.bl_rna.properties["file_format"].enum_items]
sc.render.image_settings.file_format = 'JPEG' if 'JPEG' in fmts else fmts[0]; sc.render.image_settings.quality = 86
os.makedirs(os.path.join(ROOT, "renders"), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "eskate.blend"))
sc.render.filepath = os.path.join(ROOT, "renders", "eskate.jpg"); bpy.ops.render.render(write_still=True)
print("rendered", os.path.getsize(sc.render.filepath))
