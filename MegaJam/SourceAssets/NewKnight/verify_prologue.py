import unreal
P='/Game/Assets/Prologue/'
tools=unreal.AssetToolsHelpers.get_asset_tools()
mat=tools.create_asset('M_Dragon_Proxy_Green',P,unreal.Material,unreal.MaterialFactoryNew())
color=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-200,0)
color.set_editor_property('constant',unreal.LinearColor(.12,.34,.22,1))
unreal.MaterialEditingLibrary.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
unreal.MaterialEditingLibrary.recompile_material(mat)
actors=unreal.EditorLevelLibrary.get_all_level_actors()
dragon=next(a for a in actors if a.get_actor_label()=='Dragon_Upper_Body_Cube')
dragon.static_mesh_component.set_material(0,mat)
seq=unreal.load_asset(P+'LS_Prologue_LastBattle_v4')
assert seq
bindings=seq.get_bindings()
labels=[a.get_actor_label() for a in actors]
assert 'Hero_Victor' in labels and 'Dragon_Upper_Body_Cube' in labels
assert sum(x.startswith('Subtitle_') for x in labels)==8
assert 'Developer_Note_Text' in labels and 'Lower_Body_Storage_Text' in labels
unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.EditorAssetLibrary.save_loaded_asset(seq)
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('PROLOGUE_VERIFIED actors='+str(len(actors))+' bindings='+str(len(bindings))+' subtitles=8')
