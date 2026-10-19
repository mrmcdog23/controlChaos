""" Publish and render an unreal """
from typing import Any
import unreal as ue
import cccore.utils.file_utils as file_utils
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.utils.api_wrap as api_wrap
import ccgeneral.wizard.base_wizard as base_wizard
import cccore.file_env.context as context
import cccore.file_env.context_utils as context_utils
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccunreal.wizard.pages.ls_context_page import LevelSequenceContextPage
from ccgeneral.wizard.pages.progress_page import ProgressPage
import ccunreal.wizard.exporter.level_sequence_exporter as level_sequence_exporter


class LevelSequenceWizard(base_wizard.BaseWizard):
    title = "Publish Level Sequence"

    def __init__(self, parent=None):
        super().__init__(parent)

        ls_path = unreal_utils.current_ls_path()
        usd_stage_path = self.get_open_usd_stage_path()
        if usd_stage_path:
            self.exporter = level_sequence_exporter.USDLevelSequenceExporter()
            self.ctx = context_utils.get_context_from_path(usd_stage_path)
        else:
            self.exporter = level_sequence_exporter.LevelSequenceExporter()
            ls = ue.load_asset(ls_path)
            metadata_dict = api_wrap.get_metadata_tag_values(ls)
            self.ctx = context.Context(overrides=metadata_dict)

        self.data["local"] = True
        self.data["ls_path"] = ls_path
        self.data["usd_stage_path"] = usd_stage_path
        self.data["map_path"] = unreal_utils.current_map_path()
        self.data["thumbnail_path"] = file_utils.get_temp_file_path(
            f"{self.ctx.shot}_thumbnail.png")

    @property
    def wizard_pages(self):
        # type: () -> list[Any]
        """ Add all the pages to the publishing wizard """
        pages = [LevelSequenceContextPage, ProgressPage, CompletePage]
        return pages

    def get_open_usd_stage_path(self):
        actor_sub = ue.get_editor_subsystem(ue.EditorActorSubsystem)

        # Prefer a selected USD Stage Actor, otherwise any in the level
        stage_actors = [a for a in actor_sub.get_selected_level_actors()
                        if isinstance(a, ue.UsdStageActor)]
        if not stage_actors:
            stage_actors = [a for a in actor_sub.get_all_level_actors()
                            if isinstance(a, ue.UsdStageActor)]
        if not stage_actors:
            return None

        path = stage_actors[0].get_editor_property("root_layer").file_path
        return ue.Paths.convert_relative_path_to_full(path) if path else None


def main():
    """
    Launch the shot publish wizard
    """
    ls_path = unreal_utils.current_ls_path()
    if not ls_path:
        ue.EditorDialog.show_message("No Sequence", "No level sequence open", ue.AppMsgType.OK)
        return
    unreal_utils.launch_unreal_win(LevelSequenceWizard)

