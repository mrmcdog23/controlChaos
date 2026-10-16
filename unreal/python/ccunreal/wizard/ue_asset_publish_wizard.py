""" Wizard for publishing assets """
import unreal as ue
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import AssetCmbContextPage
import ccgeneral.wizard.base_wizard as base_wizard
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.wizard.exporter.ue_asset_exporter as ue_asset_exporter


class UEAssetWizard(base_wizard.BaseWizard):
    title = "Unreal Asset Publisher"

    def __init__(self, parent=None):
        super(UEAssetWizard, self).__init__(parent)
        self.exporter = ue_asset_exporter.UEAssetExporter()

    @staticmethod
    def entity_type():
        # type: () -> str
        """ The entity type so export to check against """
        return "asset"

    @property
    def wizard_pages(self):
        """
        List of wizard pages to add

        Returns:
            pages (list[QtWidgets.QWizardPage]): List of wizard pages
        """
        pages = [
            AssetCmbContextPage,
            CompletePage
        ]
        return pages


def main():
    """
    Launch the shot publish wizard
    """
    selected = ue.EditorUtilityLibrary.get_selected_assets()
    if not selected:
        ue.EditorDialog.show_message("No Selection", "No selected assets", ue.AppMsgType.OK)
        return
    unreal_utils.launch_unreal_win(UEAssetWizard)
