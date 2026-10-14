""" Publish and render an unreal """
from typing import Any
import unreal as ue
import cccore.utils.file_utils as file_utils
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.utils.api_wrap as api_wrap
import ccgeneral.wizard.base_wizard as base_wizard
import cccore.file_env.context as context
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import ShotContextPage
from ccunreal.wizard.pages.ls_context_page import LevelSequenceContextPage
from ccgeneral.wizard.pages.progress_page import ProgressPage
import ccunreal.wizard.exporter.level_sequence_exporter as level_sequence_exporter


class LevelSequenceWizard(base_wizard.BaseWizard):
    title = "Publish Level Sequence"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.exporter = level_sequence_exporter.LevelSequenceExporter()

        ls_path = unreal_utils.current_ls_path()
        ls = ue.load_asset(ls_path)
        metadata_dict = api_wrap.get_metadata_tag_values(ls)

        self.ctx = context.Context(overrides=metadata_dict)
        self.data["local"] = True
        self.data["ls_path"] = ls_path
        self.data["map_path"] = unreal_utils.current_map_path()
        self.data["thumbnail_path"] = file_utils.get_temp_file_path(
            f"{self.ctx.shot}_thumbnail.png")

    @property
    def wizard_pages(self):
        # type: () -> list[Any]
        """ Add all the pages to the publishing wizard """
        pages = [LevelSequenceContextPage, ProgressPage, CompletePage]
        return pages


def main():
    """
    Launch the shot publish wizard
    """
    ls_path = unreal_utils.current_ls_path()
    if not ls_path:
        ue.EditorDialog.show_message("No Sequence", "No level sequence open", ue.AppMsgType.OK)
        return
    unreal_utils.launch_unreal_win(LevelSequenceWizard)
