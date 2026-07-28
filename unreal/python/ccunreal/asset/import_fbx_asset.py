""" Import fbx asset from asset version """
import os
import unreal as ue
import ccftrack.asset_version as ft_version
import ccunreal.unreal_constants as unreal_constants
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.cache_importer as cache_importer
import ccunreal.asset.create_turntable as cc_turntable
import ccunreal.asset.material_linker as material_linker


class ImportAsset(object):
    """
    Import a cache asset into the scene
    """
    def __init__(self, ftver, asset_version_id, component_path=None):
        # type: (ft_version.FtAssetVersion, str, str) -> None
        """
        Args:
            ftver: An instance of the ftrack asset version
            asset_version_id: The asset version id
            component_path: Path to import
        """
        self.ftver = ftver
        self.ftver.asset_version_id = asset_version_id
        self.asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
        self.ctx = unreal_utils.context_from_ftver(self.ftver)
        self.latest_version = self.ctx.latest_version
        self.fbx_path = component_path or self.ftver.fbx_component_path
        self.destination_dir = self.ctx.ue_asset_version_directory

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

        asset_importer = cache_importer.CacheImporter(self.destination_dir, self.fbx_path)
        if self.ftver.task_name == "rigging":
            asset_importer.import_skeleton_mesh()
        elif self.ftver.task_name in ["lookdev", "modeling"]:
            asset_importer.import_static_mesh()
        else:
            ue.log_error("Not supported type")

        # run post import commands
        self.organize_asset()
        self.apply_metadata_tags()
        self.create_arnold_texture()
        self.apply_previous_materials()
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
        # check there is a fbx path
        if not self.fbx_path:
            ue.log_warning(f"No FBX path found on asset version {self.ftver.asset_build_name}")
            return False

        # check the fbx path exists on disk
        if not os.path.exists(self.fbx_path):
            ue.log_warning(f"Fbx path does not exist in {self.ftver.asset_build_name}")
            return False

        # if the asset exists let the artist know
        if ue.EditorAssetLibrary.does_directory_exist(self.destination_dir):
            ue.log_warning(f"Path exists: {self.destination_dir}")
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

    def create_arnold_texture(self):
        """
        From the material description create
        the missing textures
        """
        material_linker.link_materials(self.ftver.matdesc_component_path)

    def apply_previous_materials(self):
        """
        If there is a previous version use its shaders
        """
        if not self.latest_version:
            return

        # in this case latest version is the last version
        # of the skeleton before the new one was importer
        self.ctx.use_version = self.latest_version
        previous_skeleton_mesh_path = self.ctx.ue_skeleton_mesh_path
        prev_skeleton_mesh = ue.load_asset(previous_skeleton_mesh_path)

        # start the material array to assign
        material_array = ue.Array(ue.SkeletalMaterial)
        for index, material in enumerate(prev_skeleton_mesh.materials):
            # check if there is an existing material on the new asset
            try:
                existing_material = self.skeleton_mesh.materials[index]
            except IndexError:
                ue.log_warning("Existing material does not exist!")
                existing_material = None

            if existing_material:
                # remove the previous materials
                ue.log(f"Deleting existing material {existing_material.material_slot_name}")
                ue.EditorAssetLibrary.delete_loaded_assets([existing_material.material_interface])

                # set the existing material slot to the previous one
                existing_material.material_interface = material.material_interface
                existing_material.material_slot_name = material.material_slot_name
                material_array.append(material)
            else:
                # create a new material and assign it.
                new_material = ue.SkeletalMaterial()
                new_material.material_interface = material.material_interface
                new_material.material_slot_name = material.material_slot_name
                self.skeleton_mesh.materials.append(new_material)
            self.skeleton_mesh.modify()

        # set the materials which completes the assignments
        self.skeleton_mesh.set_editor_property("materials", material_array)

    def save_asset(self):
        """
        Save the imported assets
        """
        ue.EditorAssetLibrary.save_directory(self.destination_dir)

    def create_turntable(self):
        """
        Create the turntable setup for the asset
        """
        cc_turntable.main(
            self.skeleton_mesh.get_full_name(),
            asset=self.skeleton_mesh
        )
