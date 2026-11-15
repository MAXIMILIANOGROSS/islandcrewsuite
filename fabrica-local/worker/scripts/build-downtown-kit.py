#!/usr/bin/env python3
"""Empaqueta piezas modulares del Downtown City MegaKit (Quaternius, CC0) en un único Kit.glb ligero.
Uso (variante arena: añade "white" al final): python3 scripts/build-downtown-kit.py "<carpeta glTF (Godot)>" "<carpeta Textures>" public/world/downtown/Kit.glb
Solo conserva color base (JPEG 512 px); sin normal/ORM para que pese poco."""
import sys, json, struct, io, os
from PIL import Image

PIECES = ["Brick_Plain_3", "Brick_Window_Square_Single", "Brick_Window_Trim_Single", "DoorFrame_Wooden", "Door_1",
          "Cornice_Brick_Center", "Cornice_Brick_L", "Cornice_Brick_R", "Floor_4x4", "Brick_Corner_Plain"]
src, tex, out = sys.argv[1], sys.argv[2], sys.argv[3]
WHITE = len(sys.argv) > 4 and sys.argv[4] == "white"  # variante encalada/arena (estilo Corralejo): ladrillo -> hormigón aclarado
SIZE = 512
bin_blob = bytearray(); bviews = []; accessors = []; meshes = []; nodes = []; mats = []; mat_ix = {}; images = []; textures = []; img_ix = {}

def add_view(data, target=None):
    while len(bin_blob) % 4: bin_blob.append(0)
    off = len(bin_blob); bin_blob.extend(data)
    v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
    if target: v["target"] = target
    bviews.append(v); return len(bviews) - 1

def image_for(uri):
    if uri in img_ix: return img_ix[uri]
    name = os.path.basename(uri)
    if WHITE and "RedBrick_BaseColor" in name: name = "T_Concrete_BaseColor.png"
    im = Image.open(os.path.join(tex, name)).convert("RGB").resize((SIZE, SIZE))
    if WHITE and name == "T_Concrete_BaseColor.png": im = Image.blend(im, Image.new("RGB", im.size, (240, 230, 208)), 0.6)
    b = io.BytesIO(); im.save(b, "JPEG", quality=80)
    vi = add_view(b.getvalue()); images.append({"bufferView": vi, "mimeType": "image/jpeg"})
    textures.append({"source": len(images) - 1}); img_ix[uri] = len(textures) - 1; return img_ix[uri]

for name in PIECES:
    j = json.load(open(os.path.join(src, name + ".gltf"))); raw = open(os.path.join(src, j["buffers"][0]["uri"]), "rb").read()
    vmap = {}
    def view(i):
        if i not in vmap:
            v = j["bufferViews"][i]; vmap[i] = add_view(raw[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]], v.get("target"))
        return vmap[i]
    amap = {}
    def acc(i):
        if i not in amap:
            a = dict(j["accessors"][i]); a["bufferView"] = view(a["bufferView"]); accessors.append(a); amap[i] = len(accessors) - 1
        return amap[i]
    def mat(i):
        m = j["materials"][i]; key = m["name"]
        if key in mat_ix: return mat_ix[key]
        pbr = m.get("pbrMetallicRoughness", {}); nm = {"name": key, "pbrMetallicRoughness": {"metallicFactor": 0.0, "roughnessFactor": 0.85}}
        if "baseColorFactor" in pbr: nm["pbrMetallicRoughness"]["baseColorFactor"] = pbr["baseColorFactor"]
        bt = pbr.get("baseColorTexture")
        if bt is not None:
            uri = j["images"][j["textures"][bt["index"]]["source"]]["uri"]
            nm["pbrMetallicRoughness"]["baseColorTexture"] = {"index": image_for(uri), "texCoord": bt.get("texCoord", 0)}
        if m.get("alphaMode"): nm["alphaMode"] = m["alphaMode"]
        if "emissiveFactor" in m: nm["emissiveFactor"] = m["emissiveFactor"]
        mats.append(nm); mat_ix[key] = len(mats) - 1; return mat_ix[key]
    prims = []
    for m in j["meshes"]:
        for p in m["primitives"]:
            q = {"attributes": {k: acc(v) for k, v in p["attributes"].items() if k in ("POSITION", "NORMAL", "TEXCOORD_0")}, "material": mat(p["material"])}
            if "indices" in p: q["indices"] = acc(p["indices"])
            prims.append(q)
    meshes.append({"name": name, "primitives": prims}); nodes.append({"name": name, "mesh": len(meshes) - 1})

g = {"asset": {"version": "2.0", "generator": "island-crew build-downtown-kit"}, "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}],
     "nodes": nodes, "meshes": meshes, "materials": mats, "accessors": accessors, "bufferViews": bviews, "buffers": [{"byteLength": len(bin_blob)}]}
if images: g["images"] = images; g["textures"] = textures
js = json.dumps(g, separators=(",", ":")).encode()
while len(js) % 4: js += b" "
while len(bin_blob) % 4: bin_blob.append(0)
glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_blob)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(bin_blob), 0x004E4942) + bytes(bin_blob)
open(out, "wb").write(glb); print("OK", out, len(glb) // 1024, "KB", len(PIECES), "piezas", len(mats), "materiales")
