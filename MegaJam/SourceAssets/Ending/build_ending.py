"""Build the interactive ending. Run in Unreal Editor: Tools > Execute Python Script.

The prologue is copied only when the ending map does not already exist.
Existing ending-owned actors and sequences are rebuilt; the prologue stays intact.
"""
from pathlib import Path
import json
import unreal

P = '/Game/DirectorCut/Ending/'
LEVEL = P + 'L_BossEnding'
FPS = 24
# Top of the existing Boss Arena Stone Floor2 at the dragon's mark.
GROUND = 20.07
lib = unreal.EditorAssetLibrary
ed = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
if not lib.does_asset_exist(LEVEL):
    assert ed.load_level('/Game/DirectorCut/Prologue/L_BossPrologue')
    assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), LEVEL)
assert ed.load_level(LEVEL)
for a in actor_sub.get_all_level_actors():
    label = a.get_actor_label()
    if (label.startswith('Ending_') or 'Subtitle' in label or 'Developer_Note' in label
        or 'Storage_Sign' in label or 'NiagaraBreath' in label or label in ('Prologue Sequence', 'Player Dragon')
        or a.get_class().get_name() == 'DirectorCutSequenceTransition'):
        actor_sub.destroy_actor(a)
actors = {a.get_actor_label(): a for a in actor_sub.get_all_level_actors()}
camera = actors.get('Ending Camera') or actors['Prologue Side Camera']
camera.set_actor_label('Ending Camera')
START = (390, 1150, 245)
camera.set_actor_location(unreal.Vector(*START), False, False)
camera.set_actor_rotation(unreal.Rotator(pitch=-2, yaw=-90, roll=0), False)
upper = actors.get('Ending Dragon Upper') or actors['Prologue Dragon']
upper.set_actor_label('Ending Dragon Upper')
upper.set_actor_location(unreal.Vector(1271.6, 3.5, -17.8), False, False)
upper.set_actor_rotation(unreal.Rotator(pitch=-24.285647615, yaw=180, roll=0), False)
upper.set_actor_scale3d(unreal.Vector(7.5, 7.5, 7.5))
upper.skeletal_mesh_component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
upper.skeletal_mesh_component.set_editor_property('animation_data', unreal.SingleAnimationPlayData())
hero = actors.get('Ending Hero') or actors['BossIntro_Hero']
hero.set_actor_label('Ending Hero')
hero.skeletal_mesh_component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
hero.skeletal_mesh_component.set_animation(unreal.load_asset('/Game/Assets/Knight/Anim/Crouch_Idle'))
hero.skeletal_mesh_component.play(True)

def spawn_mesh(label, path, location, scale, rotation=(0,180,0)):
    mesh = unreal.load_asset(path)
    assert mesh, path
    a = actor_sub.spawn_actor_from_class(unreal.SkeletalMeshActor if isinstance(mesh,unreal.SkeletalMesh) else unreal.StaticMeshActor,
        unreal.Vector(*location), unreal.Rotator(pitch=rotation[0],yaw=rotation[1],roll=rotation[2]))
    a.set_actor_label('Ending_' + label)
    c = a.get_component_by_class(unreal.MeshComponent)
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    if isinstance(c,unreal.SkeletalMeshComponent): c.set_skeletal_mesh_asset(mesh)
    else: c.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(*scale))
    return a

full = spawn_mesh('Dragon_Original','/Game/DirectorCut/Dragon/Origin/SK_Dragon_Origin',(1271.6,3.5,GROUND),(7.5,7.5,7.5))
cart_origin = unreal.Vector(1165.85,3.5,GROUND)
CART_SCALE = 3.4
cart = spawn_mesh('Cart','/Game/DirectorCut/Stage1/RideCart/SM_Dragon_Ride_Cart',cart_origin.to_tuple(),(CART_SCALE,)*3)
wheels = []
for i, center in enumerate([(-37.62,-35.64,17.5),(-37.62,35.64,17.5),(36.63,-34.32,17.5),(36.63,34.32,17.5)],1):
    local = unreal.Vector(*center) * CART_SCALE
    pos = cart_origin + unreal.Vector(-local.x,-local.y,local.z)
    wheels.append(spawn_mesh('Cart_Wheel_'+str(i),f'/Game/DirectorCut/Stage1/RideCart/SM_Dragon_Cart_Wheel_{i}',pos.to_tuple(),(CART_SCALE,)*3))
hero_legs = spawn_mesh('Hero_Legs','/Game/DirectorCut/Dragon/KnightLegs/SK_Knight_LowerBody',(1165.85,3.5,GROUND),(4.1,4.1,4.1),(0,90,0))

def upper_transform(waist_z):
    # Both models face the hero. Align the cut-waist center to the new lower body's support.
    return unreal.Transform(location=unreal.Vector(1271.6,3.5,waist_z-43.75*7.5+3),rotation=unreal.Rotator(pitch=0,yaw=180,roll=0),scale=unreal.Vector(7.5,7.5,7.5))
cart_upper = upper_transform(GROUND+31.9*CART_SCALE)
hero_upper = upper_transform(GROUND+40.5*4.1)

def sequence(name, duration, keys):
    path=P+name
    if lib.does_asset_exist(path):
        assert lib.delete_asset(path)
    s=tools.create_asset(name,P,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
    s.set_display_rate(unreal.FrameRate(FPS,1))
    s.set_playback_start(0); s.set_playback_end(duration)

    binding=s.add_possessable(camera)
    t=binding.add_track(unreal.MovieScene3DTransformTrack)
    sec=t.add_section(); sec.set_range(0,duration)
    sec.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
    channels=sec.get_all_channels()
    for f,pos,rot in keys:
        values=list(pos)+[rot[2],rot[0],rot[1]]+[1,1,1]
        for ch,val in zip(channels,values):
            ch.add_key(unreal.FrameNumber(f),float(val),interpolation=unreal.MovieSceneKeyInterpolation.AUTO)
    cut=s.add_track(unreal.MovieSceneCameraCutTrack).add_section()
    cut.set_range(0,duration)
    binding_id=unreal.MovieSceneObjectBindingID()
    binding_id.set_editor_property('guid',binding.get_id())
    cut.set_camera_binding_id(binding_id)
    # The hero stays alive while the static initial pose of the dragon matches the prologue.
    hb=s.add_possessable(hero)
    anim=hb.add_track(unreal.MovieSceneSkeletalAnimationTrack).add_section()
    anim.set_range(0,duration)
    params=anim.get_editor_property('params')
    params.animation=unreal.load_asset('/Game/Assets/Knight/Anim/Crouch_Idle')
    anim.set_editor_property('params',params)
    for frame,label in [(0,'START / Prologue matching shot'),(duration-1,'HOLD / Ready for next scene')]:
        s.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(frame),label=label))
    sa=actor_sub.spawn_actor_from_class(unreal.LevelSequenceActor,unreal.Vector())
    sa.set_actor_label('Ending_'+name)
    sa.set_sequence(s)
    settings=sa.get_editor_property('playback_settings')
    settings.auto_play=False; settings.pause_at_end=False
    settings.finish_completion_state_override=unreal.MovieSceneCompletionModeOverride.FORCE_KEEP_STATE
    sa.set_editor_property('playback_settings',settings)
    lib.save_loaded_asset(s)
    return sa,s

intro,intro_seq=sequence('LS_BossEnding_Dialogue',240,[(0,START,(-2,-90,0)),(239,START,(-2,-90,0))])
dragon_idle=intro_seq.add_possessable(upper).add_track(unreal.MovieSceneSkeletalAnimationTrack).add_section()
dragon_idle.set_range(0,240)
dragon_idle.params.set_editor_property('animation',unreal.load_asset('/Game/DirectorCut/Stage1/RideCart/A_Dragon_Cart_Breathe'))
dragon_idle.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
reveal,reveal_seq=sequence('LS_BossEnding_Reveal',156,[(0,START,(-2,-90,0)),(36,(1155,2050,470),(-3,-90,0)),(72,(1155,2050,470),(-3,-90,0)),(132,START,(-2,-90,0)),(155,START,(-2,-90,0))])
for f,label in [(14,'Hero subtitle'),(130,'Dragon subtitle'),(239,'PLAYER CHOICE / no time limit')]:
    intro_seq.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(f),label=label))
for f,label in [(36,'Selected dragon full view'),(72,'Return camera movement'),(132,'Opening camera restored')]:
    reveal_seq.add_marked_frame(unreal.MovieSceneMarkedFrame(frame_number=unreal.FrameNumber(f),label=label))

cls=unreal.load_class(None,'/Script/MegaJam.DirectorCutEnding')
assert cls, 'Compile DirectorCutEnding first'
controller=actor_sub.spawn_actor_from_class(cls,unreal.Vector())
controller.set_actor_label('Ending_Controller')
for prop,val in {'IntroSequenceActor':intro,'RevealSequenceActor':reveal,'EndingCamera':camera,
    'FullDragon':full,'UpperDragon':upper,'CartBody':cart,'CartAccessories':wheels,'HeroLegs':hero_legs,
    'bUseVariantUpperTransforms':True,'CartUpperTransform':cart_upper,'HeroUpperTransform':hero_upper}.items():
    controller.set_editor_property(prop,val)
for a in [full,cart,hero_legs]+wheels:
    a.set_actor_hidden_in_game(True)
    a.set_is_temporarily_hidden_in_editor(True)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',unreal.GameModeBase)
for s in [intro_seq,reveal_seq]: lib.save_loaded_asset(s)
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(*START),unreal.Rotator(pitch=-2,yaw=-90,roll=0))
image_names=['T_Ending_DragonLegs','T_Ending_Cart','T_Ending_HeroLegs']
for name in image_names:
    if not lib.does_asset_exist(P+'UI/'+name):
        task=unreal.AssetImportTask()
        task.filename=str(Path(__file__).resolve().parent/'Images'/(name+'.png'))
        task.destination_path=P+'UI'; task.destination_name=name
        task.automated=True; task.save=True
        tools.import_asset_tasks([task])
        texture=unreal.load_asset(P+'UI/'+name)
        texture.set_editor_property('lod_group',unreal.TextureGroup.TEXTUREGROUP_UI)
        texture.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
        lib.save_loaded_asset(texture)
images=[unreal.load_asset(P+'UI/'+n) for n in image_names]
if all(images):
    controller.set_editor_property('OptionImages',images)
    unreal.EditorLevelLibrary.save_current_level()
Path(unreal.Paths.project_saved_dir(),'ending_build.json').write_text(json.dumps({'level':LEVEL,'intro':intro_seq.get_path_name(),'reveal':reveal_seq.get_path_name(),'controller':controller.get_path_name(),'camera_fov':camera.camera_component.field_of_view,'waist_metadata':lib.get_metadata_tag(hero_legs.skeletal_mesh_component.skeletal_mesh_asset,'WaistHeightCm')},indent=2),encoding='utf8')
voice_installer=Path(__file__).resolve().parent/'install_voices.py'
if voice_installer.exists() and (voice_installer.parent/'Voice'/'S_Ending_Hero.wav').exists():
    exec(compile(voice_installer.read_text(encoding='utf-8-sig'),str(voice_installer),'exec'),{'__name__':'__main__'})
alignment_installer=Path(__file__).resolve().parent/'align_lower_bodies.py'
exec(compile(alignment_installer.read_text(encoding='utf-8-sig'),str(alignment_installer),'exec'),{'__name__':'__main__'})
original_legs_builder=Path(__file__).resolve().parent/'build_original_legs_scene.py'
if original_legs_builder.exists():
    exec(compile(original_legs_builder.read_text(encoding='utf-8-sig'),str(original_legs_builder),'exec'),{'__name__':'__main__'})
cart_builder=Path(__file__).resolve().parent/'build_cart_scene.py'
if cart_builder.exists():
    exec(compile(cart_builder.read_text(encoding='utf-8-sig'),str(cart_builder),'exec'),{'__name__':'__main__'})
unreal.log('ENDING_BUILD_DONE')




