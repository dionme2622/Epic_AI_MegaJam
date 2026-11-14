import unreal as u

library = u.EditorAssetLibrary
source = '/Game/Stage1Generated/BP_Stage1Director'
target = '/Game/Stage2Workshop/BP_Stage2WorkshopDirector'
if not library.does_asset_exist(target):
    assert library.duplicate_asset(source, target)
u.log('Stage2 director copy ready')
