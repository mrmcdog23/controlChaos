""" Combo box specific for ftrack statuses """
from CCPySide import QtWidgets, QtCore, QtGui
import cccore.utils.ui_utils as ui_utils


class StatusCmb(QtWidgets.QComboBox):
    """
    Ftrack specific combobox for statuses
    """
    def __init__(self, version_statuses):
        # type: (list[str]) -> None
        """
        Args:
            version_statuses: list of ftrack version status
        """
        super().__init__()
        self.setMinimumWidth(120)
        self.version_statuses = version_statuses
        self.populate_statuses()
        self.currentIndexChanged.connect(self.update_status_colour)

    def update_status_colour(self):
        """
        When the combo box status is changed update its background
        """
        status = None
        try:
            status = self.currentData()
        except AttributeError:
            # if you can't use the new method try matching through loop
            status_name = self.currentText()
            for status in self.version_statuses:
                if status["name"] == status_name:
                    break

        style_sheet = ui_utils.get_status_stylesheet(status)
        line_edit = self.lineEdit()
        line_edit.setStyleSheet(style_sheet)

    def populate_statuses(self):
        """
        Populate the statuses combobox from ftrack
        """
        for index, status in enumerate(self.version_statuses):
            self.addItem(status["name"], status)
            color = QtGui.QColor(status['color'])
            self.setItemData(index, color, QtCore.Qt.BackgroundRole)
            text_color = QtGui.QColor(0, 0, 0)
            self.setItemData(index, text_color, QtCore.Qt.ForegroundRole)
            try:
                self.setItemData(index, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)
            except TypeError:
                pass

        self.setEditable(True)
        line_edit = self.lineEdit()
        line_edit.setAlignment(QtCore.Qt.AlignCenter)
        line_edit.setReadOnly(True)
        self.update_status_colour()

