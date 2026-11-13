import unreal
from pathlib import Path
seq=unreal.load_asset('/Game/Assets/Prologue/LS_Prologue_LastBattle_v4')
lines=[]
for b in seq.get_bindings():
    if b.get_name()=='Prologue_Camera':lines.append('CAM_BIND '+str(b.get_id().to_string()))
for t in seq.get_tracks():
    if isinstance(t,unreal.MovieSceneCameraCutTrack):
        for s in t.get_sections():
            bid=s.get_camera_binding_id()
            try:lines.append('CUT_GUID '+str(bid.get_editor_property('guid').to_string()))
            except Exception as e:lines.append('CUT_ERR '+str(e))
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if isinstance(a,unreal.LevelSequenceActor):
        lines.append('PLAYER '+a.get_actor_label()+' '+str(a.get_sequence())+' autoplay='+str(a.get_editor_property('playback_settings').get_editor_property('auto_play')))
Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\NewKnight\camera_diag.txt').write_text('\n'.join(lines),encoding='utf-8')
unreal.log('CAMERA_DIAG_SAVED')
