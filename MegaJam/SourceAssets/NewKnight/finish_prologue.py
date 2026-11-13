import unreal
P='/Game/Assets/Prologue/'
seq=unreal.load_asset(P+'LS_Prologue_LastBattle_v4')
plane=unreal.load_asset('/Engine/BasicShapes/Plane')
assert seq and plane
for label,matpath,loc,scale in [
    ('Developer_Note_Text',P+'Subtitles/MI_04_Dev_Note',(390,0,205),(4.5,.5,1)),
    ('Lower_Body_Storage_Text',P+'Subtitles/MI_08_Storage',(0,570,365),(3.4,.4,1))]:
    mat=unreal.load_asset(matpath);assert mat
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*loc),unreal.Rotator(0,0,90))
    a.set_actor_label(label);a.static_mesh_component.set_static_mesh(plane)
    a.static_mesh_component.set_material(0,mat);a.set_actor_scale3d(unreal.Vector(*scale))
    seq.add_possessable(a)
unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.EditorLevelLibrary.save_current_level()
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.log('PROLOGUE_FINISHED_OK')
