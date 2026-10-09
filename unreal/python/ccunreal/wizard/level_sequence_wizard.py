""" Publish and render an unreal """
from typing import Any
import unreal as ue
import ccunreal.utils.unreal_utils as unreal_utils
import ccgeneral.wizard.base_wizard as base_wizard
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import ShotContextPage, AssetContextPage
from ccgeneral.wizard.pages.progress_page import ProgressPage
import ccunreal.wizard.exporter.level_sequence_exporter as level_sequence_exporter


class LevelSequenceWizard(base_wizard.BaseWizard):
    title = "Publish Level Sequence"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.exporter = level_sequence_exporter.LevelSequenceExporter()
        self.ls_path = unreal_utils.current_ls_path()
        self.map_path = unreal_utils.current_map_path()
        self.ctx = unreal_utils.get_context_from_path(self.ls_path)

        self.data["local"] = True
        self.data["level_sequence_paths"] = [self.ls_path]
        self.data["map_path"] = self.map_path
        self.data["task_name"] = "previz"
        self.data["use_ffmpeg"] = True

    @property
    def wizard_pages(self):
        # type: () -> list[Any]
        """ Add all the pages to the publishing wizard """
        if self.ctx.is_build:
            context_page = AssetContextPage
        else:
            context_page = ShotContextPage
        pages = [context_page, ProgressPage, CompletePage]
        return pages

    @staticmethod
    def wip_file_path():
        """ The current maya file path """
        return str()


def main():
    """
    Launch the shot publish wizard
    """
    ls_path = unreal_utils.current_ls_path()
    if not ls_path:
        ue.EditorDialog.show_message("No Sequence", "No level sequence open", ue.AppMsgType.OK)
        return
    unreal_utils.launch_unreal_win(LevelSequenceWizard)
