"""Keep the developer note in the scene, behind the dragon and ahead of the wall."""
import unreal
from pathlib import Path
lib=unreal.EditorAssetLibrary
note=next(a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label()=='BossIntro_Developer_Note')
seq=unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
for binding in seq.get_bindings():
 if binding.get_name()=='BossIntro_Developer_Note':
  for track in binding.get_tracks():
   if isinstance(track,unreal.MovieSceneVisibilityTrack):binding.remove_track(track)
note.set_actor_hidden_in_game(False)
note.set_is_temporarily_hidden_in_editor(False)
note.set_actor_location(unreal.Vector(1210,-300,245),False,False)
# Preserve the angular size of the former foreground card at the note shot.
note.set_actor_scale3d(unreal.Vector(3.776,3.021,1))
mesh=note.get_component_by_class(unreal.StaticMeshComponent)
mesh.set_visibility(True,True)
mat=mesh.get_material(0)
base=mat
while isinstance(base,unreal.MaterialInstanceConstant):base=base.get_editor_property('parent')
depth_disabled=base.get_editor_property('disable_depth_test')
if depth_disabled:
 # Captions can retain their overlay material; only the wall note gains depth.
 path='/Game/DirectorCut/Prologue/Cinematic/M_DevNote_WorldDepth'
 depthmat=unreal.load_asset(path) if lib.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset('M_DevNote_WorldDepth','/Game/DirectorCut/Prologue/Cinematic',base)
 depthmat.set_editor_property('disable_depth_test',False)
 unreal.MaterialEditingLibrary.recompile_material(depthmat)
 mat.set_editor_property('parent',depthmat)
 lib.save_loaded_asset(depthmat,False);lib.save_loaded_asset(mat,False)
lib.save_loaded_asset(seq,False)
assert unreal.EditorLevelLibrary.save_current_level()
Path(unreal.Paths.project_saved_dir(),'note_persistent_applied.txt').write_text('location='+str(note.get_actor_location())+'\nscale='+str(note.get_actor_scale3d())+'\noriginal_depth_disabled='+str(depth_disabled)+'\nbase_material='+str(base))
