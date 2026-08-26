""" Select which assets in the maya scene to publish """
import maya.mel as mel
import maya.cmds as cmds
import ccmaya.utils.maya_utils as maya_utils
from ccgeneral.widgets.dragdrop_listwidget import DragDropListWidget
from ccgeneral.wizard.pages.base_page import BasePublishPage
from ccgeneral.widgets.line_browser import LineBrowser
from CCPySide import QtWidgets


class MayaSceneAssetsPage(BasePublishPage):
    title = "Scene Assets Page"
    subtitle = "Select scene assets to publish"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lw_scene_assets = None
        self.lw_publish_assets = None
        self.wdg_save_dir = None

    def initializePage(self):
        # type: () -> bool
        """
        Set up the page when entered

        Return:
              False if the next page
        """
        super().initializePage()
        self.create_layout()
        self.load_scene_assets()
        self.connect_signals()
        return True

    def create_layout(self):
        """
        Add the list widgets to the page of the assets to publish
        """
        if self.built_layout:
            return
        self.lw_scene_assets = DragDropListWidget()
        self.lw_layout.addWidget(self.lw_scene_assets, 1, 0)
        self.lw_publish_assets = DragDropListWidget()
        self.lw_layout.addWidget(self.lw_publish_assets, 1, 1)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.lw_publish_assets.model().rowsInserted.connect(self.check_complete)
        self.lw_publish_assets.model().rowsRemoved.connect(self.check_complete)

    def load_scene_assets(self):
        """
        Load the scene assets that are published rigs
        """
        self.lw_scene_assets.addItems(maya_utils.get_shot_namespaces())

    def check_complete(self):
        """
        When item is added or removed check for change
        """
        self.completeChanged.emit()

    def isComplete(self):
        # type: () -> bool
        """
        Check there is any asset to publish

        Returns:
            Whether there is assets to publish
        """
        if not self.lw_publish_assets:
            return
        has_assets = bool(self.lw_publish_assets.count())
        return has_assets

    def validatePage(self):
        # type: () -> bool
        """
        Store the selected options in the wizard data

        Returns:
            Whether the page is valid
        """
        self.data["namespaces"] = self.lw_publish_assets.items_text
        return True

