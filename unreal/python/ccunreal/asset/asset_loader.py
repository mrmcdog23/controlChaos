""" Unreal asset importer """
import ccunreal.utils.unreal_utils as unreal_utils
import ccgeneral.asset.asset_loader as asset_loader
import ccunreal.asset.import_fbx_asset as import_fbx_asset


class UnrealAssetLoader(asset_loader.AssetLoaderBase):
    title = "Unreal Load Asset"
    SUPPORTED_EXT = [".fbx"]

    def __init__(self, parent):
        super().__init__(parent=parent)

    def load_selected_version(self):
        """
        Function to import asset
        """
        self.save_ui_settings(self.ui_settings)
        asset_version = self.selected_version()
        self.ftver.asset_version_id = asset_version['id']

        # is the import type a skeleton mesh
        is_skeleton_mesh = self.asset_combo.task_name == "rigging"

        importer = None
        for component_path in self.selected_components:
            importer = import_fbx_asset.ImportAsset(
                component_path, asset_version["id"], is_skeleton_mesh)
            importer.import_asset()

        if importer and importer.error_msg:
            unreal_utils.unreal_messagebox(
                "Import Error", importer.error_msg, "critical", parent=self
            )


def launch():
    """ Launch the unreal asset loader """
    unreal_utils.launch_unreal_win(UnrealAssetLoader)
