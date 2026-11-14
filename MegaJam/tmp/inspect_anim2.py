import unreal,json,traceback
out={}
a=unreal.load_asset('/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Idle')
for n in ['get_animation_track_names','get_raw_track_data','get_raw_track_rotation_data','get_bone_pose_for_frame']:
 out[n]=str(getattr(unreal.AnimationLibrary,n).__doc__)
for n in ['data_model','controller']:
 try:
  v=a.get_editor_property(n); out[n]=str(v); out[n+'_methods']=[x for x in dir(v) if any(k in x for k in ('bone','track','key','frame'))]
 except: out[n+'_error']=traceback.format_exc()
try: out['tracks']=[str(v) for v in unreal.AnimationLibrary.get_animation_track_names(a)]
except: out['error']=traceback.format_exc()
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/anim_inspect2.json','w').write(json.dumps(out,indent=2))
