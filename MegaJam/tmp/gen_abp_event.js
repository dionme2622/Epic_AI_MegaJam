let fs=require('fs');let code=`(event EventBlueprintUpdateAnimation (DeltaTimeX)
  (bind owner (Animation|TryGetPawnOwner))
  (Utilities|IsValid :InputObject owner
    (:"Is Valid"
      (Variables|Default|SetIsMoving (> (Math|Vector|VectorLengthXY (Transformation|GetVelocity :self owner)) 3.0)))
    (:"Is Not Valid"
      (Variables|Default|SetIsMoving false))))`;
fs.writeFileSync('tmp/write_event.json',JSON.stringify([{toolset_name:'editor_toolset.toolsets.blueprint.BlueprintTools',tool_name:'write_graph_dsl',arguments:{graph:{refPath:'/Game/Level/Character/ABP_Dragon.ABP_Dragon:EventGraph'},code}}]));
