""" Build the current project folder structure """
import unreal as ue
import ccftrack.shot as shot
import ccftrack.asset as asset
import ccunreal.unreal_constants as unreal_constants


def create_folder(path):
    # type: (str) -> None
    """
    Create the unreal folder from a path

    Args:
        path: The game path to create the folder
    """
    if not ue.EditorAssetLibrary.does_directory_exist(path):
        ue.EditorAssetLibrary.make_directory(path)
        ue.log(f"Created: {path}")
    else:
        ue.log(f"Already exists: {path}")


def create_project_folders():
    """
    Create the project folders from FTrack
    """
    ftshot = shot.FtShot()
    ftasset = asset.FtAsset(session=ftshot.session)

    # Create the root folders
    folders = [
        unreal_constants.CC_ASSET_DIR,
        unreal_constants.CC_LEVEL_DIR,
        unreal_constants.CC_SEQUENCE_DIR
    ]
    for path in folders:
        create_folder(path)

    # create the sequence folders
    for sequence_name in ftshot.sequence_names:
        ue_sequence_folder = ue.Paths.combine([unreal_constants.CC_SEQUENCE_DIR, sequence_name])
        create_folder(ue_sequence_folder)

        # create level folder to have a sequence
        ue_level_folder = ue.Paths.combine([unreal_constants.CC_LEVEL_DIR, sequence_name])
        create_folder(ue_level_folder)

        # create the shot folders under the sequence
        ftshot.sequence_name = sequence_name
        for shot_name in ftshot.shot_names:
            ue_shot_folder = ue.Paths.combine([ue_sequence_folder, shot_name])
            create_folder(ue_shot_folder)

            # create anim folder
            ue_anim_folder = ue.Paths.combine([ue_shot_folder, "Anim"])
            create_folder(ue_anim_folder)

        # create the asset build types folders
        for asset_type in ftasset.asset_build_types_names:
            ue_asset_type_folder = ue.Paths.combine([unreal_constants.CC_ASSET_DIR, asset_type])
            create_folder(ue_asset_type_folder)

            # create the asset build names for the types
            ftasset.asset_build_type_name = asset_type
            for asset_name in ftasset.asset_build_names:
                ue_asset_name_folder = ue.Paths.combine([ue_asset_type_folder, asset_name])
                create_folder(ue_asset_name_folder)

