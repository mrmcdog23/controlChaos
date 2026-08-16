""" Load the unreal shot """
import os
import unreal as ue
import ccunreal.utils.sequencer_utils as sequencer_utils
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.unreal_constants as unreal_constants
import ccunreal.shot.cache_importer as cache_importer
import ccunreal.utils.api_wrap as api_wrap
import cccore.utils.file_utils as file_utils
import ccunreal.asset.import_fbx_asset as import_fbx_asset


# constants
MATERIAL = unreal_constants.MATERIAL
LS_PREFIX = unreal_constants.LS_PREFIX
MP_PREFIX = unreal_constants.MP_PREFIX



class UELoadShot(object):
    """
    Load the shot into unreal from its selected asset version
    """
    def __init__(self, import_file_list, data, level_path, shot_path):
        # type: (list[str], str, str, str, int, int) -> None
        """
        Args:
            import_file_list: List of files to import
            shot_name: Name of the shot importing
            level_path: Path of the map to load
            start_frame: First frame of the sequence
            end_frame: Last frame of the sequence
        """
        self.import_file_list = import_file_list
        self.data = data
        self.level_path = level_path
        self.shot_path = shot_path
        self.shot_name = ue.Paths.get_base_filename(shot_path)

        self.ls = None
        self.fps = 24.0
        self.imported_obj_paths = list()
        self._version_dir = str()

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

    @property
    def start_frame(self):
        # type: () -> int
        """ The first frame to import """
        return self.data["start_frame"]

    @property
    def end_frame(self):
        # type: () -> int
        """ The last frame to import """
        return self.data["end_frame"]

    @property
    def version_dir(self):
        # type: () -> str
        """
        Workout and set the version import directory
        """
        if self._version_dir:
            return self._version_dir

        number_of_versions = unreal_utils.list_subfolders(self.shot_path, recursive=False)
        next_version_number = len(number_of_versions) + 1
        self._version_dir = ue.Paths.combine([self.shot_path, f"v{next_version_number}"])
        return self._version_dir

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
        ls_path = ue.Paths.combine([self.version_dir, f"{LS_PREFIX}_{self.shot_name}"])

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
            file_data = self.data["exported_files_to_data"][fbx_path]

            if file_data["is_camera"]:
                self.import_camera_animation(fbx_path)

            elif file_data["is_skeleton_mesh"]:
                self.import_skeleton_mesh_animation(fbx_path, file_data)
            else:
                self.import_static_mesh(file_data)

    def import_skeleton_asset(self, file_data):
        # type: (dict) -> (ue.Skeleton, ue.SkeletonMesh)
        """
        Import the skeleton asset from the file data

        Args:
            file_data: THe information of the asset

        Returns:
            skeleton: The unreal skeleton asset
            skeleton_mesh: The unreal skeleton mesh as an asset
        """
        # import the actor and its fbx path
        asset_importer = import_fbx_asset.ImportAsset(
            file_data["asset_fbx_path"], file_data["namespace"], True)
        asset_importer.import_asset()
        return asset_importer.skeleton, asset_importer.skeleton_mesh

    def import_skeleton_mesh_animation(self, fbx_path, file_data):
        # type: (str) -> None
        """
        Import the actor with the animation

        Args:
            fbx_path: Path of the fbx file to import
        """
        # import the actor and its fbx path
        skeleton, skeleton_mesh = self.import_skeleton_asset(file_data)
        ue.log_warning(f"Skeleton: {skeleton}")
        anim_importer = cache_importer.CacheImporter(self.version_dir, fbx_path)
        anim_importer.import_animation(skeleton=skeleton)

        # get the object path to its type and remove the other asset types
        object_paths = anim_importer.imported_object_paths
        anim_sequence_path = unreal_utils.get_objects_from_list(
            object_paths, unreal_constants.ANIM_SEQUENCE)
        ue.log_warning(f"Animation sequence path: {anim_sequence_path}")

        # add the actor to the level
        actor_name = file_utils.get_file_name(fbx_path)
        self.spawn_actor_to_level(skeleton_mesh, anim_sequence_path, actor_name)

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

    def import_static_mesh(self, file_data):
        # type: (Any, dict, str) -> None
        """
        Import environment asset as a static mesh
        and add to the level

        Args:
            fbx_path: Path of the environment fbx file
        """
        # import the actor and its fbx path
        asset_importer = import_fbx_asset.ImportAsset(
            file_data["asset_fbx_path"], file_data["namespace"], False)
        asset_importer.import_asset()
        static_mesh = asset_importer.static_mesh
        ue.log_warning(f"Static mesh path: {static_mesh}")

        #api_wrap.spawn_actor_from_object(static_mesh)
