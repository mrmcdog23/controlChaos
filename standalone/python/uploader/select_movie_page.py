""" Select the movie file to publish """
import os
from CCPySide import QtWidgets, QtCore
from ccgeneral.widgets.line_browser import LineBrowser
from ccgeneral.wizard.pages.base_page import BasePublishPage
import cccore.utils.file_utils as file_utils
import cccore.utils.ffmpeg_utils as ffmpeg_utils


class SelectMoviePage(BasePublishPage):
    title = "Publish Sequences"
    subtitle = "Select the sequences to publish"

    def __init__(self, parent=None):
        super(SelectMoviePage, self).__init__(parent)

        # initialize class variable
        self.seq_path_wdg = None
        self.ui_settings = QtCore.QSettings('cc', 'list_sequences')

        # more variables
        self.create_layout()
        self.connect_signals()

    def initializePage(self):
        """
        Set the sequences from the start directory
        """
        super().initializePage()
        start_dir = self.ui_settings.value(
            "sequence_dir", self.project_data.project_root)
        self.seq_path_wdg.start_dir = start_dir

    @property
    def movie_path(self):
        # type: () -> str
        """ The selected sequence directory """
        return self.seq_path_wdg.line_edit.text()

    def create_layout(self):
        """
        Add the sequence line edit
        """
        self.seq_path_wdg = LineBrowser(
            self,
            "file",
            "Select a video to upload",
            str(),
            "Selected Movie",
            file_filter="(*.mov *.mp4)"
        )
        self.main_layout.addWidget(self.seq_path_wdg)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.seq_path_wdg.line_edit.textChanged.connect(self.check_complete)

    def check_complete(self):
        """ Emit the complete change signal """
        self.completeChanged.emit()

    def isComplete(self):
        """
        Do not go to next page if it's not the project
        """
        return bool(self.movie_path)

    def validatePage(self):
        """
        Store the thumbnail path in the wizard data
        """
        thumbnail_path = file_utils.temp_file_path("movie_upload", "png")
        ffmpeg_utils.convert_image_type(self.movie_path, thumbnail_path)
        self.data["thumbnail_path"] = thumbnail_path
        self.data["movie_component_path"] = self.movie_path
        self.data["display_name"] = os.path.basename(self.movie_path)
        return True
