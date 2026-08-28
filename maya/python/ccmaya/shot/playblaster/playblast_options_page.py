""" Playblast options such as codec and resolution """
import os
import uuid
import tempfile
import maya.cmds as cmds
import maya.mel as mel
import cccore.file_env.context as context
import ccmaya.utils.maya_utils as maya_utils
import cccore.utils.file_utils as file_utils
from ccgeneral.wizard.pages.base_page import BasePublishPage
from CCPySide import QtCore


class PlayblastOptionsPage(BasePublishPage):
    title = "Playblast options"
    subtitle = "Select options when playblasting the viewport"
    hide_objects = ["locators", "joints", "deformers"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame_range_wdg = None
        self.movie = None
        self.gif_path = None
        self.progress_wdg = None
        self.model_state = dict()
        self.ctx = context.Context()
        self.ui_settings = QtCore.QSettings('cc', 'playblast')
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.cmb_resolutions.currentIndexChanged.connect(self.enable_custom)

    def enable_custom(self, index):
        # type: (int) -> None
        """
        Enable custom options

        Args:
            index: The current index
        """
        self.custom_wdg.setEnabled(index)

    def initializePage(self):
        """
        Set buttons and populate the data
        """
        self.populate_data()
        self.set_first_page()
        self.set_next_button_text("Playblast")

    def populate_data(self):
        """
        Populate the ui data
        """
        #codecs = cmds.playblast(q=True, compression=True)
        #codecs.sort()
        self.cmb_codecs.addItems(["jpg", "tga", "tif", "png"])
        self.set_combobox_index(self.cmb_codecs, "png")

        # create the playblast directory if it doesn't exist
        playblast_movie_path = self.ctx.playblast_movie_path
        playblast_movie_dir = os.path.dirname(playblast_movie_path)
        if not os.path.exists(playblast_movie_dir):
            os.mkdir(playblast_movie_dir)
        self.le_playblast_path.setText(playblast_movie_path)

        compression = self.ui_settings.value("compression", "")
        resolution = self.ui_settings.value("resolution", "")
        width = self.ui_settings.value("width", 960)
        height = self.ui_settings.value("height", 540)
        ignore_objects = self.ui_settings.value("ignore_objects", 1)

        self.set_combobox_index(self.cmb_codecs, compression)
        self.set_combobox_index(self.cmb_resolutions, resolution)
        self.sb_width.setValue(int(width))
        self.sb_height.setValue(int(height))
        self.chk_ignore_objects.setChecked(int(ignore_objects))

    def hide_non_mesh_objects(self):
        """
        Store the current state and hide the objects
        """
        for model_panel in maya_utils.get_model_panels():
            for obj in self.hide_objects:
                state = cmds.modelEditor(model_panel, q=True, **{obj: True})
                self.model_state[obj] = state
                cmds.modelEditor(model_panel, e=True, **{obj: False})

    def validatePage(self):
        # type: () -> bool
        """
        Save the page data

        Returns:
            True if the page is valid
        """
        image_type = self.cmb_codecs.currentText()
        movie_path = self.le_playblast_path.text()
        resolution = self.cmb_resolutions.currentText()
        width = self.sb_width.value()
        height = self.sb_height.value()

        # if hide objects when checked
        ignore_objects = self.chk_ignore_objects.isChecked()
        if ignore_objects:
            self.hide_non_mesh_objects()

        playblast_path_no_ext = file_utils.join_file_names(
            tempfile.gettempdir(), "playblast", str(uuid.uuid4()))
        gif_file_path = f"{playblast_path_no_ext}.gif"
        playblast_path = f"{playblast_path_no_ext}.%04d.{image_type}"

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
            "filename": playblast_path_no_ext
        }

        if resolution == "Custom":
            playblast_args["width"] = width
            playblast_args["height"] = height

        self.data["start"] = int(cmds.playbackOptions(q=True, min=True))
        self.data["end"] = int(cmds.playbackOptions(q=True, max=True))
        self.data["mov_path"] = movie_path
        self.data["file_sequences"] = [playblast_path]
        self.data["playblast_args"] = playblast_args
        self.data["model_state"] = self.model_state
        self.data["gif_file_path"] = gif_file_path
        self.data["playblast_path"] = playblast_path

        # set the settings
        self.ui_settings.setValue("compression", image_type)
        self.ui_settings.setValue("resolution", resolution)
        self.ui_settings.setValue("width", width)
        self.ui_settings.setValue("height", height)
        self.ui_settings.setValue("ignore_objects", int(ignore_objects))
        return True
