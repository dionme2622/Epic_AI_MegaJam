import ctypes
import json
import math
import time
from pathlib import Path
import unreal as u

O=Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage4Theatre")
es=u.get_editor_subsystem(u.UnrealEditorSubsystem)
world=es.get_game_world()
assert world, "PIE must be running"
pc=u.GameplayStatics.get_player_controller(world,0)
pawn=u.GameplayStatics.get_player_character(world,0)
actors=u.GameplayStatics.get_all_actors_of_class(world,u.Actor)
theatre=next(x for x in actors if x.get_actor_label()=="Shadow Rehearsal")
motion=pawn.get_component_by_class(u.CharacterMovementComponent)
door=theatre.get_editor_property("EntranceDoor")
assert door.get_editor_property("bOpen"), "RGB lock is closed"
user32=ctypes.windll.user32
trace=[]
samples=[]
state={"phase":"start","i":0,"locked":False}
D=0x44
A=0x41
SPACE=0x20
origin=1670
jumps=[
    (302,440,580,0),(530,680,820,22),(770,915,1080,37),
    (1035,1190,1534,0),(1484,1644,1799,35),
    (1753,1900,2188,18),(2132,2294,2455,0),(2405,2560,3330,0),
]

def change(code,down):
    user32.keybd_event(code,0,0 if down else 2,0)

def stage(name):
    state["phase"]=name
    state["since"]=time.monotonic()

def grounded():
    return motion.is_moving_on_ground()

def done(error=None):
    for key in (D,A,SPACE):
        change(key,False)
    u.unregister_slate_post_tick_callback(state["handle"])
    out={
        "error":error,"landings":trace,"checkpoint":theatre.get_editor_property("Checkpoint"),
        "resets":theatre.get_editor_property("ResetCount"),"position":pawn.get_actor_location().to_tuple(),
        "samples":samples[-24:],
    }
    (O/"jump_report.json").write_text(json.dumps(out,indent=2))
    u.log("SHADOW WALK TEST "+str(out))

def tick(_):
    try:
        p=pawn.get_actor_location()
        x=p.x-origin
        now=time.monotonic()
        since=now-state["since"]
        i=state["i"]
        if since>18:
            done("Timed out at jump "+str(i)+" / "+state["phase"])
            return
        if state["phase"]=="start":
            if since < 1.2:
                return
            if state["locked"]:
                return
            state["locked"]=True
            # Focus stays in the game viewport from the editor's click.
            change(D,True)
            stage("approach")
            return
        if state["phase"]=="finish":
            if grounded() and x>2785:
                done()
            return
        takeoff,left,right,declared_z=jumps[i]
        if state["phase"]=="approach":
            if x<takeoff:
                return
            change(D,False)
            stage("wait")
        elif state["phase"]=="wait":
            if since<.22 or not grounded():
                return
            west=theatre.get_editor_property("WestRig").get_world_location().x-origin
            east=theatre.get_editor_property("EastRig").get_world_location().x-origin
            if not state.get("allow_phase",False):
                if i in [0,1,2,4,5]:
                    last=state.get("last_rigs",(west,east))
                    state["last_rigs"]=(west,east)
                    if i==0 and not (west>890 and west>last[0]+1): return
                    if i==1 and not (west>907 and west>last[0]+1): return
                    if i==2 and not (west<630 and west<last[0]-1): return
                    if i==4 and not (east>1885 and east>last[1]+1): return
                    if i==5 and not (east<1645 and east<last[1]-1): return
            change(D,True)
            change(SPACE,True)
            stage("air")
        elif state["phase"]=="air":
            if len(samples)==0 or since>=samples[-1][1]+.045 or len(trace)!=samples[-1][0]:
                samples.append([len(trace),round(since,2),round(x,1),round(p.z,1),
                    round(theatre.get_editor_property("WestRig").get_world_location().x-origin,1),
                    round(theatre.get_editor_property("EastRig").get_world_location().x-origin,1)])
            if since>.105 and not state.get("released",False):
                change(SPACE,False)
                state["released"]=True
            if x>right-76 and since>.32:
                change(D,False)
                if x >= (left+right)*.5 + 7:
                    change(A,True)
            if since>.53 and pawn.get_velocity().x <= 15:
                change(A,False)
            if since>.38 and grounded():
                if not (left-22<=x<=right+15 and p.z>declared_z+48):
                    done("Landed outside expected platform "+str(i)+" x="+str(x))
                    return
                if x < left + 28:
                    change(D,True)
                    return
                trace.append([i+1,round(x,1),round(p.z,1)])
                change(SPACE,False)
                change(A,False)
                state["released"]=False
                state["i"]+=1
                change(D,True)
                stage("finish" if state["i"]==len(jumps) else "approach")
    except Exception as e:
        done(str(e))

if not (O/"jump_report.json").exists():
    stage("start")
    state["handle"]=u.register_slate_post_tick_callback(tick)
