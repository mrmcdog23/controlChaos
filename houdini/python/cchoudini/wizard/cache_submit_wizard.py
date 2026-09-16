"""
Arnold submitter to Deadline
"""
import hou
from CCPySide import QtCore
import cccore.file_env.context as context
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.publish_cache_page import PublishCachePage
from ccgeneral.wizard.pages.context_page import ShotContextPage, AssetContextPage
from ccgeneral.wizard.pages.deadline_page import DeadlinePage
from cchoudini.wizard.pages.cache.cache_progress_page import CacheProgressPage
from cchoudini.wizard.pages.hou_validator_page import HouValidatePage
import cchoudini.wizard.hou_base_wizard as hou_base_wizard


class CacheSubmitWizard(hou_base_wizard.HouBaseWizard):
    title = "Cache Deadline Submit"

    def __init__(self, parent=hou.qt.mainWindow(), args=None):
        super(CacheSubmitWizard, self).__init__(parent, args=args)
        self.deadline_only = True
        self.data["node_type"] = "cccache"
        self.data["publish"] = True
        self.set_deadline_settings()

    def set_deadline_settings(self):
        """
        Set the deadline settings
        """
        is_abc = self.node.parm("cache_type").eval() == 2
        is_simulation = self.node.parm("cachesim").eval() == 1

        # if it is an alembic cache or a simulation then one chunk
        if is_abc or (not is_abc and is_simulation):
            one_frame_per_task = True
        else:
            one_frame_per_task = False
        self.dl_settings = {"use_pool": "h_batch", "one_frame_per_task": one_frame_per_task}

    @classmethod
    def run_checks(cls):
        # type: () -> str
        """
        Run checks that are vital before opening the publishing wizard

        Returns:
            message: Text is checks fail
        """
        message = None
        if not cls.wip_file_path():
            message = "File not saved"

        elif not context.Context().task:
            message = "Environment not set"
        return message

    @property
    def wizard_pages(self):
        """
        List of wizard pages to add

        Returns:
            pages (list[QtWidgets.QWizardPage]): List of wizard pages
        """
        if self.ctx.is_asset:
            context_page = AssetContextPage
        else:
            context_page = ShotContextPage
        pages = [PublishCachePage,
                 context_page,
                 HouValidatePage,
                 DeadlinePage,
                 CacheProgressPage,
                 CompletePage
                 ]
        return pages


def main(cc_cache_node):
    """
    Launch the asset publish wizard
    """
    if not CacheSubmitWizard.preflight_checks():
        return
    wizard = CacheSubmitWizard(args={"node": cc_cache_node})
    hou.session.mainWindow = hou.ui.mainQtWindow()
    wizard.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
