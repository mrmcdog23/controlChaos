""" Import shot to maya """
import os
import maya.cmds as cmds
from CCPySide import QtWidgets, QtCore
import ccgeneral.shot.load_shot_ui as load_shot_ui
import ccmaya.utils.maya_utils as maya_utils
import cccore.file_env.context as context


class MayaLoadShotUI(load_shot_ui.LoadShotUI):
    use_cc_ss = False
    title = "Import Maya Shot"
    ignore_types = ["fbx", "abc"]

    def __init__(self, parent):
        super().__init__(parent=parent)

    def load_settings(self):
        """
        Load the settings to create the context
        """
        self.ctx = context.Context()

    def import_files(self):
        """
        Import cameras and assets into maya
        """
        for fbx_path in self.import_files_list:
            file_data = self.data["exported_files_to_data"][fbx_path]
            namespace = file_data["namespace"]
            cmds.file(fbx_path, namespace=namespace, reference=True)

        cmds.playbackOptions(
            min=self.start_frame,
            ast=self.start_frame,
            max=self.end_frame,
            aet=self.end_frame
        )


def main():
    """
    Launch the maya multi playblast
    """
    maya_utils.launch_maya_win(MayaLoadShotUI)
