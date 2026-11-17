# Run inside Blender with turbine.blend open: rounds the hard edges of every part except the blades (their vertex order is needed for the rod shape),
# then works out how shadowed each vertex is by the parts around it (ambient occlusion) and stores it on the mesh as the attribute "ao".
# export_parts.py writes that out, so the soft contact shadows cost nothing on the page.
import bpy, bmesh, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree

objs = [o for o in bpy.data.objects if o.type == 'MESH']
strip = lambda o: o.name.startswith(("blade", "vane"))

# ---- round the edges ----
done = set(); before = sum(len(o.data.polygons) for o in objs if o.data.name not in done and not done.add(o.data.name)); done = set()
for o in objs:
    me = o.data
    if me.name in done or strip(o) or me.get("bevelled"): continue
    done.add(me.name)
    size = min(d for d in o.dimensions if d > 1e-5) if any(d > 1e-5 for d in o.dimensions) else 0.01
    w = min(0.0028, 0.1 * size)
    bm = bmesh.new(); bm.from_mesh(me)
    edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(38)]
    if edges:
        try: bmesh.ops.bevel(bm, geom=edges, offset=w, offset_type='OFFSET', segments=2, profile=0.6, affect='EDGES', clamp_overlap=True)
        except Exception as e: print("bevel", me.name, e)
    bm.to_mesh(me); bm.free(); me.update()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    try: me.set_sharp_from_angle(angle=math.radians(50))
    except Exception as e: print(e)
    me["bevelled"] = 1
done = set(); after = sum(len(o.data.polygons) for o in objs if o.data.name not in done and not done.add(o.data.name))
print("faces", before, "->", after)

# ---- ambient occlusion, per vertex, against the whole assembled turbine ----
bpy.context.view_layer.update()
verts, polys = [], []
for o in objs:
    base = len(verts); mw = o.matrix_world
    verts.extend(mw @ v.co for v in o.data.vertices)
    polys.extend(tuple(base + i for i in p.vertices) for p in o.data.polygons)
tree = BVHTree.FromPolygons(verts, polys, all_triangles=False)
random.seed(7)
dirs = []
while len(dirs) < 40:
    v = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)))
    if 0.05 < v.length <= 1: dirs.append(v.normalized())
done = set(); n = 0
for o in objs:
    me = o.data
    if me.name in done: continue
    done.add(me.name); mw = o.matrix_world; rot = mw.to_3x3()
    attr = me.attributes.get("ao") or me.attributes.new("ao", 'FLOAT', 'POINT')
    vals = []
    for v in me.vertices:
        p = mw @ v.co; nrm = (rot @ v.normal).normalized(); open_ = 0; total = 0
        for d in dirs:
            if d.dot(nrm) < 0.15: continue
            total += 1
            hit = tree.ray_cast(p + nrm * 0.004, d, 0.22)
            if hit[0] is None: open_ += 1
        vals.append(open_ / total if total else 1.0); n += 1
    lo = min(vals); attr = me.attributes["ao"]
    attr.data.foreach_set("value", [0.25 + 0.75 * x for x in vals])   # never fully black: light still bounces in
print("ao on", n, "vertices of", len(done), "meshes")
bpy.ops.wm.save_mainfile()
