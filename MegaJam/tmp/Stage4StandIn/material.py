import unreal as u
lib=u.EditorAssetLibrary
path="/Game/Stage4Integrated/Theatre/M20_Silhouette"
m=lib.load_asset(path)
m.set_editor_property("used_with_skeletal_mesh",True)
u.MaterialEditingLibrary.recompile_material(m)
assert lib.save_loaded_asset(m,only_if_is_dirty=False)
u.log("SKELETAL SHADOW MATERIAL SAVED")
