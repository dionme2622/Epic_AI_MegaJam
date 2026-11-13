(event EventTick
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  (bind goRight (or (Game|Player|IsInputKeyDown :self pc :Key "D") (Game|Player|IsInputKeyDown :self pc :Key "Right")))
  (bind goLeft (or (Game|Player|IsInputKeyDown :self pc :Key "A") (Game|Player|IsInputKeyDown :self pc :Key "Left")))
  (if goRight (Pawn|Input|AddMovementInput :self self :WorldDirection (Math|Vector|MakeVector :X 1.0 :Y 0.0 :Z 0.0) :ScaleValue 1.0))
  (if goLeft (Pawn|Input|AddMovementInput :self self :WorldDirection (Math|Vector|MakeVector :X -1.0 :Y 0.0 :Z 0.0) :ScaleValue 1.0))
  (bind pos (Transformation|GetActorLocation :self self))
  (bind cameras (Actor|GetAllActorswithTag :Tag "Stage1Camera"))
  (for camera cameras
    (Transformation|SetActorLocation :self camera :NewLocation (Math|Vector|MakeVector :X (+ (.x pos) 300.0) :Y 1400.0 :Z 420.0))
    (Game|Player|SetViewTargetwithBlend :self pc :NewViewTarget camera :BlendTime 0.0)))
