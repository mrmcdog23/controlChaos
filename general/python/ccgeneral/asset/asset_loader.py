""" Base class of asset loader """
import os
import ccgeneral.widgets.asset_cmb as asset_cmb
import ccftrack.asset as asset
import ccftrack.asset_version as ft_version
import ccgeneral.asset.base_loader as base_loader
import cccore.file_env.context as context
from CCPySide import QtCore


class AssetLoaderBase(base_loader.LoaderBase):
    label_text = "Asset"
    title = "Asset Loader"
    window_icon = "asset"
    widget_to_icon = {
        "lbl_cc_icon": "control_chaos_icon",
        "lbl_load_icon": "asset"
    }

    def __init__(self, parent):
        super().__init__(parent)

        # initialize class variables
        self.cmb_asset_build_type = None
        self.cmb_asset_build_name = None
        self.cmb_task = None
        self.asset_combo = None
        self.asset_name = str()

        # set up ftrack connections
        self.ftasset = asset.FtAsset()
        self.ftver = ft_version.FtAssetVersion(session=self.ftasset.session)
        self.ui_settings = QtCore.QSettings(os.environ["APP_NAME"], 'asset_loader')

        # run setup functions
        self.create_layout()
        self.connect_signals()
        self.update_versions()
        self.load_ui_settings(self.ui_settings)

    def create_layout(self):
        """
        Set the interface layout and look
        """
        # add the asset combo boxes
        ctx = context.Context()
        self.asset_combo = asset_cmb.AssetCmb(
            ftasset=self.ftasset, ctx=ctx, hide_cat=False, hide_tasks=False, hide_ver=True)
        self.cmb_asset_build_type = self.asset_combo.cmb_asset_build_type
        self.cmb_layout.addWidget(self.asset_combo)
        super().create_layout()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.asset_combo.cmb_category.currentIndexChanged.connect(self.update_versions)
        super().connect_signals()

    def update_versions(self):
        """
        Update the version list based on the asset selection
        """
        self.tw_versions.clear()
        self.asset_combo.set_ftasset()

        # get the versions from the combo boxes
        num_to_version_dict = self.asset_combo.ftasset.num_to_version
        self.populate_version_tree(num_to_version_dict, self.ftasset)
        self.reset_ui()
