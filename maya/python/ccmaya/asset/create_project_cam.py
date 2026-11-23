import ccftrack.asset as asset
import cccore.file_env.context as context
import cccore.folder_creator as folder_creator
import ccmaya.wizard.exporter.asset_exporter as asset_exporter
import maya.cmds as cmds


ASSET_TYPE = "camera"
ASSET_NAME = "cccamera"


def create_camera():
    """
    Create a default project camera
    """
    cmds.file(new=True, force=True)

    # create the asset on ftrack
    ftasset = asset.FtAsset()
    ftasset.create_ftrack_asset(ASSET_TYPE, ASSET_NAME)

    # create the asset on disk
    ctx = context.Context()
    folder_creator_inst = folder_creator.CreateFolders()
    folder_creator_inst.create_project_structure(ctx.project_root)

    # create the asset folders
    folder_creator_inst.create_dict  = {ASSET_TYPE: [ASSET_NAME]}
    folder_creator_inst.create_asset_folders()

    # create the camera and camera group
    cam, _ = cmds.camera()
    cmds.group(cam, n="CAM")
    cmds.rename(cam, ASSET_TYPE)

    # save the camera to the correct location
    overrides = {
        "entity": "asset",
        "task_name": "rigging",
        "app_name": "maya",
        "subfolder": "scenes",
        "asset_type": ASSET_TYPE,
        "asset_name": ASSET_NAME,
        "ext": "ma"
    }
    ctx = context.Context(overrides=overrides)
    wip_file_path = ctx.next_save_path
    cmds.file(rename=ctx.next_save_path)
    cmds.file(save=True, type="mayaAscii")

    # publish the camera to ftrack
    exporter = asset_exporter.AssetExporter()
    data = ctx.as_dict
    data["status_name"] = "WIP"
    data["comment"] = "Camera publish for project"
    data["wip_file_path"] = wip_file_path

    # run the export of the camera
    exporter.data = data
    exporter.export()
    cmds.file(new=True, force=True)
