""" Load the unreal shot """
import unreal as ue
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


# constants
MATERIAL = unreal_constants.MATERIAL
LS_PREFIX = unreal_constants.LS_PREFIX
MP_PREFIX = unreal_constants.MP_PREFIX
LOW_RES = core_constants.LOW_RES


class UELoadShot(object):
    """
    Load the shot into unreal from its selected asset version
    """
    def __init__(self, fbx_dir, destination_folder):
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
        self.start = int()
        self.end = int()
        self.fps = float()
        self.ls_master = None
        self.map_master = None
        self.map_master_actors = dict()
        self.imported_obj_paths = list()

        self.fbx_dir = fbx_dir
        self.destination_folder = destination_folder
        self.asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
        self.run_import()

    def run_import(self):
        """
        Import the shot into Unreal
        """
        for fbx_path in file_utils.get_files_recursively(self.fbx_dir, extensions=["fbx"]):
            #self.set_shot_and_context()
            self.create_master_level_and_sequence()
            self.create_shot_level_and_sequence()
            self.open_sequence()
            self.animation_import()
            self.add_to_master_sequence()

    def set_shot_and_context(self):
        """
        Set the ftrack shot and context
        """
        # use the import data to set the context.
        # If there is no import data use the shot info
        self.ctx = unreal_utils.context_from_ftver(self.ftver)
        if self.ftver.episode_name:
            self.ftshot.episode_name = self.ftver.episode_name
        self.ftshot.sequence_name = self.ftver.sequence_name
        self.ftshot.shot_name = self.ftver.shot_name

        self.start = self.ftshot.start
        self.end = self.ftshot.end
        self.fps = self.ftshot.fps

    def create_master_level_and_sequence(self):
        """
        Create the master level sequence and map
        """
        # Create master map level
        subsys = ue.LevelEditorSubsystem()
        project_map_path = self.ctx.project_map_path
        if not ue.EditorAssetLibrary.does_asset_exist(project_map_path):
            subsys.new_level(project_map_path)
        self.map_master = ue.load_asset(project_map_path)

        # create master level sequence
        self.ls_master = sequencer_utils.create_level_sequence(self.ctx.ls_master_path, self.fps)

        # show the map and sequence in the browser
        ue.EditorAssetLibrary.sync_browser_to_objects([project_map_path])

        # save the map and level sequence
        subsys = ue.get_editor_subsystem(ue.EditorAssetSubsystem)
        subsys.save_asset(self.ls_master.get_full_name())

    def create_shot_level_and_sequence(self):
        """
        Create the shot level and level sequence
        """
        # the shot level sequence
        ls_path = self.ctx.ls_path
        if not ue.EditorAssetLibrary.does_asset_exist(ls_path):
            self.ls = sequencer_utils.create_level_sequence(
                self.ctx.ls_path, self.fps)
        else:
            self.map_master_actors = self.get_map_actors()
            self.ls = ue.load_asset(ls_path)
        sequencer_utils.set_level_sequence_view_range(self.ls, self.start, self.end, self.fps)

        # Create a new empty level
        asset_tools = ue.AssetToolsHelpers.get_asset_tools()
        asset_tools.create_asset(
            asset_name=self.ctx.map_name,
            package_path=self.ctx.ue_shot_directory,
            asset_class=ue.World,
            factory=ue.WorldFactory()
        )

        # Ensure a persistent level is loaded
        persistent_level = ue.EditorLevelLibrary.get_editor_world()
        ue.EditorLevelUtils.add_level_to_world(
            persistent_level, self.ctx.map_path, ue.LevelStreamingAlwaysLoaded
        )

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
        if not actor:
            actor = unreal_utils.spawn_actor(skeleton)
            actor.set_actor_label(asset_key)

        # find the binding and use it to find the animation section
        actor_binding = sequencer_utils.find_binding_by_display_name(asset_key, self.ls)
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
        anim_section.set_range(self.start, self.end)

        # Get the section, get the parameters, set animation to anim sequence asset
        anim_seq = ue.load_asset(anim_sequence_path)
        anim_section.params.animation = anim_seq

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

    def animation_import(self):
        """
        Check for the scene assets and load them if their missing
        """
        ftver_asset = asset_version.FtAssetVersion(session=self.session)
        for component_name, cache_path in self.component_to_path.items():
            ue.log_warning(f"Importing cache: {cache_path}")
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

    def import_camera_animation(self, fbx_path):
        # type: (str) -> None
        """
        Import a camera into the level sequence by
        creating then importing the fbx afterward

        Args:
            fbx_path: Path of the camera fbx file
        """
        # check for existing camera first
        camera_name = f"{self.ftver.full_shot_name}_cam"
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
                ue.ccCineCameraActor, ue.Vector(0, 0, 0))

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

            # get the low res plates
            component_path_dict = self.ftver.get_component_path_dict()
            plates_path = component_path_dict.get(LOW_RES)
            if not plates_path:
                ue_cc.popup_message("No low resolution plates found")
                return

            # build the plates network
            ue_asset_path = self.ctx.ue_shot_directory
            prefix = self.ctx.full_shot_name
            disk_shot_dir = self.ctx.disk_shot_dir
            import_camera_plates.ImportUEPlates(
                camera_actor,
                self.ls,
                ue_asset_path,
                prefix,
                plates_path=plates_path,
                disk_shot_dir=disk_shot_dir,
                start=self.start,
                end=self.end
            )

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

    def import_actor_animation(self, ftver_asset, scene_asset, fbx_path, asset_key):
        # type: (asset_version.FtAssetVersion, dict, str, str) -> None
        """
        Import an actor into unreal and attach the fbx animation to it

        Args:
            ftver_asset: Instance of asset version
            scene_asset: Metadata dictionary of the export
            fbx_path: Path of the fbx animation to import
            asset_key: Name of the actor component
        """
        ue.log_warning("Importing actors fbx animation")
        # import the actor and its fbx path
        asset_importer = import_fbx_asset.ImportAsset(
            ftver_asset, scene_asset["ftrack_id"])
        asset_importer.import_asset()

        # display warning if there is one
        if asset_importer.error_msg:
            ue.log_warning(asset_importer.error_msg)

        if not asset_importer.skeleton_mesh:
            ue.log_warning("No skeleton mesh found")
            return

        # get shot directory from fbx path
        version_dir = self.ctx.ue_shot_version_directory
        anim_importer = cache_importer.CacheImporter(version_dir, fbx_path)
        anim_importer.import_animation(skeleton=asset_importer.skeleton)

        # get the object path to its type and remove the other asset types
        anim_sequence_path = unreal_utils.get_object_path(
            version_dir,
            unreal_constants.ANIM_SEQUENCE,
            ignore_paths=self.imported_obj_paths
        )
        ue.log_warning(f"Animation sequence path: {anim_sequence_path}")

        # add the actor to the level
        self.spawn_actor_to_level(asset_importer.skeleton, anim_sequence_path, asset_key)

    def open_sequence(self):
        """
        Open the level sequence at the end of the import
        """
        ue.LevelSequenceEditorBlueprintLibrary.open_level_sequence(self.ls)
        ue_cc.popup_message(f"Created shot: {self.ftver.full_shot_name}")

    def add_to_master_sequence(self):
        """
        Add the shot to the master sequence
        """
        # add MovieSceneCinematicShotTrack track to your master_sequence
        try:
            track = self.ls_master.get_tracks()[0]
        except IndexError:
            track = self.ls_master.add_track(ue.MovieSceneCinematicShotTrack)

        # get the frame range for the section
        offset = self.ftshot.get_shot_sequence_start(self.ftver.shot_name)
        section_start = offset + self.start
        shot_range = self.end - self.start
        section_end = section_start + shot_range

        # add a section to the track
        section = track.add_section()
        section.set_editor_property('sub_sequence', self.ls)
        section.set_range(section_start, section_end)

        # get the full frame range of the section
        all_frames = list()
        for section in track.get_sections():
            all_frames.append(section.get_start_frame())
            all_frames.append(section.get_end_frame())

        # Set the display rate
        sequencer_utils.set_level_sequence_view_range(
            self.ls_master, min(all_frames), max(all_frames), self.fps)

        ue.LevelSequenceEditorBlueprintLibrary.open_level_sequence(self.ls_master)
