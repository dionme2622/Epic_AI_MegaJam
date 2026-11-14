import unreal,json,traceback
out={}
for name in ['Idle','Combat_Idle','Run','Jump']:
 a=unreal.load_asset('/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_'+name)
 out[name]={}
 for b in ['root','pelvis','spine']:
  try:
   p,q,s=unreal.AnimationLibrary.get_raw_track_data(a,b)
   out[name][b]={'n':[len(p),len(q),len(s)],'pos':str(p[0]),'rot':str(q[0]),'scale':str(s[0]),'pose':str(unreal.AnimationLibrary.get_bone_pose_for_frame(a,b,0,False))}
  except: out[name][b]=traceback.format_exc()
c=a.get_editor_property('controller');out['set_doc']=c.set_bone_track_keys.__doc__
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/anim_inspect3.json','w').write(json.dumps(out,indent=2))
