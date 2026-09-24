""" Unreal asset importer """
import ccunreal.utils.unreal_utils as unreal_utils
import ccgeneral.asset.asset_loader as asset_loader
import ccunreal.asset.fbx_asset_import as fbx_asset_import
import ccunreal.asset.usd_asset_import as usd_asset_import


class UnrealAssetLoader(asset_loader.AssetLoaderBase):
    title = "Unreal Load Asset"
    SUPPORTED_EXT = [".fbx", ".usd"]

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

            # import fbx asset
            if component_path.endswith(".fbx"):
                importer = fbx_asset_import.FBXAssetImport(
                    component_path, self.ftver, is_skeleton_mesh)

            elif component_path.endswith(".usd"):
                importer = usd_asset_import.USDAssetImport(
                    component_path, self.ftver, is_skeleton_mesh)

            importer.import_asset()

        if importer and importer.error_msg:
            unreal_utils.unreal_messagebox(
                "Import Error", importer.error_msg, "critical", parent=self
            )


def launch():
    """ Launch the unreal asset loader """
    unreal_utils.launch_unreal_win(UnrealAssetLoader)
