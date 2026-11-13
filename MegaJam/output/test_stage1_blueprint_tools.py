import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools
bp=BlueprintTools.create('/Game/Stage1Generated','BP_Stage1Director_Test2',unreal.Actor.static_class())
graph=BlueprintTools.get_graph(bp,'EventGraph')
BlueprintTools.add_variable(bp,'IsLow','bool')
BlueprintTools.compile_blueprint(bp)
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp])
BlueprintTools.write_graph_dsl(graph,'(event EventBeginPlay (Variables|Default|SetIsLow true))')
unreal.EditorAssetLibrary.save_loaded_asset(bp)
unreal.log('STAGE1_BLUEPRINT_TOOLS_OK')
