""" A widget to browse and set the line edit """
import cccore.base_ui as base_ui
from typing import Optional
from CCPySide import QtWidgets, QtGui


class LineBrowser(base_ui.WidgetBase):
    """
    A widget to browse and set a line edit
    """
    def __init__(self, pw, mode, title, start_dir, label_text, file_filter=None):
        # type: (QtWidgets.QWidget, str, str, str, str, Optional[str]) -> None
        """
        Args:
            mode: Search folder or file: "dir", "file", "save"
            title: Browser title
            start_dir: Open the dialog at the directory
            label_text: The label text
            file_filter : Filter for files
        """
        super(LineBrowser, self).__init__(mode=mode)

        # initialize class widgets
        self.label = None
        self.line_edit = None
        self.btn_browse = None

        # set class variables
        self.pw = pw
        self.mode = mode
        self.title = title
        self.start_dir = start_dir
        self.label_text = label_text
        self.file_filter = file_filter

        # run setup functions
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        """
        Create the line edit browser layout
        """
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)

        # create the path label
        self.label = QtWidgets.QLabel()
        self.label.setText(self.label_text)
        main_layout.addWidget(self.label)

        # create the line edit for the path
        self.line_edit = QtWidgets.QLineEdit()
        main_layout.addWidget(self.line_edit)

        # create browse button
        self.btn_browse = QtWidgets.QPushButton()
        icon_path = self.get_icon_path("folder")
        self.btn_browse.setIcon(QtGui.QIcon(icon_path))
        self.btn_browse.setProperty("btn_ss", True)

        main_layout.addWidget(self.btn_browse)
        self.setLayout(main_layout)

    def connect_signals(self):
        """
        Connect the browse button to the function
        """
        self.btn_browse.clicked.connect(self.browse)

    def browse(self):
        """
        Based on the mode set the browser
        """
        if self.mode == "dir":
            dialog = QtWidgets.QFileDialog.getExistingDirectory
            sel_path = dialog(
                self.pw, self.title, self.start_dir,
                QtWidgets.QFileDialog.ShowDirsOnly
            )
        elif self.mode == "save":
            dialog = QtWidgets.QFileDialog.getSaveFileName
            sel_path, _ = dialog(
                self.pw, self.title, self.start_dir, self.file_filter)
        else:
            dialog = QtWidgets.QFileDialog.getOpenFileName
            sel_path, _ = dialog(
                self.pw, self.title, self.start_dir, self.file_filter)

        if sel_path:
            self.line_edit.setText(sel_path)
            self.start_dir = sel_path

    @property
    def file_path(self):
        """
        The set file path
        """
        return self.line_edit.text()

    def set_file_path(self, file_path):
        # type: (str) -> None
        """
        Set the file path on the line edit

        Args:
            file_path: Path of the file to set
        """
        self.line_edit.setText(file_path)
