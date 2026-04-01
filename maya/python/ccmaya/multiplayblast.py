from PySide6 import QtWidgets, QtCore
import maya.cmds as cmds
import os


class MultiPlayblast(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CC Multi Playblast")
        self.ui_settings = QtCore.QSettings('controlChaos', 'multiplay')
        self.create_layout()
        self.populate_data()
        self.load_settings()
        self.connect_signals()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        lyt_cameras = QtWidgets.QHBoxLayout()
        self.lw_cameras = QtWidgets.QListWidget()
        lyt_cameras.addWidget(self.lw_cameras)

        lyt_options = QtWidgets.QVBoxLayout()

        # formats
        self.cmb_formats = QtWidgets.QComboBox()
        self.cmb_formats.addItems(["qt", "image"])
        lyt_options.addWidget(self.cmb_formats)

        # codecs
        self.cmb_codecs = QtWidgets.QComboBox()
        lyt_options.addWidget(self.cmb_codecs)

        # codecs
        self.cmb_image_type = QtWidgets.QComboBox()
        self.cmb_image_type.addItems(["jpg", "tga", "tif", "png"])
        self.cmb_image_type.setHidden(True)
        lyt_options.addWidget(self.cmb_image_type)

        # ignore objects
        self.chk_ignore_objects = QtWidgets.QCheckBox("Ignore Object")
        lyt_options.addWidget(self.chk_ignore_objects)

        lyt_res = QtWidgets.QHBoxLayout()
        self.sp_width = QtWidgets.QSpinBox()
        self.sp_width.setMaximum(99999)
        self.sp_width.setValue(720)
        self.sp_height = QtWidgets.QSpinBox()
        self.sp_height.setMaximum(99999)
        self.sp_height.setValue(576)
        lyt_res.addWidget(self.sp_width)
        lyt_res.addWidget(self.sp_height)
        lyt_options.addLayout(lyt_res)

        lyt_cameras.addLayout(lyt_options)

        lbl_dir = QtWidgets.QLabel("Output Directory")
        self.le_dir = QtWidgets.QLineEdit()
        self.btn_dir = QtWidgets.QPushButton("Select Directory")

        # add to the layout
        lyt_dir = QtWidgets.QHBoxLayout()
        lyt_dir.addWidget(lbl_dir)
        lyt_dir.addWidget(self.le_dir)
        lyt_dir.addWidget(self.btn_dir)

        self.btn_playblast = QtWidgets.QPushButton("Playblast")
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
        self.chk_ignore_objects.setChecked(ignore_objects)

        width = self.ui_settings.value("width", 720)
        self.sp_width.setValue(width)

        height = self.ui_settings.value("height", 576)
        self.sp_height.setValue(height)

    def connect_signals(self):
        self.btn_playblast.clicked.connect(self.playblast)
        self.btn_dir.clicked.connect(self.browse)
        self.lw_cameras.itemSelectionChanged.connect(self.switch_view)
        self.cmb_formats.currentIndexChanged.connect(self.hide_option)

    def hide_option(self):
        format = self.cmb_formats.currentText()
        is_qt = format == "qt"
        self.cmb_codecs.setHidden(not is_qt)
        self.cmb_image_type.setHidden(is_qt)

    def switch_view(self):
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
        # set the model panel to the turntable camera
        model_panels = cmds.getPanel(type="modelPanel")
        for panel in cmds.getPanel(vis=True):
            if panel in model_panels:
                cmds.modelPanel(panel, edit=True, cam=cam)

    def populate_data(self):
        default_cameras = ["front", "persp", "side", "top"]
        for cam in cmds.listCameras():
            if cam in default_cameras:
                continue
            item = QtWidgets.QListWidgetItem(cam)
            item.setCheckState(QtCore.Qt.Checked)
            self.lw_cameras.addItem(item)

        codecs = cmds.playblast(q=True, compression=True)
        codecs.sort()
        self.cmb_codecs.addItems(codecs)
        index = self.cmb_codecs.findText("png")
        self.cmb_codecs.setCurrentIndex(index)

    def playblast(self):
        directory = self.le_dir.text()
        ignore_objects = self.chk_ignore_objects.isChecked()
        format = self.cmb_formats.currentText()
        width = self.sp_width.value()
        height = self.sp_height.value()

        # save settings
        self.ui_settings.setValue("le_dir", directory)
        self.ui_settings.setValue("width", width)
        self.ui_settings.setValue("height", height)

        if format == "qt":
            compression = self.cmb_codecs.currentText()
        else:
            compression = self.cmb_image_type.currentText()

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

        for index in range(self.lw_cameras.count()):
            item = self.lw_cameras.item(index)
            if item.checkState() != QtCore.Qt.CheckState.Checked:
                continue

            camera_name = item.text()
            self.edit_model_panel(camera_name)
            ext = ".mov" if format == "qt" else ""
            movie_name = f"{camera_name}{ext}"
            movie_path = os.path.join(directory, movie_name)
            print (f"Playblasting...{movie_path}")
            playblast_args["filename"] = movie_path
            cmds.playblast(**playblast_args)


def main():
    # find and launch the ui under the maya window
    loading = MultiPlayblast()
    loading.show()