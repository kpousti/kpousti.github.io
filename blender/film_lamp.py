# Run with:  Blender -b --python blender/film_lamp.py -- <set> [frames] [samples] [percent]     (arguments: see filmkit.py)
# The film that opens Contact: a brass signal lamp on a sea wall above the Pacific at blue hour. The Contact section already sends Morse; this is the lamp that would.
# Built here: the lamp, its tripod, the wall, and Blender's own ocean and sky. There is no .blend file.
#
# The shot, by share of the film:
#   0.00  the lamp on its tripod at the wall, the sea and the last light behind it, the lamp dark
#   0.20 to 0.58  closing in while it flashes: short, long, short
#   0.70  it comes on and stays on
#   1.00  very close, square on to the ribbed glass, glowing
import bpy, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filmkit import *
from mathutils import Vector

sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
dusk(sc, -2.5, 0.5); ocean = sea(sc, wave=0.8)

brass = metal("brass", (0.86, 0.64, 0.27), 0.2, 0.08, 60); steel = metal("steel", (0.8, 0.83, 0.87), 0.15)
def plain(name, color, rough, grain=0.0, scale=40): m = metal(name, color, rough, grain, scale); bsdf(m).inputs["Metallic"].default_value = 0.0; return m
wood = plain("wood", (0.11, 0.055, 0.03), 0.45, 0.1, 25); stone = plain("stone", (0.035, 0.037, 0.042), 0.8, 0.12, 3)
glass = bpy.data.materials.new("glass"); glass.use_nodes = True; gb = bsdf(glass); gb.inputs["Roughness"].default_value = 0.03; gb.inputs["IOR"].default_value = 1.5
gb.inputs["Transmission Weight" if "Transmission Weight" in gb.inputs else "Transmission"].default_value = 1.0; gb.inputs["Base Color"].default_value = (1.0, 0.95, 0.86, 1)
fire = glow("fire", (1.0, 0.56, 0.2), 0.0); fb = bsdf(fire)

# ---------- the wall the lamp stands on: its top is 3 m above the sea ----------
box(stone, 0, -3.4, -4, 14, 9.2, 7); box(stone, 0, 1.0, 3.0, 14, 0.45, 0.55); build(sc, edge=0.02)

# ---------- the lamp head, built along its own axis (Z, the glass at the front) and then turned to face where the camera ends ----------
HEAD = Vector((0, 0, 4.3)); FACE = Vector((-0.26, -1.0, 0.03)).normalized()
head = bpy.data.objects.new("head", None); sc.collection.objects.link(head); head.location = HEAD; head.rotation_euler = FACE.to_track_quat("Z", "Y").to_euler()
turned(brass, [(0.0, -0.21), (0.05, -0.21), (0.11, -0.185), (0.145, -0.15), (0.15, -0.12), (0.15, 0.075), (0.166, 0.08), (0.166, 0.112), (0.15, 0.116), (0.146, 0.1), (0.146, 0.02), (0.0, 0.02)])   # the drum, open at the front, its inside the reflector
ridge = [(0.0, 0.078), (0.143, 0.078), (0.143, 0.09)]   # the glass: flat behind, ringed with ridges in front, a dome in the middle
for k in range(5, -1, -1): ridge += [(0.04 + (k + 1) * 0.0172, 0.09), (0.04 + k * 0.0172, 0.104), (0.04 + k * 0.0172, 0.09)]
ridge += [(0.03, 0.099), (0.02, 0.104), (0.01, 0.1065), (0.0, 0.107)]
turned(glass, ridge, 128)
turned(fire, [(0.035 * math.sin(math.radians(a)), 0.062 - 0.035 * math.cos(math.radians(a))) for a in range(0, 181, 12)], 32)   # the burner
for i in range(8): a = math.tau * i / 8; cyl(steel, 0.158 * math.cos(a), 0.158 * math.sin(a), 0.11, 0.006, 0.004, 16)   # screws round the glass
cyl(brass, 0, 0.19, -0.14, 0.012, 0.26, 24); box(brass, 0, 0.165, -0.1, 0.012, 0.04, 0.012); box(brass, 0, 0.165, 0.05, 0.012, 0.04, 0.012)   # the sighting tube on top
for sy in (-0.05, 0.05): box(brass, 0, sy, -0.27, 0.014, 0.014, 0.06)
box(wood, 0, 0, -0.3, 0.036, 0.14, 0.036)                                                                                                    # the grip at the back
for sx in (-1, 1): box(brass, sx * 0.165, 0, -0.03, 0.03, 0.04, 0.04); box(brass, sx * 0.185, -0.11, -0.03, 0.014, 0.26, 0.04)               # the yoke it tilts in
box(brass, 0, -0.24, -0.03, 0.384, 0.016, 0.04)
build(sc, smooth=("brass", "glass", "fire", "steel"), sharp=("glass", "fire"), parent=head, edge=0.0015)

# ---------- the tripod ----------
TOP = Vector((0, 0, 4.04)); rod(sc, brass, TOP, HEAD + Vector((0, 0, -0.245)), 0.02); rod(sc, brass, TOP + Vector((0, 0, -0.05)), TOP + Vector((0, 0, 0.012)), 0.06, 40)
for i in range(3):
    a = math.radians(90 + 120 * i); foot = Vector((0.6 * math.cos(a), 0.6 * math.sin(a), 3.0)); knee = TOP + Vector((0.05 * math.cos(a), 0.05 * math.sin(a), -0.03))
    rod(sc, wood, knee, foot.lerp(knee, 0.06), 0.022); rod(sc, brass, foot.lerp(knee, 0.07), foot, 0.025)

def pulse(p, a, b, edge=0.012): return smooth((p - a) / edge) * (1 - smooth((p - b) / edge))
def pose(scene, *a):
    p = share(scene); ocean.time = p * 4.0
    lit = max(pulse(p, 0.2, 0.25), pulse(p, 0.33, 0.45), pulse(p, 0.53, 0.58), smooth((p - 0.7) / 0.05))   # short, long, short, then on
    fb.inputs["Emission Strength"].default_value = 55 * lit
bpy.app.handlers.frame_change_pre.append(pose)

# ---------- light and camera: the sky, a cool key for the brass, a warm rim from the afterglow; the lamp lights itself ----------
lamp(sc, "key", (-3.0, -5.0, 7.0), 260, (0.72, 0.82, 1.0), 3.0, tuple(HEAD)); lamp(sc, "rim", (2.6, 3.0, 5.2), 160, (1.0, 0.6, 0.35), 2.0, tuple(HEAD))
far = 1.0 if SET == "d" else 1.2   # phones: farther back, so the tripod fits a tall picture
A0 = Vector((0, 0, 4.0)); A1 = Vector((0, 0, 4.25)); END = HEAD + FACE * 1.1
cam, aim = camera(sc, [  # share, camera, aim, lens (mm), f-stop
    (0.00, tuple(A0 + (Vector((-2.2, -7.5, 4.9)) - A0) * far), tuple(A0), 40, 4.0),
    (0.50, tuple(A1 + (Vector((-1.2, -3.6, 4.55)) - A1) * far), tuple(A1), 50, 2.8),
    (1.00, tuple(END), tuple(HEAD + FACE * 0.09), 70 if SET == "d" else 55, 4.0)])
cam.data.clip_end = 30000
render(sc, "lamp", exposure=0.6, backdrop=True)
