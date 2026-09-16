""" mplayer publish wizard """
import os
import hou
from typing import Optional
from CCPySide import QtCore
import cccore.file_env.context as context
import cchoudini.exporter.mplay_exporter as mplay_exporter
import ccgeneral.wizard.base_wizard as base_wizard
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import ShotContextPage, AssetContextPage
from cchoudini.wizard.pages.hou_progress_page import HouProgressPage
from ccgeneral.wizard.pages.export_type_page import ExportTypePage


class MPlayPublishWizard(base_wizard.BaseWizard):
    title = "MPlay Publish Wizard"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {'subfolder': 'render', 'ext': 'png'}
        self.exporter = mplay_exporter.MPlayExporter()
        self.set_publish_data()

    @staticmethod
    def wip_file_path():
        # type: () -> Optional[str]
        """ Get the current wip file path """
        return os.environ["CURRENT_FILE_PATH"]

    @classmethod
    def run_checks(cls):
        # type: () -> str
        """
        Run checks that are vital before opening the publishing wizard

        Returns:
            True if valid to publish
        """
        ctx = context.Context()
        message = None
        if cls.wip_file_path() == "untitled.hip":
            message = "File not saved"

        elif not ctx.task:
            message = "Environment not set"
        return message

    @property
    def wizard_pages(self):
        """
        List of wizard pages to add

        Returns:
            pages (list[QtWidgets.QWizardPage]): List of wizard pages
        """
        if self.ctx.is_asset:
            context_page = AssetContextPage
        else:
            context_page = ShotContextPage
        pages = [
            context_page,
            ExportTypePage,
            HouProgressPage,
            CompletePage
        ]
        return pages


def main():
    """
    Launch the asset publish wizard
    """
    if not MPlayPublishWizard.preflight_checks():
        return

    wizard = MPlayPublishWizard()
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
