""" Unreal cache importer """
import unreal as ue
import cccore.utils.file_utils as file_utils


class CacheImporter(object):
    """
    Import fbx files into the Unreal project
    """
    def __init__(self, directory, fbx_path):
        # type: (str, str) -> None
        """
        Args:
            directory: Directory to import into
            fbx_path: FBX path to import
        """
        self.task = None
        self.imported_object_paths = list()
        self.directory = directory
        self.fbx_path = fbx_path

    def run_task(self, task):
        """
        Run import assets tasks
        """
        ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        self.imported_object_paths = task.imported_object_paths
        ue.EditorAssetLibrary.sync_browser_to_objects(self.imported_object_paths)

    def create_asset_import_task(self):
        # type: (ue.AssetImportTask) -> None
        """
        Create the asset import task to use to import the fbx
        
        Returns:
            task: The asset import task
        """
        asset_import_task = ue.AssetImportTask()
        asset_import_task.automated = True
        asset_import_task.destination_name = file_utils.get_file_name(self.fbx_path)
        asset_import_task.filename = self.fbx_path
        asset_import_task.destination_path = self.directory
        return asset_import_task

    def import_skeleton_mesh(self):
        """
        Import skeleton mesh into the project
        """
        asset_import_task = self.create_asset_import_task()

        options = ue.FbxImportUI()
        options.automated_import_should_detect_type = False
        options.import_mesh = True
        options.import_materials = True
        options.import_textures = True
        options.import_as_skeletal = True
        options.create_physics_asset = True
        options.mesh_type_to_import = ue.FBXImportType.FBXIT_SKELETAL_MESH

        # Static mesh specific data
        static_mesh_data = ue.FbxStaticMeshImportData()
        static_mesh_data.combine_meshes = True  # merges all meshes into ONE static mesh asset
        static_mesh_data.generate_lightmap_u_vs = True
        static_mesh_data.auto_generate_collision = True

        options.static_mesh_import_data = static_mesh_data
        asset_import_task.options = options
        self.run_task(asset_import_task)

    def import_static_mesh(self):
        """
        Import static mesh into the project
        """
        self.create_asset_import_task()
        self.task.options = ue.FbxImportUI()

        # add static mesh import data
        sm_import_data = ue.FbxStaticMeshImportData()
        sm_import_data.set_editor_property("combine_meshes", True)
        self.task.options.static_mesh_import_data = sm_import_data
        self.run_task()

    def import_animation(self, skeleton=None):
        # type: (ue.Skeleton) -> None
        """
        Import the fbx animation file and set the skeleton to be used

        Args:
            Associated skeleton
        """
        asset_import_task = self.create_asset_import_task()
        options = ue.FbxImportUI()
        if skeleton:
            options.skeleton = skeleton

        # --- Static Mesh Import Options ---
        options.import_mesh = True
        options.import_as_skeletal = False   # False = static mesh
        options.import_animations = True
        options.import_materials = True
        options.import_textures = True
        options.mesh_type_to_import = ue.FBXImportType.FBXIT_ANIMATION

        # Static mesh specific data
        static_mesh_data = ue.FbxStaticMeshImportData()
        static_mesh_data.combine_meshes = True  # merges all meshes into ONE static mesh asset
        static_mesh_data.generate_lightmap_u_vs = True
        static_mesh_data.auto_generate_collision = True

        options.static_mesh_import_data = static_mesh_data
        asset_import_task.options = options

        self.run_task(asset_import_task)

    def import_alembic_file(self):
        """
        Import the alembic file
        """
        self.create_asset_import_task()
        method = ue.AbcGeometryCacheMotionVectorsImport.IMPORT_ABC_VELOCITIES_AS_MOTION_VECTORS
        options = ue.AbcImportSettings()
        options.import_type = ue.AlembicImportType.GEOMETRY_CACHE
        options.material_settings.create_materials = True
        options.material_settings.find_materials = False
        options.geometry_cache_settings.flatten_tracks = True
        options.geometry_cache_settings.optimize_index_buffers = False
        options.geometry_cache_settings.motion_vectors = method
        options.conversion_settings.preset = ue.AbcConversionPreset.CUSTOM
        options.conversion_settings.flip_u = False
        options.conversion_settings.flip_v = True
        options.conversion_settings.rotation = ue.Vector(x=90.0, y=0.0, z=0.0)
        options.conversion_settings.scale = ue.Vector(x=1.0, y=-1.0, z=1.0)
        options.sampling_settings.skip_empty = True
        self.task.options = options
        self.run_task()

    def import_groom(self):
        """
        Import the alembic groom file
        """
        self.create_asset_import_task()
        conversion_settings = ue.GroomConversionSettings(
            rotation=[90.0, 0.0, 0.0], scale=[1.0, -1.0, 1.0])
        options = ue.GroomImportOptions()
        options.conversion_settings = conversion_settings
        groom_data = ue.GroomAssetImportData(options)
        self.task.options = groom_data
        self.run_task()

