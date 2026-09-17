""" Import shot to maya """
import os
from CCPySide import QtWidgets, QtCore
import ccgeneral.shot.load_shot_ui as load_shot_ui
import cchoudini.utils.hou_utils as hou_utils
import cccore.file_env.context as context
import cchoudini.asset.alembic_loader as alembic_loader
import cchoudini.asset.fbx_loader as fbx_loader


class HouLoadShotUI(load_shot_ui.LoadShotUI):
    use_cc_ss = False
    title = "Import Houdini Shot"
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
        for cache_path in self.import_files_list:
            file_data = self.data["exported_files_to_data"][cache_path]
            namespace = file_data["namespace"]
            if cache_path.endswith(".abc"):
                alembic_loader.AlembicLoader(cache_path, namespace)
        '''
            cmds.file(fbx_path, namespace=namespace, reference=True)

        cmds.playbackOptions(
            min=self.start_frame,
            ast=self.start_frame,
            max=self.end_frame,
            aet=self.end_frame
        )
        '''


def main():
    """ Launch the houdini shot loader """
    hou_utils.launch_hou_win(HouLoadShotUI)
