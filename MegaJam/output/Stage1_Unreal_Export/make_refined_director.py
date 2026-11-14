from pathlib import Path
p=Path('output/Stage1_Unreal_Export')
code=(p/'director_v3.dsl').read_text(encoding='utf8')
def change(old,new):
 global code
 assert code.count(old)==1, (old,code.count(old))
 code=code.replace(old,new)
# A running lift must finish its trip before a quality switch.  Otherwise its
# state machine pauses while the player's movement remains locked indefinitely.
change('(and (Variables|Default|GetMenuOpen) (Game|Player|WasInputKeyJustPressed :self pc :Key "One"))',
       '(and (and (Variables|Default|GetMenuOpen) (not (Variables|Default|GetLiftActive))) (Game|Player|WasInputKeyJustPressed :self pc :Key "One"))')
change('(and (Variables|Default|GetMenuOpen) (Game|Player|WasInputKeyJustPressed :self pc :Key "Two"))',
       '(and (and (Variables|Default|GetMenuOpen) (not (Variables|Default|GetLiftActive))) (Game|Player|WasInputKeyJustPressed :self pc :Key "Two"))')
change('(and (not (Variables|Default|GetMenuOpen)) (Game|Player|WasInputKeyJustPressed :self pc :Key "Q"))',
       '(and (and (not (Variables|Default|GetMenuOpen)) (not (Variables|Default|GetLiftActive))) (Game|Player|WasInputKeyJustPressed :self pc :Key "Q"))')
needle='  (if (and (Variables|Default|GetMenuOpen) (Game|Player|WasInputKeyJustPressed :self pc :Key "Three"))'
change(needle,'''  (if (and (Variables|Default|GetLiftActive)
    (or (Game|Player|WasInputKeyJustPressed :self pc :Key "Q")
        (or (Game|Player|WasInputKeyJustPressed :self pc :Key "One")
            (Game|Player|WasInputKeyJustPressed :self pc :Key "Two"))))
    (Development|PrintString :InString "WAIT UNTIL THE LIFT ARRIVES TO CHANGE QUALITY" :Duration 2.5))
'''+needle)
# Both variants retain the same orientation when their geometry is swapped.
change(':Pitch (select low 0.0 (* (- wx 440.0) -0.572958))',
       ':Pitch (* (- wx 440.0) -0.572958)')
# Keep the high and low gear teeth aligned, and visibly rotate with the platform.
needle='  (if (and (and (Variables|Default|GetLiftActive) (not low)) (not (Variables|Default|GetMenuOpen)))'
change(needle,'''  (bind highGears (Actor|GetAllActorswithTag :Tag "GearHigh"))
  (for gear highGears
    (Transformation|SetActorRotation :self gear :NewRotation (Math|Rotator|MakeRotator :Pitch (* (Variables|Default|GetLiftAlpha) 2.0)) :bTeleportPhysics true))
  (bind lowGears (Actor|GetAllActorswithTag :Tag "GearLow"))
  (for gear lowGears
    (Transformation|SetActorRotation :self gear :NewRotation (Math|Rotator|MakeRotator :Pitch (* (Variables|Default|GetLiftAlpha) 2.0)) :bTeleportPhysics true))
'''+needle)
(p/'director_refined.dsl').write_text(code,encoding='utf8')
