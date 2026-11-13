import unreal
from pathlib import Path
seq=unreal.load_asset('/Game/Assets/Prologue/LS_Prologue_LastBattle_v4')
actors=unreal.EditorLevelLibrary.get_all_level_actors()
camera=next(a for a in actors if a.get_actor_label()=='Prologue_Camera')
lines=['CAM '+str(camera.get_actor_transform())]
for a in actors:
    if a.get_actor_label().startswith('Subtitle_'):
        lines.append(a.get_actor_label()+' world='+str(a.get_actor_transform())+' rel='+str(a.static_mesh_component.get_relative_transform())+' material='+str(a.static_mesh_component.get_material(0)))
for t in seq.get_tracks():
    lines.append('TRACK '+t.get_class().get_name())
    if isinstance(t,unreal.MovieSceneCameraCutTrack):
        for s in t.get_sections():lines.append('CAMCUT '+str(s.get_camera_binding_id()))
for b in seq.get_bindings():lines.append('BIND '+b.get_name()+' '+str(b.get_id()))
Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\NewKnight\subtitle_diagnostics.txt').write_text('\n'.join(lines),encoding='utf-8')
unreal.log('SUBTITLE_DIAGNOSTICS_SAVED')
