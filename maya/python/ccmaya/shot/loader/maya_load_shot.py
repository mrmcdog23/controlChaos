""" Import shot to maya """
import os
import maya.cmds as cmds
import maya.mel as mel
from CCPySide import QtWidgets, QtCore
import ccgeneral.shot.load_shot_ui as load_shot_ui
import ccmaya.utils.maya_utils as maya_utils
import cccore.file_env.context as context
import ccftrack.asset_version as ft_version
import ccmaya.shot.loader.fbx_import_settings as fbx_import_settings


class MayaLoadShotUI(load_shot_ui.LoadShotUI):
    use_cc_ss = False
    title = "Import Maya Shot"

    def __init__(self, parent):
        super().__init__(parent=parent)
        # Make sure the plugin is loaded
        if not cmds.pluginInfo("mayaUsdPlugin", q=True, loaded=True):
            cmds.loadPlugin("mayaUsdPlugin")
        self.set_frame_range()

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

    def load_camera(self, fbx_path, namespace):
        # type: (str, str) -> None
        """
        Load the camera by referencing the latest
        one in then applying the fbx data

        Args:
            fbx_path: Path of the camera fbx file to load
            namespace: Namespace of the camera to load
        """
        # set the latest camera to set
        self.ftasset.asset_build_type_name = "camera"
        self.ftasset.asset_build_name = "cccamera"
        self.ftasset.task_name = "rigging"

        # set the latest version to load
        ftver_inst = ft_version.FtAssetVersion(session=self.ftasset.session)
        ftver_inst.asset_version_id = self.ftasset.latest_asset_version["id"]

        # reference the latest camera
        cmds.file(
            ftver_inst.master_component_path,
            namespace=namespace,
            reference=True
        )

        # import the fbx camera animation
        camera_nodes = cmds.file(fbx_path, i=True, rnn=True)
        found_camera = False
        for camera_node in camera_nodes:

            # get the camera and rename the cam node
            # to camera to match the fbx name
            if cmds.objectType(camera_node) == "camera":
                cam = cmds.listRelatives(camera_node, p=True)[0]
                cmds.rename(cam, "camera")
                found_camera = True

        # import the fbx data onto the camera
        if found_camera:
            fbx_import_settings.run_temp_fbx_data(namespace, "camera")

    def reference_asset(self, fbx_path, file_data):
        # type: (str, dict) -> None
        """
        Reference the maya asset and load the fbx data on to it

        Args:
            fbx_path: The animation file to import on to the asset
            file_data: Full data of the asset being imported
        """
        namespace = file_data["namespace"]
        if file_data["is_camera"]:
            self.load_camera(fbx_path, namespace)
            return

        # reference the maya asset into the scene
        self.ftver.asset_version_id = file_data["ftrack_id"]
        cmds.file(
            self.ftver.master_component_path,
            namespace=namespace,
            reference=True
        )

        # if it is a static asset then not animation applied
        if not file_data.get("is_skeleton_mesh"):
            return

        # apply the fbx animation
        fbx_import_settings.create_joint_data(fbx_path, namespace)

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
                    self.reference_asset(fbx_path, file_data)

    def set_frame_range(self):
        """
        Set the start and end frame animation and time slider
        """
        start_frame = self.data["start_frame"]
        end_frame = self.data["end_frame"]
        cmds.playbackOptions(min=start_frame, ast=start_frame, max=end_frame, aet=end_frame)


def main():
    """
    Launch the maya multi playblast
    """
    maya_utils.launch_maya_win(MayaLoadShotUI)
