""" Add a dockable widget in Maya """
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI
from typing import Any
from CCPySide import QtWidgets, QtCore, shiboken


class CreateDockableWidget(object):
    """
    Create a dockable widget from the QWidget class
    """
    def __init__(self, widget_cls, panel_name, panel_label, panel_width):
        # type: (Any, str, str, int) -> None
        """
        Args:
            widget_cls: The QWidget class to create
            panel_name: Name of the panel object
            panel_label: The display label to the panel
            panel_width: Width of the panel on creation
        """
        self.widget_cls = widget_cls
        self.panel_name = panel_name
        self.panel_label = panel_label
        self.panel_width = panel_width
        self.create_doc_panel_maya()
        self.show_panel()

    @property
    def panel_exists(self):
        # type: () -> bool
        """ Does the panel already exist """
        return cmds.workspaceControl(self.panel_name, exists=True)

    def create_doc_panel_maya(self):
        """
        Create a dockable widget in Maya
        """
        if self.panel_exists:
            return

        dock_panel = cmds.workspaceControl(
            self.panel_name,
            tabToControl=["AttributeEditor", -1],
            initialWidth=self.panel_width,
            minimumWidth=True,
            widthProperty="preferred",
            label=self.panel_label
        )
        dock_ptr = OpenMayaUI.MQtUtil.findControl(dock_panel)
        dock_widget = shiboken.wrapInstance(int(dock_ptr), QtWidgets.QWidget)
        dock_widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        child = self.widget_cls(dock_widget)
        dock_widget.layout().addWidget(child)

    def show_panel(self):
        """
        Show the panel if already created
        """
        cmds.evalDeferred(
            lambda *args: cmds.workspaceControl(
                self.panel_name,
                edit=True,
                restore=True
            )
        )


