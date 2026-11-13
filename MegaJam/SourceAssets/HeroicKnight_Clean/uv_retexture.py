"""Re-unwrap and repaint the supplied unrigged knight in Blender 5.3.

Requires xatlas==0.0.11 in Blender's bundled Python.
Run with blender -b --factory-startup --python uv_retexture.py.
The FBX and original texture are read only. All outputs use the CleanUV_ prefix.
"""

import bpy
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import xatlas
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
STEM = "tripo_convert_d5780a3a-1d2e-4f65-993d-11e07520e1d0"
SOURCE_FBX = ROOT / (STEM + ".fbx")
SOURCE_COLOR = ROOT / (STEM + ".fbm") / "heroic_knight_3d_model_basecolor.PNG"
ATLAS_SIZE = 4096
BASE_OUT = ROOT / "CleanUV_BaseColor.png"
ORM_OUT = ROOT / "CleanUV_ORM.png"
BLEND_OUT = ROOT / "CleanUV_Knight.blend"
PREVIEW_OUT = ROOT / "CleanUV_Preview.png"
REPORT_OUT = ROOT / "CleanUV_report.json"


def island_count(mesh, uv_name):
    uv = mesh.uv_layers[uv_name].data
    edge_faces = defaultdict(list)
    for p in mesh.polygons:
        ls = list(p.loop_indices)
        for i, li in enumerate(ls):
            lj = ls[(i + 1) % len(ls)]
            a, b = mesh.loops[li].vertex_index, mesh.loops[lj].vertex_index
            edge_faces[tuple(sorted((a, b)))].append((p.index, a, tuple(uv[li].uv), tuple(uv[lj].uv)))
    parent = list(range(len(mesh.polygons)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for pair in edge_faces.values():
        if len(pair) != 2:
            continue
        p, a, u0, u1 = pair[0]
        q, a2, v0, v1 = pair[1]
        if a == a2:
            delta = max(*(abs(u0[i] - v0[i]) for i in range(2)), *(abs(u1[i] - v1[i]) for i in range(2)))
        else:
            delta = max(*(abs(u0[i] - v1[i]) for i in range(2)), *(abs(u1[i] - v0[i]) for i in range(2)))
        if delta < 1e-5:
            parent[find(p)] = find(q)
    return len({find(i) for i in range(len(mesh.polygons))})


def uv_stats(mesh, uv_name):
    uv = mesh.uv_layers[uv_name].data
    areas, stretch, bad = [], [], []
    for p in mesh.polygons:
        ls = list(p.loop_indices)
        u = [uv[li].uv for li in ls]
        v = [mesh.vertices[mesh.loops[li].vertex_index].co for li in ls]
        area = abs((u[1] - u[0]).cross(u[2] - u[0])) * 0.5
        rates = [(u[i] - u[j]).length / max((v[i] - v[j]).length, 1e-9)
                 for i, j in ((0, 1), (1, 2), (2, 0))]
        ratio = max(rates) / max(min(rates), 1e-12)
        areas.append(area)
        stretch.append(ratio)
        if area < 1e-12 or ratio > 3.0:
            bad.append(p.index)
    a = np.asarray(areas)
    s = np.asarray(stretch)
    layer = mesh.uv_layers[uv_name]
    bounds = [[float(min(d.uv[i] for d in layer.data)), float(max(d.uv[i] for d in layer.data))]
              for i in range(2)]
    return {
        "islands": island_count(mesh, uv_name),
        "uv_area_sum": float(a.sum()),
        "zero_area_faces": int(np.sum(a < 1e-12)),
        "stretch_p50": float(np.percentile(s, 50)),
        "stretch_p95": float(np.percentile(s, 95)),
        "stretch_max": float(s.max()),
        "stretch_over_3_faces": int(np.sum(s > 3)),
        "bounds": bounds,
    }, bad


def sampled_overlap(mesh, uv_name, resolution=1024):
    """Raster-test triangle interiors, excluding shared edges to avoid false hits."""
    uv = mesh.uv_layers[uv_name].data
    hits = np.zeros((resolution, resolution), dtype=np.uint8)
    for p in mesh.polygons:
        coords = np.asarray([tuple(uv[li].uv) for li in p.loop_indices], dtype=np.float64)
        u0, u1, u2 = coords
        area2 = (u1[0]-u0[0])*(u2[1]-u0[1])-(u1[1]-u0[1])*(u2[0]-u0[0])
        if abs(area2) < 1e-12:
            continue
        xmin = max(0, int(math.floor(coords[:, 0].min() * resolution)))
        xmax = min(resolution-1, int(math.ceil(coords[:, 0].max() * resolution)))
        ymin = max(0, int(math.floor(coords[:, 1].min() * resolution)))
        ymax = min(resolution-1, int(math.ceil(coords[:, 1].max() * resolution)))
        if xmin > xmax or ymin > ymax:
            continue
        xs = (np.arange(xmin, xmax+1, dtype=np.float64) + 0.5) / resolution
        ys = (np.arange(ymin, ymax+1, dtype=np.float64) + 0.5) / resolution
        xx, yy = np.meshgrid(xs, ys)
        edges = []
        for a, b in ((u0,u1),(u1,u2),(u2,u0)):
            edges.append((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))
        tolerance = abs(area2) * 1e-5
        inside = np.logical_and.reduce([e > tolerance for e in edges]) if area2 > 0 else np.logical_and.reduce([e < -tolerance for e in edges])
        hits[ymin:ymax+1, xmin:xmax+1][inside] += 1
    return {"sample_resolution": resolution,
            "occupied_pixels": int(np.count_nonzero(hits)),
            "overlap_pixels": int(np.count_nonzero(hits > 1)),
            "max_triangle_hits": int(hits.max())}


def repaint(baked):
    """Retain the recognizable palette while improving color and surface response."""
    raw = np.empty(ATLAS_SIZE * ATLAS_SIZE * 4, dtype=np.float32)
    baked.pixels.foreach_get(raw)
    raw = raw.reshape(ATLAS_SIZE, ATLAS_SIZE, 4)
    base = raw.copy()
    orm = np.empty_like(base)
    orm[..., 0] = 1.0   # white AO; the atlas has no trustworthy occlusion source
    orm[..., 1] = 0.70
    orm[..., 2] = 0.0
    orm[..., 3] = 1.0

    # Process strips to avoid large temporary arrays at 4K resolution.
    counts = defaultdict(int)
    for y0 in range(0, ATLAS_SIZE, 256):
        y1 = min(y0 + 256, ATLAS_SIZE)
        src = np.clip(raw[y0:y1, :, :3], 0, 1)
        # Blender's byte image pixel API exposes the PNG channel values here.
        rgb = src.copy()
        alpha = raw[y0:y1, :, 3]
        used = alpha > 0.001
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        maxc = np.maximum(np.maximum(r, g), b)
        minc = np.minimum(np.minimum(r, g), b)
        sat = maxc - minc

        gold = used & (r > 0.52) & (g > 0.38) & (b < 0.42) & (r > g * 1.12) & (g > r * 0.58) & (g > b * 1.25)
        armor = used & (r > 0.52) & (g > 0.50) & (b > 0.43) & (sat < 0.28)
        burgundy = used & (r > g * 1.18) & (r > b * 1.06) & (b > g * 0.72) & (r < 0.68) & (g < 0.36)
        green = used & (g > r * 0.94) & (g > b * 1.06) & (r < 0.51) & (g < 0.58)
        skin = used & (r > 0.52) & (g > 0.31) & (b > 0.31) & (r > g * 1.10) & (b > g * 0.66)
        # Material priority: metal > skin > cloth. Soft-painted border colors stay neutral.
        skin &= ~(gold | armor)
        burgundy &= ~(gold | armor | skin)
        green &= ~(gold | armor | skin | burgundy)

        rgb = np.clip((rgb - 0.5) * 1.025 + 0.5, 0, 1)
        luminance = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
        rgb = np.clip(luminance[..., None] + (rgb - luminance[..., None]) * 1.045, 0, 1)
        for mask, target, amount, roughness, metalness, name in (
            (gold, (0.83, 0.55, 0.18), 0.16, 0.34, 0.75, "gold"),
            (armor, (0.81, 0.79, 0.72), 0.12, 0.42, 0.52, "pale_armor"),
            (skin, (0.80, 0.55, 0.44), 0.07, 0.57, 0.0, "skin"),
            (burgundy, (0.48, 0.12, 0.23), 0.13, 0.78, 0.0, "burgundy_cloth"),
            (green, (0.23, 0.34, 0.23), 0.12, 0.77, 0.0, "green_cloth"),
        ):
            rgb[mask] = rgb[mask] * (1 - amount) + np.asarray(target, dtype=np.float32) * amount
            orm[y0:y1, :, 1][mask] = roughness
            orm[y0:y1, :, 2][mask] = metalness
            counts[name] += int(np.count_nonzero(mask))
        counts["used"] += int(np.count_nonzero(used))

        # A neutral background prevents black mip fringes beyond the bake dilation.
        rgb[~used] = (0.40, 0.32, 0.28)
        base[y0:y1, :, :3] = rgb
        base[y0:y1, :, 3] = 1.0

    base_img = bpy.data.images.new("CleanUV_BaseColor", width=ATLAS_SIZE, height=ATLAS_SIZE, alpha=True)
    base_img.pixels.foreach_set(base.ravel())
    base_img.filepath_raw = str(BASE_OUT)
    base_img.file_format = "PNG"
    base_img.save()
    orm_img = bpy.data.images.new("CleanUV_ORM", width=ATLAS_SIZE, height=ATLAS_SIZE, alpha=True)
    orm_img.colorspace_settings.name = "Non-Color"
    orm_img.pixels.foreach_set(orm.ravel())
    orm_img.filepath_raw = str(ORM_OUT)
    orm_img.file_format = "PNG"
    orm_img.save()
    print("REPAINT_COUNTS", dict(counts), flush=True)
    return base_img, orm_img, dict(counts)


def make_material(base_img, orm_img):
    mat = bpy.data.materials.new("M_Knight_Clean_PBR")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    tex = nodes.new("ShaderNodeTexImage")
    tex.name = "BaseColor_4K"
    tex.image = base_img
    tex.location = (-560, 180)
    orm = nodes.new("ShaderNodeTexImage")
    orm.name = "ORM_4K"
    orm.image = orm_img
    orm.location = (-560, -160)
    separate = nodes.new("ShaderNodeSeparateColor")
    separate.location = (-250, -160)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (30, 120)
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (380, 120)
    links = mat.node_tree.links
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(orm.outputs["Color"], separate.inputs["Color"])
    links.new(separate.outputs["Green"], bsdf.inputs["Roughness"])
    links.new(separate.outputs["Blue"], bsdf.inputs["Metallic"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat


def render_preview(obj):
    scene = bpy.context.scene
    camera_data = bpy.data.cameras.new("Preview_Camera")
    camera = bpy.data.objects.new("Preview_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0.0, -4.0, 1.10)
    direction = Vector((0.0, 0.0, 0.90)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 2.42
    scene.camera = camera

    for name, loc, energy, size in (
        ("Key", (-2.2, -2.7, 4.5), 530, 3.0),
        ("Fill", (2.6, -1.5, 2.6), 310, 3.2),
        ("Rim", (0.0, 2.0, 3.8), 420, 2.3),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = loc
        light.rotation_euler = (Vector((0, 0, 0.88)) - light.location).to_track_quat("-Z", "Y").to_euler()

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW_OUT)
    scene.world.color = (0.18, 0.18, 0.18)
    bpy.ops.render.render(write_still=True)

    # Source .blend remains an uncomplicated mesh-only handoff to rigging.
    for other in list(scene.objects):
        if other is not obj:
            bpy.data.objects.remove(other, do_unlink=True)
    scene.camera = None


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(SOURCE_FBX))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(meshes) == 1, f"Expected one mesh, got {len(meshes)}"
    obj = meshes[0]
    obj.name = "Knight_Body"
    mesh = obj.data
    assert len(mesh.polygons) == 5100
    assert len(mesh.uv_layers) == 1
    mesh.uv_layers[0].name = "UV_Original"
    source_stats, _ = uv_stats(mesh, "UV_Original")

    # xatlas charts and packs the triangles without the self-overlaps produced
    # by Blender's angle-based unwrap on this closed, irregular mesh.
    vertices = np.asarray([tuple(v.co) for v in mesh.vertices], dtype=np.float32)
    faces = np.asarray([[mesh.loops[li].vertex_index for li in p.loop_indices]
                        for p in mesh.polygons], dtype=np.uint32)
    atlas = xatlas.Atlas()
    atlas.add_mesh(vertices, faces)
    chart_options = xatlas.ChartOptions()
    pack_options = xatlas.PackOptions()
    pack_options.resolution = ATLAS_SIZE
    pack_options.padding = 18
    atlas.generate(chart_options, pack_options, verbose=False)
    vmapping, atlas_faces, atlas_uvs = atlas[0]
    face_lookup = defaultdict(list)
    for p in mesh.polygons:
        face_lookup[tuple(sorted(faces[p.index]))].append(p.index)
    clean = mesh.uv_layers.new(name="UV_Clean")
    for tri in atlas_faces:
        original_vertices = vmapping[tri]
        key = tuple(sorted(original_vertices))
        p = mesh.polygons[face_lookup[key].pop()]
        for li in p.loop_indices:
            vertex_id = mesh.loops[li].vertex_index
            atlas_corner = next(i for i in range(3) if original_vertices[i] == vertex_id)
            clean.data[li].uv = atlas_uvs[tri[atlas_corner]]
    assert all(not ids for ids in face_lookup.values())
    mesh.uv_layers.active = clean
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    clean_stats, _ = uv_stats(mesh, "UV_Clean")
    print("UV_FINAL", clean_stats, flush=True)
    assert clean_stats["zero_area_faces"] == 0
    assert clean_stats["islands"] < source_stats["islands"] // 3
    assert clean_stats["stretch_max"] < 3.1
    assert all(0 <= lo < hi <= 1 for lo, hi in clean_stats["bounds"])
    overlap_stats = sampled_overlap(mesh, "UV_Clean")
    print("UV_OVERLAP", overlap_stats, flush=True)
    assert overlap_stats["overlap_pixels"] == 0

    # Normalize source FBX centimeters to the scene's meter scale, then bring
    # the stylized T pose to about 1.74 m for Unreal.
    obj.scale = (0.02, 0.02, 0.02)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    world_bounds = [[float(min((obj.matrix_world @ Vector(c))[i] for c in obj.bound_box)),
                     float(max((obj.matrix_world @ Vector(c))[i] for c in obj.bound_box))]
                    for i in range(3)]
    print("WORLD_BOUNDS", world_bounds, flush=True)

    # Bake original color from its original UVs into the new atlas.
    source_image = bpy.data.images.load(str(SOURCE_COLOR), check_existing=True)
    source_mat = bpy.data.materials.new("Bake_Source")
    source_mat.use_nodes = True
    nodes = source_mat.node_tree.nodes
    nodes.clear()
    uv = nodes.new("ShaderNodeUVMap")
    uv.uv_map = "UV_Original"
    src = nodes.new("ShaderNodeTexImage")
    src.image = source_image
    emission = nodes.new("ShaderNodeEmission")
    out = nodes.new("ShaderNodeOutputMaterial")
    target = nodes.new("ShaderNodeTexImage")
    target.name = "BAKE_TARGET"
    baked = bpy.data.images.new("CleanUV_BakedSource", width=ATLAS_SIZE, height=ATLAS_SIZE,
                                alpha=True)
    baked.generated_color = (0, 0, 0, 0)
    target.image = baked
    nodes.active = target
    links = source_mat.node_tree.links
    links.new(uv.outputs["UV"], src.inputs["Vector"])
    links.new(src.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], out.inputs["Surface"])
    mesh.materials.clear()
    mesh.materials.append(source_mat)
    mesh.uv_layers.active = mesh.uv_layers["UV_Clean"]
    mesh.uv_layers.active_render = mesh.uv_layers["UV_Clean"]
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 1
    scene.render.bake.use_clear = True
    scene.render.bake.margin = 8
    scene.render.bake.margin_type = "EXTEND"
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    print("BAKE_START", ATLAS_SIZE, flush=True)
    bpy.ops.object.bake(type="EMIT")
    print("BAKE_DONE", flush=True)

    base_img, orm_img, palette_counts = repaint(baked)
    mesh.materials.clear()
    final_material = make_material(base_img, orm_img)
    mesh.materials.append(final_material)
    mesh.uv_layers.remove(mesh.uv_layers["UV_Original"])
    assert len(mesh.uv_layers) == 1 and mesh.uv_layers[0].name == "UV_Clean"
    base_img.pack()
    orm_img.pack()
    base_img.filepath = "//CleanUV_BaseColor.png"
    orm_img.filepath = "//CleanUV_ORM.png"
    for mat in list(bpy.data.materials):
        if mat is not final_material and mat.users == 0:
            bpy.data.materials.remove(mat)
    for img in list(bpy.data.images):
        if img not in (base_img, orm_img) and img.users == 0:
            bpy.data.images.remove(img)

    render_preview(obj)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    report = {
        "source": str(SOURCE_FBX),
        "source_texture": str(SOURCE_COLOR),
        "vertices": len(mesh.vertices),
        "triangles": len(mesh.polygons),
        "source_uv": source_stats,
        "clean_uv": clean_stats,
        "uv_overlap_test": overlap_stats,
        "world_bounds_m": world_bounds,
        "atlas_pixels": ATLAS_SIZE,
        "bake_margin_pixels": 8,
        "xatlas_charts": int(atlas.chart_count),
        "xatlas_atlas_size": [int(atlas.width), int(atlas.height)],
        "xatlas_padding": 18,
        "xatlas_version": xatlas.__version__,
        "palette_texels": palette_counts,
        "outputs": [str(BASE_OUT), str(ORM_OUT), str(BLEND_OUT), str(PREVIEW_OUT)],
    }
    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("COMPLETE", REPORT_OUT, flush=True)


if __name__ == "__main__":
    main()
