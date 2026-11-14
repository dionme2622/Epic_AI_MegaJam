import unreal,json,traceback
a=unreal.load_asset('/Game/DirectorCut/Dragon/Upper/SK_Dragon_UpperArmature_Idle'); c=a.get_editor_property('controller'); out={}
try:
 m=c.get_model_interface();out['model']=str(m);out['methods']=[x for x in dir(m) if 'bone' in x or 'track' in x or 'key' in x];out['type']=str(type(m))
except:out['err']=traceback.format_exc()
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/model.json','w').write(json.dumps(out,indent=2))
