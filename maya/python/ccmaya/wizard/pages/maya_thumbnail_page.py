""" Capture the image thumbnail """
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
import cccore.utils.file_utils as file_utils
from CCPySide import QtWidgets
from ccgeneral.wizard.pages.thumbnail_page import ThumbnailPage


class MayaThumbnailPage(ThumbnailPage):
    title = "Create Thumbnail Page"
    subtitle = "Create a thumbnail for the asset"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.panel_name = str()
        self.add_thumbnail_label()

    @property
    def thumbnail_path(self):
        # type: () -> str
        """ Path of the thumbnail image to save """
        if self._thumbnail_path:
            return self._thumbnail_path
        self._thumbnail_path = file_utils.temp_file_path("thumbnail", "png")
        return self._thumbnail_path

    def add_thumbnail_label(self):
        """
        Create and add a label to the page
        """
        self.thumbnail_image = QtWidgets.QLabel()
        self.thumbnail_image.setObjectName("thumbnail_image")
        self.thumbnail_image.setMinimumWidth(543)
        self.thumbnail_image.setMinimumHeight(300)
        self.thumbnail_image.setScaledContents(True)
        self.verticalLayout.addWidget(self.thumbnail_image)

    def initializePage(self):
        """
        Initialize the data of the asset types
        and names and connect the signals
        """
        self.connect_signals()
        self.capture_thumbnail()

    def connect_signals(self):
        """
        Connect the signals to the widget
        """
        self.btn_capture_thumbnail.clicked.connect(self.capture_thumbnail)

    def closeEvent(self, event):
        """
        Emit complete change on close

        Args:
            event: Close event
        """
        self.completeChanged.emit()

    def capture_thumbnail(self):
        """
        Save the thumbnail to disk
        """
        view = OpenMayaUI.M3dView.active3dView()
        image = OpenMaya.MImage()
        view.readColorBuffer(image, True)
        image.writeToFile(self.thumbnail_path, "png")
        self.set_widget_icons(icon_dict={self.thumbnail_path: "thumbnail_image"})

        self.created_thumbnail = True
        self.completeChanged.emit()

    def validatePage(self):
        """
        Store the thumbnail path in the wizard data
        """
        self.data["thumbnail_path"] = self.thumbnail_path
        return True

    def isComplete(self):
        # type: () -> bool
        """ Is complete once the picture is taken """
        return self.created_thumbnail
