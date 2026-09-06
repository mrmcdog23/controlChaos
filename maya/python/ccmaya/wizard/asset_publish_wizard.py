""" Wizard for publishing assets """
import maya.cmds as cmds
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.maya_constants as maya_constants
import ccmaya.wizard.exporter.asset_exporter as asset_exporter
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import AssetContextPage
from ccmaya.wizard.pages.maya_thumbnail_page import MayaThumbnailPage
from ccmaya.wizard.pages.maya_progress_page import MayaProgressPage
from ccmaya.wizard.pages.maya_validator_page import MayaValidatePage
from ccmaya.wizard.maya_base_wizard import MayaBaseWizard


class AssetWizard(MayaBaseWizard):
    title = "Asset Publisher"

    def __init__(self, parent=None):
        super(AssetWizard, self).__init__(parent)
        self.qt_model_widget = None
        self.exporter = asset_exporter.AssetExporter()

    @staticmethod
    def entity_type():
        # type: () -> str
        """ The entity type so export to check against """
        return "build"

    @property
    def wizard_pages(self):
        """
        List of wizard pages to add

        Returns:
            pages (list[QtWidgets.QWizardPage]): List of wizard pages
        """
        pages = [AssetContextPage,
                 MayaValidatePage,
                 MayaThumbnailPage,
                 MayaProgressPage,
                 CompletePage
                 ]
        return pages

    @classmethod
    def run_checks(cls):
        # type: () -> str
        """
        Run checks that are vital before opening the publishing wizard

        Returns:
            True if valid to publish
        """
        message = super(AssetWizard, cls).run_checks()
        if not maya_utils.get_asset_top_node():
            group_names = ', '.join(maya_constants.GRP_NAMES)
            message = f'Need a group named: {group_names}'
        return message



def main():
    """
    Launch the asset publish wizard
    """
    message = AssetWizard.preflight_checks()
    if not message:
        return
    maya_utils.launch_wizard(AssetWizard)
