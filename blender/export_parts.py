# Run inside Blender: writes every mesh object in the open file as "parts" the site can load without any extra library.
# One file: [uint32 header length][JSON header][Int16 positions][Int8 normals][Uint16 indices][Float32 part transforms][Uint8 blade-section point][Uint8 vertex colours, if some mesh uses more than one material or has baked shading].
# Coordinates are turned from Blender's Z-up to the site's Y-up: (x, y, z) -> (x, z, -y).
import bpy, json, struct, array, os

OUT = os.path.join(os.path.dirname(bpy.data.filepath), "..", "models", os.path.splitext(os.path.basename(bpy.data.filepath))[0] + ".bin")
KINDS = ["blade", "vane", "disc", "can", "nozzle", "bolt", "case", "core"]  # what a part is, so the site knows how it should fly
def kind(name):
    for k in KINDS[:6]:
        if name.startswith(k): return KINDS.index(k)
    return 6 if name.startswith(("case", "flange")) else 7

def srgb(c): return round((c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055) * 255)

objs = sorted((o for o in bpy.data.objects if o.type == 'MESH'), key=lambda o: o.name)
mats, meshes, mesh_id, centre = [], [], {}, {}
pos, nor, idx, ring, vcol = array.array('f'), array.array('b'), array.array('H'), array.array('B'), array.array('B')
multi = any(len({p.material_index for p in o.data.polygons}) > 1 for o in objs)  # then every vertex carries its own colour
shaded = any(o.data.attributes.get("ao") for o in objs)  # baked ambient occlusion (finish_turbine.py): then every vertex carries how shadowed it is
def unsrgb(b): c = b / 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def rgb(m):
    c = next(nd for nd in m.node_tree.nodes if nd.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value
    return (srgb(c[0]), srgb(c[1]), srgb(c[2]))

for o in objs:
    me = o.data
    if me.name in mesh_id: continue
    mesh_id[me.name] = len(meshes)
    # Blades and vanes keep their root as origin. Every other mesh is re-centred on the middle of its box, so each part turns, scales and rounds into a ball about its own middle.
    strip = o.name.startswith(("blade", "vane")); c = (0.0, 0.0, 0.0)
    if not strip and not o.name.startswith("kit.") and not o.get("keep"):  # kit pieces and scene parts keep the origin they were drawn around (it is their pivot)
        c = tuple((min(v.co[a] for v in me.vertices) + max(v.co[a] for v in me.vertices)) / 2 for a in range(3))
    centre[me.name] = c
    m = me.materials[0]
    if m.name not in [x["name"] for x in mats]:
        b = next(nd for nd in m.node_tree.nodes if nd.type == "BSDF_PRINCIPLED")
        col = b.inputs["Base Color"].default_value
        mats.append({"name": m.name, "c": (srgb(col[0]) << 16) | (srgb(col[1]) << 8) | srgb(col[2]), "m": round(b.inputs["Metallic"].default_value, 2), "r": round(b.inputs["Roughness"].default_value, 2)})
    me.calc_loop_triangles()
    cn = me.corner_normals; ao = me.attributes.get("ao")
    seen, v0, i0 = {}, len(pos) // 3, len(idx)
    for t in me.loop_triangles:
        for li in t.loops:
            vi = me.loops[li].vertex_index; nv = cn[li].vector; mi = me.polygons[t.polygon_index].material_index
            key = (vi, round(nv.x, 2), round(nv.y, 2), round(nv.z, 2), mi)
            if key not in seen:
                seen[key] = len(seen); co = me.vertices[vi].co
                pos.extend((co.x - c[0], co.z - c[2], -(co.y - c[1])))
                nor.extend((round(nv.x * 127), round(nv.z * 127), round(-nv.y * 127)))
                c3 = rgb(me.materials[mi]) if multi else (255, 255, 255)   # without per-vertex colours the part keeps its material colour and this is just the shading
                if ao: c3 = tuple(srgb(unsrgb(c) * ao.data[vi].value) for c in c3)
                vcol.extend(c3)
                ring.append(vi % 6 if strip else 255)  # which of the six points round a blade section this is, so the site can round the blade into a rod
            idx.append(seen[key])
    assert len(seen) < 65536
    meshes.append({"name": o.name, "mat": [x["name"] for x in mats].index(m.name), "v": [v0, len(seen)], "i": [i0, len(idx) - i0]})

parts, pm, pk, pr = array.array('f'), [], [], []
for o in objs:
    loc, rot, scl = o.matrix_world.decompose(); c = centre[o.data.name]
    loc = loc + o.matrix_world.to_3x3() @ __import__("mathutils").Vector(c)
    parts.extend((loc.x, loc.z, -loc.y, rot.x, rot.z, -rot.y, rot.w, scl.x, scl.z, scl.y))
    pm.append(mesh_id[o.data.name]); pk.append(kind(o.name)); pr.append(1 if o.users_collection[0].name == "rotor" else 0)

scale = max(abs(x) for x in pos) / 32767
q = array.array('h', (round(x / scale) for x in pos))
def pad(b): return b + b"\0" * (-len(b) % 4)
blobs = [pad(q.tobytes()), pad(nor.tobytes()), pad(idx.tobytes()), parts.tobytes(), pad(ring.tobytes())] + ([pad(vcol.tobytes())] if multi or shaded else [])
offs, at = [], 0
for b in blobs: offs.append(at); at += len(b)
head = json.dumps({"scale": scale, "mats": mats, "meshes": meshes, "verts": len(pos) // 3, "off": offs, "mesh": pm, "kind": pk, "rotor": pr, "pname": [o.name for o in objs], "multi": multi}, separators=(",", ":")).encode()
head += b" " * (-len(head) % 4)  # spaces, so the header still parses as JSON
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "wb") as f:
    f.write(struct.pack("<I", len(head))); f.write(head)
    for b in blobs: f.write(b)
print("wrote", os.path.normpath(OUT), os.path.getsize(OUT), "bytes;", len(objs), "parts,", len(meshes), "meshes,", len(pos) // 3, "verts,", len(idx) // 3, "triangles")
