import unreal,json
from pathlib import Path
controller=unreal.get_default_object(unreal.DirectorCutLobbyController)
# ConstructorHelpers loads these dependencies when the controller CDO is built.
music=unreal.find_object(None,'/Game/DirectorCut/Audio/S_Gameplay_ProcessingPower.S_Gameplay_ProcessingPower')
click=unreal.find_object(None,'/Game/DirectorCut/Ending/SFX/S_UI_Select.S_UI_Select')
assert music and click
assert music.get_path_name()=='/Game/DirectorCut/Audio/S_Gameplay_ProcessingPower.S_Gameplay_ProcessingPower'
assert music.get_editor_property('looping')
assert click.get_path_name()=='/Game/DirectorCut/Ending/SFX/S_UI_Select.S_UI_Select'
assert 0 < click.get_editor_property('duration') < 1
Path(unreal.Paths.project_dir(),'SourceAssets/GameplayBGM/lobby_verification.json').write_text(json.dumps(dict(
 music=music.get_path_name(),looping=True,click=click.get_path_name(),
 click_duration=click.get_editor_property('duration'),passed=True),indent=2),encoding='utf8')
unreal.log('LOBBY_AUDIO_ASSET_VERIFICATION_PASS')
