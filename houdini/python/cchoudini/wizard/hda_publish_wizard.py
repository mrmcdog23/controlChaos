""" The hda wizard publisher """
import hou
from CCPySide import QtCore
from cchoudini.wizard.pages.hou_progress_page import HouProgressPage
from ccgeneral.wizard.pages.complete_page import CompletePage
from cchoudini.wizard.pages.hda_context_page import HDAProjectContextPage, \
    HDALibraryContextPage, HDAShowOrGeneralPage
from cchoudini.wizard.pages.hou_thumbnail_page import HouThumbnailPage
import cchoudini.exporter.hda_exporter as hda_exporter
from cchoudini.wizard.hou_base_wizard import HouBaseWizard
import cchoudini.node.hda as hda


class HDAPublishWizard(HouBaseWizard):
    title = "Houdini Publish Asset"

    def __init__(self, parent=hou.qt.mainWindow()):
        super(HDAPublishWizard, self).__init__(parent)
        self.exporter = hda_exporter.HDAExporter()
        self.data["local"] = True
        self.data["category"] = "HDA"

    @property
    def wizard_pages(self):
        """
        List of wizard pages to add

        Returns:
            pages (list[QtWidgets.QWizardPage]): List of wizard pages
        """
        pages = [HDAShowOrGeneralPage,
                 HDAProjectContextPage,
                 HDALibraryContextPage,
                 HouThumbnailPage,
                 HouProgressPage,
                 CompletePage
                 ]
        return pages

    @staticmethod
    def wip_file_path():
        # type: () -> str
        """
        Get the current wip file path
        """
        return hou.hipFile.name()

    @classmethod
    def run_checks(cls):
        # type: () -> str
        """
        Run checks that are vital before opening the publishing wizard

        Returns:
            message: The error message if there is one
        """
        nodes = hou.selectedNodes()

        message = None
        if not cls.wip_file_path():
            message = "File not saved"

        elif not nodes:
            message = "No node selected!"

        if nodes:
            hda_inst = hda.HDA(nodes[0])
            if hda_inst.is_published_digital_asset:
                message = "HDA is published. Make local"

        return message


def main():
    """
    Launch the asset publish wizard
    """
    if not HDAPublishWizard.preflight_checks():
        return

    wizard = HDAPublishWizard()
    hou.session.mainWindow = hou.ui.mainQtWindow()
    wizard.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
