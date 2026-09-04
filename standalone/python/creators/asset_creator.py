import cccore.data.server_data as server_data
import cccore.base_ui as base_ui
import ccftrack.asset as asset
import cccore.utils.ui_utils as ui_utils
import cccore.utils.cc_logging as cc_logging


IGNORE_ASSET_BUILDS = ["Lighting", "Rendering"]


class AssetCreator(base_ui.StandaloneWindowBase):
    title = "Asset Creator"
    window_icon = "asset"
    widget_to_icon = {"lbl_project_icon": "project"}

    def __init__(self):
        super(AssetCreator, self).__init__()
        self.project_data = server_data.ProjectData()
        self.ftasset = asset.FtAsset()
        self.logger = cc_logging.cc_logger()
        self.lbl_project_name.setText(self.project_data.project_name)

        # initialize the ui
        self.populate_asset_build_types()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.btn_create_asset.clicked.connect(self.create_asset)
        self.le_name.textChanged.connect(self.validate_text)

    def validate_text(self, text):
        # type: (str) -> None
        """
        Validate the asset name text is camel case

        Args:
            text: The asset name text
        """
        self.btn_create_asset.setEnabled(bool(text))

    def populate_asset_build_types(self):
        """
        Populate the combo box of projects from ftrack
        """
        self.cmb_asset_builds.clear()
        asset_build_types_names = self.ftasset.asset_build_types_names
        for ignore in IGNORE_ASSET_BUILDS:
            if ignore in asset_build_types_names:
                asset_build_types_names.remove(ignore)
        self.cmb_asset_builds.addItems(asset_build_types_names)
        self.add_icons_to_combo(self.cmb_asset_builds, asset_build_types_names)

    def create_asset(self):
        """
        Create the asset on disk and on ftrack
        """
        asset_build_name = self.le_name.text()
        if self.ftasset.get_asset_build_from_name(asset_build_name):
            ui_utils.messagebox(
                "Asset Exists",
                f"Asset {asset_build_name} already exists",
                "critical",
                buttons=["Ok"],
                parent=self
            )
            return

        create = ui_utils.messagebox(
            "Create",
            f"Create asset {asset_build_name}?",
            "question",
            buttons=["Create", "Cancel"],
            parent=self
        )

        if create != "Create":
            return

        self.logger.info("Creating asset...")

        # gather ui publish data
        asset_build_type_name = self.cmb_asset_builds.currentText()

        # create the dictionary of the creator class
        self.ftasset.create_ftrack_asset(asset_build_type_name, asset_build_name)

        # show the display message
        self.logger.info("Asset creation complete")
        ui_utils.messagebox(
            "Complete",
            "Asset Created",
            "info",
            parent=self
        )


if __name__ == "__main__":
    base_ui.open_ui(AssetCreator)
