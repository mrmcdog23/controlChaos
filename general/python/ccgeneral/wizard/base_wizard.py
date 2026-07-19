""" Base wizard class """
from typing import Any
from CCPySide import QtWidgets, QtCore, QtGui
import cccore.base_ui as base_ui
import cccore.utils.ui_utils as ui_utils
import cccore.utils.cc_logging as cc_logging


class BaseWizard(base_ui.WizardBase):
    FINAL_PAGE = None
    title = "Wizard"
    banner_name = "wizard_banner.png"

    def __init__(self, parent=None, cc_ss=None):
        super(BaseWizard, self).__init__(parent, cc_ss=cc_ss)

        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        self.setTitleFormat(QtCore.Qt.PlainText)
        self.setSubTitleFormat(QtCore.Qt.RichText)
        self.setWindowModality(QtCore.Qt.NonModal)
        self.setOption(QtWidgets.QWizard.NoBackButtonOnLastPage, True)
        self.setOption(QtWidgets.QWizard.NoCancelButtonOnLastPage, True)
        self.setModal(True)

        # initialize class variables
        self.exporter = None
        self.asset_version_id = None
        self.pages_dict = dict()
        self.data = dict()

        # initialize deadline variables
        self.deadline_only = False
        self.chunk_size = None
        self.dl_settings = None
        self.pool = None
        self.output_subfolder = None

        self.logger = cc_logging.cc_logger()

        # set the wizard banner
        banner_path = self.get_icon_path(self.banner_name)
        pixmap = QtGui.QPixmap(banner_path)
        self.setPixmap(QtWidgets.QWizard.BannerPixmap, pixmap)

        self.add_wizard_pages()
        self.set_publish_data()

    @property
    def wizard_pages(self):
        # type: () -> list[QtWidgets.QWizardPage]
        """ List of wizard pages to add """
        return list()

    def add_wizard_pages(self):
        """
        Get the configured pages and add them to the
        wizard in the order they were given in the config
        """
        for index, page in enumerate(self.wizard_pages):
            self.add_page_with_id(page(parent=self), index)

    def add_page_with_id(self, page_cls, page_id):
        # type: (Any, int) -> int
        """
        Adds the page and automatically sets the page id.

        Args:
            page_cls: The page to add to the wizard
            page_id: Index of page

        Return:
            page_id: New index of page
        """
        if page_id in self.pageIds():
            page_id = sorted(self.pageIds())[-1] + 1
        page_cls.page_index = page_id
        self.setPage(page_id, page_cls)
        self.pages_dict[page_id] = page_cls
        return page_id

    def pageId(self, page):
        # type: (base_ui.WizardPageBase) -> int
        """
        Gets the id of the page
        """
        for page_id in self.pageIds():
            if self.pages_dict[page_id] == page:
                return page_id
        return -1

    def nextId(self):
        # type: () -> int
        """
        Get the id of the next page.
        """
        next_id = self.currentPage().nextId()
        if next_id is None:
            next_id = -1

        if next_id == -1:
            index = self.pageIds().index(self.currentId()) + 1
        else:
            index = self.pageIds().index(next_id)

        for page_id in self.pageIds()[index:]:
            if page_id in list(self.pages_dict.keys()):
                page = self.pages_dict[page_id]
            else:
                page = self.page(page_id)

            if not page:
                return -1

            if not hasattr(page, 'skipPage') or not page.skipPage():
                return page_id
        return -1

    @property
    def index(self):
        # type: () -> int
        """ Get the current page index """
        next_id = self.currentPage().nextId()
        if next_id is None:
            next_id = -1

        if next_id == -1:
            index = self.pageIds().index(self.currentId()) + 1
        else:
            index = self.pageIds().index(next_id)
        return index

    @property
    def is_first_page(self):
        # type: () -> int
        """ If it is the first page then return True """
        return self.index == 1

    @property
    def is_last_page(self):
        # type: () -> int
        """ If it is the last page then return True """
        return bool(self.index == len(self.pageIds()))

    @staticmethod
    def wip_file_path():
        # type: () -> str
        """ The wip file path """
        return str()

    @staticmethod
    def entity_type():
        # type: () -> str
        """ Either a shot or asset """
        return str()

    def set_publish_data(self):
        """
        Set the core publish data to save
        """
        self.data["wip_file_path"] = self.wip_file_path()

    @classmethod
    def run_checks(cls):
        # type: () -> str
        """
        Run checks that are vital before opening the publishing wizard

        Returns:
            message: Error message of issue
        """
        message = None
        if not cls.wip_file_path():
            message = "File not saved"
        return message

    @classmethod
    def preflight_checks(cls):
        # type: () -> bool
        """
        Run checks before submitting to Deadline

        Returns:
            True if good to continue
        """
        message = cls.run_checks()
        if message:
            ui_utils.messagebox("Not valid", message, "critical")
            return False
        return True
