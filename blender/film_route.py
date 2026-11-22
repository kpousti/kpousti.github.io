# Run with:  Blender -b blender/city.blend --python blender/film_route.py -- <set> [frames] [samples] [percent]     (arguments: see filmkit.py)
# The film that opens Projects: the San Diego model, and Route Engine planning the home trip on it. It is the first project itself, played before its section.
# Nothing in it is invented. blender/city_layout.json is the page's own city and the page's own A* run, written by `node blender/dump_city.mjs`: the same corners, streets and costs,
# the same buildings on the same lots, the streets in the order the search explored them (67 of 169), and the route it found (14 streets). This script only lights and films it.
# The kit pieces come from city.blend (blender/build_city.py); the streets, the search light, the route and the windows are added here.
#
# The shot, by share of the film:
#   0.00  the whole model from the bay side, as the page shows it, at dusk; one amber bead on the corner the trip starts from
#   0.05 to 0.47  the search: blue light runs along each street as A* explores it, at an even pace, in A*'s own order
#   0.50 to 0.84  the route: an amber line draws from the start corner to the goal along the cheapest way; the search dims behind it; the camera follows its head
#   1.00  low and close on the brass marker at the goal, the route arriving, the city and the bay out of focus behind
import bpy, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filmkit import *
from mathutils import Vector

sc = bpy.context.scene
C = json.load(open(os.path.join(ROOT, "blender", "city_layout.json")))
X = C["nx"]; Y = [-z for z in C["nz"]]   # the page's z runs toward the viewer; here that is -y, so the bay is on the near side
kit = {o.name[4:]: o.data for o in bpy.data.objects if o.name.startswith("kit.")}
for o in list(bpy.data.objects): bpy.data.objects.remove(o)   # the kit's own pieces leave the scene; copies of their meshes are placed below

# ---------- materials: the kit's flat colours, made fit for a close-up ----------
def M(name): return bpy.data.materials[name]
def emit(m, color, strength): b = bsdf(m); b.inputs["Emission Color" if "Emission Color" in b.inputs else "Emission"].default_value = (*color, 1); b.inputs["Emission Strength"].default_value = strength
AMBER = (1.0, 0.38, 0.06); BLUE = (0.06, 0.3, 1.0)
emit(M("lit"), (1.0, 0.58, 0.26), 2.0)
for name, metal_, rough in (("glass", 0.9, 0.08), ("water", 0.6, 0.07), ("steel", 1.0, 0.22), ("brass", 1.0, 0.2), ("dark", 0.7, 0.36), ("roof", 0.3, 0.5), ("trim", 0.5, 0.35)):
    b = bsdf(M(name)); b.inputs["Metallic"].default_value = metal_; b.inputs["Roughness"].default_value = rough
def windows(m, lit_share=0.34, su=0.011, sv=0.0125):
    """Rows of small windows on every upright face, some of them lit: sized in the model's own units, so a tower gets many rows and a low block two or three."""
    nt = m.node_tree; b = bsdf(m); geo = nt.nodes.new("ShaderNodeNewGeometry"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sp.inputs[0]); sn = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], sn.inputs[0])
    def op(kind, a, c=None, clamp=False):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = kind; n.use_clamp = clamp
        for i, v in enumerate((a, c)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    u = op("DIVIDE", op("ADD", sp.outputs["X"], sp.outputs["Y"]), su); v = op("DIVIDE", sp.outputs["Z"], sv); fu, fv = op("FRACT", u), op("FRACT", v)
    pane = op("MULTIPLY", op("MULTIPLY", op("GREATER_THAN", fu, 0.22), op("LESS_THAN", fu, 0.78)), op("MULTIPLY", op("GREATER_THAN", fv, 0.28), op("LESS_THAN", fv, 0.8)))
    wall = op("LESS_THAN", op("ABSOLUTE", sn.outputs["Z"]), 0.5); pane = op("MULTIPLY", pane, wall)
    cell = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(op("FLOOR", u), cell.inputs[0]); nt.links.new(op("FLOOR", v), cell.inputs[1]); wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"; nt.links.new(cell.outputs[0], wn.inputs["Vector"])
    on = op("MULTIPLY", pane, op("LESS_THAN", wn.outputs["Value"], lit_share))
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = "RGBA"; nt.links.new(pane, mixc.inputs["Factor"]); mixc.inputs["A"].default_value = b.inputs["Base Color"].default_value[:]; mixc.inputs["B"].default_value = (0.012, 0.016, 0.03, 1)
    nt.links.new(mixc.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Emission Color" if "Emission Color" in b.inputs else "Emission"].default_value = (1.0, 0.42, 0.12, 1); nt.links.new(op("MULTIPLY", on, op("ADD", op("MULTIPLY", wn.outputs["Value"], 4.5), 0.4)), b.inputs["Emission Strength"])   # lit panes differ: the noise that picks them (below lit_share) also sets how bright each is
for name in ("wall", "wall2", "grey", "sand", "brick", "white"): windows(M(name))
for m in bpy.data.materials:   # every edge catches a thin line of light, as on a machined scale model (rounded at render time; the meshes stay as they are)
    if m.use_nodes and any(n.type == "BSDF_PRINCIPLED" for n in m.node_tree.nodes): bv = m.node_tree.nodes.new("ShaderNodeBevel"); bv.samples = 4; bv.inputs["Radius"].default_value = 0.0012; m.node_tree.links.new(bv.outputs["Normal"], bsdf(m).inputs["Normal"])

# ---------- the model: the plate, then every piece where the page puts it ----------
def put(name, x, z, w, d, h, ang=0.0, up=0.0):
    o = bpy.data.objects.new(name, kit[name]); sc.collection.objects.link(o); o.location = (x, -z, up); o.rotation_euler = (0, 0, ang); o.scale = (w, d, h); return o
put("plate", 0, 0, 1, 1, 1)
for L in C["sites"]: put(L["kit"], L["cx"], L["cz"], L["w"], L["d"], L["h"], L["ang"])
for Q in C["parks"]: put("park", Q["cx"], Q["cz"], Q["w"], Q["d"], 0.05, Q["ang"])

# ---------- the streets, and the two lights that run along them ----------
def plain(name, color, rough, metal_=0.0): m = metal(name, color, rough); bsdf(m).inputs["Metallic"].default_value = metal_; return m
road = plain("road", (0.024, 0.03, 0.05), 0.42, 0.3); rivet = plain("rivet", (0.2, 0.22, 0.27), 0.3, 1.0)
def light(name, color, base, head, tail):
    """A line of light that draws itself. Every point of it carries the moment it comes on ('at'); the material has a clock and a dimmer. Before its moment a point is not there at all;
    at its moment it flares (head), and over 'tail' it settles to its steady glow (base). Answers the material, its clock and its dimmer."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    def op(kind, a, c=None, clamp=False):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = kind; n.use_clamp = clamp
        for i, v in enumerate((a, c)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "at"; clock = nt.nodes.new("ShaderNodeValue"); dimmer = nt.nodes.new("ShaderNodeValue"); dimmer.outputs[0].default_value = 1.0
    since = op("SUBTRACT", clock.outputs[0], at.outputs["Fac"]); on = op("GREATER_THAN", since, 0.0); flare = op("SUBTRACT", 1.0, op("DIVIDE", since, tail), clamp=True)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*color, 1); nt.links.new(op("MULTIPLY", op("ADD", base, op("MULTIPLY", op("POWER", flare, 2.0), head)), dimmer.outputs[0]), em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader"); out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(on, mx.inputs["Fac"]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m, clock.outputs[0], dimmer.outputs[0]
K = len(C["order"])
search, search_clock, search_dim = light("search", BLUE, 3.0, 12.0, 5.0)        # its clock counts streets: at 12.5 the search is half way along the thirteenth street it explored
way, way_clock, way_dim = light("way", AMBER, 2.6, 12.0, 0.07)                 # its clock is the share of the route's length drawn so far
def ribbon(m, a, b, width, z, v0=None, v1=None):   # a flat strip from a to b; with v0 and v1, the moments its two ends come on
    g = bag(m); n0 = len(g["v"]); dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); px, py = -dy / L * width / 2, dx / L * width / 2
    g["v"] += [(a[0] + px, a[1] + py, z), (a[0] - px, a[1] - py, z), (b[0] - px, b[1] - py, z), (b[0] + px, b[1] + py, z)]; g["f"].append((n0, n0 + 1, n0 + 2, n0 + 3))
    if v0 is not None: g["at"].setdefault("at", []).extend([v0, v0, v1, v1])
def tube(m, a, b, r, z, v0, v1, segs=12):   # a round bar lying along the street from a to b
    g = bag(m); n0 = len(g["v"]); dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); sx, sy = -dy / L, dx / L
    for p, v in ((a, v0), (b, v1)):
        for i in range(segs): t = math.tau * i / segs; g["v"].append((p[0] + sx * r * math.cos(t), p[1] + sy * r * math.cos(t), z + r * math.sin(t))); g["at"].setdefault("at", []).append(v)
    g["f"] += [(n0 + i, n0 + (i + 1) % segs, n0 + segs + (i + 1) % segs, n0 + segs + i) for i in range(segs)]
def ball(m, c, r, z, v, segs=12, rings=8):   # rounds the bar off at a corner of the route
    g = bag(m); n0 = len(g["v"])
    for j in range(rings + 1):
        for i in range(segs): t = math.pi * j / rings; s = math.tau * i / segs; g["v"].append((c[0] + r * math.sin(t) * math.cos(s), c[1] + r * math.sin(t) * math.sin(s), z + r * math.cos(t))); g["at"].setdefault("at", []).append(v)
    g["f"] += [(n0 + j * segs + i, n0 + (j + 1) * segs + i, n0 + (j + 1) * segs + (i + 1) % segs, n0 + j * segs + (i + 1) % segs) for j in range(rings) for i in range(segs)]
at = lambda q: (X[q], Y[q])
for e in C["edges"]: ribbon(road, at(e["a"]), at(e["b"]), 0.024, 0.0012)   # the plate's top is at 0
for q in range(len(X)): cyl(rivet, X[q], Y[q], 0.0012, 0.0075, 0.0022, 16)
# The search, replayed. The page records the streets in the order A* took them; each was entered from the end the search had already reached.
reached = {C["start"]}
for k, ei in enumerate(C["order"]):
    e = C["edges"][ei]; a, b = (e["a"], e["b"]) if e["a"] in reached else (e["b"], e["a"]); reached.add(b)
    ribbon(search, at(a), at(b), 0.009, 0.0026, k, k + 1)
# The route, by length: each corner's share of the way.
path = C["path"]; run = [0.0]
for q in range(1, len(path)): run.append(run[-1] + math.hypot(X[path[q]] - X[path[q - 1]], Y[path[q]] - Y[path[q - 1]]))
LEN = run[-1]; run = [r / LEN for r in run]; RZ, RR = 0.007, 0.0046
for q in range(1, len(path)): tube(way, at(path[q - 1]), at(path[q]), RR, RZ, run[q - 1], run[q])
for q in range(len(path)): ball(way, at(path[q]), RR, RZ, run[q])
def head(u):   # where the front of the route is when a share u of it is drawn
    u = max(0.0, min(1.0, u)); q = max(1, next((i for i in range(1, len(run)) if run[i] >= u), len(run) - 1)); t = (u - run[q - 1]) / max(1e-9, run[q] - run[q - 1])
    return Vector((mix(X[path[q - 1]], X[path[q]], t), mix(Y[path[q - 1]], Y[path[q]], t), RZ))
bead = glow("bead", AMBER, 5.0); bpy.ops.mesh.primitive_uv_sphere_add(radius=0.013, location=(X[C["start"]], Y[C["start"]], 0.0145), segments=32, ring_count=16); bpy.context.object.data.materials.append(bead); bpy.ops.object.shade_smooth()   # the corner the trip starts from
G = Vector((X[C["goal"]], Y[C["goal"]], 0.0))
build(sc, smooth=("rivet", "way"), sharp=("road", "search", "way", "rivet"))
# The brass marker at the goal. The kit's own pin is a few flat faces, made to be seen an inch high; the film ends close on it, so here it is turned round: a ball on a cone on a foot, the kit pin's size.
R, zc, th0 = 0.023, 0.061, math.asin(0.0155 / 0.023)
turned(M("brass"), [(0.0, 0.0), (0.0235, 0.0), (0.0235, 0.0022), (0.0215, 0.003), (0.0035, 0.003), (0.0035, 0.006), (0.0155, zc - R * math.cos(th0))] + [(R * math.sin(t), zc - R * math.cos(t)) for t in [th0 + (math.pi - th0) * i / 28 for i in range(1, 29)]])
pin = build(sc, smooth=("brass",), sharp=("brass",))[0]; pin.location = (G.x, G.y, 0.002)

SEARCH = (0.05, 0.47); ROUTE = (0.50, 0.84)
def lin(p, a, b): return max(0.0, min(1.0, (p - a) / (b - a)))
def pose(scene, *a):
    p = share(scene)
    search_clock.default_value = K * lin(p, *SEARCH)                         # an even pace: every street takes the same time, in A*'s order
    search_dim.default_value = mix(1.0, 0.16, smooth(lin(p, ROUTE[0] - 0.02, ROUTE[0] + 0.18)))   # once the route is found, the search steps back
    way_clock.default_value = mix(-0.001, 1.001, lin(p, *ROUTE))
bpy.app.handlers.frame_change_pre.append(pose)

# ---------- light and camera: dusk, a low warm key from the west as on the page, a cool rim from behind; the streets' own light does the rest ----------
studio(sc, 0.36, 200)
lamp(sc, "key", (-3.0, -1.6, 1.5), 380, (1.0, 0.72, 0.46), 1.8); lamp(sc, "rim", (2.4, 2.8, 1.6), 190, (0.5, 0.68, 1.0), 1.6); lamp(sc, "top", (0.0, -0.4, 3.2), 70, (0.72, 0.8, 1.0), 3.0)
S = Vector((X[C["start"]], Y[C["start"]], 0.02)); far = 1.0 if SET == "d" else 1.45   # phones: farther back, so the square model fits a tall picture
def back(cam, aim, k=None): c, a = Vector(cam), Vector(aim); return tuple(a + (c - a) * (far if k is None else k)), tuple(a)
shots = [  # share, camera, aim, lens (mm), f-stop
    (0.00, *back((0.5, -4.4, 2.5), (0.0, -0.05, 0.0)), 50, 5.6),
    (0.24, *back((-2.1, -2.7, 1.25), (-0.35, -0.2, 0.0)), 45, 4.0),
    (0.50, *back((-2.0, -1.3, 0.7), S), 50, 4.0),
    (0.67, *back((-1.3, 0.75, 0.5), head(0.5)), 50, 2.8),
    (0.84, *back((0.35, 1.5, 0.3), G + Vector((0, 0, 0.03))), 55, 2.8),
    (1.00, *back(G + Vector((0.25, 0.43, 0.13)), G + (Vector((0.043, -0.025, 0.062)) if SET == "d" else Vector((0, 0, 0.045))), 1.0 if SET == "d" else 1.15), 70, 2.8)]   # computers: aimed beside and above the marker, so it stands right of centre and low, clear of the chapter's name that comes up over this picture
if SET == "p":   # phones: a square model cannot fill a tall picture from the side, so the film opens looking down on it, from the bay up to the far edge
    shots[0] = (0.00, (-0.2, -3.1, 3.3), (-0.15, -0.15, 0.0), 35, 5.6); shots[1] = (0.24, (-1.9, -2.9, 2.2), (-0.4, -0.2, 0.0), 40, 4.0)
cam, aim = camera(sc, shots)
render(sc, "route")
