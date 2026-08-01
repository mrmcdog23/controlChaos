""" Load the unreal shot """
import unreal as ue
import ccunreal.utils.sequencer_utils as sequencer_utils
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.unreal_constants as unreal_constants
import ccunreal.shot.cache_importer as cache_importer
import ccunreal.utils.api_wrap as api_wrap
import cccore.utils.file_utils as file_utils
'''
import cccore.utils.file_utils as file_utils
import cccore.core_constants as core_constants
import ccunreal.asset.import_fbx_asset as import_fbx_asset
import ccunreal.utils.unreal_utils as unreal_utils
#import ccunreal.utils.sequencer_utils as sequencer_utils
#import ccunreal.shot.import_camera_plates as import_camera_plates
#import ccunreal.cache_importer as cache_importer
import ccunreal.unreal_constants as unreal_constants
#import ccunreal.unreal_context as unreal_context
#import ccunreal.api_wrap as api_wrap
from typing import Optional, Any

'''
# constants
MATERIAL = unreal_constants.MATERIAL
LS_PREFIX = unreal_constants.LS_PREFIX
MP_PREFIX = unreal_constants.MP_PREFIX



class UELoadShot(object):
    """
    Load the shot into unreal from its selected asset version
    """
    def __init__(self, import_file_list, shot_name, start_frame, end_frame):
        # type: (str, str, Optional[str], Optional[dict], Optional[ftrack_api.Session]) -> None
        """
        Args:
            sequence_name: Name of the sequence importing
            shot_name: Name of the shot importing
            episode_name: Name of the episode to create
            import_data: Import data
            session: Connected ftrack version
        """
        self.ls = None
        self.ctx = None
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.fps = 24.0
        self.imported_obj_paths = list()
        self.import_file_list = import_file_list
        self.shot_name = shot_name
        self.version_dir = f"/Game/Shot/{self.shot_name}"
        self.asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
        self.run_import()

    def run_import(self):
        """
        Import the shot into Unreal
        """
        self.create_level()
        self.create_ls()
        self.open_sequence()
        self.animation_import()

    def create_level(self):
        # Create a new empty level
        level_name = "mrdog"
        level_dir = "/Game/Level/"
        level_path = f"{level_dir}/{level_name}"

        if ue.EditorAssetLibrary.does_asset_exist(level_path):
            ue.log_warning(f"Loading level path: {level_path}")
            ue.EditorLevelLibrary.load_level(level_path)
        else:
            ue.log_warning(f"Creating level path: {level_path}")
            ue.EditorLevelLibrary.new_level(level_path)
            unreal_utils.create_sky_and_lights()

        # save the map and level sequence
        subsys = ue.get_editor_subsystem(ue.EditorAssetSubsystem)
        subsys.save_asset(level_path)
        ue.log_warning(f"Level path: {level_path}")

    def create_ls(self):
        """
        Create the shot level and level sequence
        """
        # the shot level sequence
        ls_path = f"/Game/Shot/{self.shot_name}/{LS_PREFIX}_{self.shot_name}"

        # create the level sequence first
        if ue.EditorAssetLibrary.does_asset_exist(ls_path):
            self.ls = ue.load_asset(ls_path)
        else:
            self.ls = sequencer_utils.create_level_sequence(ls_path, self.fps)
            subsys = ue.get_editor_subsystem(ue.EditorAssetSubsystem)
            subsys.save_asset(self.ls.get_full_name())
            ue.log_warning(f"Level sequence path: {self.ls.get_full_name()}")

        sequencer_utils.set_level_sequence_view_range(
            self.ls, self.start_frame, self.end_frame, self.fps)

    def open_sequence(self):
        """
        Open the level sequence at the end of the import
        """
        ue.LevelSequenceEditorBlueprintLibrary.open_level_sequence(self.ls)

    def animation_import(self):
        """
        Check for the scene assets and load them if their missing
        """
        for fbx_path in self.import_file_list:
            if not fbx_path.endswith(".fbx"):
                continue

            file_name = file_utils.get_file_name(fbx_path)
            if "cam" in file_name.lower():
                self.import_camera_animation(fbx_path)

            if "env" in file_name.lower():
                self.import_environment_mesh(fbx_path)

            else:
                self.import_actor_animation(fbx_path)

    def import_actor_animation(self, fbx_path):
        ue.log_warning(f"Importing cache: {fbx_path}")
        anim_importer = cache_importer.CacheImporter(self.version_dir, fbx_path)
        anim_importer.import_animation()

        # get the object path to its type and remove the other asset types
        object_paths = anim_importer.imported_object_paths
        anim_sequence_path = unreal_utils.get_objects_from_list(
            object_paths, unreal_constants.ANIM_SEQUENCE)
        ue.log_warning(f"Animation sequence path: {anim_sequence_path}")

        skeleton_mesh_path = unreal_utils.get_objects_from_list(
            object_paths, unreal_constants.SKELETON_MESH)
        skeleton = ue.load_asset(skeleton_mesh_path)
        ue.log_warning(f"Skeleton mesh path: {skeleton_mesh_path}")

        # add the actor to the level
        self.spawn_actor_to_level(skeleton, anim_sequence_path, "Cunt")

    def spawn_actor_to_level(self, skeleton, anim_sequence_path, asset_key):
        # type: (ue.Object, str, str) -> None
        """
        Add the actor to the level along with the animation

        Args:
            skeleton: The skeleton asset to add
            anim_sequence_path: Path of the new animation sequence
            asset_key: Name of the actor component
        """
        actor = self.find_actor_with_label(asset_key)
        ue.log_warning(f"Found actor: {actor}")
        if not actor:
            actor = api_wrap.spawn_actor_from_object(skeleton)
            actor.set_actor_label(asset_key)

        # find the binding and use it to find the animation section
        actor_binding = sequencer_utils.find_binding_by_display_name(asset_key, self.ls)
        ue.log_warning(f"Actor binding: {actor_binding}")
        if actor_binding:
            anim_track = actor_binding.get_tracks()[0]
            anim_section = anim_track.get_sections()[0]
        else:
            # add the actor and create the track and the section
            actor_binding = self.ls.add_possessable(actor)
            anim_track = actor_binding.add_track(ue.MovieSceneSkeletalAnimationTrack)
            anim_section = anim_track.add_section()

        # Get level sequence start and end frame
        # Set section range to level sequence start and end frame
        anim_section.set_range(self.start_frame, self.end_frame)

        # Get the section, get the parameters, set animation to anim sequence asset
        anim_seq = ue.load_asset(anim_sequence_path)
        anim_section.params.animation = anim_seq

    @staticmethod
    def find_actor_with_label(actor_label):
        # type: (str) -> Optional[ue.Actor]
        """
        Find an actor with a label on the level

        Args:
            actor_label: Actor label to find

        Returns:
            actor: The actor found matching the label
        """
        level_actors = ue.EditorLevelLibrary.get_all_level_actors()
        for actor in level_actors:
            if actor.get_actor_label() == actor_label:
                return actor

    def import_camera_animation(self, fbx_path):
        # type: (str) -> None
        """
        Import a camera into the level sequence by
        creating then importing the fbx afterwards

        Args:
            fbx_path: Path of the camera fbx file
        """
        ue.log_warning("loading camera")
        editor_subsys = ue.get_editor_subsystem(ue.LevelSequenceEditorSubsystem)

        # check for existing camera first
        camera_actor = unreal_utils.actor_type_on_level(ue.CineCameraActor)
        if camera_actor:
            # try to find binding and if one isn't found create one
            binding = self.find_camera_binding()
            if not binding:
                binding = self.ls.add_possessable(camera_actor)
        else:
            # if no binding found spawn one
            binding, camera_actor = editor_subsys.create_camera(spawnable=False)
            camera_actor.set_actor_label(f"{self.shot_name}_cam")

        # apply the sequence animation
        world = ue.EditorLevelLibrary.get_editor_world()
        ue.SequencerTools.import_level_sequence_fbx(
            world, self.ls, [binding], unreal_utils.camera_ue_options(), fbx_path
        )

    def import_environment_mesh(self, fbx_path):
        # type: (Any, dict, str) -> None
        """
        Import environment asset as a static mesh
        and add to the map and level sequence
        """
        asset_importer = cache_importer.CacheImporter(self.version_dir, fbx_path)
        asset_importer.import_static_mesh()
        actor = unreal_utils.spawn_actor(asset_importer.static_mesh)
        self.ls.add_possessable(actor)

    '''
        
        
        # check for existing camera first
        camera_name = f"{self.shot_name}_cam"
        camera_actor = self.find_actor_with_label(camera_name)
        if camera_actor:
            current_fbx_path = unreal_utils.fbx_from_actor_tag(camera_actor)
            if current_fbx_path == fbx_path:
                ue.log_warning(f"Camera {camera_name} fbx is up to date")
                return

            # try to find binding and if one isn't found create one
            ue.log_warning(f"Updating camera {camera_name} fbx...")
            binding = sequencer_utils.find_binding_by_actor_class(ue.CineCameraActor, self.ls)
            if not binding:
                self.ls.add_possessable(camera_actor)
        else:

            # spawn a cc camera to the map
            camera_actor = ue.EditorLevelLibrary.spawn_actor_from_class(
                ue.CineCameraActor, ue.Vector(0, 0, 0))

            # add to the level sequence
            api_wrap.add_actors_to_current_sequence([camera_actor])
            binding = sequencer_utils.find_binding_by_actor_class(ue.CineCameraActor, self.ls)

            # set tag and label
            camera_actor.tags = [fbx_path]
            camera_actor.set_actor_label(camera_name)

            # apply the sequence animation
            ue.CameraFbxImporter.load_camera(
                self.map_master, self.ls, [binding],
                unreal_utils.camera_ue_options(),
                fbx_path,
            )
            api_wrap.convert_to_possessable(binding)



            import_fbx_settings = unreal_utils.camera_ue_options()
            bindings = self.ls.get_bindings()
            world = ue.EditorLevelLibrary.get_editor_world()
            # Perform the import
            result = ue.SequencerTools.import_level_sequence_fbx(
                world,
                self.ls,
                bindings,
                import_fbx_settings,
                fbx_path
            )

            if result:
                ue.log(f"Successfully imported FBX camera animation from {fbx_path}")
            else:
                ue.log_error("FBX camera import failed")


            if not cache_path.endswith(".fbx"):
                continue

            scene_asset = self.get_scene_asset(component_name)
            if scene_asset:
                asset_key = component_name.replace("fbx_", "")

                # get the fbx file path and convert to windows
                cache_path = file_utils.convert_path_to_win(cache_path)
                ue.log_warning(f"Importing cache: {cache_path}")

                # load the environment asset
                asset_build_type_name = scene_asset["asset_build_type_name"]

                if asset_build_type_name == "Environment":
                    self.import_environment_mesh(ftver_asset, scene_asset, cache_path)
                elif asset_build_type_name == "Camera":
                    self.import_camera_animation(cache_path)
                else:
                    self.import_actor_animation(ftver_asset, scene_asset, cache_path, asset_key)

            else:
                # for unpublished fbx paths most likely tracking
                if "cam" in cache_path.lower():
                    self.import_camera_animation(cache_path)
                else:
                    # import the fbx of geometry and add it to the level sequence
                    self.import_unpublished_geo(cache_path)

        # set the metadata on the asset
        unreal_utils.apply_metadata(self.ftver.as_dict, self.ls)
        unreal_utils.apply_metadata(self.ftver.as_dict, self.map_master)

        # save the map and level sequence
        subsys = ue.get_editor_subsystem(ue.EditorAssetSubsystem)
        subsys.save_asset(self.ls.get_full_name())
        subsys.save_asset(self.map_master.get_full_name())

    def get_scene_asset(self, component_name):
        # type: (str) -> Optional[dict]
        """
        Find the metadata file and from the component name get the asset

        Args:
            component_name: Component name to find asset for

        Returns:
            scene_asset: The scene asset data
        """
        if not self.ftver.metadata_component_path:
            return
        # reading metadata of the scene and get the asset data
        scene_assets = file_utils.read_json(self.ftver.metadata_component_path)
        asset_key = component_name.replace("fbx_", "")
        scene_asset = scene_assets.get(asset_key)
        return scene_asset

    def import_environment_mesh(self, ftver_asset, scene_asset, cache_path):
        # type: (Any, dict, str) -> None
        """
        Import environment asset as a static mesh
        and add to the map and level sequence
        """
        asset_importer = import_fbx_asset.ImportAsset(
            ftver_asset, scene_asset["ftrack_id"], cache_path)
        asset_importer.import_asset()
        actor = unreal_utils.spawn_actor(asset_importer.static_mesh)
        self.ls.add_possessable(actor)

    def import_unpublished_geo(self, cache_path):
        # type: (str) -> None
        """
        Import a fbx into the scene and add it to the level

        Args:
            cache_path: Fbx path of geometry to import
        """
        ue.log_warning("Importing unpublished geo")
        version_dir = self.ctx.ue_shot_version_directory
        static_mesh_before = unreal_utils.find_all_assets_of_type(
            version_dir, unreal_constants.STATIC_MESH)
        cache_importer_inst = cache_importer.CacheImporter(version_dir, cache_path)
        cache_importer_inst.import_static_mesh()

        # find the new static meshes
        static_mesh = unreal_utils.find_asset_of_type(
            version_dir, unreal_constants.STATIC_MESH, assets_before=static_mesh_before)
        ue.log_warning(f"Adding {static_mesh} to level")
        unreal_utils.spawn_actor(static_mesh)

    @staticmethod
    def get_asset_directory_from_path(path):
        # type: (str) -> str
        """
        From the full asset path remove the filename and
        the version number so when adding to the sequence
        there isn't a version of the rig already present

        Args:
            path: Full asset path with te file name

        Returns:
            Path of the directory of the asset minus the version
        """
        actor_version_dir = ue.Paths.get_path(path)
        return ue.Paths.get_path(actor_version_dir)

    def get_map_actors(self):
        # type: () -> dict
        """
        Get all the skeleton actors to its path dictionary

        Returns:
            map_actors: Path to the ue.Object
        """
        map_actors = dict()
        level_actors = ue.EditorLevelLibrary.get_all_level_actors()
        for actor in level_actors:
            if isinstance(actor, ue.SkeletalMeshActor):
                asset = actor.skeletal_mesh_component.skeletal_mesh
                path = asset.get_path_name()
                actor_dir = self.get_asset_directory_from_path(path)
                map_actors[actor_dir] = actor
        return map_actors
    '''