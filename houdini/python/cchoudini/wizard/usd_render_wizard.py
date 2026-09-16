"""
USD Render to Deadline
"""
import hou
from CCPySide import QtCore
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import ShotContextPage, AssetContextPage
from cchoudini.wizard.pages.usd_submit_page import USDRenderProgressPage
from ccgeneral.wizard.pages.deadline_page import DeadlinePage
from cchoudini.wizard.pages.hou_validator_page import HouValidatePage
import cchoudini.wizard.hou_base_wizard as hou_base_wizard


class USDRenderSubmitWizard(hou_base_wizard.HouBaseWizard):
    title = "USD Render Submit"

    def __init__(self, parent=hou.qt.mainWindow(), args=None):
        super().__init__(parent, args=args)
        self.data["deadline_mode"] = True
        self.data["node_type"] = "usdrender_rop"
        self.dl_settings = {"use_pool": "h_batch"}
        self.deadline_only = True

    @property
    def wizard_pages(self):
        """
        List of wizard pages to add
        """
        if self.ctx.is_asset:
            context_page = AssetContextPage
        else:
            context_page = ShotContextPage

        pages = [context_page,
                 HouValidatePage,
                 DeadlinePage,
                 USDRenderProgressPage,
                 CompletePage
                 ]
        return pages


def main(node):
    """
    Launch the usd render submit wizard
    """
    if not USDRenderSubmitWizard.preflight_checks():
        return

    wizard = USDRenderSubmitWizard(args={"node": node})
    hou.session.mainWindow = hou.ui.mainQtWindow()
    wizard.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
