"""
Arnold submitter to Deadline
"""
import hou
from CCPySide import QtCore
from typing import Any
from ccgeneral.wizard.pages.deadline_page import DeadlinePage
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import ShotContextPage, AssetContextPage
from cchoudini.wizard.pages.cache.cache_publish_progress_page import CachePublishProgressPage
import cchoudini.wizard.hou_base_wizard as hou_base_wizard
import cccore.file_env.context_utils as context_utils


class PublishCacheWizard(hou_base_wizard.HouBaseWizard):
    title = "Publish Cache Submit"

    def __init__(self, parent=hou.qt.mainWindow(), args=None):
        super().__init__(parent, args=args)
        self.dl_settings = {"use_pool": "python", "one_frame_per_task": True}

        # use the path of publish context
        cc_cache_node = args["node"]
        output_path = cc_cache_node.parm("output_path").evalAsString()
        self.ctx = context_utils.get_context_from_path(output_path)
        self.deadline_only = output_path.endswith(".abc")

    @property
    def wizard_pages(self):
        # type: () -> list[Any]
        """ List of wizard pages to add """
        if self.ctx.is_asset:
            context_page = AssetContextPage
        else:
            context_page = ShotContextPage
        pages = [context_page,
                 DeadlinePage,
                 CachePublishProgressPage,
                 CompletePage
                 ]
        return pages


def main(cc_cache_node):
    """
    Launch the asset publish wizard
    """
    wizard = PublishCacheWizard(args={"node": cc_cache_node})
    hou.session.mainWindow = hou.ui.mainQtWindow()
    wizard.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
