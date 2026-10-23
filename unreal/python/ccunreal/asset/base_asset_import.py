""" Import fbx asset from asset version """
import re
import os
import unreal as ue
import ccunreal.unreal_constants as unreal_constants
import ccunreal.utils.unreal_utils as unreal_utils
import cccore.utils.file_utils as file_utils


class BaseAssetImport(object):
    """
    Import a cache asset into the scene
    """
    asset_root = "/Game/ControlChaos/Asset"

    def __init__(self, source_asset_path, ftver, is_skeleton_mesh):
        # type: (str, str) -> None
        """
        Args:
            ftver: An instance of the ftrack asset version
            asset_version_id: The asset version id
            component_path: Path to import
        """
        self.asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
        self.source_asset_path = source_asset_path
        self.is_skeleton_mesh = is_skeleton_mesh
        self.ftver = ftver

        # initialize class variables
        self.error_msg = str()
        self.destination_dir = str()
        self._skeleton = None
        self._skeleton_mesh = None
        self._static_mesh = None

    def set_destination_dir(self):
        """
        Workout the destination directory
        """
        extension = file_utils.get_extension(self.source_asset_path)
        self.destination_dir = ue.Paths.combine(
            [self.asset_root,
             self.ftver.asset_build_type_name,
             self.ftver.asset_build_name,
             self.ftver.version_padded,
             extension
        ])

    def organize_asset(self):
        """
        Organise the assets into subfolders
        """
        # move assets to their respective folders
        ue.log_warning(f"Organizing assets into subfolders: {self.destination_dir}")
        path_to_type = unreal_utils.get_path_to_type_dict(self.destination_dir)
        for object_path, asset_type in path_to_type.items():
            if asset_type == unreal_constants.SKELETON_MESH:
                self._skeleton_mesh = ue.load_asset(object_path)

            elif asset_type == unreal_constants.STATIC_MESH:
                self._static_mesh = ue.load_asset(object_path)

            # if it's a type to ignore then continue
            if asset_type in unreal_constants.IGNORE_IMPORT_TYPES:
                continue

            # move the asset to the correct place
            asset = self.asset_registry.get_asset_by_object_path(object_path)
            dest_path = f"{self.destination_dir}/{asset_type}/{asset.asset_name}"
            ue.EditorAssetLibrary.rename_asset(object_path, dest_path)

    def add_metadata_to_asset(self):
        """
        Add metadata to the asset
        """
        asset_data = self.ftver.as_dict
        for asset in [self._static_mesh, self._skeleton_mesh]:
            if not asset:
                continue
            ue.log_warning(f"Applying metadata to: {asset}. Asset data: {asset_data}")
            unreal_utils.apply_metadata(asset_data, asset)
            return
        raise Exception("No skeleton or static asset found")

    def save_asset(self):
        """
        Save the imported assets
        """
        ue.EditorAssetLibrary.save_directory(self.destination_dir)
