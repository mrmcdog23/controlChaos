""" Import fbx asset from asset version """
import re
import os
import unreal as ue
import ccunreal.unreal_constants as unreal_constants
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.shot.cache_importer as cache_importer
import ccunreal.asset.base_asset_import as base_asset_import


class FBXAssetImport(base_asset_import.BaseAssetImport):
    """
    Import a cache asset into the scene
    """
    def __init__(self, source_asset_path, ftver, is_skeleton_mesh):
        super().__init__(source_asset_path, ftver, is_skeleton_mesh)

    def import_asset(self):
        """
        Function to import asset
        """
        self.set_destination_dir()

        loaded_asset = unreal_utils.get_asset_from_path(
            self.source_asset_path, folder_root=self.destination_dir)
        if loaded_asset:
            ue.log_warning(f"Loaded asset already found: {loaded_asset}")
            return

        if not self.is_import_valid:
            ue.log_warning("Import invalid so skipping")
            return

        asset_importer = cache_importer.CacheImporter(self.destination_dir, self.source_asset_path)
        if self.is_skeleton_mesh:
            ue.log_warning(f"Importing skeleton mesh: {self.source_asset_path}")
            asset_importer.import_skeleton_mesh()
        else:
            ue.log_warning(f"Importing static mesh: {self.source_asset_path}")
            asset_importer.import_static_mesh()

        # run post import commands
        self.organize_asset()
        self.save_asset()

    @property
    def skeleton_mesh(self):
        # type: () -> ue.Object
        """
        The skeleton mesh asset of the fbx

        Returns:
            skeleton: The skeleton asset
        """
        if not self._skeleton_mesh:
            self._skeleton_mesh = unreal_utils.find_asset_of_type(
                self.destination_dir, unreal_constants.SKELETON_MESH
            )
        return self._skeleton_mesh

    @property
    def static_mesh(self):
        # type: () -> ue.Object
        """ The skeleton mesh asset of the fbx """
        if not self._static_mesh:
            self._static_mesh = unreal_utils.find_asset_of_type(
                self.destination_dir, unreal_constants.STATIC_MESH
            )
        return self._static_mesh

    @property
    def skeleton(self):
        # type: () -> ue.Object
        """ The skeleton asset of the fbx """
        if not self._skeleton:
            self._skeleton = unreal_utils.find_asset_of_type(
                self.destination_dir, unreal_constants.SKELETON
            )
        return self._skeleton

    @property
    def is_import_valid(self):
        # type: () -> bool
        """
        Is the fbx file exist and in the asset version.
        Also check the destination directory exists and
        if the task type is supporting
        """
        # check the fbx path exists on disk
        if not os.path.exists(self.source_asset_path):
            ue.log_warning(f"Fbx path does not exist for {self.source_asset_path}")
            return False
        return True
