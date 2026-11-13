import json
from pathlib import Path
import unreal

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_registry.get_assets_by_path('/Game/DirectorCut/Dragon/Upper', recursive=True)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ok = levels.load_level('/Game/Level/Stage1')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if ok else []
report = {
    'loaded_stage1': ok,
    'actors': [{'label': a.get_actor_label(), 'class': a.get_class().get_name()} for a in actors],
    'dragon_assets': [str(a.package_name) for a in assets],
}
path = Path(r'C:\LHH\Epic_AI_MegaJam\MegaJam\output\Stage1_Unreal_Export\stage1_inspection.json')
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
unreal.log('STAGE1_INSPECTION_COMPLETE')
