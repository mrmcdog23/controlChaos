""" Maya specific progress page """
import re
import maya.cmds as cmds
from typing import Optional
from ccgeneral.wizard.pages.progress_page import ProgressPage


class MayaProgressPage(ProgressPage):
    title = "Progress Page"
    subtitle = "Exporting the shot assets"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.found_standard_error = False

    def save_file(self):
        """
        Save the current file
        """
        filename = cmds.file(q=True, sn=True)
        cmds.file(rename=filename)
        cmds.file(save=True, type='mayaAscii')

    def start_export_process(self, arg_list, output_path=None):
        # type: (list[str], Optional[str]) -> None
        """
        Start the maya export process

        Args:
            arg_list: List of export arguments
            output_path: Path of the log file
        """
        self.progress_wdg.start_maya_process(arg_list, output_path=output_path)

    def add_parent_message(self, message):
        # type: (str) -> None
        """
        Appends a message to the text widget as a new line
        to show the project text

        Args:
            message: Additional text to display
        """
        # if the standard error is found no need for error checking as its last
        if "Exception ignored in: <function MCallbackIdWrapper.__del__ at " in message:
            self.found_standard_error = True

        if self.found_standard_error:
            return

        # if the standard error not found then through the error if found
        if 'Traceback (most recent call last):' in message:
            self.page_errored = True


class AnimProgressPage(MayaProgressPage):
    title = "Shot Progress Page"
    subtitle = "Shot Publishing the version"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_progress = 0

    def add_message(self, message):
        # type: (str) -> None
        """
        Check for alembic cache progres which is a single digit

        Args:
            message: Progress message
        """
        alembic_progress = re.search("(.*)\n", message)
        if alembic_progress and alembic_progress.group(1).isdigit():

            # get the progress value and divide it by 10 for a better value
            progress_value = int(alembic_progress.group(1))
            new_progress = int(progress_value / 10)

            # if the new value is more than the last increment
            if new_progress != self.current_progress:
                self.current_progress = new_progress
                self.progress_wdg.add_to_progress(1)
            return

        super(AnimProgressPage, self).add_message(message)

    def save_file(self):
        """
        Save the current file
        """
        pass