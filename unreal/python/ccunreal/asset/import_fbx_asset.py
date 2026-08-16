""" Import fbx asset from asset version """
import os
import unreal as ue
import ccunreal.unreal_constants as unreal_constants
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.shot.cache_importer as cache_importer


class ImportAsset(object):
    """
    Import a cache asset into the scene
    """
    asset_root = "/Game/ControlChaos/Asset"

    def __init__(self, asset_fbx_path, namespace, is_skeleton_mesh):
        # type: (str, str) -> None
        """
        Args:
            ftver: An instance of the ftrack asset version
            asset_version_id: The asset version id
            component_path: Path to import
        """
        self.asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
        self.asset_fbx_path = asset_fbx_path
        self.is_skeleton_mesh = is_skeleton_mesh
        self.destination_dir = ue.Paths.combine([self.asset_root, namespace])

        # initialize class variables
        self.error_msg = str()
        self._skeleton = None
        self._skeleton_mesh = None
        self._static_mesh = None

    def import_asset(self):
        """
        Function to import asset
        """
        if not self.is_import_valid:
            ue.log_warning("Import invalid so skipping")
            return

        asset_importer = cache_importer.CacheImporter(self.destination_dir, self.asset_fbx_path)
        if self.is_skeleton_mesh:
            ue.log_warning(f"Importing skeleton mesh: {self.asset_fbx_path}")
            asset_importer.import_skeleton_mesh()
        else:
            ue.log_warning(f"Importing static mesh: {self.asset_fbx_path}")
            asset_importer.import_static_mesh()

        # run post import commands
        self.organize_asset()
        self.apply_metadata_tags()
        #self.create_arnold_texture()
        #self.apply_previous_materials()
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
        if not os.path.exists(self.asset_fbx_path):
            ue.log_warning(f"Fbx path does not exist for {self.asset_fbx_path}")
            return False
        return True

    def organize_asset(self):
        """
        Organise the assets into subfolders
        """
        # move assets to their respective folders
        path_to_type = unreal_utils.get_path_to_type_dict(self.destination_dir)
        for object_path, asset_type in path_to_type.items():
            if asset_type == unreal_constants.SKELETON_MESH:
                self._skeleton_mesh = ue.load_asset(object_path)

            # if it's a type to ignore then continue
            if asset_type in unreal_constants.IGNORE_IMPORT_TYPES:
                continue

            # move the asset to the correct place
            asset = self.asset_registry.get_asset_by_object_path(object_path)
            dest_path = f"{self.destination_dir}/{asset_type}/{asset.asset_name}"
            ue.EditorAssetLibrary.rename_asset(object_path, dest_path)

    def apply_metadata_tags(self):
        """
        Apply the import data to the asset
        """
        if not self._skeleton_mesh:
            return
        unreal_utils.add_cc_metadata_dict(self._skeleton_mesh, self.ftver.as_dict)
        unreal_utils.add_metadata_value(self._skeleton_mesh, "ftrack_id", self.ftver.asset_version_id)

    def save_asset(self):
        """
        Save the imported assets
        """
        ue.EditorAssetLibrary.save_directory(self.destination_dir)
