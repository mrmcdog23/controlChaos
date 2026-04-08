""" Generate maya utilities """
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI
from typing import Optional, Any
from CCPySide import QtWidgets, shiboken
import cccore.utils.cc_logging as cc_logging


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
