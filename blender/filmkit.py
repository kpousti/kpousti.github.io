# Shared by the section films (film_turbine.py, film_armillary.py): arguments, light, camera keys and the render loop.
# film_galton.py came first and keeps its own copy of the same steps.
#   Blender -b [file.blend] --python blender/film_<name>.py -- <set> [frames] [samples] [percent]
#   <set>     d (computers: 1920 x 1080, 120 frames) or p (phones: 720 x 1280, 80 frames)
#   [frames]  "all" (default), a list such as 1,40,75, or a range such as 1-40 (so several Blenders can share one film)
#   [samples] Cycles samples per pixel (default 64)
#   [percent] picture size as a percentage, for quick drafts (default 100); drafts go to film/<name>/draft-<set>/
# Pictures go to film/<name>/<set>/0001.webp ... with no background: the page's own sky shows through, as in the opening film.
import bpy, math, os, sys, time
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SET = argv[0] if argv else "d"
assert SET in ("d", "p"), "set must be d or p"
N = 120 if SET == "d" else 80
def _frames(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-"); out += range(int(a), int(b or a) + 1)
    return out
ONLY = None if len(argv) < 2 or argv[1] == "all" else _frames(argv[1])
SAMPLES = int(argv[2]) if len(argv) > 2 else 64
PERCENT = int(argv[3]) if len(argv) > 3 else 100
W, H = (1920, 1080) if SET == "d" else (720, 1280)

def smooth(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def mix(a, b, t): return a + (b - a) * t
def share(scene): return (scene.frame_current - 1) / (N - 1)   # how far through the film this frame is, 0 to 1

def bsdf(m): return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
def metal(name, color, rough, grain=0.0, scale=40.0):
    """A metal whose roughness wanders a little (grain), so a close-up is not one flat sheen."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; b = bsdf(m)
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = 1; b.inputs["Roughness"].default_value = rough
    if grain:
        nt = m.node_tree; nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 6
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = max(0.02, rough - grain); mr.inputs["To Max"].default_value = rough + grain
        tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    return m

# ---------- many small solid parts, gathered per material and then made into one object each (film_circuit.py, film_phone.py) ----------
GEO = {}
def bag(m): return GEO.setdefault(m.name, {"mat": m, "v": [], "f": [], "at": {}})
def box(m, x, y, z0, sx, sy, sz, rot=0.0):
    g = bag(m); n0 = len(g["v"]); c, s = math.cos(rot), math.sin(rot)
    for dz in (0, sz):
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)): lx, ly = dx * sx / 2, dy * sy / 2; g["v"].append((x + lx * c - ly * s, y + lx * s + ly * c, z0 + dz))
    g["f"] += [tuple(n0 + i for i in f) for f in ((3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))]
def cyl(m, x, y, z0, r, h, segs=40):
    g = bag(m); n0 = len(g["v"])
    for dz in (0, h): g["v"] += [(x + r * math.cos(math.tau * i / segs), y + r * math.sin(math.tau * i / segs), z0 + dz) for i in range(segs)]
    g["f"] += [(n0 + i, n0 + (i + 1) % segs, n0 + segs + (i + 1) % segs, n0 + segs + i) for i in range(segs)] + [tuple(n0 + segs + i for i in range(segs))] + [tuple(n0 + segs - 1 - i for i in range(segs))]
def rrect(w, h, r, segs=10):   # the outline of a rectangle with rounded corners, anticlockwise
    out = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        out += [(cx + r * math.cos(math.radians(a0 + 90 * k / segs)), cy + r * math.sin(math.radians(a0 + 90 * k / segs))) for k in range(segs + 1)]
    return out
def slab(m, outline, z0, h, hole=None):   # an outline pushed up into a plate; with a hole outline (same number of points) it is a frame
    g = bag(m); n0 = len(g["v"]); n = len(outline)
    for z in (z0, z0 + h): g["v"] += [(x, y, z) for x, y in outline]
    g["f"] += [(n0 + i, n0 + (i + 1) % n, n0 + n + (i + 1) % n, n0 + n + i) for i in range(n)]
    if hole is None: g["f"] += [tuple(n0 + n + i for i in range(n)), tuple(n0 + n - 1 - i for i in range(n))]
    else:
        m0 = len(g["v"])
        for z in (z0, z0 + h): g["v"] += [(x, y, z) for x, y in hole]
        g["f"] += [(m0 + (i + 1) % n, m0 + i, m0 + n + i, m0 + n + (i + 1) % n) for i in range(n)]   # the inside wall
        g["f"] += [(n0 + n + i, n0 + n + (i + 1) % n, m0 + n + (i + 1) % n, m0 + n + i) for i in range(n)] + [(n0 + (i + 1) % n, n0 + i, m0 + i, m0 + (i + 1) % n) for i in range(n)]   # top and bottom rings
def build(sc, smooth=(), sharp=(), parent=None, edge=0.0012):
    """Makes one object per material from everything gathered so far, and starts a new gathering. smooth: materials shaded round; sharp: materials whose edges are not rounded off."""
    global GEO
    made = []
    for name, g in GEO.items():
        me = bpy.data.meshes.new(name); me.from_pydata(g["v"], [], g["f"]); me.materials.append(g["mat"])
        for an, vals in g["at"].items(): me.attributes.new(an, "FLOAT", "POINT").data.foreach_set("value", vals)
        me.polygons.foreach_set("use_smooth", [name in smooth] * len(me.polygons))
        if name in smooth: me.set_sharp_from_angle(angle=math.radians(40))
        me.update(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.parent = parent; made.append(o)
        if name not in sharp: b = o.modifiers.new("edge", "BEVEL"); b.width = edge; b.segments = 2; b.limit_method = "ANGLE"; b.angle_limit = math.radians(40)
    GEO = {}
    return made

def glow(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = bsdf(m); b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Emission Color" if "Emission Color" in b.inputs else "Emission"].default_value = (*color, 1); b.inputs["Emission Strength"].default_value = strength; return m
def pulse_metal():
    """Gold traces with pulses of light running along them. Each trace's vertices carry how far along it they are (u), its own offset (ph) and its colour (hue: 0 amber, 1 blue).
    Answers the material and its clock: set clock.default_value each frame to move the pulses."""
    trace = metal("trace", (0.86, 0.6, 0.24), 0.3); nt = trace.node_tree; tb = bsdf(trace)
    def attr(n): a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = n; return a.outputs["Fac"]
    def op(kind, a, b=None):
        m = nt.nodes.new("ShaderNodeMath"); m.operation = kind
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): m.inputs[i].default_value = v
            else: nt.links.new(v, m.inputs[i])
        return m.outputs[0]
    clockv = nt.nodes.new("ShaderNodeValue")
    head = op("POWER", op("FRACT", op("ADD", op("SUBTRACT", op("MULTIPLY", attr("u"), 0.8), clockv.outputs[0]), attr("ph"))), 9)   # a bright head with a short tail, repeating along the trace
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = "RGBA"; nt.links.new(attr("hue"), mixc.inputs["Factor"]); mixc.inputs["A"].default_value = (1.0, 0.5, 0.12, 1); mixc.inputs["B"].default_value = (0.35, 0.58, 1.0, 1)
    nt.links.new(mixc.outputs["Result"], tb.inputs["Emission Color" if "Emission Color" in tb.inputs else "Emission"]); nt.links.new(op("ADD", op("MULTIPLY", head, 26), 0.1), tb.inputs["Emission Strength"])
    return trace, clockv.outputs[0]
def pins(tin, x, y, w, l, n, rot, sides, z=0.001):   # gull-wing legs along the chosen sides of a w by l chip body
    c, s = math.cos(rot), math.sin(rot)
    for side in sides:
        along, out = (w, l / 2) if side in (0, 2) else (l, w / 2)
        for i in range(n):
            t = (i + 0.5) / n - 0.5; lx, ly = (t * along * 0.86, (out + 0.008) * (1 if side == 0 else -1)) if side in (0, 2) else ((out + 0.008) * (1 if side == 1 else -1), t * along * 0.86)
            box(tin, x + lx * c - ly * s, y + lx * s + ly * c, z, 0.007 if side in (0, 2) else 0.02, 0.02 if side in (0, 2) else 0.007, 0.006, rot)
def chip2(body, tin, x, y, rot=0.0, k=1.0, z=0.001):   # a two-ended part: a small capacitor or resistor
    c, s = math.cos(rot), math.sin(rot); box(body, x, y, z, 0.02 * k, 0.016 * k, 0.013 * k, rot)
    for e in (-1, 1): box(tin, x + e * 0.0135 * k * c, y + e * 0.0135 * k * s, z, 0.008 * k, 0.0166 * k, 0.0136 * k, rot)
def shifted(pts, off):   # the same path moved sideways by off, corners mitred
    out = []
    for i, p in enumerate(pts):
        ns = []; segs = ([(pts[i - 1], p)] if i else []) + ([(p, pts[i + 1])] if i < len(pts) - 1 else [])
        for a, b in segs: L = math.hypot(b[0] - a[0], b[1] - a[1]); ns.append((-(b[1] - a[1]) / L, (b[0] - a[0]) / L))
        nx, ny = (ns[0][0] + ns[-1][0]), (ns[0][1] + ns[-1][1]); k = off / (1 + ns[0][0] * ns[-1][0] + ns[0][1] * ns[-1][1]) if len(ns) == 2 else off / 2
        out.append((p[0] + nx * k, p[1] + ny * k))
    return out
def bus(trace, pts, lanes, pitch, z, hue, rnd, width=0.006):
    """A bus of parallel traces along the path pts, as flat ribbons of the pulse_metal material. Answers both ends of every lane (for vias)."""
    tg = bag(trace); at = tg["at"]; ends = []
    for an in ("u", "ph", "hue"): at.setdefault(an, [])
    for j in range(lanes):
        off = (j - (lanes - 1) / 2) * pitch; mid = shifted(pts, off); a, b = shifted(pts, off - width / 2), shifted(pts, off + width / 2); n0 = len(tg["v"]); u = 0.0; ph = rnd.random()
        for i in range(len(mid)):
            if i: u += math.hypot(mid[i][0] - mid[i - 1][0], mid[i][1] - mid[i - 1][1])
            tg["v"] += [(a[i][0], a[i][1], z), (b[i][0], b[i][1], z)]; at["u"] += [u, u]; at["ph"] += [ph, ph]; at["hue"] += [hue, hue]
            if i: tg["f"].append((n0 + 2 * i - 2, n0 + 2 * i - 1, n0 + 2 * i + 1, n0 + 2 * i))
        ends += [mid[0], mid[-1]]
    return ends

def studio(sc, strength=0.55, turn=200):
    """Blender's own sunset sky for the reflections, low sun behind and to the left: warm edges, like the page's dusk."""
    world = bpy.data.worlds.new("film"); sc.world = world; world.use_nodes = True; nt = world.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    hdr = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.join(os.path.dirname(bpy.app.binary_path), "..", "Resources")) for f in fn if f == "sunset.exr"]
    env.image = bpy.data.images.load(hdr[0]); bg = next(n for n in nt.nodes if n.type == "BACKGROUND"); nt.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = strength
    mp = nt.nodes.new("ShaderNodeMapping"); tc = nt.nodes.new("ShaderNodeTexCoord"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(turn))
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])

def dusk(sc, elevation, strength):
    """Blender's own sky as light and as backdrop, the sun low in the +Y direction: a few degrees up is sunset, a few degrees under the horizon is blue hour. Answers the sky node (its sun_elevation can be changed each frame)."""
    w = bpy.data.worlds.new("dusk"); sc.world = w; w.use_nodes = True; nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky"); bg = next(n for n in nt.nodes if n.type == "BACKGROUND"); nt.links.new(sky.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = strength
    sky.sun_elevation = math.radians(elevation); sky.sun_rotation = 0; sky.sun_size = math.radians(1.0); sky.sun_intensity = 0.5; sky.air_density = 1.4; sky.aerosol_density = 2.5; sky.ozone_density = 2.5
    return sky
def sea(sc, wave=1.6, wind=8.0, chop=1.3):
    """An ocean, 300 m square round the origin with still water under it out to the horizon. Answers the ocean modifier: set its .time each frame to move the waves."""
    bpy.ops.mesh.primitive_plane_add(size=2); o = bpy.context.object; o.name = "sea"; m = o.modifiers.new("ocean", "OCEAN")
    m.geometry_mode = "GENERATE"; m.repeat_x = 6; m.repeat_y = 6; m.resolution = 12; m.spatial_size = 50; m.size = 1.0; m.wave_scale = wave; m.choppiness = chop; m.wind_velocity = wind; m.wave_scale_min = 0.02; m.wave_alignment = 0.6; m.wave_direction = math.radians(90)
    o.location = (-150, -150, 0)
    mat = bpy.data.materials.new("water"); mat.use_nodes = True; mn = mat.node_tree; b = bsdf(mat); b.inputs["Base Color"].default_value = (0.003, 0.01, 0.018, 1); b.inputs["Roughness"].default_value = 0.02; b.inputs["IOR"].default_value = 1.33
    nz = mn.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 8; bump = mn.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.05   # fine ripples the wave mesh is too coarse for
    tc = mn.nodes.new("ShaderNodeTexCoord"); mn.links.new(tc.outputs["Object"], nz.inputs["Vector"]); mn.links.new(nz.outputs["Fac"], bump.inputs["Height"]); mn.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    o.data.materials.append(mat); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_plane_add(size=20000, location=(0, 0, -3.0)); bpy.context.object.data.materials.append(mat)
    return m
def turned(m, profile, segs=96):   # an outline (radius, height) swept round the Z axis, added to the gathering
    g = bag(m); n0 = len(g["v"]); n = len(profile)
    for s in range(segs): a = math.tau * s / segs; g["v"] += [(r * math.cos(a), r * math.sin(a), z) for r, z in profile]
    g["f"] += [(n0 + s * n + i, n0 + ((s + 1) % segs) * n + i, n0 + ((s + 1) % segs) * n + i + 1, n0 + s * n + i + 1) for s in range(segs) for i in range(n - 1)]
def rod(sc, m, a, b, r, segs=24, parent=None):   # a round bar from a to b, as its own object
    a, b = Vector(a), Vector(b); L = (b - a).length; v = [(r * math.cos(math.tau * i / segs), r * math.sin(math.tau * i / segs), z) for z in (0, L) for i in range(segs)]
    f = [(i, (i + 1) % segs, segs + (i + 1) % segs, segs + i) for i in range(segs)] + [tuple(segs + i for i in range(segs)), tuple(segs - 1 - i for i in range(segs))]
    me = bpy.data.meshes.new("rod"); me.from_pydata(v, [], f); me.materials.append(m); me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.set_sharp_from_angle(angle=math.radians(40))
    o = bpy.data.objects.new("rod", me); sc.collection.objects.link(o); o.parent = parent; o.location = a; o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler(); return o
def lamp(sc, name, loc, energy, color, size, at=(0, 0, 0)):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.color = color; d.size = size; o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o

def camera(sc, shots):
    """shots: (share of the film, camera place, what it looks at, lens in mm, f-stop). One continuous move through them; focus stays on what it looks at."""
    cam_d = bpy.data.cameras.new("film"); cam = bpy.data.objects.new("film", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    aim = bpy.data.objects.new("aim", None); sc.collection.objects.link(aim)
    tr = cam.constraints.new("TRACK_TO"); tr.target = aim; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
    cam_d.sensor_fit = "VERTICAL" if SET == "p" else "AUTO"; cam_d.dof.use_dof = True; cam_d.dof.focus_object = aim; cam_d.clip_start = 0.01
    for (p, c, a, lens, fs) in shots:
        f = 1 + p * (N - 1); cam.location = c; aim.location = a; cam_d.lens = lens; cam_d.dof.aperture_fstop = fs
        cam.keyframe_insert("location", frame=f); aim.keyframe_insert("location", frame=f); cam_d.keyframe_insert("lens", frame=f); cam_d.dof.keyframe_insert("aperture_fstop", frame=f)
    return cam, aim

def render(sc, name, exposure=-0.25, backdrop=False):   # backdrop: the film has its own sky, so its pictures are plain ones (no see-through)
    sc.frame_start, sc.frame_end = 1, N
    r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y, r.resolution_percentage = W, H, PERCENT; r.film_transparent = not backdrop
    r.image_settings.file_format = "WEBP"; r.image_settings.color_mode = "RGB" if backdrop else "RGBA"; r.image_settings.quality = (64 if SET == "d" else 62) if backdrop else (72 if SET == "d" else 68)   # see-through pictures are saved again later by film_flatten.py
    cy = sc.cycles; cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.03; cy.use_denoising = True; cy.max_bounces = 6; cy.glossy_bounces = 4; cy.transmission_bounces = 6; cy.caustics_reflective = False; cy.caustics_refractive = False
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()
        for d in prefs.devices: d.use = True
        cy.device = "GPU" if PERCENT == 100 else "CPU"   # drafts run on the processor, so one can be made while a full render has the GPU (two renders on this Mac's GPU run it out of memory)
    except Exception as e: print("no GPU:", e)
    try: sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - High Contrast"; sc.view_settings.exposure = exposure
    except Exception as e: print("view:", e)
    out = os.path.join(ROOT, "film", name, SET if PERCENT == 100 else "draft-" + SET); os.makedirs(out, exist_ok=True)
    for f in (ONLY or range(1, N + 1)):
        t0 = time.time(); sc.frame_set(f); r.filepath = os.path.join(out, f"{f:04d}.webp"); bpy.ops.render.render(write_still=True)
        print(f"frame {f}/{N}: {time.time() - t0:.1f}s, {os.path.getsize(r.filepath) // 1024} KB", flush=True)
