""" Arnold submitter to Deadline """
import hou
from typing import Any
from CCPySide import QtCore
from cchoudini.wizard.pages.hou_validator_page import HouValidatePage
from cchoudini.wizard.pages.render.arnold_progress_page import ArnoldProgressPage
from cchoudini.wizard.pages.render.mantra_progress_page import MantraProgressPage
from ccgeneral.wizard.pages.complete_page import CompletePage
from ccgeneral.wizard.pages.context_page import ShotContextPage, AssetContextPage
from cchoudini.wizard.task_pages.render_deadline_page import RenderDeadlinePage
from cchoudini.wizard.pages.hou_publish_renders_page import HouPublishRenderRendersPage
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.exporter.ass_exporter as ass_exporter
import cchoudini.wizard.hou_base_wizard as hou_base_wizard


class RenderSubmitWizard(hou_base_wizard.HouBaseWizard):
    title = "Deadline Submit"

    def __init__(self, parent=hou.qt.mainWindow(), args=None):
        self.deadline_node = args.get("node")
        super(RenderSubmitWizard, self).__init__(parent, args=args)
        self.exporter = ass_exporter.AssExporter()
        self.output_subfolder = "arnold_render"
        self.data["deadline_mode"] = True
        self.data["node_type"] = "ccsubmit"
        self.dl_settings = {"use_pool": "houdini"}
        self.deadline_only = True

    @property
    def render_progress_page(self):
        # type: () -> Any
        """ The progress page based on the render type """
        if not self.deadline_node:
            return ArnoldProgressPage

        if hou_utils.input_nodes_of_type(self.deadline_node, ["mantra", "ifd"]):
            return MantraProgressPage
        else:
            return ArnoldProgressPage

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

        pages = [
            HouValidatePage,
            context_page,
            HouPublishRenderRendersPage,
            RenderDeadlinePage,
            self.render_progress_page,
            CompletePage
        ]
        return pages


def main(node=None):
    """
    Launch the asset publish wizard
    """
    if not RenderSubmitWizard.preflight_checks():
        return

    wizard = RenderSubmitWizard(args={"node": node})
    hou.session.mainWindow = hou.ui.mainQtWindow()
    wizard.setParent(hou.session.mainWindow, QtCore.Qt.Window)
    wizard.setWindowFlags(wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    wizard.show()
