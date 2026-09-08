""" Import shot to Unreal """
import os
from CCPySide import QtWidgets, QtCore
import ccgeneral.shot.load_shot_ui as load_shot_ui
import ccmaya.utils.maya_utils as maya_utils
import cccore.file_env.context as context


class MayaLoadShotUI(load_shot_ui.LoadShotUI):
    use_cc_ss = False
    title = "Import Maya Shot"

    def __init__(self, parent):
        super().__init__(parent=parent)

    def load_settings(self):
        """
        Load the settings to create the context
        """
        self.ctx = context.Context()

    def import_files(self):
        """
        Import cameras into unreal
        """
        print("build")


def main():
    """
    Launch the maya multi playblast
    """
    maya_utils.launch_maya_win(MayaLoadShotUI)
