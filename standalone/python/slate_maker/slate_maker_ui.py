""" Extract all text from a PDF file. """
import os
import re
import sys
import extract_pdf_data
import cccore.base_ui as base_ui
from dataclasses import asdict
from CCPySide import QtWidgets, QtCore, QtGui
from ccgeneral.widgets.line_browser import LineBrowser


# constants
CHECKED_INDEX = 0
CHECKED_WIDTH = 0
THUMBNAIL_WIDTH = 250
THUMBNAIL_HEIGHT = 160


class PasteTableWidget(QtWidgets.QTableWidget):
    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.StandardKey.Paste):
            self.paste_to_selection()
        else:
            super().keyPressEvent(event)

    def paste_to_selection(self):
        clipboard = QtWidgets.QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return
        items = self.selectedItems()
        for item in items:
            item.setText(text)


class SlateMakerUI(base_ui.StandaloneWindowBase):
    title = "Slate Maker"
    window_icon = "slate_maker"
    icon_to_widget = {"refresh": "btn_refresh"}

    def __init__(self):
        super().__init__()
        self.headers = [
            " ", "thumbnail", "show_name", "shot_name", "duration",
            "focal_length", "resolution", "version", "notes"
        ]
        self.pdf_data_inst = None
        self.use_last_resolution = str()
        self.shot_to_data = dict()
        self.ui_settings = QtCore.QSettings('controlChaos', 'slate_maker')

        # set the ui size and title
        self.setWindowTitle("Control Chaos Slate Maker")
        self.setMinimumSize(1200, 800)

        # run the setup functions
        self.create_layout()
        self.set_table_attributes()
        self.load_settings()
        self.connect_signals()

    def create_layout(self):
        """
        Create the layout for the slate maker
        """
        # add the line edits
        self.browse_pdf_wdg = LineBrowser(self, "dir", "Select PDF Directory", "", "PDF Directory")
        self.browse_pdf_wdg.label.setMinimumWidth(90)

        # movie folder widget
        self.browse_movie_wdg = LineBrowser(self, "dir", "Select Movie Directory", "", "Movie Directory")
        self.browse_movie_wdg.label.setMinimumWidth(90)

        # output directory widget
        self.browse_output_wdg = LineBrowser(self, "dir", "Select Output Directory", "", "Output Directory")

        # add table to layout
        self.tbw_shots = PasteTableWidget(0, len(self.headers))
        self.lyt_table.addWidget(self.tbw_shots)

        # add all browsers to the widget
        self.lyt_browsers.addWidget(self.browse_pdf_wdg)
        self.lyt_browsers.addWidget(self.browse_movie_wdg)
        self.lyt_output_file.addWidget(self.browse_output_wdg)

    def set_table_attributes(self):
        """
        Set the table heads and width
        """
        self.tbw_shots.setColumnWidth(self.headers.index("thumbnail"), THUMBNAIL_WIDTH)
        self.tbw_shots.setColumnWidth(self.headers.index(" "), CHECKED_WIDTH)
        self.tbw_shots.setHorizontalHeaderLabels(self.headers)
        self.tbw_shots.horizontalHeader().setStretchLastSection(True)
        self.tbw_shots.verticalHeader().setVisible(False)
        self.tbw_shots.setRowCount(0)

    def load_settings(self):
        """
        Load the previous settings to the widgets
        """
        # save the path in the q-settings
        le_pdf_dir = self.ui_settings.value("le_pdf_dir", str())
        self.browse_pdf_wdg.set_file_path(le_pdf_dir)

        # save the path in the q-settings
        le_movie_dir = self.ui_settings.value("le_movie_dir", str())
        self.browse_movie_wdg.set_file_path(le_movie_dir)

        # save the output directory
        le_output_dir = self.ui_settings.value("le_output_dir", str())
        self.browse_output_wdg.set_file_path(le_output_dir)

        # save the latest revision check box
        chk_latest_rev = self.ui_settings.value("chk_latest_rev", 1)
        self.chk_latest_rev.setChecked(int(chk_latest_rev))

        self.use_last_resolution =  self.ui_settings.value("use_last_resolution", str())

    def save_settings(self):
        """
        Save the path in the q-settings
        """
        self.ui_settings.setValue("le_pdf_dir", self.browse_pdf_wdg.file_path)
        self.ui_settings.setValue("le_movie_dir", self.browse_movie_wdg.file_path)
        self.ui_settings.setValue("le_output_dir", self.browse_output_wdg.file_path)
        self.ui_settings.setValue("chk_latest_rev", int(self.chk_latest_rev.isChecked()))

        # get the resolution from the first row
        resolution_index = self.headers.index("resolution")
        resolution = self.tbw_shots.item(0, resolution_index).text()
        self.ui_settings.setValue("use_last_resolution", resolution)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.btn_extract_data.clicked.connect(self.extract_data)
        self.btn_create_slates.clicked.connect(self.create_slates)
        self.chk_all.toggled.connect(self.check_all)
        self.rbn_icon_view.toggled.connect(self.toggle_view)
        self.btn_version_up.clicked.connect(self.version_up)
        self.tbw_shots.model().rowsInserted.connect(self.enable_button)
        self.tbw_shots.model().rowsRemoved.connect(self.enable_button)
        self.tbw_shots.itemChanged.connect(self.enable_button)
        self.btn_refresh.clicked.connect(self.refresh_ui)

    def refresh_ui(self):
        """
        Clear the table and set the button
        """
        self.tbw_shots.clear()
        self.set_table_attributes()
        self.enable_button()

    def version_up(self):
        """
        Version up the slates by one
        """
        version_index = self.headers.index("version")
        for row_index in range(self.tbw_shots.rowCount()):
            item = self.tbw_shots.item(row_index, version_index)
            next_version = int(item.text()) + 1
            item.setText(str(next_version))

    def enable_button(self):
        """
        If there are slates to create enable the main button
        """
        count = self.tbw_shots.rowCount()
        if count:
            # check for any slates that are checked
            for row_index in range(count):
                item = self.tbw_shots.item(row_index, CHECKED_INDEX)
                if not item:
                    continue

                # if one is checked set enabled
                if item.checkState() == QtCore.Qt.Checked:
                    self.btn_create_slates.setEnabled(True)
                    return
        self.btn_create_slates.setEnabled(False)

    def toggle_view(self, icon_view):
        # type: (bool) -> None
        """
        Toggle between the view types
        """
        height = THUMBNAIL_HEIGHT if icon_view else 30
        for row in range(self.tbw_shots.rowCount()):
            self.tbw_shots.setRowHeight(row, height)

    def check_all(self, checked):
        # type: (bool) -> None
        """
        Set the rows check state based on the main checkbox

        Args:
            checked: State to check the rows to
        """
        state = QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked
        for row_index in range(self.tbw_shots.rowCount()):
            item = self.tbw_shots.item(row_index, CHECKED_INDEX)
            item.setCheckState(state)

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

    def create_checkbox_item(self):
        # type: () -> QtWidgets.QTableWidgetItem
        """
        Check a table widget item checkbox
        """
        checkbox_item = QtWidgets.QTableWidgetItem()
        checkbox_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkbox_item.setCheckState(QtCore.Qt.Checked)
        checkbox_item.setTextAlignment(QtCore.Qt.AlignCenter)
        return checkbox_item

    def get_dict_of_shot_to_versions(self, pdf_dir):
        shot_to_versions = dict()
        for row_index, pdf_file_name in enumerate(os.listdir(pdf_dir)):
            # only deal with files
            if not "." in pdf_file_name:
                continue

            # extract the shot name and version number
            re_groups = re.search("(.*)_rev(\d+)_(.*)", pdf_file_name)
            if re_groups:
                shot_name, version_str, _ = re_groups.groups()
                shot_versions = shot_to_versions.get(shot_name, list())
                shot_versions.append(int(version_str))
                shot_to_versions[shot_name] = shot_versions
        return shot_to_versions

    def get_pdf_files_list(self, pdf_dir, latest_rev):
        # type: (str, bool) -> list[str]
        """
        Get a list of pdf files in the directory name given.
        If latest_rev is true then only show the latest revisions

        Args:
            pdf_dir: Directory containing pdf files
            latest_rev: Whether to get all or latest pdfs

        Returns:
            pdf_files_list: List of pdf file paths
        """
        shot_to_versions = self.get_dict_of_shot_to_versions(pdf_dir)
        pdf_files_list = list()
        for row_index, pdf_file_name in enumerate(os.listdir(pdf_dir)):
            # only deal with files
            if not "." in pdf_file_name:
                continue

            if latest_rev:
                re_groups = re.search("(.*)_rev(\d+)_(.*)", pdf_file_name)
                if re_groups:
                    shot_name, version_str, _ = re_groups.groups()
                    shot_versions = shot_to_versions[shot_name]
                    if max(shot_versions) != int(version_str):
                        continue

            pdf_path = os.path.join(pdf_dir, pdf_file_name)
            pdf_files_list.append(pdf_path)
        return pdf_files_list

    def extract_data(self):
        """
        Find the PDF files and extract the data from them
        """
        self.tbw_shots.clear()
        self.set_table_attributes()

        # Populate table with data
        shot_name_index = self.headers.index("shot_name")

        pdf_dir = self.browse_pdf_wdg.file_path
        movie_dir = self.browse_movie_wdg.file_path
        latest_rev = self.chk_latest_rev.isChecked()

        self.pdf_data_inst = extract_pdf_data.ExtractData(movie_dir)
        pdf_files_list = self.get_pdf_files_list(pdf_dir, latest_rev)
        for row_index, pdf_path in enumerate(pdf_files_list):
            # add a new row
            self.tbw_shots.setRowCount(row_index + 1)

            # get the PDF data
            pdf_data = self.pdf_data_inst.get_data_from_pdf(pdf_path)
            pdf_data.resolution = self.use_last_resolution

            # loop through the headers and populate the data
            for column, header in enumerate(self.headers):

                # for the checkbox create a table item
                if header == " ":
                    self.tbw_shots.setItem(row_index, column, self.create_checkbox_item())
                    continue

                # create a QLabel widget and set it in the cell
                if header == "thumbnail":
                    lb_thumbnail = self.make_image_label(pdf_data.thumbnail_path)
                    thumbnail_index = self.headers.index("thumbnail")
                    self.tbw_shots.setCellWidget(row_index, thumbnail_index, lb_thumbnail)
                    self.tbw_shots.setRowHeight(row_index, THUMBNAIL_HEIGHT)
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
            shot_name = self.tbw_shots.item(row_index, shot_name_index).text()
            self.shot_to_data[shot_name] = pdf_data
        self.save_settings()

    def update_pdf_data(self):
        """
        Update the data from the table information
        """
        shot_name_index = self.headers.index("shot_name")
        duration_index = self.headers.index("duration")
        focal_length_index = self.headers.index("focal_length")
        res_index = self.headers.index("resolution")
        version_index = self.headers.index("version")
        notes_index = self.headers.index("notes")

        for row_index in range(self.tbw_shots.rowCount()):
            # get the first item data
            shot_name = self.tbw_shots.item(row_index, shot_name_index).text()
            pdf_data = self.shot_to_data[shot_name]

            # update the PDF data with the table information
            pdf_data.duration = self.tbw_shots.item(row_index, duration_index).text()

            # update the PDF data with the table information
            pdf_data.focal_length = self.tbw_shots.item(row_index, focal_length_index).text()

            # update the PDF data with the table information
            pdf_data.resolution = self.tbw_shots.item(row_index, res_index).text()

            # update the table version
            pdf_data.version = self.tbw_shots.item(row_index, version_index).text()

            # get the notes and add to the table
            pdf_data.notes = self.tbw_shots.item(row_index, notes_index).text()
            self.shot_to_data[shot_name] = pdf_data

    def create_slates(self):
        """
        Get the slate data and create the slates
        """
        self.save_settings()
        self.update_pdf_data()

        output_dir =  self.browse_output_wdg.file_path
        shot_name_index = self.headers.index("shot_name")
        for row_index in range(self.tbw_shots.rowCount()):
            # skip if the row is unchecked
            item = self.tbw_shots.item(row_index, CHECKED_INDEX)
            if item.checkState() != QtCore.Qt.Checked:
                continue
                
            shot_name = self.tbw_shots.item(row_index, shot_name_index).text()
            pdf_data = self.shot_to_data[shot_name]

            # loop through the PDF data and create the slates
            self.pdf_data_inst.create_slate(pdf_data, output_dir)
            self.ui_settings.setValue(pdf_data.shot_name, pdf_data.version)

        # display created message
        QtWidgets.QMessageBox.information(self, "Created", "Created slates", QtWidgets.QMessageBox.Ok)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SlateMakerUI()
    window.show()
    sys.exit(app.exec())
