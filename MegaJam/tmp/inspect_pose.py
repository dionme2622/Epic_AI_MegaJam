import unreal,json,traceback
out={}
for name in ['Idle','Combat_Idle','Run']:
 a=unreal.load_asset('/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_'+name)
 out[name]={}
 for b in ['root','pelvis','spine','chest','head']:
  try: out[name][b]=[str(unreal.AnimationLibrary.get_bone_pose_for_frame(a,b,i,False)) for i in [0,10]]
  except:out[name][b]=traceback.format_exc()
 out[name]['keys']=unreal.AnimationLibrary.get_num_keys(a)
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/anim_pose.json','w').write(json.dumps(out,indent=2))
