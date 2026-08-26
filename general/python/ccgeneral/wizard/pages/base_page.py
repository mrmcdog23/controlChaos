""" Base page of a wizard """
import enum
from typing import Any
from CCPySide import QtWidgets
import cccore.base_ui as base_ui


class PagePosition(enum.Enum):
    """
    Page position enum
    """
    FIRST = "first"
    MIDDLE = "middle"
    LAST = "last"


class BasePublishPage(base_ui.WizardPageBase):
    title = str()
    subtitle = str()

    def __init__(self, parent=None):
        super(BasePublishPage, self).__init__(parent)
        self.pw = parent
        if self.title:
            self.setTitle(self.title)
        if self.subtitle:
            self.setSubTitle(self.subtitle)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.built_layout = False
        self.page_index = None

    @property
    def data(self):
        # type: () -> dict
        """ Gathered wizard data """
        return self.wizard().data

    @property
    def project_data(self):
        # type: () -> Any
        """ Project data """
        return self.wizard().project_data

    def cleanupPage(self):
        """
        When the user leaves the page by clicking Back the
        default implementation resets the page's fields to
        their original values
        """
        super(BasePublishPage, self).cleanupPage()

    def initializePage(self):
        """
        Prepare the page just before it is shown.
        This function is only called the first
        time the page is shown.
        """
        super(BasePublishPage, self).initializePage()
        self.set_page_buttons()

    def set_page_buttons(self):
        """
        Based on the position of the page set the button layout
        """
        number_of_pages = len(self.wizard().pages_dict)
        if self.page_index == 0:
            self.set_first_page()
        elif self.page_index >= (number_of_pages - 1):
            self.set_last_page()
        else:
            self.set_middle_page()

    def set_buttons(self, page_position):
        # type: (PagePosition) -> None
        """
        Set the buttons to the wizard page

        Args:
            page_position:  Enum of page position
        """
        btn_list = [QtWidgets.QWizard.Stretch]

        if page_position == PagePosition.LAST:
            btn_list.append(QtWidgets.QWizard.FinishButton)

        else:
            if page_position != PagePosition.FIRST:
                btn_list.append(QtWidgets.QWizard.BackButton)

            btn_list.extend([QtWidgets.QWizard.NextButton,
                             QtWidgets.QWizard.CancelButton
                             ])

        self.pw.setButtonLayout(btn_list)

    def set_first_page(self):
        """ Set the first page button layout """
        self.set_buttons(PagePosition.FIRST)

    def set_middle_page(self):
        """ Set the middle page of the wizard button layout """
        self.set_buttons(PagePosition.MIDDLE)

    def set_last_page(self):
        """ Set the last page layout """
        self.set_buttons(PagePosition.LAST)

    def set_next_button_text(self, button_text):
        # type: (str) -> None
        """ Set the next button text """
        self.setButtonText(QtWidgets.QWizard.NextButton, button_text)

    def isComplete(self):
        """
        Determine whether the Next or Finish
        button should be enabled or disabled.
        """
        return super(BasePublishPage, self).isComplete()

    def nextId(self):
        """
        To find out which page to show when the user clicks the Next button.
        The return value is the ID of the next page, or -1 if no page follows.
        By reimplementing this function, you can specify a dynamic page order.
        """
        return None

    def validatePage(self):
        # type: () -> bool
        """
        When the user clicks Next or Finish to perform some  last-minute validation.
        If it returns true, the next page is shown (or the wizard finishes), otherwise
        the current page stays up.

        Returns:
            The default implementation returns True
        """
        return super(BasePublishPage, self).validatePage()

    def skipPage(self):
        # type: () -> bool
        """ Decides whether a page should be skipped. """
        return False

    @property
    def exporter(self):
        # type: () -> Any
        """ The class to be used to export """
        return self.wizard().exporter
