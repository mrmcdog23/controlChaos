""" Capture a thumbnail of the houdini asset """
from CCPySide import QtWidgets
from ccgeneral.wizard.pages.thumbnail_page import ThumbnailPage
import cchoudini.utils.hou_utils as hou_utils


class HouThumbnailPage(ThumbnailPage):
    def __init__(self, parent=None):
        super(HouThumbnailPage, self).__init__(parent)
        self.lbl_thumbnail = None
        self.ext = "jpg"

    def initializePage(self):
        """
        Initialize the data of the asset types
        and names and connect the signals
        """
        super(HouThumbnailPage, self).initializePage()
        self.lbl_thumbnail = QtWidgets.QLabel()
        self.lbl_thumbnail.setScaledContents(True)
        self.verticalLayout.addWidget(self.lbl_thumbnail)
        self.capture_thumbnail()

    def validatePage(self):
        """
        Store the thumbnail path in the wizard data
        """
        self.wizard().data["thumbnail_path"] = self.thumbnail_path
        return True

    def capture_thumbnail(self):
        """
        Save the thumbnail to disk
        """
        hou_utils.viewport_snapshot(self.thumbnail_path)
        self.icon_to_widget = {self.thumbnail_path: self.lbl_thumbnail}
        self.set_widget_icons()

    def isComplete(self):
        return True
