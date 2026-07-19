""" Maya shot publish wizard """
from typing import Any
import maya.cmds as cmds
import ccgeneral.wizard.base_wizard as base_wizard
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.wizard.exporter.shot_exporter as shot_exporter
from ccmaya.wizard.pages.maya_progress_page import AnimProgressPage
from ccmaya.wizard.pages.maya_validator_page import MayaValidatePage
from ccmaya.wizard.pages.scene_assets_page import MayaSceneAssetsPage
from ccgeneral.wizard.pages.complete_page import CompletePage


class ShotExportWizard(base_wizard.BaseWizard):
    title = "Shot Export"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.exporter = shot_exporter.ShotExporter()
        self.set_publish_data()

    @property
    def wizard_pages(self):
        # type: () -> list[Any]
        """ List of wizard pages to add """
        pages = [MayaValidatePage,
                 MayaSceneAssetsPage,
                 AnimProgressPage,
                 CompletePage
                 ]
        return pages

    @staticmethod
    def wip_file_path():
        """ The current maya file path """
        return cmds.file(q=True, sn=True)


def main():
    """
    Launch the asset publish wizard
    """
    message = ShotExportWizard.preflight_checks()
    if not message:
        return
    maya_utils.launch_wizard(ShotExportWizard)
