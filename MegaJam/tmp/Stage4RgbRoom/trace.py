import unreal as u
from pathlib import Path
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
start=u.Vector(1020,0,75)
end=u.Vector(1230,0,75)
for label,x in (("room",0),("join",1205)):
    hit=u.SystemLibrary.line_trace_single(world,u.Vector(x,0,15),u.Vector(x,0,-35),
        u.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],u.DrawDebugTrace.NONE,True)
    assert hit,label
gate_hit=u.SystemLibrary.line_trace_single(world,start,end,u.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],u.DrawDebugTrace.NONE,True)
door=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.Actor) if a.get_actor_label()=="Color_ExitDoor")
p=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4RgbRoom/collision.txt")
p.write_text(str((bool(gate_hit),door.get_editor_property("bOpen"),str(gate_hit)[:650])))
