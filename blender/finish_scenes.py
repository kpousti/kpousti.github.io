# Run on scenes.blend (or city.blend), for instance:  Blender -b blender/scenes.blend --python blender/finish_scenes.py
# The turbine's soft-shadow recipe (finish_turbine.py) for the scene models: works out how shadowed each vertex is by the parts around it
# (ambient occlusion, against the whole assembled model) and stores it on the mesh as the attribute "ao". Then runs export_parts.py, which writes it into the model file
# as a vertex colour, so crevices and the places where parts meet are darker at no cost on the page. The .blend itself is not saved.
import bpy, random, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

objs = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.context.view_layer.update()
verts, polys = [], []
for o in objs:
    base = len(verts); mw = o.matrix_world
    verts.extend(mw @ v.co for v in o.data.vertices)
    polys.extend(tuple(base + i for i in p.vertices) for p in o.data.polygons)
tree = BVHTree.FromPolygons(verts, polys, all_triangles=False)
random.seed(7)
dirs = []
while len(dirs) < 32:
    v = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)))
    if 0.05 < v.length <= 1: dirs.append(v.normalized())
done = set(); n = 0
for o in objs:
    me = o.data
    if me.name in done: continue
    done.add(me.name); mw = o.matrix_world; rot = mw.to_3x3()
    vals = []
    for v in me.vertices:
        p = mw @ v.co; nrm = (rot @ v.normal).normalized(); open_ = 0; total = 0
        for d in dirs:
            if d.dot(nrm) < 0.15: continue
            total += 1
            if tree.ray_cast(p + nrm * 0.004, d, 0.2)[0] is None: open_ += 1
        vals.append(open_ / total if total else 1.0); n += 1
    attr = me.attributes.get("ao") or me.attributes.new("ao", 'FLOAT', 'POINT')
    attr.data.foreach_set("value", [0.3 + 0.7 * x ** 0.8 for x in vals])   # never fully black: the page's own lights still shade it
print("ambient occlusion on", n, "vertices of", len(done), "meshes")
exec(compile(open(os.path.join(os.path.dirname(bpy.data.filepath), "export_parts.py")).read(), "export_parts.py", "exec"))
