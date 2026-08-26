""" Wrapper of tree widget """
from typing import Optional, Any
from CCPySide import QtWidgets, QtCore


FIRST_INDEX = 0


class CCTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """
    Subclass of tree widget item
    """
    def __init__(self, text_list):
        super().__init__(text_list)

    def disable_row(self):
        """ Make row uncheckable and greyed out """
        for index in range(self.columnCount()):
            self.setForeground(index, QtCore.Qt.darkGray)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsUserCheckable)

    @property
    def is_checked(self):
        # type: () -> bool
        """ Is the item checked """
        return self.checkState(FIRST_INDEX) == QtCore.Qt.Checked

    def set_checked(self):
        """ Set the item as checked """
        self.setCheckState(FIRST_INDEX, QtCore.Qt.Checked)

    def set_unchecked(self):
        """ Set the item as unchecked """
        self.setCheckState(FIRST_INDEX, QtCore.Qt.Unchecked)

    def set_data(self, data):
        # type: (Any) -> None
        """ Set the items data """
        self.setData(FIRST_INDEX, QtCore.Qt.UserRole, data)

    @property
    def user_data(self):
        # type: () -> Any
        """ Return the user data """
        return self.data(FIRST_INDEX, QtCore.Qt.UserRole)

    def set_checked_state(self, checked):
        # type: (bool) -> None
        """
        Set the check state if it is a file node

        Args:
            checked: Set checked if true
        """
        self.set_checked() if checked else self.set_unchecked()


class CCTreeWidget(QtWidgets.QTreeWidget):
    """
    Subclass of tree widget for repeated functionality
    """
    adjust_to_context = True

    def __init__(self, labels):
        super().__init__()
        self.setColumnCount(len(labels))
        self.setHeaderLabels(labels)

    def set_column_widths(self, column_widths):
        # type: (list[int]) -> None
        """
        Set the tree column widths

        Args:
            column_widths: The column widths in order
        """
        for index, width in enumerate(column_widths):
            self.setColumnWidth(index, width)

    def enable_sorting(self):
        """
        Set the columns to sorted in the first column
        """
        self.setSortingEnabled(True)
        self.sortByColumn(FIRST_INDEX, QtCore.Qt.DescendingOrder)

    def standard_column_widths(self, column_width):
        # type: (int) -> None
        """
        Set all column widths the same size

        Args:
            column_width: The column width to set
        """
        column_count = self.columnCount()
        for index in range(column_count):
            self.setColumnWidth(index, column_width)

    def set_to_content(self):
        """
        Resize all the columns to the content
        and stretch the last column
        """
        if not self.adjust_to_context:
            return
        header = self.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    @property
    def checked_items(self):
        # type: () -> list[QtWidgets.QTreeWidgetItem]
        """
        Get a list of all checked items
        """
        return self.checked_items_index(FIRST_INDEX)

    def checked_items_index(self, checked_index):
        # type: (int) -> list[CCTreeWidgetItem]
        """
        Get a list of checked items

        Args:
            checked_index: The index of the checked items

        Returns:
            checked_items: List of checked items
        """
        checked_items = list()
        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            if item.checkState(checked_index) == QtCore.Qt.Checked:
                checked_items.append(item)
        return checked_items

    @property
    def items(self):
        # type: () -> list[QtWidgets.QTreeWidgetItem]
        """
        Get a list of all items
        """
        items = list()
        for index in range(self.topLevelItemCount()):
            items.append(self.topLevelItem(index))
        return items

    def populate_items(self, text_list, checked=True, unchecked=False):
        # type: (list[str], Optional[bool], Optional[bool]) -> None
        """
        From a list of strings create tree widget items

        Args:
            text_list: List of strings
            checked: Set the item checked
            unchecked: Set the item unchecked
        """
        for text in text_list:
            if isinstance(text, str):
                self.add_item_text_list([text], checked, unchecked)
            else:
                self.add_item_text_list(text, checked, unchecked)

    def add_item_text_list(self, text_list, checked, unchecked, data=None):
        item = CCTreeWidgetItem(text_list)
        if checked:
            item.set_checked()
        if unchecked:
            item.set_unchecked()
        if data:
            item.set_data(data)
        self.addTopLevelItem(item)
        return item

    @staticmethod
    def set_item_check_state(item, checked):
        # type: (QtWidgets.QTreeWidgetItem, bool) -> None
        """
        Set the first index of the tree widget item

        Args:
            item: Item to set the check state
            checked: The state to set the item
        """
        if checked:
            item.setCheckState(FIRST_INDEX, QtCore.Qt.Checked)
        else:
            item.setCheckState(FIRST_INDEX, QtCore.Qt.Unchecked)

    def items_text(self, checked_only=True):
        # type: (Optional[bool]) -> list[str]
        """
        Get a list of all items text

        Args:
            checked_only: Get only checked items

        Return:
            items_text: List of text items
        """
        items_text = list()
        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            if checked_only and not item.is_checked:
                continue
            items_text.append(item.text(FIRST_INDEX))
        return items_text

    @property
    def count(self):
        # type: () -> int
        """ Get the number of items """
        return self.topLevelItemCount()

    def check_all(self, checked):
        # type: (bool) -> None
        """
        Check or uncheck all tree items

        Args:
            checked: If true set checked
        """
        for item in self.items:
            item.set_checked_state(checked)