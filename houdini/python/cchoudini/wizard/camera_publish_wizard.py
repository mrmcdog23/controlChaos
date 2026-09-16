""" Publish cameras wizard """
import hou
from CCPySide import QtCore
import cccore.file_env.context as context
import cchoudini.exporter.camera_exporter as camera_exporter
from cchoudini.wizard.pages.camera_assets_page import HoudiniCameraAssetsPage
from cchoudini.wizard.pages.hou_progress_page import HouProgressPage
from ccgeneral.wizard.pages.complete_page import CompletePage
from cchoudini.wizard.hou_base_wizard import HouBaseWizard
from ccgeneral.wizard.pages.context_page import ShotContextPage


class CameraPublishWizard(HouBaseWizard):
    title = "Houdini Camera Publish"

    def __init__(self, parent=hou.qt.mainWindow()):
        super(CameraPublishWizard, self).__init__(parent)
        self.exporter = camera_exporter.CameraExporter()
        self.data["local"] = True

    @property
    def wizard_pages(self):
        """
        List of wizard pages to add

        Returns:
            pages (list[QtWidgets.QWizardPage]): List of wizard pages
        """
        pages = [ShotContextPage,
                 HoudiniCameraAssetsPage,
                 HouProgressPage,
                 CompletePage
                 ]
        return pages

    @staticmethod
    def wip_file_path():
        # type: () -> str
        """
        Get the current wip houdini file path
        """
        return hou.hipFile.name()

    @classmethod
    def run_checks(cls):
        # type: () -> str
        """
        Run checks that are vital before opening the publishing wizard

        Returns:
            Error message if there is one
        """
        ctx = context.Context()
        nodes = hou.selectedNodes()

        message = None
        if not cls.wip_file_path():
            message = "File not saved"

        elif not nodes:
            message = "No node selected!"

        elif not ctx.task:
            message = "Environment not set"
        return message


def main():
    """
    Launch the asset publish wizard
    """
    wizard = CameraPublishWizard()
    hou.session.mainWindow = hou.ui.mainQtWindow()
    wizard.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
