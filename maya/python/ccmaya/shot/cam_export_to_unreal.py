""" Export FBX cameras to Unreal """
import pymel.core as pm
import maya.cmds as cmds
from CCPySide import QtWidgets, QtCore
import ccmaya.utils.maya_utils as maya_utils
import cccore.base_ui as base_ui
import cccore.utils.cc_logging as cc_logging
import cccore.utils.file_utils as file_utils
from ccgeneral.widgets.line_browser import LineBrowser


class CamerasToUnreal(base_ui.WindowBase):
    title = "Cameras To Unreal"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.logger = cc_logging.cc_logger()


        # run setup functions
        self.load_fbx_plugin()
        self.create_layout()
        self.populate_data()
        self.connect_signals()

    def load_fbx_plugin(self):
        if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
            cmds.loadPlugin("fbxmaya")

    def create_layout(self):
        self.browse_output_wdg = LineBrowser(
            self, "dir", "Select Out Directory", "", "Output Directory")
        self.lyt_browse.addWidget(self.browse_output_wdg)

    def connect_signals(self):
        """
        Connect the signal to the widgets
        """
        self.btn_export_cameras.clicked.connect(self.export_cameras)
        self.lw_cameras.itemSelectionChanged.connect(self.switch_view)
        self.chk_all.toggled.connect(self.check_all)

    def check_all(self, checked):
        # type: (bool) -> None
        """
        Check all the camera items

        Args:
            checked: State to check the items
        """
        state = QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked
        for index in range(self.lw_cameras.count()):
            item = self.lw_cameras.item(index)
            item.setCheckState(state)

    def switch_view(self):
        """
        Switch the model view to the selected camera
        """
        item = self.lw_cameras.currentItem()
        camera_name = item.text()
        self.edit_model_panel(camera_name)

    @staticmethod
    def edit_model_panel(cam):
        # type: (str) -> None
        """
        Set the model panel to the given camera name

        Args:
            cam: The camera name to switch to
        """
        model_panels = cmds.getPanel(type="modelPanel")
        for panel in cmds.getPanel(vis=True):
            if panel in model_panels:
                cmds.modelPanel(panel, edit=True, cam=cam)

    def populate_data(self):
        """
        Populate the cameras with all render cameras
        """
        default_cameras = ["front", "persp", "side", "top"]
        for cam in cmds.listCameras():
            if cam in default_cameras:
                continue

            # create the list widget item
            item = QtWidgets.QListWidgetItem(cam)
            item.setCheckState(QtCore.Qt.Checked)
            self.lw_cameras.addItem(item)

    @property
    def checked_cameras(self):
        # type: () -> list[str]
        """ Get a list of checked cameras """
        checked_cameras = list()
        for index in range(self.lw_cameras.count()):
            item = self.lw_cameras.item(index)
            if item.checkState() != QtCore.Qt.CheckState.Checked:
                continue
            checked_cameras.append(item.text())
        return checked_cameras

    @staticmethod
    def export_unreal_fbx(camera_name, output_dir, start_frame, end_frame):
        # type: (str, int, int) -> None
        """
        Export an animated fbx to be compatible with Unreal

        Args:
            camera_name: Name of the camera to save
            output_dir: Directory path to export to
            start_frame: Start of the cache
            end_frame: End of the cache
        """
        # select the joint and geometry roots and the hierarchy
        cmds.select(camera_name)
        cmds.select(hierarchy=True)

        # run the fbx export commands
        pm.mel.FBXResetExport()
        pm.mel.FBXExportFileVersion(v="FBX201900")
        pm.mel.FBXExportInAscii(v=False)
        pm.mel.FBXExportUpAxis("Y")
        pm.mel.FBXExportScaleFactor(1)
        pm.mel.FBXExportEmbeddedTextures(v=True)
        pm.mel.FBXExportInputConnections(v=True)
        pm.mel.FBXExportIncludeChildren(v=True)
        pm.mel.FBXExportCameras(v=True)
        pm.mel.FBXExportLights(v=True)
        pm.mel.FBXExportConstraints(v=False)
        pm.mel.FBXExportShapes(v=True)
        pm.mel.FBXExportSkins(v=True)
        pm.mel.FBXExportHardEdges(v=False)
        pm.mel.FBXExportSmoothMesh(v=False)
        pm.mel.FBXExportSmoothingGroups(v=True)
        pm.mel.FBXExportBakeComplexAnimation(v=True)
        pm.mel.FBXExportSkeletonDefinitions(v=False)
        pm.mel.FBXExportBakeComplexStart(v=start_frame)
        pm.mel.FBXExportBakeComplexEnd(v=end_frame)
        pm.mel.FBXExportHardEdges(v=False)
        pm.mel.FBXExportTangents(v=True)
        pm.mel.FBXExportAnimationOnly(v=False)
        pm.mel.FBXExportInstances(v=False)

        # set the animation properties
        pm.mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v 1;')
        pm.mel.eval('FBXProperty "Export|IncludeGrp|Animation|Deformation" -v 1;')
        pm.mel.eval('FBXProperty "Export|IncludeGrp|Geometry|SelectionSet" -v 0;')

        # export the fbx path
        camera_name_clean = camera_name.replace(":", "_")
        fbx_path = file_utils.join_file_names(output_dir, f"{camera_name_clean}.fbx")
        pm.mel.FBXExport(f=fbx_path, s=True)

    def export_cameras(self):
        """
        Either playblast or render the checked cameras
        """
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))
        output_dir = self.browse_output_wdg.file_path
        for camera_name in self.checked_cameras:
            self.export_unreal_fbx(camera_name, output_dir, start_frame, end_frame)
        QtWidgets.QMessageBox.information(
            self,
            "Export Cameras",
            f"Exported FBX Cameras",
            QtWidgets.QMessageBox.Ok
        )


def main():
    """
    Launch the maya export cameras to unreal
    """
    maya_utils.launch_maya_win(CamerasToUnreal)