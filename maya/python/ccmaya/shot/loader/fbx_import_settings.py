import os
import maya.cmds as cmds
import maya.mel as mel
import cccore.utils.file_utils as file_utils
import ccmaya.maya_constants as maya_constants


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
    if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
        cmds.loadPlugin("fbxmaya")
    for path, val in SETTINGS.items():
        if isinstance(val, str):
            val = '"{}"'.format(val)
        elif isinstance(val, bool):
            val = "true" if val else "false"
        try:
            mel.eval('FBXProperty "{}" -v {};'.format(path, val))
            print ('FBXProperty "{}" -v {};'.format(path, val))
        except RuntimeError as e:
            print("Skipped {}: {}".format(path, e))


def create_joint_data(fbx_path, namespace):
    apply_fbx_settings()


    nodes = cmds.file(fbx_path, i=True, rnn=True)
    jnts_group = None
    for node in nodes:
        if node.endswith(maya_constants.JNT_GRP):
            jnts_group = node
            break

    if not jnts_group:
        return
    root_jnt = cmds.listRelatives(node)[0]

    # get the top group node
    top_node = root_jnt
    while top_node:
        group_node = top_node
        top_node = cmds.listRelatives(top_node, p=True)

    # unparent and delete the rest of the new group
    cmds.parent(root_jnt, w=True)
    cmds.delete(group_node)
    run_temp_fbx_data(namespace, root_jnt)


def run_temp_fbx_data(namespace, select_node):

    # export the joints as a temp fbx file
    cmds.select(select_node)
    temp_fbx_path = file_utils.temp_file_path(namespace, "fbx")
    cmds.file(temp_fbx_path, force=True, typ="FBX export", pr=True, es=True)
    cmds.delete(select_node)

    use_namespace = f":{namespace}"
    if not cmds.namespace(ex=use_namespace):
        cmds.namespace(add=use_namespace)
    cmds.namespace(set=use_namespace)

    # import FBX
    mel.eval(f'file -import -type "FBX" -ignoreVersion -importTimeRange '
             f'"combine" -options "v=0;" "{temp_fbx_path}"');

    cmds.select(cl=True)
    os.remove(temp_fbx_path)
    cmds.namespace(setNamespace=":")