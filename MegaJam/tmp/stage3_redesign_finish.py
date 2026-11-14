import unreal as u
from pathlib import Path
root=Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam')
exec(compile((root/'tmp/Stage3ResolutionArt/import_assets.py').read_text(encoding='utf8'),str(root/'tmp/Stage3ResolutionArt/import_assets.py'),'exec'))
api=u.get_editor_subsystem(u.EditorActorSubsystem); levels=u.get_editor_subsystem(u.LevelEditorSubsystem); lib=u.EditorAssetLibrary
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name()=='/Game/DirectorCut/Stage/Stage3_.Stage3_'
existing={a.get_actor_label():a for a in api.get_all_level_actors()}
def add(label,mesh,xyz,scale=(1,1,1)):
 a=existing.get(label)
 if not a:
  a=api.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*xyz),u.Rotator()); a.set_actor_label(label); existing[label]=a
 a.set_folder_path('Stage3/Film Archive/Resolution Dressing')
 a.set_actor_location(u.Vector(*xyz),False,True);a.set_actor_scale3d(u.Vector(*scale))
 c=a.static_mesh_component;c.set_static_mesh(lib.load_asset('/Game/Stage3Integrated/Archive/'+mesh));c.set_collision_profile_name('NoCollision');c.set_cast_shadow(False);c.set_editor_property('affect_distance_field_lighting',False)
 return a
# The gallery tiles are visual overlays only. The puzzle floor and fall tiles
# retain their original collision; the fourth floor ends before the tile course.
for i in range(1,6):
 a=existing['Archive Stone Floor '+str(i)];p=a.get_actor_location();p.z=1.0;a.set_actor_location(p,False,True)
# The former plain orange block is a large rear workbench, not the walkable path.
work=existing['Focus_Stage'];work.static_mesh_component.set_material(0,lib.load_asset('/Game/Stage4Integrated/Theatre/M10_Plank'))
cube=lib.load_asset('/Engine/BasicShapes/Cube');gold=lib.load_asset('/Game/Stage4Integrated/Theatre/M07_Tarnish')
for label,x,y,z,sx,sy,sz in [
 ('Focus Workbench Top Trim',500,-95,145,7.05,.1,.12),
 ('Focus Workbench Bottom Trim',500,-95,18,7.05,.1,.08),
 ('Focus Workbench Left Trim',162,-95,80,.09,.1,1.3),
 ('Focus Workbench Right Trim',838,-95,80,.09,.1,1.3)]:
 a=existing.get(label)
 if not a: a=api.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,z),u.Rotator());a.set_actor_label(label)
 a.set_folder_path('Stage3/Film Archive/Puzzle Props');a.set_actor_location(u.Vector(x,y,z),False,True);a.set_actor_scale3d(u.Vector(sx,sy,sz))
 c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,gold);c.set_collision_profile_name('NoCollision');c.set_cast_shadow(False)
for i,x in enumerate((5550,5710,5870,6030,6190),1):
 add('Archive Mosaic Frame '+str(i),'SM_S3_DotRing',(x,-219,160),(.55,.55,.55))
for i,x in enumerate((5400,6350),1):
 add('Archive Mosaic Stained Glass '+str(i),'SM_S3_StainedGlass',(x,-242,210),(.9,.9,.9))
assert levels.save_current_level()

# Replace only the artwork components of the existing Bloom sign actors;
# the actors, input targets and puzzle references remain untouched.
assert levels.load_level('/Game/Stage3Integrated/Sections/L_Bloom')
actors={a.get_actor_label():a for a in api.get_all_level_actors()}
face_mat=lib.load_asset('/Game/BloomPuzzlePrototype/M_BloomFace')
for name,suffix in [('Star','Star'),('Moon','Moon'),('Sun','Sun')]:
 a=actors['Bloom_Sign_'+name]
 comps={c.get_name():c for c in a.get_components_by_class(u.StaticMeshComponent)}
 mesh=lib.load_asset('/Game/Stage3Integrated/Archive/SM_S3_Bloom'+suffix)
 assert mesh and face_mat
 frame=comps['Frame'];frame.set_static_mesh(mesh);frame.set_relative_scale3d(u.Vector(1.05,1.05,1.05))
 # Slot overrides inherited from the old frame must not tint the new model.
 for idx in range(frame.get_num_materials()):frame.set_material(idx,mesh.get_material(idx))
 face=comps['Face'];face.set_static_mesh(mesh);face.set_relative_scale3d(u.Vector(.84,.84,.84))
 for idx in range(face.get_num_materials()):face.set_material(idx,face_mat)
assert levels.save_current_level()
assert levels.load_level('/Game/DirectorCut/Stage/Stage3_')
u.log('STAGE3 REFERENCE-INSPIRED REDESIGN SAVED')
