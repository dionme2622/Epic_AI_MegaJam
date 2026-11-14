import bpy, math
from mathutils import Vector
from pathlib import Path

out=Path('C:/LHH/Epic_AI_MegaJam/MegaJam/output/Stage1_Unreal_Export/Refined')
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color,metal=0,rough=.6):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if p is None:
  p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');o=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],o.inputs['Surface'])
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
stone=material('WheelStone',(0.22,.20,.23),0,.82)
light=material('WheelStoneLight',(.47,.41,.37),0,.8)
bronze=material('AgedBronze',(.43,.23,.07),.7,.35)
edge=material('PaleBrass',(.72,.49,.18),.65,.29)
iron=material('DarkIron',(.11,.14,.17),.75,.38)
wood=material('WarmWood',(.25,.10,.045),0,.75)
allm=[stone,light,bronze,edge,iron,wood]
def mat(o,m):
 o.data.materials.append(m);return o
def mesh(name,verts,faces,m):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);return mat(ob,m)
def annulus(name,outer,inner,depth,y,n,m,phase=0):
 verts=[]
 for yy in [y-depth/2,y+depth/2]:
  for r in [outer,inner]:
   for i in range(n):
    a=2*math.pi*i/n+phase;verts.append((r*math.cos(a),yy,r*math.sin(a)))
 faces=[]
 for i in range(n):
  j=(i+1)%n;faces += [(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]
 return mesh(name,verts,faces,m)
def disk(name,r,depth,y,n,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=depth,location=(0,y,0),rotation=(math.pi/2,0,0))
 o=bpy.context.object;o.name=name;return mat(o,m)
def bolt(name,x,z,y,r,m,n=12):
 bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=.028,location=(x,y,z),rotation=(math.pi/2,0,0))
 o=bpy.context.object;o.name=name;mat(o,m)
 # raised head and dark slit give fasteners readable silhouettes
 return o
def spoke(name,a,r1,r2,width,depth,y,m):
 r=(r1+r2)/2
 bpy.ops.mesh.primitive_cube_add(size=1,location=(r*math.cos(a),y,r*math.sin(a)))
 o=bpy.context.object;o.name=name;o.dimensions=(r2-r1,depth,width);o.rotation_euler[1]=-a
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mat(o,m)
 bevel=o.modifiers.new('Soft machined edges','BEVEL');bevel.width=.018;bevel.segments=2
 return o
def gear_body(name,n,root,tip,depth,m):
 angles=[]
 for i in range(n):
  for f,r in [(0,root),(.19,tip),(.60,tip),(.79,root)]:
   a=2*math.pi*(i+f)/n;angles.append((a,r))
 verts=[];N=len(angles)
 for yy in [-depth/2,depth/2]:
  for a,r in angles:verts.append((r*math.cos(a),yy,r*math.sin(a)))
  for a,r in angles:verts.append((.67*math.cos(a),yy,.67*math.sin(a)))
 faces=[]
 for i in range(N):
  j=(i+1)%N;faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
 o=mesh(name,verts,faces,m);be=o.modifiers.new('Tooth bevel','BEVEL');be.width=.016;be.segments=2;return o
def wheel(high):
 n=64 if high else 8
 disk('Stone core',.87,.48,0,n,stone)
 annulus('Stone rim',1.0,.74,.52,0,n,stone,math.pi/n if not high else 0)
 for side in [-1,1]:
  y=.275*side
  annulus('Outer metal tire',.985,.91,.035,y,n,iron)
  annulus('Fine bronze inlay',.89,.855,.04,y+side*.014,n,bronze)
  disk('Carved face',.72,.028,y,n,light)
  annulus('Face rim',.71,.65,.038,y+side*.022,n,bronze)
  for i in range(8 if high else 4):
   a=2*math.pi*i/(8 if high else 4)
   spoke('Raised radial relief',a,.24,.63,.07 if high else .09,.045,y+side*.04,stone)
   if high:bolt('Rim rivet',.94*math.cos(a),.94*math.sin(a),y+side*.035,.025,edge)
  disk('Hub base',.25,.065,y+side*.03,n,iron)
  disk('Hub ring',.19,.078,y+side*.055,n,bronze)
  disk('Hub cap',.115,.09,y+side*.075,n,edge)
  if high:
   for i in range(8):
    a=2*math.pi*i/8+math.pi/8;bolt('Hub bolt',.15*math.cos(a),.15*math.sin(a),y+side*.115,.016,iron)
def gear(high):
 n=18 if high else 8;seg=72 if high else 8
 gear_body('Gear teeth',n,.87,1.09 if high else 1.015,.30,bronze)
 for side in [-1,1]:
  y=.17*side
  annulus('Rim border',.86,.76,.045,y,seg,iron)
  annulus('Inset gold line',.755,.72,.048,y+side*.012,seg,edge)
  for i in range(8 if high else 4):
   a=2*math.pi*i/(8 if high else 4)
   spoke('Gear spoke',a,.23,.75,.13,.12,0,bronze)
   if high:bolt('Tooth rivet',.81*math.cos(a),.81*math.sin(a),y+side*.04,.025,edge)
  disk('Bearing',.29,.14,y+side*.02,seg,iron)
  disk('Axle ring',.235,.18,y+side*.04,seg,bronze)
  disk('Axle cap',.13,.21,y+side*.055,12 if high else 6,edge)
  if high:
   for i in range(6):
    a=2*math.pi*i/6;bolt('Bearing bolt',.19*math.cos(a),.19*math.sin(a),y+side*.145,.018,iron)
def join_export(name,fn,high):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 fn(high)
 for o in list(bpy.context.scene.objects):
  if o.type=='MESH':
   bpy.context.view_layer.objects.active=o;o.select_set(True)
   for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
   o.select_set(False)
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join()
 o=bpy.context.object;o.name=name
 # Set an exact shared pivot; the Stage1 Blueprint rotates about this origin.
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
 print('EXPORTED',name,'vertices',len(o.data.vertices),'materials',[m.name for m in o.data.materials],flush=True)
 # Save each editable source with its original material assignments.
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
for name,fn,high in [('Wheel_Refined_High',wheel,True),('Wheel_Refined_Low',wheel,False),('Gear_Refined_High',gear,True),('Gear_Refined_Low',gear,False)]:
 join_export(name,fn,high)
