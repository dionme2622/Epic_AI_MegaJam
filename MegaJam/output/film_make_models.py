import bpy,math
from pathlib import Path
out=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/FilmRestore');out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def cube(name,pos,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def polygon(name,pts):
 n=len(pts);vs=[(x,-.035,z) for x,z in pts]+[(x,.035,z) for x,z in pts];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 if len(objects)>1:bpy.ops.object.join()
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.context.object.name=name
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
frame=[cube('Top',(0,0,1.75),(5.7,.18,.22)),cube('Bottom',(0,0,-1.75),(5.7,.18,.22)),cube('Left',(-2.75,0,0),(.20,.18,3.4)),cube('Right',(2.75,0,0),(.20,.18,3.4))]
for x in [-2.5,-1.7,-.9,-.1,.7,1.5,2.3]:frame.append(cube('Rivet',(x,-.12,-1.75),(.09,.05,.09)))
export('SM_Film_Frame',frame)
curve=bpy.data.curves.new('Number3','FONT');curve.body='3';curve.align_x='CENTER';curve.align_y='CENTER';curve.size=1.45;curve.extrude=.04
number=bpy.data.objects.new('Number3',curve);bpy.context.collection.objects.link(number);bpy.context.view_layer.objects.active=number;number.select_set(True);number.rotation_euler.x=math.pi/2;bpy.ops.object.convert(target='MESH');export('SM_Film_Three',[number])
arrow=polygon('Arrow',[(-.65,-.15),(.12,-.15),(.12,-.38),(.70,0),(.12,.38),(.12,.15),(-.65,.15)])
export('SM_Film_Arrow',[arrow])
shadow=polygon('Shadow',[(-1.3,-.95),(.95,-.9),(1.3,-.45),(1.1,.85),(-.9,1.0),(-1.25,.55)])
export('SM_Film_Shadow',[shadow])
# Gear silhouette with a real central opening.
n=48;outer=[]
for i in range(n):
 a=2*math.pi*i/n;r=.58 if i%4 in (0,1) else .43;outer.append((r*math.cos(a),r*math.sin(a)))
vs=[]
for y in [-.04,.04]:
 vs += [(x,y,z) for x,z in outer]+[(.22*math.cos(2*math.pi*i/n),y,.22*math.sin(2*math.pi*i/n)) for i in range(n)]
faces=[]
for i in range(n):
 j=(i+1)%n
 faces += [(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]
me=bpy.data.meshes.new('Gear');me.from_pydata(vs,[],faces);me.update();gear=bpy.data.objects.new('Gear',me);bpy.context.collection.objects.link(gear);export('SM_Film_Gear',[gear])
projector=[cube('ProjectorBase',(0,0,.22),(1,.65,.35)),cube('ProjectorBody',(0,0,.75),(.95,.6,.75))]
for x in [-.27,.27]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.28,depth=.10,location=(x,0,1.35),rotation=(math.pi/2,0,0));projector.append(bpy.context.object)
bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.20,depth=.40,location=(.62,0,.8),rotation=(0,math.pi/2,0));projector.append(bpy.context.object)
export('SM_Film_Projector',projector)
for i,o in enumerate(bpy.context.scene.objects):
 if o.type=='MESH':o.location.x=i*6
bpy.ops.wm.save_as_mainfile(filepath=str(out/'FilmRestore_Source.blend'))
print('FILM_MODELS',out)
