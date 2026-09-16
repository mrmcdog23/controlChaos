""" Houdini specific progress page """
from typing import Optional
from ccgeneral.wizard.pages.progress_page import ProgressPage


class HouProgressPage(ProgressPage):
    title = "Houdini Progress Page"
    subtitle = "Publishing the version"

    def __init__(self, parent=None):
        super(HouProgressPage, self).__init__(parent)

    def save_file(self):
        pass

    def start_export_process(self, arg_list, output_path=None):
        # type: (list[str], Optional[str]) -> None
        """
        Run the houdini function in batch mode

        Args:
            arg_list: Command line arguments
            output_path: Record to process output file path
        """
        self.wizard().logger.info(arg_list)
        self.progress_wdg.start_houdini_process(arg_list, output_path=output_path)
