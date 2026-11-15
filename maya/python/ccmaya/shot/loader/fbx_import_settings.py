import os
import maya.cmds as cmds
import maya.mel as mel
import cccore.utils.file_utils as file_utils
import ccmaya.maya_constants as maya_constants
import cccore.utils.cc_logging as cc_logging


logger = cc_logging.cc_logger()
SETTINGS = {
    'Export|IncludeGrp|Animation': 1,
    'Export|IncludeGrp|Animation|BakeComplexAnimation': 0,
    'Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart': 1001,
    'Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd': 1020,
    'Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep': 1,
    'Export|IncludeGrp|Animation|Deformation': 1,
    'Export|IncludeGrp|Animation|Deformation|Skins': 1,
    'Export|IncludeGrp|Animation|Deformation|Shape': 1,
    'Export|IncludeGrp|Geometry|SmoothingGroups': 0,
    'Export|IncludeGrp|Geometry|Triangulate': 0,
    'Export|IncludeGrp|InputConnectionsGrp|IncludeChildren': 1,
    'Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion': 1,
    'Export|AdvOptGrp|UnitsGrp|UnitsSelector': 'Centimeters',
    'Export|AdvOptGrp|AxisConvGrp|UpAxis': 'Y',
    'Export|AdvOptGrp|Fbx|AsciiFbx': 'Binary',
    'Import|IncludeGrp|Animation': 1,
    'Import|AdvOptGrp|UnitsGrp|DynamicScaleConversion': 1,
    'Import|AdvOptGrp|AxisConvGrp|UpAxis': 'Y',
}

def apply_fbx_settings():
    """
    Apply the correct fbx settings to import correctly
    """
    if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
        cmds.loadPlugin("fbxmaya")
    for path, val in SETTINGS.items():

        # work out the value to set
        if isinstance(val, str):
            val = f'"{val}"'
        elif isinstance(val, bool):
            val = "true" if val else "false"
        try:
            mel.eval(f'FBXProperty "{path}" -v {val};')
        except RuntimeError as e:
            logger.error(f"Skipped {path}: {e}")


def create_joint_data(fbx_path, namespace):
    # type: (str, str) -> None
    """
    Create the joint data by exporting the joints
    as its own fbx file to match the hierarchy

    Args:
        fbx_path: Path of the fbx file to load
        namespace: Name of the namespace to export under
    """
    apply_fbx_settings()

    # find the node group in the imported fbx
    nodes = cmds.file(fbx_path, i=True, rnn=True)
    jnts_group = None
    for node in nodes:
        if node.endswith(maya_constants.JNT_GRP):
            jnts_group = node
            break

    # if it's not found skip the rest
    if not jnts_group:
        logger.error(f"Could not find JNT group in {fbx_path}")
        return
    root_jnt = cmds.listRelatives(node)[0]

    # get the top group node of the imported fbx
    top_node = root_jnt
    while top_node:
        group_node = top_node
        top_node = cmds.listRelatives(top_node, p=True)

    # unparent and delete the rest of the new group
    cmds.parent(root_jnt, w=True)
    cmds.delete(group_node)

    # apply the fbx data to the joints
    run_temp_fbx_data(namespace, root_jnt)


def run_temp_fbx_data(namespace, select_node):
    # type: (str, str) -> None
    """
    Select an asset and export it as an fbx file

    Args:
        namespace: Name of the namespace to export under
        select_node: The node to select to export
    """
    # export the joints as a temp fbx file
    cmds.select(select_node)
    temp_fbx_path = file_utils.temp_file_path(namespace, "fbx")
    cmds.file(temp_fbx_path, force=True, typ="FBX export", pr=True, es=True)
    cmds.delete(select_node)

    # set the namespace to apply to the fbx import
    use_namespace = f":{namespace}"
    if not cmds.namespace(ex=use_namespace):
        cmds.namespace(add=use_namespace)
    cmds.namespace(set=use_namespace)

    # import FBX file and it should apply to the asset
    mel.eval(f'file -import -type "FBX" -ignoreVersion -importTimeRange '
             f'"combine" -options "v=0;" "{temp_fbx_path}"')

    # clear selection and namespace and remove the temp file
    cmds.select(cl=True)
    os.remove(temp_fbx_path)
    cmds.namespace(setNamespace=":")