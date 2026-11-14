import unreal as u

for package in ('/Game/DirectorCut/Transitions/BP_StageRightExit', '/Game/Stage3Integrated/BP_Stage2ToStage3'):
    blueprint = u.EditorAssetLibrary.load_asset(package)
    assert blueprint, package
    assert u.EditorAssetLibrary.save_loaded_asset(blueprint, only_if_is_dirty=False), package
    u.log('Saved story transition: ' + package)
