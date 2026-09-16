""" The hda wizard publisher """
import hou
from CCPySide import QtCore
from cchoudini.wizard.pages.hou_progress_page import HouProgressPage
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import AssetContextPage
from cchoudini.wizard.pages.hou_thumbnail_page import HouThumbnailPage
import cchoudini.exporter.fbx_exporter as fbx_exporter
from cchoudini.wizard.hou_base_wizard import HouBaseWizard
from typing import Any


class FBXPublishWizard(HouBaseWizard):
    title = "FBX Publish Asset"

    def __init__(self, parent=hou.qt.mainWindow()):
        super().__init__(parent)
        self.exporter = fbx_exporter.FBXExporter()
        self.data["local"] = True
        self.data["category"] = "Scene"
        self.data["node_paths"] = self.node_paths

    @property
    def wizard_pages(self):
        # type: () -> list[Any]
        """
        List of wizard pages to add

        Returns:
            pages: List of wizard pages
        """
        pages = [AssetContextPage,
                 HouThumbnailPage,
                 HouProgressPage,
                 CompletePage
                 ]
        return pages

    @property
    def node_paths(self):
        # type: () -> list[str]
        """ List of the selected nodes paths """
        return [node.path() for node in self.selected_nodes]

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
        return message


def main():
    """
    Launch the asset publish wizard
    """
    if not FBXPublishWizard.preflight_checks():
        return

    wizard = FBXPublishWizard()
    hou.session.mainWindow = hou.ui.mainQtWindow()
    wizard.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
