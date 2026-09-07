""" Create a thumbnail for the asset page """
import cccore.file_env.context as context
from ccgeneral.wizard.pages.base_page import BasePublishPage


class ThumbnailPage(BasePublishPage):
    title = "Create Thumbnail Page"
    subtitle = "Create a thumbnail for the asset"

    def __init__(self, parent=None):
        super(ThumbnailPage, self).__init__(parent)
        self.ctx = context.Context()
        self.thumbnail_image = None
        self._thumbnail_path = str()
        self.created_thumbnail = False
        self.ext = "png"

    @property
    def thumbnail_path(self):
        # type: () -> str
        """
        Thumbnail path to save

        Returns:
            Path of the image to save
        """
        return self.wizard().data['path_suffix'] + self.ext

    def initializePage(self):
        """
        Initialize the data of the asset types
        and names and connect the signals
        """
        super(ThumbnailPage, self).initializePage()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widget
        """
        self.btn_capture_thumbnail.clicked.connect(self.capture_thumbnail)

    def closeEvent(self, event):
        """
        Run the complete event when page is closed

        Args:
            event: The event to run
        """
        self.completeChanged.emit()

    def capture_thumbnail(self):
        """
        Save the thumbnail to disk
        """
        pass

    def isComplete(self):
        # type: () -> bool
        """
        Is complete once the picture is taken

        Returns:
            Whether there is text in the description
        """
        return self.created_thumbnail

    def nextId(self):
        """
        Will go to the next page
        """
        return self.wizard().FINAL_PAGE
