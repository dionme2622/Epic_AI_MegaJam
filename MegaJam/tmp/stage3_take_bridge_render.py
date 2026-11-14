import bpy, pathlib
from mathutils import Vector
root = pathlib.Path('SourceAssets/Stage3TakeBridge/Exports')
bpy.ops.wm.open_mainfile(filepath=str(root/'Stage3TakeBridge.blend'))
placements = {
    'SM_S3Take_PressurePlate':(-3.95,0,0.02),
    'SM_S3Take_CueLamp':(-3.95,-.55,0),
    'SM_S3Bridge_Platform':(-1.5,0,.72),
    'SM_S3Bridge_SpliceDesk':(1,0,0),
    'SM_S3Bridge_FilmClip':(.57,.455,.72),
    'SM_S3Bridge_Rail':(-1.5,0,0),
    'SM_S3Bridge_ProjectionScreen':(0,-1.3,3.16),
}
for name, loc in placements.items():
    obj = bpy.data.objects[name]
    obj.hide_set(False)
    obj.location=loc
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.08))
floor = bpy.context.object
floor.scale=(12,6,.16)
material=bpy.data.materials.new('Floor Preview')
material.diffuse_color=(.1,.075,.13,1)
floor.data.materials.append(material)
scene=bpy.context.scene
bpy.ops.object.camera_add(location=(2.6,11,8))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,2))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=12
scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD'
scene.render.resolution_x=1200
scene.render.resolution_y=650
scene.render.resolution_percentage=100
scene.render.filepath='//../../tmp/stage3_take_bridge_props_preview.png'
bpy.ops.render.render(write_still=True)
