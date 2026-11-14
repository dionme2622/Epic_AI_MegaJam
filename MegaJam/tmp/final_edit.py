import unreal,json,traceback
out={}
try:
 base='/Game/DirectorCut/Dragon/Upper/'
 a=unreal.load_asset(base+'SK_Dragon_UpperArmature_Idle')
 test=unreal.load_asset(base+'SK_Dragon_UpperArmature_Idle_OrientationTest')
 n=unreal.AnimationLibrary.get_num_keys(a)
 original=[unreal.AnimationLibrary.get_bone_pose_for_frame(a,'root',i,False) for i in range(n)]
 corrected=[unreal.AnimationLibrary.get_bone_pose_for_frame(test,'root',i,False).rotation for i in range(n)]
 before={b:[str(unreal.AnimationLibrary.get_bone_pose_for_frame(a,b,i,False)) for i in (0,n//2,n-1)] for b in ['pelvis','head','wing_l']}
 assert a.get_editor_property('controller').set_bone_track_keys('root',[p.translation for p in original],corrected,[p.scale3d for p in original])
 after={b:[str(unreal.AnimationLibrary.get_bone_pose_for_frame(a,b,i,False)) for i in (0,n//2,n-1)] for b in before}
 # Compare values, not struct addresses.
 out['unchanged_other_tracks']=all([s.split('{',1)[1] for s in before[b]]==[s.split('{',1)[1] for s in after[b]] for b in before)
 assert out['unchanged_other_tracks']
 out['saved']=unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
 out['frames']=n
 out['root_first']=str(unreal.AnimationLibrary.get_bone_pose_for_frame(a,'root',0,False))
 out['root_last']=str(unreal.AnimationLibrary.get_bone_pose_for_frame(a,'root',n-1,False))
except:out['error']=traceback.format_exc()
open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/final_edit.json','w').write(json.dumps(out,indent=2))
