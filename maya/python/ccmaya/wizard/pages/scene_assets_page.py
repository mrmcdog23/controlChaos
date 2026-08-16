""" Select which assets in the maya scene to publish """
import maya.mel as mel
import maya.cmds as cmds
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.asset.scene_asset as scene_asset
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
        self.lw_scene_assets = DragDropListWidget()
        self.lw_layout.addWidget(self.lw_scene_assets, 1, 0)

        self.lw_publish_assets = DragDropListWidget()
        self.lw_layout.addWidget(self.lw_publish_assets, 1, 1)

        # add save to directory
        self.wdg_save_dir = LineBrowser(
            self, "dir", "Select Output Directory", "", "Output Directory")
        self.lyt_save_dir.addWidget(self.wdg_save_dir)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.lw_publish_assets.model().rowsInserted.connect(self.check_complete)
        self.lw_publish_assets.model().rowsRemoved.connect(self.check_complete)
        self.wdg_save_dir.line_edit.textChanged.connect(self.check_complete)

    def load_scene_assets(self):
        """
        Load the scene assets that are published rigs
        """
        self.lw_scene_assets.addItems(maya_utils.get_shot_assets())

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
        if not self.wdg_save_dir or not self.lw_publish_assets:
            return

        has_assets = bool(self.lw_publish_assets.count())
        save_dir = self.wdg_save_dir.file_path

        if save_dir and has_assets:
            return True
        return False

    def validatePage(self):
        # type: () -> bool
        """
        Store the selected options in the wizard data

        Returns:
            Whether the page is valid
        """
        namespaces_to_fbx = dict()
        for index in range(self.lw_publish_assets.count()):
            item = self.lw_publish_assets.item(index)
            namespace = item.text()
            scene_asset_inst = scene_asset.SceneAsset(namespace)
            namespaces_to_fbx[namespace] = scene_asset_inst.reference_path

        self.data["namespaces_to_fbx"] = namespaces_to_fbx
        self.data["save_dir"] = self.wdg_save_dir.file_path
        return True

