""" cc Playblast tool """
import maya.cmds as cmds
from CCPySide import QtWidgets
import cccore.utils.ffmpeg_utils as ffmpeg_utils
import cccore.utils.sequence_utils as sequence_utils
import ccmaya.utils.maya_utils as maya_utils
from ccgeneral.wizard.pages.base_page import BasePublishPage


class PreviewPage(BasePublishPage):
    title = "Preview Playblast"
    subtitle = "Preview playblast page"

    def __init__(self, parent=None):
        super().__init__(parent)

        # set class variables
        self.lbl_playblast_display = None
        self.mov_path = str()
        self.movie = None

        # create the layout
        self.create_layout()

    def create_layout(self):
        """
        Create the layout of the page
        """
        self.lbl_playblast_display = QtWidgets.QLabel()
        self.lbl_playblast_display.setFrameStyle(QtWidgets.QFrame.Box)
        self.lbl_playblast_display.setFixedSize(600, 400)
        self.lbl_playblast_display.setScaledContents(True)
        self.main_layout.addWidget(self.lbl_playblast_display)

    def initializePage(self):
        """
        Set page text and run playblast
        """
        self.set_next_button_text("Publish")
        cmds.playblast(**self.data['playblast_args'])

        # generate the gif file
        playblast_path = self.data["playblast_path"]
        gif_file_path = self.data["gif_file_path"]

        success = ffmpeg_utils.run_ffmpeg_mov_to_gif_command(playblast_path, gif_file_path)
        if not success:
            return

        self.set_gif_on_label(self, gif_file_path, self.lbl_playblast_display, 600, 400)

        # if ignore objects is empty then skip
        model_state = self.data["model_state"]
        if not model_state:
            return
        for model_panel in maya_utils.get_model_panels():
            for obj, state in model_state.items():
                cmds.modelEditor(model_panel, e=True, **{obj: state})

    def validatePage(self):
        # type: () -> bool
        """
        Store page data and return True
        """
        playblast_path = self.data["playblast_path"]
        seq_data = sequence_utils.get_sequence_data(playblast_path)
        self.data["thumbnail_path"] = seq_data.first_frame_path
        return True
