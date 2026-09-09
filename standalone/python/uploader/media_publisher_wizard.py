""" The standalone video publisher """
import cccore.base_ui as base_ui
import ccgeneral.wizard.base_wizard as base_wizard
from ccgeneral.wizard.pages.context_page import ShotComboBoxContextPage
from ccgeneral.wizard.pages.complete_page import CompletePage
from upload_progress_page import UploadProgressPage
from select_movie_page import SelectMoviePage


class  MediaPublisherWizard(base_wizard.BaseWizard):
    title = "Media Publisher"
    window_icon = "media_publisher.png"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data["log_prefix"] = "media_publisher"
        self.data["local"] = True

    @property
    def wizard_pages(self):
        # type: () -> list[Any]
        """ List of wizard pages to add """
        pages = [
            CompletePage,
            ShotComboBoxContextPage,
            SelectMoviePage,
            UploadProgressPage,
            CompletePage
        ]
        return pages


if __name__ == "__main__":
    base_ui.open_ui(MediaPublisherWizard)
