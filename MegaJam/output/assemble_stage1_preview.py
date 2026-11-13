import json
from pathlib import Path
import unreal

src='/Game/Level/Stage1'
dst='/Game/Stage1Generated/L_Stage1_Assembly'
library=unreal.EditorAssetLibrary
if library.does_asset_exist(dst):
    raise RuntimeError('Assembly already exists; refusing to overwrite '+dst)
if not library.duplicate_asset(src,dst):
    raise RuntimeError('Could not duplicate Stage1')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not levels.load_level(dst):
    raise RuntimeError('Could not load assembly level')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
paths={
 'Ground':'/Game/Stage1Generated/Meshes/Stage1_Ground',
 'Backdrop':'/Game/Stage1Generated/Meshes/Stage1_Backdrop',
 'WheelHigh':'/Game/Stage1Generated/PivotReady/Wheel_High',
 'WheelLow':'/Game/Stage1Generated/PivotReady/Wheel_Low',
 'GearHigh':'/Game/Stage1Generated/PivotReady/Gear_High',
 'GearLow':'/Game/Stage1Generated/PivotReady/Gear_Low',
 'Lift':'/Game/Stage1Generated/PivotReady/LiftPlatform',
}
locations={'Ground':(0,0,0),'Backdrop':(0,0,0),'WheelHigh':(440,0,149),'WheelLow':(440,0,149),'GearHigh':(8200,-153,200),'GearLow':(8200,-153,200),'Lift':(8700,0,15)}
spawned={}
for name,path in paths.items():
    mesh=unreal.load_asset(path)
    if not mesh: raise RuntimeError('Missing asset '+path)
    if name=='Ground':
        body=mesh.get_editor_property('body_setup')
        body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        library.save_loaded_asset(mesh)
    x,y,z=locations[name]
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z))
    actor.set_actor_label('Stage1_'+name)
    comp=actor.static_mesh_component
    comp.set_static_mesh(mesh)
    if name=='Backdrop': comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    if name in ('WheelLow','GearLow'):
        actor.set_actor_hidden_in_game(True)
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    spawned[name]=actor.get_path_name()
dragon=unreal.load_asset('/Game/DirectorCut/Dragon/Upper/SK_Dragon_Upper')
if not dragon: raise RuntimeError('Missing SK_Dragon_Upper')
preview=actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(-1000,0,60))
preview.set_actor_label('Dragon_Reference_NotPlayer')
preview.skeletal_mesh_component.set_skeletal_mesh_asset(dragon)
if not levels.save_current_level(): raise RuntimeError('Could not save assembly level')
Path(r'C:\LHH\Epic_AI_MegaJam\MegaJam\output\Stage1_Unreal_Export\assembly_report.json').write_text(json.dumps({'level':dst,'actors':spawned,'dragon':preview.get_path_name()},indent=2),encoding='utf8')
unreal.log('STAGE1_PREVIEW_ASSEMBLY_COMPLETE')
