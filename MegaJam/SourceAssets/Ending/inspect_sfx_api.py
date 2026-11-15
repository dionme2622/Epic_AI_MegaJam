import unreal,json
from pathlib import Path
out={}
for name in ['AnimPoseExtensions','AnimPoseEvaluationOptions','AnimPose','AnimationLibrary']:
 c=getattr(unreal,name,None)
 out[name]={n:getattr(c,n).__doc__ for n in dir(c or []) if any(k in n for k in ['pose_at','bone_pose','bone_names','transform','evaluate'])}
Path(unreal.Paths.project_dir(),'SourceAssets/Ending/sfx_api.json').write_text(json.dumps(out,indent=2),encoding='utf8')
