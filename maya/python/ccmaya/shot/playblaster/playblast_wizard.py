""" cc playblast tool to publish to ftrack """
from typing import Any
import maya.cmds as cmds
import ccmaya.utils.maya_utils as maya_utils
from ccmaya.shot.playblaster.playblast_options_page import PlayblastOptionsPage
from ccmaya.shot.playblaster.preview_page import PreviewPage
from ccmaya.wizard.pages.maya_progress_page import AnimProgressPage
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import ShotContextPage
import ccgeneral.wizard.base_wizard as base_wizard
import ccmaya.wizard.exporter.shot_exporter as shot_exporter


class PlayblastWizard(base_wizard.BaseWizard):
    title = "Playblast Wizard"
    use_cc_ss = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.exporter = shot_exporter.ShotExporter()
        self.dl_settings = {
            "use_pool": "python",
            "one_frame_per_task": True,
            "priority": 50,
            "local_default": True
        }
        self.set_publish_data()

    @property
    def wizard_pages(self):
        # type: () -> list[Any]
        """ List of wizard pages to add """
        pages = [PlayblastOptionsPage,
                 PreviewPage,
                 ShotContextPage,
                 AnimProgressPage,
                 CompletePage
                 ]
        return pages

    @staticmethod
    def wip_file_path():
        # type: () -> str
        """ The current maya file path """
        return cmds.file(q=True, sn=True)

    @staticmethod
    def entity_type():
        # type: () -> str
        """ The entity type so export to check against """
        return "shot"


def main():
    """
    Launch the asset publish wizard
    """
    message = PlayblastWizard.preflight_checks()
    if not message:
        return
    maya_window = maya_utils.get_maya_main_window()
    wizard = PlayblastWizard(parent=maya_window)
    wizard.show()
    wizard.exec_()
