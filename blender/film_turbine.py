# Run with:  Blender -b blender/turbine.blend --python blender/film_turbine.py -- <set> [frames] [samples]     (arguments: see filmkit.py)
# The film that opens Experience: one continuous camera move over the 477-part gas turbine as it comes apart.
#
# The shot, by share of the film:
#   0.00  the whole engine from the front and above, rotor turning, top half of the casing already off (the model is a cutaway)
#   0.10 to 0.40  it opens: every stage slides apart along the shaft, the casing halves drop away, the combustor cans fan outward
#   0.45  in close over the first compressor stages
#   0.65  over the combustor cans, heat-tinted from straw to blue
#   0.85 to 1.00  along the turbine stages, ending very close on one row of blades
import bpy, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filmkit import *
from mathutils import Matrix, Vector

sc = bpy.context.scene
for o in list(bpy.data.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)

# ---------- metals for a close-up: the page's palette (steel blue, amber, dark enamel), with a little grain in the sheen ----------
metal("steel", (0.56, 0.62, 0.72), 0.16, 0.07, 55); metal("bolt", (0.72, 0.75, 0.8), 0.2, 0.06, 80); metal("dark", (0.045, 0.055, 0.08), 0.26, 0.08, 30)
metal("amber", (0.9, 0.5, 0.17), 0.2, 0.07, 55)
case = metal("case", (0.03, 0.05, 0.11), 0.34, 0.06, 20); bsdf(case).inputs["Metallic"].default_value = 0.6
heat = metal("heat", (0.5, 0.4, 0.3), 0.24, 0.07, 40)   # the cans: steel that has run hot, tinted along its length the way real exhaust parts are
nt = heat.node_tree; tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); ramp = nt.nodes.new("ShaderNodeValToRGB")
nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"]); nt.links.new(sep.outputs["X"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bsdf(heat).inputs["Base Color"])
els = ramp.color_ramp.elements; els[0].position = 0.0; els[0].color = (0.62, 0.6, 0.58, 1); els[1].position = 1.0; els[1].color = (0.1, 0.22, 0.55, 1)
for pos, col in ((0.35, (0.75, 0.52, 0.2, 1)), (0.6, (0.5, 0.2, 0.42, 1)), (0.8, (0.22, 0.2, 0.6, 1))): e = els.new(pos); e.color = col

# ---------- every part: where it goes when the engine opens, and whether it turns with the rotor ----------
SPREAD = 1.75   # how far apart the stages slide along the shaft
parts = []
for o in bpy.data.objects:
    if o.type != "MESH": continue
    nm = o.name.split("."); kind = nm[0]; base = o.matrix_world.copy()
    bb = [base @ Vector(c) for c in o.bound_box]; cx = sum(v.x for v in bb) / 8
    off = Vector((cx * (SPREAD - 1), 0, 0)); turns = kind in ("blade", "disc", "shaft", "nose")
    if kind == "shaft": off = Vector((0, 0, 0))                      # the shaft stays: everything else slides along it
    elif kind in ("case", "flange", "bolt", "vane"): off.z -= 0.34   # the casing's lower half, with its vanes and bolts, drops away
    elif kind in ("can", "nozzle"):                                  # each can moves straight out from the shaft
        r = Vector((0, o.location.y, o.location.z)).normalized(); off += r * 0.16
        if kind == "nozzle": off.x -= 0.1
    elif kind == "fuel": off.x -= 0.12
    elif kind == "combustor": off = Vector((cx * (SPREAD - 1), 0, 0))
    parts.append((o, base, off, turns))

# ---------- blades for a close-up. The page's blades are 26 flat faces each; the film gets real sections: a cambered aerofoil, twisted from root to tip, on a root platform ----------
def blade_mesh(name, span, chord, thick, camber, stagger, twist, pitch, mat, NA=22, NS=14):
    def section(t):   # one closed loop round the aerofoil at share t of the span (NACA four-digit thickness on a parabolic camber line)
        c = chord * mix(1.0, 0.82, t); th = math.radians(stagger + twist * (t - 0.5)); pts = []
        for i in range(2 * NA):
            u = i / NA if i < NA else 2 - i / NA; x = 0.5 * (1 - math.cos(math.pi * u)); side = 1 if i < NA else -1
            yt = 5 * thick * (0.2969 * math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1036 * x ** 4); yc = 4 * camber * x * (1 - x)
            a = (x - 0.5) * c; b = (yc + side * yt) * c
            pts.append((a * math.cos(th) - b * math.sin(th), a * math.sin(th) + b * math.cos(th), 0.004 + t * (span - 0.004)))
        return pts
    verts, faces, L = [], [], 2 * NA
    for k in range(NS + 1): verts += section(k / NS)
    for k in range(NS):
        for i in range(L): faces.append((k * L + i, k * L + (i + 1) % L, (k + 1) * L + (i + 1) % L, (k + 1) * L + i))
    faces.append(tuple(NS * L + i for i in range(L)))   # the tip
    hx, hy, n0 = chord * 0.52, pitch * 0.46, len(verts)   # the root platform: neighbours' platforms meet in a ring round the disc
    verts += [(sx * hx, sy * hy, z) for z in (-0.006, 0.005) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    faces += [(n0, n0 + 1, n0 + 2, n0 + 3), (n0 + 7, n0 + 6, n0 + 5, n0 + 4)] + [(n0 + i, n0 + 4 + i, n0 + 4 + (i + 1) % 4, n0 + (i + 1) % 4) for i in range(4)]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.set_sharp_from_angle(angle=math.radians(50)); me.materials.append(mat); me.update()
    return me
stage = {}
for o, base, off, turns in parts:
    nm = o.name.split(".")
    if nm[0] != "blade": continue
    if nm[1] not in stage:
        hot = nm[1][0] == "t"; zs = [c[2] for c in o.bound_box]; xs = [c[0] for c in o.bound_box]; count = sum(1 for q in bpy.data.objects if q.name.startswith("blade." + nm[1] + "."))
        root = math.hypot(o.location.y, o.location.z)
        stage[nm[1]] = blade_mesh("film." + nm[1], max(zs), (max(xs) - min(xs)) * (1.15 if hot else 1.3), 0.17 if hot else 0.075, 0.2 if hot else 0.06, -32 if hot else 38, 14 if hot else 26, math.tau * root / count, o.data.materials[0])
    o.data = stage[nm[1]]

def pose(scene, *a):
    p = share(scene); e = smooth((p - 0.10) / 0.30); spin = Matrix.Rotation(mix(0.6, 14 * math.tau / 32, p), 4, "X")   # ends a whole number of blade spacings round, so a blade of the middle turbine stage (32 blades) stands exactly where the last shot looks
    for o, base, off, turns in parts:
        o.matrix_world = Matrix.Translation(off * e) @ (spin @ base if turns else base)
bpy.app.handlers.frame_change_pre.append(pose)

# ---------- light and camera ----------
studio(sc, 0.5, 200)
lamp(sc, "key", (-2.4, -2.8, 3.0), 520, (1.0, 0.84, 0.64), 2.2); lamp(sc, "rim", (2.8, 2.0, 1.8), 420, (0.6, 0.76, 1.0), 1.6); lamp(sc, "low", (0.6, -2.4, -0.6), 90, (1.0, 0.66, 0.4), 2.5)
X = SPREAD   # places along the opened engine
if SET == "d":
    SHOTS = [  # share, camera, aim, lens (mm), f-stop
        (0.00, (-2.9, -3.45, 2.2), (0.06, 0.0, -0.06), 50, 5.6),
        (0.24, (-2.5, -2.2, 1.6), (-0.4, 0.0, 0.0), 50, 4.0),
        (0.45, (-0.72 * X - 0.62, -0.7, 0.66), (-0.60 * X, 0.0, 0.2), 60, 4.0),
        (0.65, (0.29 * X - 0.5, -1.0, 0.62), (0.29 * X, -0.14, 0.2), 60, 4.0),
        (0.86, (0.56 * X - 0.42, -0.72, 0.56), (0.62 * X, 0.0, 0.26), 65, 4.0),
        (1.00, (0.67 * X - 0.34, -0.42, 0.46), (0.67 * X, -0.02, 0.28), 70, 4.0)]
else:   # phones: the engine seen more end-on, so it runs up a tall picture
    SHOTS = [
        (0.00, (-4.6, -1.5, 3.1), (0.1, 0.0, -0.05), 50, 5.6),
        (0.24, (-3.2, -1.2, 2.1), (-0.3, 0.0, 0.0), 50, 4.0),
        (0.45, (-0.72 * X - 0.7, -0.46, 0.72), (-0.60 * X, 0.0, 0.2), 55, 4.0),
        (0.65, (0.29 * X - 0.5, -1.2, 0.95), (0.29 * X, -0.3, 0.12), 55, 4.0),
        (0.86, (0.56 * X - 0.5, -0.5, 0.62), (0.62 * X, 0.0, 0.26), 60, 4.0),
        (1.00, (0.67 * X - 0.3, -0.26, 0.46), (0.67 * X, -0.02, 0.28), 65, 4.0)]
camera(sc, SHOTS)
render(sc, "turbine")
