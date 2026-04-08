""" Multiple playblast or Arnold render of the file """
import os
import glob
import shutil
import subprocess
import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore
import ccmaya.utils.maya_utils as maya_utils
import cccore.base_ui as base_ui
import cccore.utils.cc_logging as cc_logging


FFMPEG_EXE = "C:/ffmpeg/bin/ffmpeg.exe"


class MultiPlayblast(base_ui.WindowBase):
    title = "CC Multi Playblast"
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui_settings = QtCore.QSettings('controlChaos', 'multiplay')
        self.logger = cc_logging.cc_logger()

        # run setup functions
        self.populate_data()
        self.load_settings()
        self.connect_signals()

    def load_settings(self):
        """
        Load the previous settings to the widgets
        """
        le_dir = self.ui_settings.value("le_dir", str())
        self.le_dir.setText(le_dir)

        ignore_objects = self.ui_settings.value("ignore_objects", True)
        self.chk_ignore_objects.setChecked(bool(ignore_objects))

        width = self.ui_settings.value("width", 720)
        self.sp_width.setValue(int(width))

        height = self.ui_settings.value("height", 576)
        self.sp_height.setValue(int(height))

    def connect_signals(self):
        """
        Connect the signal to the widgets
        """
        self.btn_playblast.clicked.connect(self.playblast_or_render)
        self.btn_dir.clicked.connect(self.browse)
        self.lw_cameras.itemSelectionChanged.connect(self.switch_view)
        self.chk_all.toggled.connect(self.check_all)
        self.rbn_playblast.toggled.connect(self.enable_pb_options)

    def enable_pb_options(self):
        """
        Enable the playblast options
        """
        enable = self.rbn_playblast.isChecked()
        self.grp_playblast.setEnabled(enable)

        # update the button text
        btn_text = "Playblast" if enable else "Render"
        self.btn_playblast.setText(btn_text)

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

    def browse(self):
        # type: (str) -> None
        """
        Select and set the directory to the line edit

        Args:
            line_edit: The line edit widget to set
        """
        sel_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", "",
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        self.le_dir.setText(sel_path)

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
        self.cmb_image_type.addItems(["jpg", "tga", "tif", "png"])

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

    def playblast_or_render(self):
        """
        Either playblast or render the checked cameras
        """
        if self.rbn_playblast.isChecked():
            self.playblast()
        else:
            self.arnold_render()

    def arnold_render(self):
        """
        Render the cameras via arnold
        """
        # set the output render directory
        render_directory = self.le_dir.text()
        current_workspace = cmds.workspace(q=True, openWorkspace=True)
        cmds.workspace(render_directory, openWorkspace=True)

        # get the frame range
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))

        # set the render globals
        cmds.setAttr('defaultRenderGlobals.animation', 1)
        cmds.setAttr('defaultRenderGlobals.startFrame', start_frame)
        cmds.setAttr('defaultRenderGlobals.endFrame', end_frame)
        cmds.setAttr('defaultRenderGlobals.outFormatControl', 0)  # name.#.ext
        cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', 1)
        cmds.setAttr('defaultRenderGlobals.extensionPadding', 4)
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix', "<Camera>", type="string")

        # loop through each camera and render the scene
        for camera_name in self.checked_cameras:
            cmds.arnoldRender(batch=True, camera=camera_name)
        cmds.workspace(current_workspace, openWorkspace=True)

        # move to correct location
        image_paths = glob.glob(f"{render_directory}/*/*.exr")
        if not image_paths:
            return

        # find each image and move to the directory
        for image_path in image_paths:
            image_name = os.path.basename(image_path)
            dest_path = os.path.join(render_directory, image_name)
            shutil.move(image_path, dest_path)

    @staticmethod
    def run_ffmpeg_command(command):
        # type: (str) -> None
        """
        Run the ffmpeg subprocess

        Args:
            command: The command to run
        """
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        process.communicate()

    def playblast(self):
        """
        Playblast the current maya scene
        """
        directory = self.le_dir.text()
        ignore_objects = self.chk_ignore_objects.isChecked()
        width = self.sp_width.value()
        height = self.sp_height.value()

        # save settings
        self.ui_settings.setValue("le_dir", directory)
        self.ui_settings.setValue("width", width)
        self.ui_settings.setValue("height", height)

        # get the compression of the output
        image_type = self.cmb_image_type.currentText()
        create_movie = self.chk_create_movie.isChecked()

        # build the playblast dictionary
        playblast_args = {
            "format": "image",
            "percent": 100,
            "quality": 100,
            "sequenceTime": 0,
            "clearCache": True,
            "viewer": False,
            "showOrnaments": not ignore_objects,
            "fp": 4,
            "compression": image_type,
            "exposure": 0,
            "gamma": 1,
            "forceOverwrite": True,
            "width": width,
            "height": height
        }

        # loop through each camera and playblast
        for camera_name in self.checked_cameras:
            self.edit_model_panel(camera_name)

            # work out the output file name
            sequence_name_clean = camera_name.replace("|", "_")
            sequence_path = os.path.join(directory, sequence_name_clean)

            sequence_padded_name = f"{sequence_name_clean}.%04d.{image_type}"
            sequence_padded_path = os.path.join(directory, sequence_padded_name)

            # run the playblast of the camera
            self.logger.info(f"Playblasting...{sequence_path}")
            playblast_args["filename"] = sequence_path
            cmds.playblast(**playblast_args)

            if create_movie:
                movie_path = os.path.join(directory, f"{sequence_name_clean}.mov")
                start = int(cmds.playbackOptions(q=True, ast=True))
                command = (f"ffmpeg -y  -start_number {start} -i {sequence_padded_path} "
                           f"-c:v libx264 -pix_fmt yuv420p {movie_path}")
                self.logger.info(command)
                self.run_ffmpeg_command(command)

def main():
    """
    Launch the maya multi playblast
    """
    maya_utils.launch_maya_win(MultiPlayblast)