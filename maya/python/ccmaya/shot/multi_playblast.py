""" Multiple playblast or Arnold render of the file """
import os
import glob
import shutil
import maya.cmds as cmds
from PySide6 import QtWidgets, QtCore
import ccmaya.utils.maya_utils as maya_utils
import cccore.base_ui as base_ui


class MultiPlayblast(base_ui.WidgetBase):
    title = "CC Multi Playblast"
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui_settings = QtCore.QSettings('controlChaos', 'multiplay')

        # run setup functions
        self.create_layout()
        self.populate_data()
        self.load_settings()
        self.connect_signals()

    def horizontal_spacer(self):
        # type: () -> QtWidgets.QSpacerItem
        """ Create a horizontal spacer """
        return QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    def vertical_spacer(self):
        # type: () -> QtWidgets.QSpacerItem
        """ Create a vertical spacer """
        return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    def create_layout(self):
        """
        Create the layout of the window
        """
        main_layout = QtWidgets.QVBoxLayout(self)

        # create the top options
        lyt_controls = QtWidgets.QHBoxLayout()
        self.chk_all = QtWidgets.QCheckBox("Check All")
        self.chk_all.setChecked(True)

        # select either the playblast or render buttons
        self.rbn_playblast = QtWidgets.QRadioButton("Playblast")
        self.rbn_playblast.setChecked(True)
        self.rbn_render = QtWidgets.QRadioButton("Render")
        lyt_controls.addWidget(self.chk_all)
        lyt_controls.addSpacerItem(self.horizontal_spacer())
        lyt_controls.addWidget(self.rbn_playblast)
        lyt_controls.addWidget(self.rbn_render)
        lyt_controls.addSpacerItem(self.horizontal_spacer())

        # create the cameras list widget
        lyt_cameras = QtWidgets.QHBoxLayout()
        self.lw_cameras = QtWidgets.QListWidget()
        lyt_cameras.addWidget(self.lw_cameras)

        # create the playblast options
        lyt_options = QtWidgets.QVBoxLayout()
        lyt_options.addSpacerItem(self.vertical_spacer())

        # formats
        self.cmb_formats = QtWidgets.QComboBox()
        self.cmb_formats.addItems(["qt", "image"])
        lyt_options.addWidget(self.cmb_formats)

        # codecs
        self.cmb_codecs = QtWidgets.QComboBox()
        lyt_options.addWidget(self.cmb_codecs)

        # images types for image playblast
        self.cmb_image_type = QtWidgets.QComboBox()
        self.cmb_image_type.addItems(["jpg", "tga", "tif", "png"])
        self.cmb_image_type.setHidden(True)
        lyt_options.addWidget(self.cmb_image_type)

        # ignore objects
        self.chk_ignore_objects = QtWidgets.QCheckBox("Ignore Object")
        lyt_options.addWidget(self.chk_ignore_objects)

        # the resolution options
        lyt_res = QtWidgets.QHBoxLayout()
        self.sp_width = QtWidgets.QSpinBox()
        self.sp_width.setMaximum(99999)
        self.sp_width.setValue(720)
        self.sp_height = QtWidgets.QSpinBox()
        self.sp_height.setMaximum(99999)
        self.sp_height.setValue(576)
        lyt_res.addWidget(self.sp_width)
        lyt_res.addWidget(self.sp_height)

        # add spacer and add to main widget
        lyt_options.addSpacerItem(self.vertical_spacer())
        lyt_options.addLayout(lyt_res)
        lyt_cameras.addLayout(lyt_options)

        # add the select the output directory buttons
        lbl_dir = QtWidgets.QLabel("Output Directory")
        self.le_dir = QtWidgets.QLineEdit()
        self.btn_dir = QtWidgets.QPushButton("Select Directory")

        # add to the layout
        lyt_dir = QtWidgets.QHBoxLayout()
        lyt_dir.addWidget(lbl_dir)
        lyt_dir.addWidget(self.le_dir)
        lyt_dir.addWidget(self.btn_dir)

        # main playblast button
        self.btn_playblast = QtWidgets.QPushButton("Playblast")

        # add all to the main layout
        main_layout.addLayout(lyt_controls)
        main_layout.addLayout(lyt_cameras)
        main_layout.addLayout(lyt_dir)
        main_layout.addWidget(self.btn_playblast)

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
        self.cmb_formats.currentIndexChanged.connect(self.hide_option)
        self.chk_all.toggled.connect(self.check_all)
        self.rbn_playblast.toggled.connect(self.enable_pb_options)

    def enable_pb_options(self):
        """
        Enable the playblast options
        """
        enable = self.rbn_playblast.isChecked()
        widgets = [
            self.cmb_codecs, self.cmb_image_type, self.cmb_formats,
            self.chk_ignore_objects, self.sp_width, self.sp_height
        ]
        for wdg in widgets:
            wdg.setEnabled(enable)

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

    def hide_option(self):
        """
        Hide the image or codec options
        """
        qt_format = self.cmb_formats.currentText()
        is_qt = qt_format == "qt"
        self.cmb_codecs.setHidden(not is_qt)
        self.cmb_image_type.setHidden(is_qt)

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

    def edit_model_panel(self, cam):
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

        # populate the list codec list
        codecs = cmds.playblast(q=True, compression=True)
        codecs.sort()
        self.cmb_codecs.addItems(codecs)

        # set to png by default
        index = self.cmb_codecs.findText("png")
        self.cmb_codecs.setCurrentIndex(index)

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

    def playblast(self):
        """
        Playblast the current maya scene
        """
        directory = self.le_dir.text()
        ignore_objects = self.chk_ignore_objects.isChecked()
        format = self.cmb_formats.currentText()
        width = self.sp_width.value()
        height = self.sp_height.value()

        # save settings
        self.ui_settings.setValue("le_dir", directory)
        self.ui_settings.setValue("width", width)
        self.ui_settings.setValue("height", height)

        # get the compression of the output
        if format == "qt":
            compression = self.cmb_codecs.currentText()
        else:
            compression = self.cmb_image_type.currentText()

        # build the playblast dictionary
        playblast_args = {
            "format": format,
            "percent": 100,
            "quality": 100,
            "sequenceTime": 0,
            "clearCache": True,
            "viewer": False,
            "showOrnaments": not ignore_objects,
            "fp": 4,
            "compression": compression,
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
            ext = ".mov" if format == "qt" else ""
            movie_name_clean = camera_name.replace("|", "_")
            movie_name = f"{movie_name_clean}{ext}"
            movie_path = os.path.join(directory, movie_name)

            # run the playblast of the camera
            print(f"Playblasting...{movie_path}")
            playblast_args["filename"] = movie_path
            cmds.playblast(**playblast_args)


def main():
    """
    Launch the maya multi playblast
    """
    maya_utils.launch_maya_win(MultiPlayblast)