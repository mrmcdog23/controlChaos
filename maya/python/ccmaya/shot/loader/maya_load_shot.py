""" Import shot to maya """
import os
import maya.cmds as cmds
import mayaUsd.ufe as mufe
from CCPySide import QtWidgets, QtCore
import ccgeneral.shot.load_shot_ui as load_shot_ui
import ccmaya.utils.maya_utils as maya_utils
import cccore.file_env.context as context


class MayaLoadShotUI(load_shot_ui.LoadShotUI):
    use_cc_ss = False
    title = "Import Maya Shot"

    def __init__(self, parent):
        super().__init__(parent=parent)
        # Make sure the plugin is loaded
        if not cmds.pluginInfo("mayaUsdPlugin", q=True, loaded=True):
            cmds.loadPlugin("mayaUsdPlugin")

    def load_settings(self):
        """
        Load the settings to create the context
        """
        self.ctx = context.Context()

    def import_usd_file_as_stage(self, usd_path, namespace):
        # type: (str, str) -> None
        """
        Import usd file as stage

        Args:
            usd_path: Path to the usd file to import
            namespace: The namespace to use on the object
        """
        proxy = cmds.createNode("mayaUsdProxyShape", name=namespace)
        cmds.setAttr(proxy + ".filePath", usd_path, type="string")
        cmds.connectAttr("time1.outTime", proxy + ".time")
        self.logger.info(f"proxy: {proxy}")
        proxy_root = cmds.listRelatives(proxy, parent=True)
        cmds.rename(proxy_root, namespace + "_root")

    def import_files(self):
        """
        Import cameras and assets into maya
        """
        if self.all_usd and self.chk_all_usd.isChecked():
            self.import_usd_file_as_stage(self.all_usd, "all")
        else:
            for fbx_path in self.import_files_list:
                file_data = self.data["exported_files_to_data"][fbx_path]
                namespace = file_data["namespace"]

                if fbx_path.endswith(".usd"):
                    self.import_usd_file_as_stage(fbx_path, namespace)
                else:
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
