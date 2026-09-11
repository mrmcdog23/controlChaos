""" Generate maya utilities """
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI
from typing import Optional, Any
from CCPySide import QtWidgets, shiboken
import cccore.utils.cc_logging as cc_logging
import ccmaya.maya_constants as maya_constants
import cccore.utils.ui_utils as ui_utils
import cccore.file_env.ctx_constants as ctx_constants


logger = cc_logging.cc_logger()


def get_maya_main_window():
    # type: () -> Optional[QtWidgets.QMainWindow]
    """
    Get the main Maya window as a QtWidgets.QMainWindow instance

    Returns:
         instance of the top level Maya windows
    """
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(int(ptr), QtWidgets.QWidget)


def launch_maya_win(win_class):
    # type: (Any) -> None
    """
    Launch the maya window

    Args:
        win_class: Class of ui to open
    """
    # delete all current versions of the tool
    for inst in QtWidgets.QApplication.topLevelWidgets():
        if win_class.title == inst.windowTitle():
            inst.close()
            inst.deleteLater()

    # find and launch the ui under the maya window
    loading = win_class(parent=None)

    # move the ui to a central position
    loading.move(900, 200)

    # set the window
    loading.show()


def launch_wizard(wizard_cls):
    """
    Launch the asset publish wizard
    """
    wizard_cls.control_chaos_ss = "../../css/maya_stylesheet.css"
    maya_window = get_maya_main_window()
    wizard = wizard_cls(parent=maya_window)
    wizard.show()
    wizard.exec_()


def load_plugins(plugin_list):
    # type: (list[str]) -> None
    """
    Load a list of plugins into Maya

    Args:
        plugin_list: List of plugins to load
    """
    for plugin in plugin_list:
        if not cmds.pluginInfo(plugin, query=True, loaded=True):
            cmds.loadPlugin(plugin)


def add_export_attribute():
    """
    Add export attributes to the node
    """
    selected_nodes = cmds.ls(sl=True)
    if not selected_nodes:
        cmds.warning("Nothing selected!")
        return

    # if the attribute exists then skip
    selected_node = selected_nodes[0]
    if not cmds.objExists( f"{selected_node}.export"):
        cmds.addAttr(selected_node, longName="export", at='bool')
    else:
        cmds.warning("Export attribute already exists!")


def get_shot_namespaces():
    # type: (Any) -> dict
    """
    Get all shot assets that have a geometry group

    Args:
        session: Current ftrack session

    Returns:
        shot_assets_dict: Dict of published assets
    """
    shot_assets_list = list()
    for geo_grp in cmds.ls("*:GEO"):
        is_referenced = cmds.referenceQuery(geo_grp, inr=True)
        if not is_referenced:
            continue
        namespace = geo_grp.split(":")[0]
        shot_assets_list.append(namespace)
    shot_assets_list.extend(render_cameras())
    return shot_assets_list


def render_cameras():
    # type: () -> list[str]
    """
    Get a list of all cameras bar the defaults

    Returns:
        cameras: List of cameras
    """
    cameras = list()
    for cam in cmds.ls(type="camera"):
        cam_transform = cmds.listRelatives(cam, p=True)[0]
        if cam_transform not in maya_constants.DEFAULT_CAMERAS:
            cameras.append(cam_transform)
    return cameras


def cc_save():
    # type: () -> str
    """
    Save the file path next file

    Returns:
        save_path: Path of the file to save
    """
    overrides = {"ext": "ma"}
    save_path = ui_utils.cc_save_path(
        get_maya_main_window(), overrides=overrides)
    if not save_path:
        return str()
    cmds.file(rename=save_path)
    cmds.file(save=True, type='mayaAscii')
    return save_path


def cc_save_panel_refresh():
    """ Save and refresh maya panel """
    cc_save()
    maya_window = get_maya_main_window()
    ctx_panel = maya_window.findChild(QtWidgets.QWidget, ctx_constants.CONTEXT_PANEL)
    ctx_panel.populate_wip_versions()


def get_model_panels():
    # type: () -> list[cmds.modelPanel]
    """ All model panels """
    all_model_panels = list()
    model_panels = cmds.getPanel(type="modelPanel")
    for model_panel in cmds.getPanel(visiblePanels=True):
        if model_panel in model_panels:
            all_model_panels.append(model_panel)
    return all_model_panels


def get_top_level_nodes():
    # type: () -> list[str]
    """
    Get a list of top level nodes in the scene
    """
    return [x for x in cmds.ls(assemblies=True)
            if x not in maya_constants.DEFAULT_CAMERAS]


def get_asset_top_node():
    # type: () -> Optional[str]
    """
    Get the top node of the asset

    Returns:
        grp_name: Name of the top node
    """
    top_nodes = get_top_level_nodes()
    for grp_name in maya_constants.GRP_NAMES:
        if grp_name in top_nodes:
            return grp_name


def add_ftrack_tag_to_asset(ftrack_id):
    # type: (str) -> None
    """
    Add the ftrack id as an attribute and set the published id

    Args:
        ftrack_id: Published ftrack id
    """
    top_node = get_top_level_nodes()[0]
    add_string_attribute(top_node, maya_constants.FTRACK_ID, ftrack_id)


def add_string_attribute(top_node, attribute_name, attribute_value):
    # type: (str, str, str) -> None
    """
    Add a string attribute to a maya object

    Args:
        top_node: The node to add the attribute to
        attribute_name: Attribute name to add
        attribute_value: The string text to set
    """
    attribute_long_name = f"{top_node}.{attribute_name}"
    if not cmds.objExists(attribute_long_name):
        cmds.addAttr(top_node, longName=attribute_name, dt='string')

    # unlock, set and lock the attribute
    cmds.setAttr(attribute_long_name, l=False)
    cmds.setAttr(attribute_long_name, attribute_value, type="string")
    cmds.setAttr(attribute_long_name, l=True)


def get_root_joint(namespace=None):
    # type: (Optional[str]) -> Optional[str]
    """
    Find the root joint of a rig

    Args:
        namespace: Root joint namespace

    Returns:
        jnt: Root joint of the rig
    """
    if namespace:
        joints = cmds.ls(f"{namespace}:*", type="joint")
    else:
        joints = cmds.ls(type="joint")

    # if there are no joints then warn the user
    if not joints:
        logger.critical("No joints found")
        return None

    # set the joint and start count as a fail-safe
    jnt = joints[0]
    count = 0

    # keep getting the joint parent until the parent is not a joint
    while count < 100:
        count += 1

        # if there is no parent then the joint is the top level
        parent_obj = cmds.listRelatives(jnt, p=True)
        if not parent_obj:
            break

        # if the parent is a joint set that as the new joint
        if cmds.objectType(parent_obj[0]) == "joint":
            jnt = parent_obj[0]
        else:
            # if the parent isn't a joint then its the root
            break
    return jnt


def get_scene_frame_range():
    # type: () -> (int, int)
    """
    Get the start and end frame of the current scene

    Returns:
        start: First frame
        end: Last frame
    """
    start = int(cmds.playbackOptions(q=True, min=True))
    end = int(cmds.playbackOptions(q=True, max=True))
    return start, end