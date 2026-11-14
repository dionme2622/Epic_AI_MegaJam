import bpy,math
from pathlib import Path
out=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/BloomPuzzle');out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def export(name,items):
 bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
 return o
def cube(name,location,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def polygon(name,points):
 # One concave face, extruded along Y and triangulated by Blender's exporter.
 n=len(points); verts=[(x,-.035,z) for x,z in points]+[(x,.035,z) for x,z in points]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return o
frame=[cube('Top',(0,0,.72),(1.55,.16,.13)),cube('Bottom',(0,0,-.72),(1.55,.16,.13)),cube('Left',(-.72,0,0),(.13,.16,1.35)),cube('Right',(.72,0,0),(.13,.16,1.35))]
export('SM_Bloom_Frame',frame)
star=[]
for i in range(10):
 a=math.pi/2+i*math.pi/5;r=.48 if i%2==0 else .21;star.append((r*math.cos(a),r*math.sin(a)))
export('SM_Bloom_Star',[polygon('star',star)])
# Crescent with rounded outer and inner arcs, bounded by a single concave outline.
outer=[(.45*math.cos(math.radians(a)),.45*math.sin(math.radians(a))) for a in range(55,306,10)]
inner=[(.18+.34*math.cos(math.radians(a)),.34*math.sin(math.radians(a))) for a in range(275,84,-10)]
export('SM_Bloom_Moon',[polygon('moon',outer+inner)])
sun=[]
for i in range(32):
 a=2*math.pi*i/32;r=.46 if i%4 in (0,1) else .29;sun.append((r*math.cos(a),r*math.sin(a)))
export('SM_Bloom_Sun',[polygon('sun',sun)])
# Reorganize source pieces apart for editing; exports already use a zero origin.
for i,o in enumerate(bpy.context.scene.objects):
 if o.type=='MESH': o.location.x=i*2.0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Bloom_Signs_Source.blend'))
print('BLOOM_MODELS',out)
