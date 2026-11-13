import unreal
from pathlib import Path
a={x.get_actor_label():x for x in unreal.EditorLevelLibrary.get_all_level_actors()}
lines=[]
for name in ('Toy_Castle_Stage','Hero_Victor','Dragon_Upper_Body_Cube','Prologue_Camera','Subtitle_01_Victory'):
    x=a[name]
    lines.append(name+' loc='+str(x.get_actor_location())+' rot='+str(x.get_actor_rotation())+' scale='+str(x.get_actor_scale3d())+' bounds='+str(x.get_actor_bounds(False)))
lines.append('camera_forward='+str(a['Prologue_Camera'].get_actor_forward_vector()))
Path(r'D:\UnrealProject\Epic_AI_MegaJam\MegaJam\SourceAssets\NewKnight\stage_diag.txt').write_text('\n'.join(lines),encoding='utf-8')
unreal.log('STAGE_DIAG_SAVED')
