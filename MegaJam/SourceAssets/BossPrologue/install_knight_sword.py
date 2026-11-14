import unreal,json
from pathlib import Path
P='/Game/DirectorCut/Prologue/'
seq=unreal.load_asset(P+'LS_BossPrologue_Cinematic')
hero=next(a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label()=='BossIntro_Hero')
mesh=hero.get_component_by_class(unreal.SkeletalMeshComponent)
anim=unreal.load_asset('/Game/Assets/Knight/Anim/Withdrawing_Sword')
opts=unreal.AnimPoseEvaluationOptions();opts.optional_skeletal_mesh=mesh.skeletal_mesh_asset
samples=[]
for i in range(46):
 t=i/60
 pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,t,opts)
 h=pose.get_bone_pose('RightHand',unreal.AnimPoseSpaces.WORLD)
 l=pose.get_bone_pose('LeftUpLeg',unreal.AnimPoseSpaces.WORLD)
 samples.append((h.translation.distance(l.translation),t,pose))
dist,t,pose=min(samples,key=lambda x:x[0])
world=mesh.get_world_transform()
def bone(n):return unreal.MathLibrary.compose_transforms(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD),world)
hand=bone('RightHand');thigh=bone('LeftUpLeg');knee=bone('LeftLeg');finger=bone('RightHandMiddle1')
grasp=hand.translation+(finger.translation-hand.translation)*.42
thigh_axis=(knee.translation-thigh.translation).normal()
original_rotation=unreal.MathLibrary.make_rot_from_z(thigh_axis)
# Reverse the blade 180 degrees around its local width axis, at the grip.
# The wrist then carries the same grip from the inward stowed pose to a
# forward, thumb-side blade when the knight raises his right hand.
blade=thigh_axis*-1.0
rotation=unreal.MathLibrary.make_rot_from_xz(
 unreal.MathLibrary.get_forward_vector(original_rotation),blade)
scale=.72
sword_world=unreal.Transform(grasp+blade*(8*scale),rotation,unreal.Vector(scale,scale,scale))
relative_thigh=unreal.MathLibrary.make_relative_transform(sword_world,thigh)
relative_hand=unreal.MathLibrary.make_relative_transform(sword_world,hand)
# Play the 1.5 second clip exactly once over its existing 51 frame slot.
hero_binding=next(b for b in seq.get_bindings() if b.get_name()=='BossIntro_Hero')
for track in hero_binding.get_tracks():
 if isinstance(track,unreal.MovieSceneSkeletalAnimationTrack):
  for section in track.get_sections():
   if section.params.animation==anim:
    params=section.params
    params.set_editor_property('play_rate',unreal.MovieSceneTimeWarpVariant(anim.get_play_length()/(51/24)))
    section.params=params
switch=171+round(t/anim.get_play_length()*51)
for b in seq.get_bindings():
 if b.get_name()=='BossIntro_Knight_Sword':b.remove()
for a in unreal.EditorLevelLibrary.get_all_level_actors():
 if a.get_actor_label()=='BossIntro_Knight_Sword':unreal.EditorLevelLibrary.destroy_actor(a)
sword=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(),unreal.Rotator())
sword.set_actor_label('BossIntro_Knight_Sword')
sword.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sword.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Assets/Knight/Knight_Sword'))
sword.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
sword.attach_to_component(mesh,'LeftUpLeg',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
sword.static_mesh_component.set_relative_transform(relative_thigh,False,False)
b=seq.add_possessable(sword)
attach=b.add_track(unreal.MovieScene3DAttachTrack)
transform=b.add_track(unreal.MovieScene3DTransformTrack)
parent=unreal.MovieSceneObjectBindingID();parent.set_editor_property('guid',hero_binding.get_id())
for start,end,socket,relative in [(0,switch,'LeftUpLeg',relative_thigh),(switch,600,'RightHand',relative_hand)]:
 s=attach.add_section();s.set_range(start,end);s.set_constraint_binding_id(parent)
 s.set_editor_property('attach_component_name',mesh.get_name());s.set_editor_property('attach_socket_name',socket)
 for axis in ['location','rotation','scale']:s.set_editor_property('attachment_'+axis+'_rule',unreal.AttachmentRule.KEEP_RELATIVE)
 ts=transform.add_section();ts.set_range(start,end)
 loc=relative.translation;rot=relative.rotation.rotator();sc=relative.scale3d
 values=[loc.x,loc.y,loc.z,rot.roll,rot.pitch,rot.yaw,sc.x,sc.y,sc.z]
 for c,v in zip(ts.get_all_channels(),values):c.set_default(v)
lib=unreal.EditorAssetLibrary
lib.save_loaded_asset(seq,False)
unreal.EditorLevelLibrary.save_current_level()
Path(unreal.Paths.project_saved_dir(),'sword_installed.txt').write_text(f'contact_time={t} switch_frame={switch} distance={dist}\nworld={sword_world}\n thigh={relative_thigh}\nhand={relative_hand}')


