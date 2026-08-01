""" Load the unreal shot """
import os
import unreal as ue
import ccunreal.utils.sequencer_utils as sequencer_utils
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.unreal_constants as unreal_constants
import ccunreal.shot.cache_importer as cache_importer
import ccunreal.utils.api_wrap as api_wrap
import cccore.utils.file_utils as file_utils


# constants
MATERIAL = unreal_constants.MATERIAL
LS_PREFIX = unreal_constants.LS_PREFIX
MP_PREFIX = unreal_constants.MP_PREFIX



class UELoadShot(object):
    """
    Load the shot into unreal from its selected asset version
    """
    def __init__(self, import_file_list, shot_name, level_path, start_frame, end_frame):
        # type: (list[str], str, str, int, int) -> None
        """
        Args:
            import_file_list: List of files to import
            shot_name: Name of the shot importing
            level_path: Path of the map to load
            start_frame: First frame of the sequence
            end_frame: Last frame of the sequence
        """
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.import_file_list = import_file_list
        self.shot_name = shot_name
        self.level_path = level_path

        self.ls = None
        self.fps = 24.0
        self.imported_obj_paths = list()
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
        """
        Create or load the map to use
        """
        # Create a new empty level
        if ue.EditorAssetLibrary.does_asset_exist(self.level_path):
            ue.EditorLevelLibrary.load_level(self.level_path)
        else:
            ue.EditorLevelLibrary.new_level(self.level_path)
            unreal_utils.create_sky_and_lights()

        # save the map and level sequence
        subsys = ue.get_editor_subsystem(ue.EditorAssetSubsystem)
        subsys.save_asset(self.level_path)
        ue.log(f"Level path: {self.level_path}")

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
            ue.log(f"Level sequence path: {self.ls.get_full_name()}")

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
            elif "env" in file_name.lower():
                self.import_environment_mesh(fbx_path)
            else:
                self.import_actor_animation(fbx_path)

    def import_actor_animation(self, fbx_path):
        # type: (str) -> None
        """
        Import the actor with the animation

        Args:
            fbx_path: Path of the fbx file to import
        """
        ue.log(f"Importing cache: {fbx_path}")
        anim_importer = cache_importer.CacheImporter(self.version_dir, fbx_path)
        anim_importer.import_animation()

        # get the object path to its type and remove the other asset types
        object_paths = anim_importer.imported_object_paths
        anim_sequence_path = unreal_utils.get_objects_from_list(
            object_paths, unreal_constants.ANIM_SEQUENCE)
        ue.log(f"Animation sequence path: {anim_sequence_path}")

        skeleton_mesh_path = unreal_utils.get_objects_from_list(
            object_paths, unreal_constants.SKELETON_MESH)
        skeleton = ue.load_asset(skeleton_mesh_path)
        ue.log(f"Skeleton mesh path: {skeleton_mesh_path}")

        # add the actor to the level
        actor_name = file_utils.get_file_name(fbx_path)
        self.spawn_actor_to_level(skeleton, anim_sequence_path, actor_name)

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
        and add to the level

        Args:
            fbx_path: Path of the environment fbx file
        """
        asset_importer = cache_importer.CacheImporter(self.version_dir, fbx_path)
        asset_importer.import_static_mesh()
        '''
        object_paths = asset_importer.imported_object_paths
        static_mesh_path = unreal_utils.get_objects_from_list(
            object_paths, unreal_constants.STATIC_MESH)
        static_mesh = ue.load_asset(static_mesh_path)
        ue.log_warning(f"Skeleton mesh path: {static_mesh}")

        api_wrap.spawn_actor_from_object(static_mesh)
        '''
