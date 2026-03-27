""" Extract all text from a PDF file. """
import os
import sys
import extract_pdf_data
from dataclasses import asdict
from PySide6 import QtWidgets, QtCore, QtGui


# constants
THUMBNAIL_WIDTH = 250
THUMBNAIL_HEIGHT = 160


class SlateMakerUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.headers = [
            "thumbnail", "show_name", "shot_name", "duration",
            "focal_length", "resolution", "version", "notes"
        ]
        self.pdf_data_inst = None
        self.ui_settings = QtCore.QSettings('controlChaos', 'slate_maker')

        # set the ui size and title
        self.setWindowTitle("Control Chaos Slate Maker")
        self.setMinimumSize(1200, 600)

        # run the setup functions
        self.create_layout()
        self.load_settings()
        self.connect_signals()

    def create_line_edit(self, label_text, btn_label_text):
        # type: (str, str) -> (QtWidgets.QLineEdit, QtWidgets.QPushButton)
        """
        Create a line edit widget with a label and browser button

        Args:
            label_text: The text to set on the label
            btn_label_text: Text to set on the button

        Returns:
            le_dir: The line edit for the path
            btn_dir: Button to browse the directories
        """
        lbl_dir = QtWidgets.QLabel(label_text)
        le_dir = QtWidgets.QLineEdit()
        btn_dir = QtWidgets.QPushButton(btn_label_text)

        # add to the layout
        lyt_dir = QtWidgets.QHBoxLayout()
        lyt_dir.addWidget(lbl_dir)
        lyt_dir.addWidget(le_dir)
        lyt_dir.addWidget(btn_dir)
        self.main_layout.addLayout(lyt_dir)
        return le_dir, btn_dir

    def create_layout(self):
        """
        Create the ui layout widget
        """
        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        self.main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # browse the pdf directory
        self.le_pdf_dir, self.btn_pdf_dir = self.create_line_edit("PDF Directory", "Browse PDF Directory")

        # browse the movie directory
        self.le_movie_dir, self.btn_movie_dir = self.create_line_edit("Movie Directory", "Browse Movie Directory")

        self.btn_extract_data = QtWidgets.QPushButton("Extract Data")
        self.main_layout.addWidget(self.btn_extract_data)

        self.tbw_shots = QtWidgets.QTableWidget(0, len(self.headers))
        self.tbw_shots.setColumnWidth(0, THUMBNAIL_WIDTH)
        self.tbw_shots.setHorizontalHeaderLabels(self.headers)
        self.tbw_shots.horizontalHeader().setStretchLastSection(True)
        self.main_layout.addWidget(self.tbw_shots)

        # browse the movie directory
        self.le_output_dir, self.btn_output_dir = self.create_line_edit("Output Directory", "Browse Output Directory")

        # Button
        self.btn_create_slates = QtWidgets.QPushButton("Create Slates")
        self.main_layout.addWidget(self.btn_create_slates)

    def load_settings(self):
        """
        Load the previous settings to the widgets
        """
        # save the path in the q-settings
        le_pdf_dir = self.ui_settings.value("le_pdf_dir", str())
        self.le_pdf_dir.setText(le_pdf_dir)

        # save the path in the q-settings
        le_movie_dir = self.ui_settings.value("le_movie_dir", str())
        self.le_movie_dir.setText(le_movie_dir)

        # save the path in the q-settings
        le_output_dir = self.ui_settings.value("le_output_dir", str())
        self.le_output_dir.setText(le_output_dir)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.btn_pdf_dir.clicked.connect(self.select_pdf_dir)
        self.btn_movie_dir.clicked.connect(self.select_movie_dir)
        self.btn_output_dir.clicked.connect(self.select_output_dir)
        self.btn_extract_data.clicked.connect(self.extract_data)
        self.btn_create_slates.clicked.connect(self.create_slates)

    def make_image_label(self, path):
        # type: (str) -> QtWidgets.QLabel
        """
        Make image label of the thumbnail to add to the table

        Args:
            path: The path of the thumbnail to add

        Returns:
            label: The created label to add to the table
        """
        size = (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)
        label = QtWidgets.QLabel()
        label.setAlignment(QtCore.Qt.AlignCenter)

        # create the pixmap
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            pixmap = QtGui.QPixmap(*size)
            pixmap.fill(QtCore.Qt.lightGray)

        # set the image size on the label
        label.setPixmap(
            pixmap.scaled(*size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        )
        return label

    def select_pdf_dir(self):
        """ Select the PDF directory """
        self.set_line_edit_path(self.le_pdf_dir)

    def select_movie_dir(self):
        """ Select the movie directory """
        self.set_line_edit_path(self.le_movie_dir)

    def select_output_dir(self):
        """ Select the output directory """
        self.set_line_edit_path(self.le_output_dir)

    def set_line_edit_path(self, line_edit):
        # type: (str) -> None
        """
        Select and set the directory to the line edit

        Args:
            line_edit: The line edit widget to set
        """
        sel_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", "",
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        line_edit.setText(sel_path)

    def extract_data(self):
        """
        Find the PDF files and extract the data from them
        """
        # Populate table with data
        pdf_dir = self.le_pdf_dir.text()
        movie_dir = self.le_movie_dir.text()
        self.pdf_data_inst = extract_pdf_data.ExtractData(movie_dir)

        for row_index, pdf_file_name in enumerate(os.listdir(pdf_dir)):
            self.tbw_shots.setRowCount(row_index + 1)

            # get the PDF data
            pdf_path = os.path.join(pdf_dir, pdf_file_name)
            pdf_data = self.pdf_data_inst.get_data_from_pdf(pdf_path)

            # create a QLabel widget and set it in the cell
            lb_thumbnail = self.make_image_label(pdf_data.thumbnail_path)
            self.tbw_shots.setCellWidget(row_index, 0, lb_thumbnail)
            self.tbw_shots.setRowHeight(row_index, THUMBNAIL_HEIGHT)

            # loop through the headers and populate the data
            for column, header in enumerate(self.headers):
                if header == "thumbnail":
                    continue

                # using the header get the value
                value = asdict(pdf_data).get(header, "n/a")

                # get the version number if the previous shot exists in the settings
                if header == "shot_name":
                    pdf_data.version = self.ui_settings.value(value, "n/a")

                # create the table widget item and add it to the table
                item = QtWidgets.QTableWidgetItem(value)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.tbw_shots.setItem(row_index, column, item)

            # add the data to the table widget item
            first_item = self.tbw_shots.item(row_index, 1)
            first_item.setData(QtCore.Qt.UserRole, pdf_data)

    def get_all_data(self):
        data = []
        for row_index in range(self.tbw_shots.rowCount()):
            # get the first item data
            first_item = self.tbw_shots.item(row_index, 1)
            pdf_data = first_item.data(QtCore.Qt.UserRole)

            # update the PDF data with the table information
            res_index = self.headers.index("resolution")
            pdf_data.resolution = self.tbw_shots.item(row_index, res_index).text()

            # update the table version
            version_index = self.headers.index("version")
            pdf_data.version = self.tbw_shots.item(row_index, version_index).text()

            # get the notes and add to the table
            notes_index = self.headers.index("notes")
            pdf_data.notes = self.tbw_shots.item(row_index, notes_index).text()
            data.append(pdf_data)
        return data

    def create_slates(self):
        """
        Get the slate data and create the slates
        """
        output_dir = self.le_output_dir.text()
        data = self.get_all_data()

        # loop through the PDF data and create the slates
        for pdf_data in data:
            self.pdf_data_inst.create_slate(pdf_data, output_dir)
            self.ui_settings.setValue(pdf_data.shot_name, pdf_data.version)

        # save the path in the q-settings
        self.ui_settings.setValue("le_pdf_dir", self.le_pdf_dir.text())
        self.ui_settings.setValue("le_movie_dir", self.le_movie_dir.text())
        self.ui_settings.setValue("le_output_dir", output_dir)

        # display created message
        QtWidgets.QMessageBox.information(self, "Created", "Created slates", QtWidgets.QMessageBox.Ok)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SlateMakerUI()
    window.show()
    sys.exit(app.exec())
