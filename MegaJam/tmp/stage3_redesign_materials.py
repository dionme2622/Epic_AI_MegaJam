import unreal as u
api=u.get_editor_subsystem(u.EditorActorSubsystem);le=u.get_editor_subsystem(u.LevelEditorSubsystem);lib=u.EditorAssetLibrary
def actors(): return {a.get_actor_label():a for a in api.get_all_level_actors()}
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name()=='/Game/DirectorCut/Stage/Stage3_.Stage3_'
a=actors()
dark=lib.load_asset('/Game/Stage4Integrated/Theatre/M03_Slate')
gold=lib.load_asset('/Game/Stage4Integrated/Theatre/M08_Highlight')
assert dark and gold
a['Focus_Floor'].static_mesh_component.set_material(0,dark)
controller=a['Focus_Controller']
for prop in ('NearPiece','FarPiece'):
 c=controller.get_editor_property(prop)
 for i in range(c.get_num_materials()):c.set_material(i,gold)
assert le.save_current_level()
assert le.load_level('/Game/Stage3Integrated/Sections/L_Bloom')
a=actors();a['Bloom_Floor'].static_mesh_component.set_material(0,dark)
assert le.save_current_level()
assert le.load_level('/Game/Stage3Integrated/Sections/L_Resolution')
a=actors()
for label in ('Resolution_StartFloor','Resolution_EndFloor'):
 a[label].static_mesh_component.set_material(0,dark)
for i in (1,2,3,4,5):
 c=a['Resolution_Tile_'+str(i)].get_editor_property('Mesh')
 if c.get_num_materials()>1:c.set_material(1,lib.load_asset('/Game/Stage4Integrated/Theatre/M05_Capstone'))
assert le.save_current_level()
assert le.load_level('/Game/DirectorCut/Stage/Stage3_')
u.log('STAGE3 CONTRAST AND FLOOR MATERIALS SAVED')
