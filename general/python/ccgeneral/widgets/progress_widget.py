""" Progress widget for updating a process with text """
import re
from typing import Optional
from CCPySide import QtCore, QtGui, QtWidgets
import cccore.base_ui as base_ui
import cccore.app_starter as app_starter
import cccore.utils.cc_logging as cc_logging
import cccore.core_constants as core_constants


class ProgressWidget(base_ui.WidgetBase):
    def __init__(self, parent):
        super(ProgressWidget, self).__init__(parent)
        self.write_file = None
        self.asset_version_id = None
        self.parent = parent
        self.logger = cc_logging.cc_logger()

        # create the q-process
        self.proc = QtCore.QProcess()
        self.proc.readyReadStandardOutput.connect(self.handle_stdout)
        self.proc.readyReadStandardError.connect(self.handle_stderr)
        self.proc.stateChanged.connect(self.handle_state)
        self.proc.finished.connect(self.process_finished)

    def add_widget_message(self, message):
        # type: (str) -> None
        """
        All output messages head and extract relevant information

        Args:
            message: Text to add to the parent widget
        """
        progress_msg = core_constants.PROGRESS_TEXT in message
        maximum_msg = core_constants.MAXIMUM_VALUE_TEXT in message

        if progress_msg:
            regex_txt = "{0} (.*)".format(core_constants.PROGRESS_TEXT)
            progress_num = re.search(regex_txt, message).group(1)
            self.add_to_progress(progress_num)

        if maximum_msg:
            regex_txt = "{0} (.*)".format(core_constants.MAXIMUM_VALUE_TEXT)
            maximum_value = re.search(regex_txt, message).group(1)
            self.set_maximum_progress(int(maximum_value))

        else:
            self.text_edit.append(message)
            QtWidgets.QApplication.processEvents()
        # add to the parent window message ui
        try:
            self.parent.add_parent_message(message)
        except AttributeError:
            pass

    def complete_progress_bar(self):
        """
        Complete the progress bar
        """
        self.progress_bar.setValue(100)

    def add_to_progress(self, value):
        # type: (int) -> None
        """
        Add progress to the progress bar

        Args:
            value: Value to add to the progress bar
        """
        current = self.progress_bar.value()
        self.progress_bar.setValue(int(value) + current)

        # if at maximum then next page
        if self.progress_bar.value() >= self.progress_bar.maximum():
            self.process_finished()

    def set_maximum_progress(self, maximum_value):
        # type: (int) -> None
        """
        Set the maximum value of the progress bar

        Args:
            maximum_value: Maximum value of the progress bar
        """
        self.progress_bar.setMaximum(int(maximum_value))

    def complete_progress(self):
        """
        Set the progress bar to be the maximum value
        """
        maximum = self.progress_bar.maximum()
        self.progress_bar.setValue(maximum)

    def handle_state(self, state):
        # type: (QtCore.QProcess) -> None
        """
        Update the message when the state changes

        Args:
            state: Current process state
        """
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.add_widget_message(state_name)

    def handle_stderr(self):
        """
        Connect the error to the text edit
        """
        data = self.proc.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        if self.write_file:
            self.write_file.write(stderr)
        self.add_widget_message(stderr)

    def handle_stdout(self):
        """
        Connect the output to the text edit
        """
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        if self.write_file:
            self.write_file.write(stdout)
        self.add_widget_message(stdout)

    def process_finished(self):
        """
        When the process finishes go to the next page
        """
        if not self.proc:
            return
        self.add_widget_message("Process finished.")
        if self.write_file:
            self.write_file.close()
        try:
            self.parent.process_finished()
        except AttributeError:
            pass
        self.proc = None

    def start_process(self, exe_path, arg_list, output_path=None):
        # type: (str, list[str], Optional[str]) -> None
        """
        Start a QtCore.QProcess

        Args:
            exe_path: Path to the .exe file
            arg_list: Command line arguments
            output_path: Log output path as .txt file
        """
        if output_path:
            self.write_file = open(output_path, 'w')
            self.logger.info(f"Output Path: {output_path}")
        self.logger.info(f"{exe_path} {arg_list}")
        self.proc.setProgram(exe_path)
        self.proc.setArguments(arg_list)
        self.proc.start()

    def start_python_process(self, arg_list, output_path=None):
        # type: (list[str], Optional[str]) -> None
        """
        Start a python process

        Args:
            arg_list: Command line arguments
            output_path: Log output path as .txt file
        """
        self.start_process(core_constants.PYTHON_EXE, arg_list, output_path)

    def start_maya_process(self, arg_list, output_path=None):
        # type: (list[str], Optional[str]) -> None
        """
        Start a maya process

        Args:
            arg_list: Command line arguments
            output_path: Log output path as .txt file
        """
        maya_py_exe = app_starter.MayaPyApp().exe_path
        self.start_process(maya_py_exe, arg_list, output_path)

    def start_houdini_process(self, arg_list, output_path=None):
        # type: (list[str], Optional[str]) -> None
        """
        Start a houdini process

        Args:
            arg_list: Command line arguments
            output_path: Log output path as .txt file
        """
        houdini_py_exe = app_starter.HythonApp().exe_path
        self.start_process(houdini_py_exe, arg_list, output_path)

    def start_nuke_process(self, arg_list, output_path=None):
        # type: (list[str], Optional[str]) -> None
        """
        Start a nuke process

        Args:
            arg_list: Command line arguments
            output_path: Log output path as .txt file
        """
        nuke_exe = app_starter.NukeApp().exe_path
        arg_list.insert(0, "-t")
        self.start_process(nuke_exe, arg_list, output_path)

    def set_font_size(self, font_size):
        # type: (int) -> None
        """
        Set the font size of the output text
        """
        font = QtGui.QFont()
        font.setPointSize(font_size)
        self.text_edit.setFont(font)

    def add_text(self, message):
        # type: (str) -> None
        """
        Add text to the text edit

        Args:
            message: The text to display
        """
        self.text_edit.append(message)

    def set_errored(self):
        """
        Set the stylesheet_to_red
        """
        self.progress_bar.setStyleSheet(
            "QProgressBar::chunk {background-color: red}"
            "QProgressBar {color: red}"
        )
        self.text_edit.setStyleSheet("color: red")


