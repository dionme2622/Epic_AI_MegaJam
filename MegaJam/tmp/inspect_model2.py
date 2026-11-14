import unreal,json,traceback
a=unreal.load_asset('/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Idle'); c=a.get_editor_property('controller');m=c.get_model_interface();out={}
for n in ['get_bone_animation_tracks','get_bone_track_by_name','get_bone_track_names']:
 out[n+'_doc']=str(getattr(m,n).__doc__)
try:
 out['names']=[str(x) for x in m.get_bone_track_names()];out['track']=str(m.get_bone_track_by_name('root'))
except:out['err']=traceback.format_exc()
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/model2.json','w').write(json.dumps(out,indent=2))
