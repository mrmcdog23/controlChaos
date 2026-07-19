""" Subclass of widget to allow drag and drops """
from CCPySide import QtWidgets, QtCore
from typing import Any, Optional


class DragDropListWidget(QtWidgets.QListWidget):
    """
    Subclass of list widget to allow drag and drops
    """
    def __init__(self, parent=None):
        super(DragDropListWidget, self).__init__(parent)
        self.setIconSize(QtCore.QSize(124, 124))
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)

    def dragMoveEvent(self, event):
        """
        Drag an item event function

        Args:
            event:
        """
        items = event.source().selectedItems()
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            super(DragDropListWidget, self).dragMoveEvent(event)
        for item in items:
            self.takeItem(self.row(item))

    @property
    def list_names(self):
        # type: () -> list[str]
        """ Get a list of names in the list widget """
        names = list()
        for index in range(self.count()):
            item = self.item(index)
            names.append(item.text())
        return names

    @property
    def list_items(self):
        # type: () -> list[QtWidgets.QListWidgetItem]
        """ Get a list of names in the list widget """
        items = list()
        for index in range(self.count()):
            item = self.item(index)
            items.append(item)
        return items

    @property
    def items_added(self):
        # type: () -> bool
        """ Whether there are items added """
        return bool(self.count())

    def add_text_items(self, text_list, data=None, clear=True):
        # type: (list[str], Optional[Any], Optional[bool]) -> None
        """
        Add a list of strings as items

        Args:
            text_list: List of text to add
            data: User data to set in the item
            clear: Whether to clear the list first
        """
        if clear:
            self.clear()
        for text in text_list:
            item = QtWidgets.QListWidgetItem(text)
            if data:
                item.setData(QtCore.Qt.UserRole, data)
            self.addItem(item)
