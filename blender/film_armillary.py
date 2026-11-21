# Run with:  Blender -b --python blender/film_armillary.py -- <set> [frames] [samples]     (arguments: see filmkit.py)
# The film that opens Skills: a brass armillary. Eight rings (the Skills table has eight rows, and the page's own Skills model is eight rings),
# each hung inside the next on two pins, the way a gimbal is. The whole instrument is built here; there is no .blend file.
#
# The shot, by share of the film:
#   0.00  closed: all eight rings lie flat in one disc, facing the camera, on a stem and a round foot
#   0.05 to 0.55  it opens: each ring turns out on its own pins, one after another from the outside in, into a sphere
#   0.35  the camera has come round to the left and closer
#   0.70  inside the outer rings, the bands crossing in front
#   1.00  very close on the polished ball at the centre, the rings and the sky mirrored in it
import bpy, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filmkit import *

sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)

brass = metal("brass", (0.86, 0.64, 0.27), 0.17, 0.07, 60); bronze = metal("bronze", (0.5, 0.3, 0.14), 0.3, 0.08, 40); steel = metal("steel", (0.8, 0.83, 0.87), 0.04)
enamel = metal("enamel", (0.03, 0.04, 0.07), 0.3, 0.06, 20); bsdf(enamel).inputs["Metallic"].default_value = 0.4

def add(name, verts, faces, mats, face_mat=None, parent=None, angle=40):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for m in mats: me.materials.append(m)
    if face_mat: me.polygons.foreach_set("material_index", face_mat)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.set_sharp_from_angle(angle=math.radians(angle)); me.update()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.parent = parent; return o

def lathe(profile, segs=256):   # a closed outline (radius, height) swept round the ring's own axis (Z)
    verts, faces, n = [], [], len(profile)
    for s in range(segs):
        a = math.tau * s / segs; verts += [(r * math.cos(a), r * math.sin(a), z) for r, z in profile]
    for s in range(segs):
        for i in range(n): faces.append((s * n + i, ((s + 1) % segs) * n + i, ((s + 1) % segs) * n + (i + 1) % n, s * n + (i + 1) % n))
    return verts, faces

def band(R, w, t, bev=0.004):   # the outline of a ring's section: a rectangle w tall and t thick with rounded corners
    out = []
    for cx, cz, a0 in ((R + t / 2 - bev, w / 2 - bev, 0), (R - t / 2 + bev, w / 2 - bev, 90), (R - t / 2 + bev, -w / 2 + bev, 180), (R + t / 2 - bev, -w / 2 + bev, 270)):
        for k in range(4): a = math.radians(a0 + 30 * k); out.append((cx + bev * math.cos(a), cz + bev * math.sin(a)))
    return out

def box(verts, faces, mat_i, idx, c, ex, ey, ez, hx, hy, hz):   # a small block at c with its own three directions: the degree marks
    n0 = len(verts)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1): verts.append(tuple(c[i] + sx * hx * ex[i] + sy * hy * ey[i] + sz * hz * ez[i] for i in range(3)))
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)): faces.append(tuple(n0 + i for i in f)); mat_i.append(idx)

def cyl(name, r, length, axis, mat, parent, at=(0, 0, 0), segs=32, cap=0.0):   # a pin along +axis and -axis through `at`; cap > 0 rounds the ends into knobs
    prof = [(0, -length / 2)] + [(r + cap * math.sin(math.radians(a)), -length / 2 + cap * (1 - math.cos(math.radians(a)))) for a in range(0, 91, 30)] if cap else [(0, -length / 2), (r, -length / 2)]
    prof += [(rr, -z) for rr, z in reversed(prof)]
    v, f = lathe(prof, segs); o = add(name, v, f, [mat], parent=parent); o.location = at
    o.rotation_euler = (0, math.radians(90), 0) if axis == "X" else (math.radians(90), 0, 0) if axis == "Y" else (0, 0, 0); return o

# ---------- the instrument ----------
NR, W_, T_ = 8, 0.05, 0.03
RAD = [1.0 - 0.09 * k for k in range(NR)]
root = bpy.data.objects.new("armillary", None); sc.collection.objects.link(root); root.rotation_euler = (math.radians(90), 0, 0)   # ring axis toward the camera: closed, it is a disc seen face on
rings, parent = [], root
for k, R in enumerate(RAD):
    v, f = lathe(band(R, W_, T_)); mi = [0] * len(f)
    for q in range(72):   # degree marks on both faces: every five degrees, a longer one every thirty
        a = math.tau * q / 72; er = (math.cos(a), math.sin(a), 0); et = (-math.sin(a), math.cos(a), 0); long = q % 6 == 0
        for side in (-1, 1): box(v, f, mi, 1, (R * er[0], R * er[1], side * W_ / 2), er, et, (0, 0, 1), 0.011 if long else 0.006, 0.0022, 0.0016)
    o = add(f"ring.{k}", v, f, [brass if k % 2 == 0 else bronze, enamel], mi, parent); rings.append(o); parent = o
    axis = "X" if k % 2 else "Y"   # each ring hangs on two pins in the ring outside it; the pins alternate between the two directions across the ring
    if k:
        gap = RAD[k - 1] - R; d = (R + RAD[k - 1]) / 2
        for sgn in (-1, 1):
            at = (sgn * d, 0, 0) if axis == "X" else (0, sgn * d, 0)
            cyl(f"pin.{k}.{sgn}", 0.011, gap + T_ * 1.5, axis, steel, rings[k - 1], at, cap=0.007)
    o["axis"] = axis
ball = add("ball", *lathe([(0.118 * math.sin(math.radians(a)), -0.118 * math.cos(math.radians(a))) for a in range(0, 181, 6)], 96), [steel], parent=rings[-1], angle=180)
cyl("axle", 0.007, 2 * (RAD[-1] - T_ / 2), "X", brass, rings[-1])
# the stand: a stem under the outer ring, down to a round foot (in the root's frame the ring plane is XY and "down" is -Y)
stem = cyl("stem", 0.028, 0.3, "Y", brass, root, (0, -(RAD[0] + T_ / 2 + 0.15), 0), cap=0.01)
foot_p = [(0, 0), (0.42, 0), (0.44, 0.012), (0.44, 0.05), (0.40, 0.065), (0.12, 0.075), (0.06, 0.1), (0, 0.1)]
foot = add("foot", *lathe(foot_p, 128), [enamel], parent=root); foot.rotation_euler = (math.radians(-90), 0, 0); foot.location = (0, -(RAD[0] + T_ / 2 + 0.3 + 0.09), 0)
rim = add("foot.rim", *lathe(band(0.445, 0.012, 0.012, 0.003), 128), [brass], parent=foot); rim.location = (0, 0, 0.03)

# ---------- it opens: ring k turns out on its pins, the outer ones first; then every ring keeps drifting slowly ----------
OPEN = [0, 62, 74, 55, 81, 48, 68, 90]   # degrees each ring ends turned, measured from the ring that carries it
def pose(scene, *a):
    p = share(scene)
    for k, o in enumerate(rings):
        if not k: continue
        th = math.radians(OPEN[k] * smooth((p - 0.05 - 0.035 * k) / 0.3) + (16 if k % 2 else -12) * p)
        o.rotation_euler = (th, 0, 0) if o["axis"] == "X" else (0, th, 0)
bpy.app.handlers.frame_change_pre.append(pose)

# ---------- light and camera ----------
studio(sc, 0.6, 200)
lamp(sc, "key", (-2.6, -3.4, 2.8), 520, (1.0, 0.84, 0.64), 2.2); lamp(sc, "rim", (2.8, 1.6, 1.8), 420, (0.6, 0.76, 1.0), 1.6); lamp(sc, "low", (0.6, -2.6, -1.4), 110, (1.0, 0.66, 0.4), 2.5)
# The way in: every ring is a hoop round the same centre, so a straight line toward the centre meets each hoop's sphere once. The camera comes in along the direction
# that stays farthest from all eight hoops (checked at three moments of the approach, since the rings keep drifting), so no band ever crosses the lens or hides the ball.
from mathutils import Vector
def hoops(p):
    sc.frame_set(round(1 + p * (N - 1))); bpy.context.view_layer.update(); return [(o.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized() for o in rings]
sets_ = [hoops(p) for p in (0.7, 0.85, 1.0)]; best = (-1, None)
for az in range(-60, 61, 2):
    for el in range(-12, 46, 2):
        d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el))))
        clear = min(abs(math.asin(max(-1, min(1, d.dot(n))))) for ns in sets_ for n in ns)
        if clear > best[0]: best = (clear, d)
IN = best[1]; print(f"way in: {tuple(round(v, 3) for v in IN)}, {math.degrees(best[0]):.1f} degrees clear of every ring", flush=True)
assert math.degrees(best[0]) > 7, "no clear way in to the ball: change OPEN"
FAR = -7.6 if SET == "d" else -8.3   # phones: far enough that the outer ring clears both sides of a tall picture
camera(sc, [  # share, camera, aim, lens (mm), f-stop
    (0.00, (0.9, FAR, 0.35), (0.0, 0.0, -0.18), 50, 5.6),
    (0.35, (-1.5, -3.9, 0.8), (0.0, 0.0, -0.05), 50, 4.0),
    (0.70, tuple(IN * 1.9), (0.0, 0.0, 0.0), 55, 2.8),
    (1.00, tuple(IN * 0.865), (0.0, 0.0, 0.0), 60 if SET == "d" else 50, 4.0)])   # ends between the second and third rings, the ball filling most of the picture
render(sc, "armillary")
