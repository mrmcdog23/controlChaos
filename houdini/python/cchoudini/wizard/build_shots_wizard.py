

""" The build shot wizard """
import hou
from CCPySide import QtCore
import cccore.core_constants as core_constants
import cchoudini.exporter.build_shots_exporter as build_shots_exporter
from cchoudini.wizard.pages.switch_shots_options import SwitchShotOptionsPage
from cchoudini.wizard.pages.build_shot_progress_page import BuildShotProgressPage
from ccgeneral.wizard.pages.complete_page import CompletePage
from cchoudini.wizard.hou_base_wizard import HouBaseWizard


class BuildShotsWizard(HouBaseWizard):
    title = "Build Houdini Shots"

    def __init__(self, parent=hou.qt.mainWindow(), args=None):
        super(BuildShotsWizard, self).__init__(parent)
        self.exporter = build_shots_exporter.BuildShotsExporter()
        self.output_subfolder = "build_shot"
        self.data.update(args)
        self.data["deadline_mode"] = True

    @property
    def wizard_pages(self):
        """
        List of wizard pages to add

        Returns:
            pages (list[QtWidgets.QWizardPage]): List of wizard pages
        """
        pages = [
            SwitchShotOptionsPage,
            BuildShotProgressPage,
            CompletePage
        ]
        return pages


def main(args):
    """
    Launch the asset publish wizard
    """
    wizard = BuildShotsWizard(args=args)
    hou.session.mainWindow = hou.ui.mainQtWindow()
    wizard.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
