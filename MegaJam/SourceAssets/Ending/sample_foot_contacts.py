import unreal,json
from pathlib import Path
out={}
for name in ['A_Dragon_AwkwardWalk','A_HeroLegs_Scurry']:
 anim=unreal.load_asset('/Game/DirectorCut/Ending/Animation/'+name)
 pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,0,unreal.AnimPoseEvaluationOptions())
 bones=[str(n) for n in pose.get_bone_names() if any(k in str(n).lower() for k in ['foot','toe'])]
 data=[]
 for f in range(49 if 'Dragon' in name else 25):
  pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,f/24,unreal.AnimPoseEvaluationOptions())
  data.append({b:pose.get_bone_pose(b,unreal.AnimPoseSpaces.WORLD).translation.to_tuple() for b in bones})
 out[name]=dict(rate=anim.get_editor_property('rate_scale'),bones=bones,samples=data)
Path(unreal.Paths.project_dir(),'SourceAssets/Ending/foot_samples.json').write_text(json.dumps(out,indent=2),encoding='utf8')
