""" Capture the image thumbnail """
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
from CCPySide import QtWidgets
from ccgeneral.wizard.pages.base_page import BasePublishPage


class TurntablePage(BasePublishPage):
    title = "Turntable Asset Page"
    subtitle = "Make a turntable of the asset on publish"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.chk_turntable.toggled.connect(self.enable_groups)

    def enable_groups(self, enable):
        # type: (bool) -> None
        """
        Enable or disable the group widgets

        Args:
            enable: enable or disable the group widgets
        """
        self.grp_renderer.setEnabled(enable)
        self.grp_object_or_camera.setEnabled(enable)

    def validatePage(self):
        """
        Store the thumbnail path in the wizard data
        """
        self.data["turntable"] = self.chk_turntable.isChecked()
        if self.rbn_playblast.isChecked():
            self.data["renderer"] = "mayaHardware2"
        else:
            self.data["renderer"] = "arnold"
        self.data["rotate_object"] = self.rbn_object.isChecked()
        return True
