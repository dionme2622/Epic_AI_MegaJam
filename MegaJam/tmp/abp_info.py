import unreal,json,traceback
out={}
for path in ['/Game/Level/Character/ABP_Dragon','/Game/Level/Character/BP_Dragon']:
 a=unreal.load_asset(path); d={'class':str(a.get_class()),'methods':[x for x in dir(a) if any(k in x for k in ['skeleton','preview','generated','status'])]}
 for p in ['target_skeleton','preview_skeletal_mesh','status','parent_class','generated_class']:
  try:d[p]=str(a.get_editor_property(p))
  except:pass
 try:
  cls=a.generated_class();cdo=unreal.get_default_object(cls)
  mesh=cdo.get_editor_property('mesh')
  for p in ['skeletal_mesh_asset','anim_class','animation_mode','relative_rotation']:
   try:d[p]=str(mesh.get_editor_property(p))
   except:pass
 except:pass
 out[path]=d
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/abp_info.json','w').write(json.dumps(out,indent=2))
