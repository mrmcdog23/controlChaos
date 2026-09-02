""" Base progress page for wizard processes """
import os
import re
import inspect
import traceback
import ccgeneral.widgets.progress_widget as progress_widget
import cccore.core_constants as core_constants
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
from CCPySide import QtCore, QtWidgets
from ccgeneral.wizard.pages.base_page import BasePublishPage


class ProgressPage(BasePublishPage):
    title = "Progress Page"
    subtitle = "Publishing the version"

    def __init__(self, parent=None):
        super(ProgressPage, self).__init__(parent)
        self.proc = None
        self.progress_wdg = None
        self.published = False
        self.write_file = None
        self.job_ids = list()
        self.job_types = list()
        self.metadata_file_path = str()
        self.output_file_path = str()
        self.page_errored = False
        self.logger = cc_logging.cc_logger()

    def export(self):
        """
        Run the export process via its correct mode
        """
        if self.data.get("local", False):
            self.local_export()
        elif self.data.get("deadline_mode", False):
            self.deadline_export()
        else:
            self.batch_export()

    def local_export(self):
        """
        Export locally by adding the wizard variables to the
        exporter variables class and exporting. If it fails then
        set red in the message
        """
        try:
            exporter = self.exporter
            exporter.ui = self
            exporter.data = self.data
            exporter.export()

        except Exception as e:
            traceback.print_exc()
            self.add_message('<font color=red>{0}</font>'.format(str(e)))
            self.add_message('<i>{0}</i>'.format("<br>\n".join(str(traceback.format_exc()).split("\n"))))
            return

    def batch_export(self):
        """
        Export the asset version in batch mode
        """
        self.set_output_paths()
        if self.proc is not None:
            return

        self.save_data_to_json()
        arg_list = [self.python_file_path, self.metadata_file_path]
        self.start_export_process(arg_list, self.output_file_path)

    def deadline_export(self):
        """
        Export locally by adding the wizard variables to the
        exporter variables class and exporting. If it fails then
        set red in the message
        """
        pass

    def save_file(self):
        """ Save the current file """
        pass

    def start_export_process(self, arg_list, output_path):
        # type: (list[str], str) -> None
        """ Run the subprocess function in batch mode """
        pass

    def add_submit_data(self, job_id, job_type):
        # type: (str, str) -> None
        """
        Add to the submit data and job ids list

        Args:
            job_id: The job id to add
            job_type: Job type to add
        """
        self.job_types.append(job_type)
        self.job_ids.append(job_id)

    def isComplete(self):
        """
        Do not go to next page
        """
        if self.published:
            self.wizard().next()
        return self.published

    def nextId(self):
        """
        Will always return the final page last but not least
        """
        return self.wizard().FINAL_PAGE

    def set_value(self, value):
        # type: (int) -> None
        """
        Set the percentage value on the progress bar

        Args:
            value: Percentage to set the progress bar to
        """
        self.progress_wdg.progress_bar.setValue(value)

    def update_progress(self, percent, msg):
        # type: (int, str) -> None
        """
        Update progress on local export

        Args:
            percent: current percent done
            msg: Display message
        """
        if percent >= 0:
            self.set_value(percent)
        if msg:
            self.add_message(msg)

    def initializePage(self):
        # type: () -> bool
        """
        Last minute validation

        Return:
             False if the next page
        """
        self.save_file()
        self.progress_wdg = progress_widget.ProgressWidget(self)
        self.main_layout.addWidget(self.progress_wdg)
        self.pw.setButtonLayout([QtWidgets.QWizard.Stretch,
                                 QtWidgets.QWizard.CancelButton]
                                )
        QtCore.QTimer.singleShot(100, self.export)
        return True

    def add_message(self, message):
        # type: (str) -> None
        """
        Appends a message to the text widget as a new line
        to show the project text

        Args:
            message: Additional text to display
        """
        self.progress_wdg.add_widget_message(message)

    def add_parent_message(self, message):
        # type: (str) -> None
        """
        Appends a message to the text widget as a new line
        to show the project text

        Args:
            message: Additional text to display
        """
        if core_constants.VERSION_TEXT in message:
            regex_txt = "{0} (.*)".format(core_constants.VERSION_TEXT)
            asset_version_id = re.search(regex_txt, message).group(1)
            asset_version_id_cleaned = re.sub(r'[^a-zA-Z0-9-]', '', asset_version_id)
            self.wizard().asset_version_id = asset_version_id_cleaned

    def local_progress(self, progress_num):
        # type: (int) -> None
        """
        Add to the progress widget for local exports

        Args:
            progress_num: The amount of progress to add
        """
        self.progress_wdg.add_to_progress(progress_num)

    @property
    def python_file_path(self):
        # type: () -> str
        """ Get the exporter file path """
        path = inspect.getfile(self.exporter.__class__)
        file_name, _ = os.path.splitext(path)
        file_path = f"{file_name}.py"
        file_path_clean = file_path.replace("\\", "/")
        return file_path_clean

    def save_data_to_json(self):
        """
        Save the data to a json file to run as an arg
        """
        # get the metadata file path
        self.data["metadata_file_path"] = self.metadata_file_path
        file_utils.write_file(self.metadata_file_path, self.data)

    def process_finished(self):
        """
        When the process finishes go to the next page
        """
        if self.page_errored:
            self.progress_wdg.set_errored()
            return

        self.data["job_types"] = self.job_types
        self.progress_wdg.complete_progress()
        self.published = True
        self.completeChanged.emit()

    def set_output_paths(self):
        """
        Get the output text file path
        """
        # get the root folder to export to. It is an app use
        output_dir = file_utils.join_file_names(os.environ["TEMP"], "maya_export")
        file_utils.create_directory(output_dir)

        # get the file name either from the wip file or the project name
        log_prefix = file_utils.get_file_name(self.data["log_prefix"])

        # set the temp file paths
        self.metadata_file_path = file_utils.temp_file_path(
            log_prefix, "json", directory=output_dir)
        self.output_file_path = self.metadata_file_path.replace("json", "txt")


class PythonProgressPage(ProgressPage):

    def start_export_process(self, arg_list, output_path=None):
        # type: (list[str], Optional[str]) -> None
        """
        Start the maya export process

        Args:
            arg_list: List of export arguments
            output_path: Path of the log file
        """
        self.progress_wdg.start_python_process(arg_list, output_path=output_path)