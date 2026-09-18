""" Create a tracking houdini scene """
import os
import hou
import sys
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
import ccftrack.asset_version as asset_version


def main(metadata_path):
    # type: (str) -> None
    """
    Create the houdini file from the 3de export

    Args:
        metadata_path: The 3de exported metadata
    """
    logger = cc_logging.cc_logger()
    logger.info("Loading Houdini file...")

    # load data and layout children
    data = file_utils.read_json(metadata_path)
    exec(open(data["equalizer_hou_py"]).read())
    hou.node("/obj").layoutChildren()

    # find the camera and set the path of the image sequence
    for node in hou.node("/obj").allSubChildren():
        if node.type().name() == "cam":
            node.parm("vm_background").set(data["hou_undistorted_sequence"])
            logger.info("Setting undistorted plates")
            break

    # get the houdini path create the directory and save the file
    hou_file_path = data["hou_file_path"]
    hou_file_dir = os.path.dirname(hou_file_path)
    file_utils.create_directories(hou_file_dir)
    hou.hipFile.save(file_name=hou_file_path)
    logger.info(f"Saved Houdini path: {hou_file_path}")

    # add the file as a save component
    ftver = asset_version.FtAssetVersion()
    ftver.asset_version_id = data["asset_version_id"]
    ftver.add_component("HoudiniFile", hou_file_path)


if __name__ == '__main__':
    equalizer_hou_py_path = sys.argv[1]
    main(equalizer_hou_py_path)
