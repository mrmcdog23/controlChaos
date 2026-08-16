""" Generate maya utilities """
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI
from typing import Optional, Any
from CCPySide import QtWidgets, shiboken
import cccore.utils.cc_logging as cc_logging
import ccmaya.maya_constants as maya_constants


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


def get_shot_assets():
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
        namespace = geo_grp.split(":")[0]
        shot_assets_list.append(namespace)

    cam_grp = cmds.ls(maya_constants.CAM_GRP)
    if cam_grp:
        shot_assets_list.extend(cam_grp)
    return shot_assets_list

