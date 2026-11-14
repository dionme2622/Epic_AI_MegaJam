import unreal, json, traceback
out={}
try:
 a=unreal.load_asset('/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Idle')
 out['asset']=str(a)
 out['anim_methods']=[x for x in dir(a) if any(k in x for k in ('model','controller','bone','track'))]
 out['lib_methods']=[x for x in dir(unreal.AnimationLibrary) if any(k in x for k in ('bone','track','key'))]
 m=a.get_data_model()
 c=a.get_controller()
 out['model_methods']=[x for x in dir(m) if any(k in x for k in ('bone','track','key','frame'))]
 out['controller_methods']=[x for x in dir(c) if any(k in x for k in ('bone','track','key'))]
 out['bones']=[str(x) for x in m.get_bone_track_names()]
 for b in out['bones'][:3]:
  out[b]=str(m.get_bone_track_transforms(b))[:3000]
except: out['error']=traceback.format_exc()
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/anim_inspect.json','w').write(json.dumps(out,indent=2))
