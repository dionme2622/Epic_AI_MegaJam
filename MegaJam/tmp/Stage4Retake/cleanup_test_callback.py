import gc
import types
import unreal as u
seen=set()
for item in gc.get_objects():
    if not isinstance(item,types.FunctionType) or item.__name__!="tick" or not item.__code__.co_filename.replace(chr(92),"/").endswith("/Stage4Retake/jump_live.py"):
        continue
    context=item.__globals__
    state=context.get("state",{})
    handle=state.get("cb")
    if handle is not None and id(handle) not in seen:
        seen.add(id(handle))
        u.unregister_slate_post_tick_callback(handle)
        u.log("Retake verifier callback removed")
performance=u.get_default_object(u.load_class(None,"/Script/UnrealEd.EditorPerformanceSettings"))
performance.set_editor_property("bThrottleCPUWhenNotForeground",True)
