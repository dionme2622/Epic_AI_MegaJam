import ctypes
import json
import time
from pathlib import Path
import unreal as u

output=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Retake/jumps.json")
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
pawn=u.GameplayStatics.get_player_character(world,0)
pc=u.GameplayStatics.get_player_controller(world,0)
manager=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.Actor) if a.get_actor_label()=="Shadow Rehearsal")
assert manager.get_editor_property("EntranceDoor").get_editor_property("bOpen")
movement=pawn.get_component_by_class(u.CharacterMovementComponent)
user32=ctypes.windll.user32
editor=u.get_editor_subsystem(u.LevelEditorSubsystem)
performance=u.get_default_object(u.load_class(None,"/Script/UnrealEd.EditorPerformanceSettings"))
old_throttle=performance.get_editor_property("bThrottleCPUWhenNotForeground")
performance.set_editor_property("bThrottleCPUWhenNotForeground",False)
u.SystemLibrary.execute_console_command(world,"t.MaxFPS 60",pc)
u.SystemLibrary.execute_console_command(world,"Slate.bAllowThrottling 0",pc)
D,A,SPACE,Q,R,E=map(ord,"DA QRE")
landings=[]
samples=[]
state={"index":0, "phase":"focus","since":time.monotonic()}
# Every transition is driven by real key down/up events and verified against
# the resulting landing. No actor teleport occurs after the first cut.
jumps=[(302,440,580,0),(530,680,820,22),(770,915,1080,37),(1035,1190,1534,0),
       (1484,1644,1799,35),(1753,1900,2188,18),(2132,2294,2455,0),(2405,2560,3330,0)]

def key(code, press):
    if code == D:
        state["right"]=press
        return
    if code == A:
        state["left"]=press
        return
    if code == SPACE:
        if press: pawn.jump()
        else: pawn.stop_jumping()
        return
    user32.keybd_event(code,0,0 if press else 2,0)

def phase(name):
    state.update(phase=name,since=time.monotonic())
    if name in ("await_cut","await_recovery"):
        (output.parent/"jump_phase.txt").write_text(f"{name} {state['index']}")

def finish(error=None):
    u.unregister_slate_post_tick_callback(state["cb"])
    performance.set_editor_property("bThrottleCPUWhenNotForeground",old_throttle)
    for k in Q,R,E: key(k,False)
    if not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world():
        return
    info={"landings":landings,"samples":samples[-24:],"error":error,"reset_count":manager.get_editor_property("ResetCount"),
          "checkpoint":manager.get_editor_property("Checkpoint"),"recovered":manager.get_editor_property("bRecovered"),
          "x":pawn.get_actor_location().x-1670}
    output.write_text(json.dumps(info,indent=2))

def tick(_):
    try:
        since=time.monotonic()-state["since"]
        p=pawn.get_actor_location()
        axis=int(state.get("right",False))-int(state.get("left",False))
        if axis: pawn.add_movement_input(u.Vector(1,0,0),axis)
        x=p.x-1670
        i=state["index"]
        mode=state["phase"]
        if since>7:
            finish(f"Timeout in {mode} at jump {i} (x={x:.1f}, z={p.z:.1f})")
            return
        if mode=="focus":
            if since>1.15:
                assert manager.get_editor_property("WestCut")==0
                key(D,True)
                phase("approach")
            return
        if mode=="aim":
            current=state["aim_key"]
            if since>.12: key(current,False)
            if since>.45:
                phase("await_cut")
            return
        if mode=="await_cut":
            take="WestCut" if i==0 else "EastCut"
            if manager.get_editor_property(take)==(1 if i==6 else 0):
                phase("cut")
            return
        if mode=="cut":
            if since>.11: key(E,False)
            if since>.82:
                cut_key="WestCut" if i==0 else "EastCut"
                expect=1 if i==6 else 0
                if manager.get_editor_property(cut_key)!=expect:
                    finish(f"{cut_key} did not commit {expect}")
                    return
                key(D,True)
                phase("approach")
            return
        if mode=="finish":
            if x>=2850:
                key(D,False)
                phase("await_recovery")
            return
        if mode=="await_recovery":
            if manager.get_editor_property("bRecovered"):
                phase("recover")
            return
        if mode=="recover":
            if since>.1: key(E,False)
            if since>2.4: finish(None if manager.get_editor_property("bRecovered") else "Recovery failed")
            return
        takeoff,left,right,z=jumps[i]
        if mode=="approach":
            if x>=takeoff:
                key(D,False)
                phase("jump")
        elif mode=="jump":
            if since>.23 and movement.is_moving_on_ground():
                key(D,True)
                key(SPACE,True)
                phase("air")
        elif mode=="air":
            if not samples or samples[-1][0]!=i or since-samples[-1][1]>.055:
                samples.append([i,round(since,2),round(x,1),round(p.z,1),round(pawn.get_velocity().x,1)])
            if since>.1: key(SPACE,False)
            if x>right-76 and since>.32:
                key(D,False)
                if x>=min(right-27,(left+right)*.5+7):
                    key(A,True)
            if since>.53 and pawn.get_velocity().x<=15:
                key(A,False)
            if since>.38 and movement.is_moving_on_ground():
                if not (left-22<=x<=right+15 and p.z>z+48):
                    finish(f"Jump {i+1} landed at x={x:.1f}, z={p.z:.1f}")
                    return
                if x<left+28:
                    key(D,True)
                    return
                key(A,False)
                landings.append(round(x,1))
                state["index"]+=1
                if i in (3,5):
                    key(D,False)
                    state["aim_key"]=Q if i==3 else R
                    key(state["aim_key"],True)
                    phase("aim")
                else:
                    key(D,True)
                    phase("finish" if i==7 else "approach")
    except Exception as e:
        finish(str(e))
state["cb"]=u.register_slate_post_tick_callback(tick)
