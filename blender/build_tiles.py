# Run with:  Blender -b --python blender/build_tiles.py [-- name ...]
# Models and renders the pictures for the "Away from the keyboard" boxes into renders/: sports, boards, cars, family, reading, markets.
# Each picture is its own small scene, drawn with real meshes (bevels, subdivision) and rendered with Cycles. Nothing here is a photo and nothing is traced from one.
import bpy, bmesh, math, os, random, sys
from mathutils import Vector

ROOT = "/Users/kiapousti/Documents/kpousti.github.io"
INK = 0x0b0d14

def lin(h): return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in [((h >> s) & 255) / 255 for s in (16, 8, 0)])
def mat(name, rgb, metal=0.0, rough=0.5, emit=0.0, coat=0.0, glass=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); i = b.inputs
    i["Base Color"].default_value = (*lin(rgb), 1); i["Metallic"].default_value = metal; i["Roughness"].default_value = rough
    if emit: i["Emission Color"].default_value = (*lin(rgb), 1); i["Emission Strength"].default_value = emit
    if coat: i["Coat Weight"].default_value = coat; i["Coat Roughness"].default_value = 0.05
    if glass: i["Transmission Weight"].default_value = glass; i["IOR"].default_value = 1.33
    return m
def link(o): bpy.context.scene.collection.objects.link(o); return o
def mesh(name, bm, mats, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    if smooth: me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    o = link(bpy.data.objects.new(name, me)); o.location = loc; o.rotation_euler = rot; o.scale = scale; return o
def box(name, size, m, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); o = mesh(name, bm, [m], loc, rot, size, smooth=False)
    if bevel: mod(o, 'BEVEL', width=bevel, segments=3)
    return o
def cyl(name, r, depth, m, loc=(0, 0, 0), rot=(0, 0, 0), seg=40, r2=None, bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=depth); o = mesh(name, bm, [m], loc, rot)
    for p in o.data.polygons: p.use_smooth = len(p.vertices) == 4
    if bevel: mod(o, 'BEVEL', width=bevel, segments=3)
    return o
def ball(name, r, m, loc=(0, 0, 0), scale=(1, 1, 1), sub=3):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r); return mesh(name, bm, [m], loc, (0, 0, 0), scale)
def mod(o, kind, **kw):
    m = o.modifiers.new(kind.lower(), kind)
    for k, v in kw.items(): setattr(m, k, v)
    return m
def grid(name, nx, ny, f, mats, pick=None, **kw):
    """a surface from f(u, v) -> (x, y, z), u and v in 0..1"""
    bm = bmesh.new(); vs = [[bm.verts.new(f(i / nx, j / ny)) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny): fc = bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1])); fc.material_index = pick(i, j) if pick else 0
    return mesh(name, bm, mats, **kw)
def light(loc, energy, color, size, aim=(0, 0, 0)):
    d = bpy.data.lights.new("light", 'AREA'); d.energy = energy; d.color = color; d.size = size
    o = link(bpy.data.objects.new("light", d)); o.location = loc; o.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
def stage(cam, aim, lens=70, floor=True, key=60):
    bpy.ops.wm.read_homefile(use_empty=True); sc = bpy.context.scene
    w = bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
    next(nd for nd in w.node_tree.nodes if nd.type == "BACKGROUND").inputs[0].default_value = (*lin(INK), 1)
    if floor: box("floor", (30, 30, 0.02), mat("floor", INK, 0.0, 0.3), (0, 0, -0.01))
    light((-1.4, -1.6, 1.8), key, (1.0, 0.84, 0.66), 1.6, aim); light((1.6, 1.2, 1.0), key * 0.8, (0.5, 0.66, 1.0), 1.4, aim); light((0.3, -2.0, 0.3), key * 0.15, (1, 1, 1), 2.0, aim)
    c = bpy.data.cameras.new("cam"); c.lens = lens; co = link(bpy.data.objects.new("cam", c)); co.location = cam
    co.rotation_euler = (Vector(aim) - Vector(cam)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
    return sc
def render(name):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 96; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1000, 500
    try: sc.view_settings.view_transform = 'Standard'
    except Exception as e: print(e)
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 84
    sc.render.filepath = os.path.join(ROOT, "renders", name + ".jpg"); bpy.ops.render.render(write_still=True)
    print("rendered", name, os.path.getsize(sc.render.filepath))

def panels(name, bm, cols, r, loc, rot):
    """a ball sewn from flat panels: every panel gets a dark seam round it, then the whole thing is rounded onto a sphere"""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    rim = bmesh.ops.inset_individual(bm, faces=bm.faces[:], thickness=0.03, depth=0.0)["faces"]
    for f in rim: f.material_index = len(cols)
    o = mesh(name, bm, cols + [mat("seam", 0x15171c, 0, 0.7)], loc, rot, (r, r, r))
    mod(o, 'SUBSURF', subdivision_type='SIMPLE', levels=3, render_levels=3); mod(o, 'CAST', factor=1.0, size=1.0, use_radius_as_size=False)  # in the mesh's own units, before the object's scale; mod(o, 'SUBSURF', levels=1, render_levels=2)
    return o

def sports():  # a basketball, a soccer ball and a volleyball
    stage((0, -2.5, 0.42), (0, 0, 0.115), 85)
    # soccer ball: an icosahedron with its corners cut off is the 12 pentagons and 20 hexagons of the real ball
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
    bmesh.ops.bevel(bm, geom=bm.verts[:], offset=1.0515 / 3, offset_type='OFFSET', segments=1, affect='VERTICES')
    for f in bm.faces: f.material_index = 1 if len(f.verts) == 5 else 0
    panels("soccer", bm, [mat("white", 0xf2f2ee, 0, 0.35), mat("black", 0x17181c, 0, 0.35)], 0.11, (0, 0.03, 0.11), (0.4, 0.2, 0.3))
    # volleyball: six faces of three strips each, the strips turning from face to face
    bm = bmesh.new()
    for a in range(3):
        for s in (-1, 1):
            for k in range(3):
                c0, c1 = -1 + 2 * k / 3, -1 + 2 * (k + 1) / 3; q = []
                for (b, c) in ((-1, c0), (1, c0), (1, c1), (-1, c1)): p = [0, 0, 0]; p[a] = s; p[(a + 1) % 3] = b; p[(a + 2) % 3] = c; q.append(bm.verts.new(p))
                bm.faces.new(q).material_index = (a + k) % 3
    panels("volley", bm, [mat("vyellow", 0xf2c530, 0, 0.4), mat("vblue", 0x2c5fb4, 0, 0.4), mat("vwhite", 0xf4f4f0, 0, 0.4)], 0.105, (0.29, -0.08, 0.105), (0.5, 0.3, 0.9))
    # basketball: pebbled orange rubber and its black channels
    m = mat("orange", 0xc8601e, 0, 0.55); nt = m.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 260; bu = nt.nodes.new("ShaderNodeBump"); bu.inputs["Strength"].default_value = 0.35
    nt.links.new(vo.outputs["Distance"], bu.inputs["Height"]); nt.links.new(bu.outputs["Normal"], b.inputs["Normal"])
    bb = ball("basket", 0.12, m, (-0.3, -0.06, 0.12), sub=5); bb.rotation_euler = (0.5, 0.35, 0.4); ch = mat("channel", 0x121316, 0, 0.6)
    for (rr, y, rx) in ((1.0, 0, 0), (1.0, 0, math.pi / 2), (0.79, 0.62, math.pi / 2), (0.79, -0.62, math.pi / 2)):
        bm = bmesh.new(); t = bpy.data.meshes.new("t"); bpy.ops.mesh.primitive_torus_add(major_radius=rr * 0.12, minor_radius=0.0016, major_segments=96, minor_segments=8)
        o = bpy.context.object; o.data.materials.append(ch); o.parent = bb; o.location = (0, y * 0.12, 0); o.rotation_euler = (rx, 0, 0); bm.free()
    render("sports")

def boards():  # a surfboard and a skateboard
    stage((0.3, -4.4, 2.3), (0.03, -0.05, 0.08), 75)
    def surf(u, v):
        w = 0.25 * math.sin(math.pi * (0.07 + 0.93 * u)) ** 0.6; y = w * (2 * v - 1)
        return (-0.95 + 1.9 * u, y, 0.07 * (2 * u - 1) ** 2 + 0.06 * u ** 4 - 0.012 * (2 * v - 1) ** 2)
    o = grid("surfboard", 48, 10, surf, [mat("foam", 0xf0eadc, 0, 0.18, coat=1), mat("stripe", 0xe2a23c, 0, 0.18, coat=1), mat("pin", 0x2a4f9a, 0, 0.18, coat=1)],
             pick=lambda i, j: 1 if 4 <= j <= 5 else 2 if j in (3, 6) and i % 48 < 48 else 0, loc=(0, 0.32, 0.16), rot=(0.12, 0.0, 0.32))
    mod(o, 'SOLIDIFY', thickness=0.055, offset=0); mod(o, 'SUBSURF', levels=2, render_levels=2)
    for (x, y, a) in ((-0.78, 0, 0), (-0.66, 0.11, 0.12), (-0.66, -0.11, -0.12)):
        f = grid("fin", 8, 6, lambda u, v: (0.11 * u - 0.07 * v * v - 0.02, 0, -0.11 * v * (1 - 0.35 * u)), [mat("fin", 0x16181d, 0, 0.3)]); f.parent = o; f.location = (x, y, 0.03); f.rotation_euler = (0, 0, a); mod(f, 'SOLIDIFY', thickness=0.006)
    def deck(u, v):
        e = max(0.0, (abs(2 * u - 1) - 0.72) / 0.28); w = 0.105 * math.sqrt(max(0.0, 1 - e * e * 0.92))
        return (-0.41 + 0.82 * u, w * (2 * v - 1), 0.062 + 0.07 * e * e + 0.006 * (2 * v - 1) ** 2)
    d = grid("deck", 40, 8, deck, [mat("grip", 0x101114, 0, 0.95), mat("maple", 0xb98a55, 0, 0.45)], loc=(0.1, -0.42, 0), rot=(0, 0, -0.18))
    mod(d, 'SOLIDIFY', thickness=0.012, offset=-1, material_offset=1, material_offset_rim=1); mod(d, 'SUBSURF', levels=2, render_levels=2)
    steel = mat("steel", 0xaab6cc, 0.9, 0.3); ure = mat("urethane", 0xe9a348, 0, 0.3)
    for x in (-0.25, 0.25):
        for p in (box("base", (0.07, 0.05, 0.008), steel, (x, 0, 0.046), bevel=0.002), box("hanger", (0.03, 0.15, 0.022), steel, (x, 0, 0.032), bevel=0.006), cyl("axle", 0.004, 0.25, steel, (x, 0, 0.027), (math.pi / 2, 0, 0), 12)): p.parent = d
        for y in (-0.113, 0.113): wh = cyl("wheel", 0.027, 0.034, ure, (x, y, 0.027), (math.pi / 2, 0, 0), 48, bevel=0.008); wh.parent = d
    render("boards")

def cars():  # detailing: a ceramic-coated panel beading water, with the clay bar, the applicator and the coating
    stage((0.0, -2.0, 1.0), (0, 0.0, -0.02), 60, floor=False, key=60)
    def z(x, y): return -0.12 * x * x - 0.35 * y * y
    o = grid("panel", 60, 40, lambda u, v: (-1.6 + 3.2 * u, -0.9 + 1.8 * v, z(-1.6 + 3.2 * u, -0.9 + 1.8 * v)), [mat("paint", 0x0c2f66, 0.75, 0.12, coat=1)]); mod(o, 'SUBSURF', levels=2, render_levels=2)
    random.seed(4); water = mat("water", 0xffffff, 0, 0.0, glass=1.0); drop = None
    for k in range(520):
        x, y, r = random.uniform(-1.0, 1.0), random.uniform(-0.45, 0.55), random.choice((0.004, 0.006, 0.006, 0.009, 0.013, 0.018))
        if 0.1 < x < 0.7 and -0.32 < y < 0.14: continue  # where the kit sits
        if drop is None: drop = ball("drop", 1, water, sub=3)
        d = drop if k == 0 else link(bpy.data.objects.new("drop", drop.data)); d.location = (x, y, z(x, y) + r * 0.25); d.scale = (r, r, r * 0.62)
    box("clay", (0.16, 0.1, 0.035), mat("clay", 0x3f78c2, 0, 0.55), (0.22, -0.02, z(0.22, 0) + 0.02), (0, 0, 0.3), bevel=0.012)
    box("pad", (0.13, 0.08, 0.04), mat("foam", 0x18191d, 0, 0.95), (0.4, -0.17, z(0.4, -0.17) + 0.022), (0, 0, -0.4), bevel=0.01)
    box("suede", (0.132, 0.082, 0.004), mat("suede", 0x8a93a6, 0, 0.9), (0.4, -0.17, z(0.4, -0.17) + 0.044), (0, 0, -0.4))
    gl = mat("bottle", 0x6b3a12, 0, 0.05, glass=0.85); zz = z(0.56, 0.02)
    cyl("bottle", 0.035, 0.11, gl, (0.56, 0.02, zz + 0.055), bevel=0.006); cyl("neck", 0.013, 0.03, gl, (0.56, 0.02, zz + 0.125)); cyl("cap", 0.017, 0.035, mat("cap", 0x111214, 0, 0.4), (0.56, 0.02, zz + 0.155), bevel=0.003)
    light((0, 1.4, 1.1), 40, (1, 1, 1), 2.2, (0, 0.3, 0))  # one long soft light overhead, for the stripe of shine along the paint
    render("cars")

def family():  # a small house at dusk with its lights on
    stage((2.3, -3.6, 1.15), (0, -0.1, 0.27), 70, key=16)
    wall = mat("wall", 0xd9cfc0, 0, 0.8); roof = mat("roof", 0x39424f, 0, 0.6); wood = mat("wood", 0x7a5a3c, 0, 0.6); glow = mat("glow", 0xffc070, 0, 0.5, emit=3.5); trim = mat("trim", 0xf3efe6, 0, 0.6)
    box("lawn", (2.6, 2.0, 0.02), mat("lawn", 0x21402c, 0, 0.9), (0, 0, 0.01), bevel=0.008)
    box("house", (0.8, 0.56, 0.36), wall, (0, 0, 0.2), bevel=0.004)
    bm = bmesh.new(); pts = [(-0.46, -0.33, 0.38), (0.46, -0.33, 0.38), (0.46, 0.33, 0.38), (-0.46, 0.33, 0.38), (-0.46, 0, 0.66), (0.46, 0, 0.66)]; v = [bm.verts.new(p) for p in pts]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4), (3, 2, 1, 0)): bm.faces.new([v[k] for k in f])
    r = mesh("roof", bm, [roof], smooth=False); mod(r, 'BEVEL', width=0.006, segments=2)
    box("chimney", (0.09, 0.09, 0.3), mat("brick", 0x8a4a3a, 0, 0.8), (0.22, 0.12, 0.62), bevel=0.004)
    box("door", (0.11, 0.012, 0.21), wood, (-0.02, -0.283, 0.125), bevel=0.003); box("step", (0.2, 0.1, 0.03), trim, (-0.02, -0.33, 0.035), bevel=0.004); ball("knob", 0.007, mat("brass", 0xd9a54a, 0.9, 0.3), (0.02, -0.292, 0.12))
    for (x, zc) in ((-0.26, 0.23), (0.22, 0.23)):
        box("frame", (0.16, 0.014, 0.15), trim, (x, -0.282, zc), bevel=0.002); box("pane", (0.135, 0.016, 0.125), glow, (x, -0.283, zc)); box("bar", (0.006, 0.02, 0.125), trim, (x, -0.284, zc)); box("bar", (0.135, 0.02, 0.006), trim, (x, -0.284, zc))
    for y in (-0.12, 0.12): box("frame", (0.014, 0.15, 0.15), trim, (0.402, y, 0.23), bevel=0.002); box("pane", (0.016, 0.125, 0.125), glow, (0.403, y, 0.23))
    box("attic", (0.016, 0.1, 0.08), glow, (0.462, 0, 0.5))
    for k in range(34):
        x = -1.1 + 2.2 * k / 33
        if abs(x + 0.02) > 0.14: box("picket", (0.03, 0.012, 0.13), trim, (x, -0.72, 0.085), bevel=0.003)
    for zc in (0.06, 0.12): box("rail", (0.95, 0.008, 0.014), trim, (-0.63, -0.714, zc)); box("rail", (0.95, 0.008, 0.014), trim, (0.6, -0.714, zc))
    for k in range(7): box("path", (0.16, 0.085, 0.012), mat("stone" + str(k), 0x8d8f96, 0, 0.8), (-0.02 + 0.012 * math.sin(k * 2.1), -0.41 - 0.1 * k * 0.42, 0.024), (0, 0, 0.1 * math.sin(k)), bevel=0.006)
    leaf = mat("leaf", 0x2f5a3a, 0, 0.85)
    for (x, y, s) in ((-0.78, 0.1, 1.0), (0.82, -0.2, 0.8), (-0.62, -0.42, 0.55)):
        cyl("trunk", 0.022 * s, 0.3 * s, wood, (x, y, 0.15 * s), seg=12); t = ball("crown", 0.2 * s, leaf, (x, y, 0.42 * s), (1, 1, 1.15), 3); mod(t, 'DISPLACE', strength=0.05 * s, texture=bpy.data.textures.new("n", 'CLOUDS'))
    light((-2.2, -1.2, 1.4), 26, (0.45, 0.55, 1.0), 2.5, (0, 0, 0.3))  # the last blue of the evening
    render("family")

def reading():  # the two books named in the box, and one lying open
    stage((0.55, -1.45, 0.5), (0, 0, 0.085), 80)
    paper = mat("paper", 0xeee6d2, 0, 0.85); foil = mat("foil", 0xe6c27a, 0.9, 0.3)
    def book(title, author, cover, zc, turn, L=0.46, D=0.3, T=0.06):
        root = link(bpy.data.objects.new("book", None)); root.location = (0, 0, zc); root.rotation_euler = (0, 0, turn)
        for p in (box("cover", (L, D, T), cover, bevel=0.004), box("pages", (L - 0.012, D - 0.012, T - 0.012), paper, (0, 0.012, 0))): p.parent = root
        for (txt, x, size) in ((title, -0.02, 0.026), (author, 0.0, 0.012)):
            c = bpy.data.curves.new("t", 'FONT'); c.body = txt; c.size = size; c.align_x = 'CENTER'; c.align_y = 'CENTER'; c.extrude = 0.0006
            o = link(bpy.data.objects.new("t", c)); o.data.materials.append(foil); o.parent = root; o.location = (x, -D / 2 - 0.0008, 0.008 if txt == title else -0.017); o.rotation_euler = (math.pi / 2, 0, 0)
        return root
    book("MAN'S SEARCH FOR MEANING", "VIKTOR E. FRANKL", mat("c1", 0x1f3d6b, 0, 0.5), 0.03, 0.05)
    book("FUTURE PROOFING YOU", "JAY SAMIT", mat("c2", 0x9a3b2b, 0, 0.5), 0.09, -0.12, L=0.42, D=0.28)
    # an open book on top: two leaves of pages rising from the spine
    op = link(bpy.data.objects.new("open", None)); op.location = (0.02, 0.045, 0.122); op.rotation_euler = (0, 0, 0.22)
    c = box("ocover", (0.44, 0.3, 0.008), mat("c3", 0x2d4a3a, 0, 0.5), (0, 0, 0.004), bevel=0.003); c.parent = op
    for s in (-1, 1):
        lf = grid("leaf", 14, 2, lambda u, v: (s * 0.21 * u, -0.142 + 0.284 * v, 0.012 + 0.03 * math.sin(math.pi * min(1, u * 1.6)) * (1 - 0.45 * u)), [paper]); lf.parent = op; mod(lf, 'SOLIDIFY', thickness=0.014, offset=-1); mod(lf, 'SUBSURF', levels=2, render_levels=2)
    render("reading")

def markets():  # a candlestick chart as an object: synthetic prices, amber for an up day and blue for a down one
    stage((-1.5, -4.0, 1.05), (0.0, 0, 0.33), 75)
    random.seed(12); up = mat("up", 0xf2b56b, 0.2, 0.3, emit=0.5); dn = mat("down", 0x3f78c2, 0.2, 0.3, emit=0.3); n = 34; p = 0.16; closes = []
    box("base", (1.9, 0.5, 0.03), mat("base", 0x12161f, 0.6, 0.25), (0, 0, 0.015), bevel=0.006)
    for k in range(7): box("rule", (1.8, 0.003, 0.002), mat("rule" + str(k), 0x3a4558, 0, 0.5, emit=0.6), (0, 0.2, 0.08 + 0.09 * k))
    box("back", (1.84, 0.01, 0.66), mat("glass", 0x0e1524, 0.4, 0.1), (0, 0.21, 0.36))
    for k in range(n):
        o = p; p = max(0.06, p + random.gauss(0.011, 0.03)); hi = max(o, p) + abs(random.gauss(0, 0.014)); lo = min(o, p) - abs(random.gauss(0, 0.014)); x = -0.85 + 1.7 * k / (n - 1); m = up if p >= o else dn; closes.append((x, p))
        box("body", (0.032, 0.032, max(0.006, abs(p - o))), m, (x, 0, 0.05 + (o + p) / 2), bevel=0.003); cyl("wick", 0.0028, hi - lo, m, (x, 0, 0.05 + (hi + lo) / 2), seg=10)
    cu = bpy.data.curves.new("avg", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.004; sp = cu.splines.new('NURBS'); pts = []
    for k in range(4, n): pts.append((closes[k][0], -0.03, 0.05 + sum(c[1] for c in closes[k - 4:k + 1]) / 5))
    sp.points.add(len(pts) - 1)
    for q, pt in zip(sp.points, pts): q.co = (*pt, 1)
    sp.use_endpoint_u = True; link(bpy.data.objects.new("avg", cu)).data.materials.append(mat("line", 0xf4f1e8, 0, 0.3, emit=1.2))
    render("markets")

ALL = {"sports": sports, "boards": boards, "cars": cars, "family": family, "reading": reading, "markets": markets}
want = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(ALL)
for name in want: ALL[name]()
