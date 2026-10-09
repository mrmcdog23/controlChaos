""" Export level sequence actors as fbx files """
import unreal as ue
import no8core.folder.folder_creator as folder_creator
import no8ftrack.publish as publish
import no8unreal.ue_no8 as ue_no8
import no8core.utils.file_utils as file_utils
import no8unreal.utils.unreal_utils as unreal_utils
import no8unreal.utils.sequencer_utils as sequencer_utils
import no8unreal.unreal_context as unreal_context
import no8unreal.render.movie_render_queue as movie_render_queue
from ccgeneral.exporter.base_exporter import BaseExporter


class LevelSequenceExporter(BaseExporter):
    def __init__(self):
        super().__init__()
        self.ls = None
        self.map = None
        self.create_folders = None
        self.output_name = str()
        self.scene_data = dict()
        self.additional_components = dict()
        self.asset_version_id = str()

    def export(self):
        """
        Loop through the level sequence paths and
        """
        self.log("Exporting level sequences...")
        level_sequence_paths = self.data["level_sequence_paths"]
        map_path = self.data["map_path"]
        self.map = ue.load_asset(map_path)

        # load each the level sequence and export
        for ls_path in level_sequence_paths:
            self.ls = ue.load_asset(ls_path)
            self.set_export_context()
            self.create_shot_folder()
            self.export_sequence_level()
            self.save_scene_metadata()
            self.publish_fbx_files()
            self.render_movie_queue()
        self.finish_exporter_process()

    @BaseExporter.add_to_percentage(10)
    def export_sequence_level(self):
        """
        Get the characters to export and create a fbx export
        """
        self.log(f"Level name: {self.ls.get_name()}")
        bindings = self.ls.get_bindings()
        for binding in bindings:
            sequence_actor = self.get_level_sequence_actor(binding)

            # skip the camera component as its not needed
            if isinstance(sequence_actor, ue.CineCameraComponent):
                ue.log_warning("Skipping ue.CineCameraComponent")
                continue

            # get the fbx export path
            binding_name = binding.get_name()
            self.ctx.use_aov = binding_name
            self.ctx.use_subfolder = "cache"
            fbx_path = self.ctx.win_sequence_path

            # export the fbx file to disk
            sequencer_utils.export_fbx_file(fbx_path, self.map, self.ls, [binding])
            self.log(f"FBX Path: {fbx_path}")
            namespace_info = {"fbx_path": fbx_path}

            # save the camera data as a camera only
            if isinstance(sequence_actor, ue.CineCameraActor):
                ue.log_warning("Storing camera metadata...")
                namespace_info["asset_type_name"] = "camera"

            elif isinstance(sequence_actor, ue.SkeletalMeshActor):
                ftrack_id = self.get_level_sequence_actor_ftrack_id(binding)
                namespace_info["ftrack_id"] = ftrack_id
                ue.log_warning(f"No8 ftrack asset version: {ftrack_id}")

            self.scene_data[binding_name] = namespace_info
            self.additional_components[binding_name] = fbx_path
        self.data["additional_components"] = self.additional_components

    def set_export_context(self):
        # type: () -> unreal_context.UnrealContext
        """
        Fron the level sequence path get an instance of
        the context class to export the fbx paths

        Returns:
            ue_ctx: The level sequence context instance
        """
        self.output_name = self.ls.get_name()

        # create the initial context from the level sequence path
        ls_path = self.ls.get_path_name()
        ctx = unreal_utils.get_context_from_path(ls_path)

        # create overrides to get the unreal context
        overrides = ctx.as_dict().copy()
        overrides["task_name"] = "previz"
        overrides["aov"] = "main"
        overrides["ext"] = "fbx"
        overrides["version"] = 1

        # set the next version for the exports
        self.ctx = unreal_context.UnrealContext(overrides=overrides)
        use_version = self.ctx.next_sequence_version
        self.ctx.use_version = use_version
        self.data["version_num"] = use_version

    def create_shot_folder(self):
        """
        Check the shots exists on ftrack and on disk and create
        """
        # set the ftrack instance to the new project
        self.create_folders = folder_creator.CreateFolders()
        self.log("Creating default shot and assets...")

        context_dict = self.ctx.as_dict()
        sequence_name = context_dict["sequence_name"]
        shot_name = context_dict["shot_name"]

        # create previz sequence and shot
        create_dict = {
            "sequence_name": sequence_name,
            "shot_dicts": [{"name": shot_name}]
        }

        # if it is not a commercial then add an episode
        episode_name = context_dict.get("episode_name")
        if not self.ftshot.is_commercial:
            create_dict["episode_name"] = episode_name

        # create shots on disk
        self.create_folders.create_dict = create_dict
        self.create_folders.create_all_shot_folders()
        self.ftshot.commit()

    def get_level_sequence_actor(self, binding):
        # type: (ue.MovieSceneBindingProxy) -> ue.Actor
        """
        Get the bound actor from the binding

        Args:
            binding: The binding to get the actor from

        Returns:
            The level sequence actor
        """
        binding_id = self.ls.get_portable_binding_id(self.ls, binding)
        bound_actors = ue.LevelSequenceEditorBlueprintLibrary.get_bound_objects(binding_id)
        return bound_actors[0]

    def get_level_sequence_actor_ftrack_id(self, binding):
        # type: (ue.MovieSceneBindingProxy) -> str
        """
        From the binding get the actors ftrack rig id

        Args:
            binding: The binding to get the actor from

        Returns:
            ftrack_id: The rig asset version id
        """
        actor = binding.sequence.locate_bound_objects(binding, self.map)
        if not actor:
            self.log(f"Not FTrack id found on {actor}")
            return str()
        skeletal_mesh_asset = actor[0].skeletal_mesh_component.skeletal_mesh
        ftrack_id = ue_no8.get_ftrack_id(skeletal_mesh_asset.get_path_name())
        self.log(f"FTrack id {ftrack_id}")
        return ftrack_id

    def save_scene_metadata(self):
        """
        Save the scene data file in the same
        place as the published scene
        """
        self.ctx.use_aov = "scene_data"
        self.ctx.use_ext = "json"
        scene_data_path = self.ctx.win_sequence_path
        self.log(f"Saving metadata path: {scene_data_path}")
        file_utils.write_json(scene_data_path, self.scene_data)
        self.additional_components["Metadata"] = scene_data_path

    @BaseExporter.add_to_percentage(40)
    def publish_fbx_files(self):
        """
        Publish the fbx files and data to ftrack
        """
        # add all additional components to the data
        self.data["additional_components"] = self.additional_components

        # publish to ftrack
        ftrack_pub_inst = publish.FtrackPublish(self.data)
        self.asset_version_id = ftrack_pub_inst.asset_version["id"]
        self.log(f"Asset Version: {self.asset_version_id}")

    @BaseExporter.add_to_percentage(20)
    def render_movie_queue(self):
        """
        Render the level via the movie render
        """
        ue.log_warning(f"asset_version_id: {self.asset_version_id}")
        add_to_queue = False
        self.ctx.use_subfolder = "render"
        self.ctx.use_ext = "exr"
        sequence_path = self.ctx.sequence_path

        ls_path = self.ls.get_path_name()
        map_path = self.map.get_path_name()
        job_cls = movie_render_queue.CreateMovieRenderQueueJob(
            add_to_queue,
            sequence_path,
            ls_path,
            map_path,
            self.ftshot.resolution,
            asset_version_id=self.asset_version_id,
        )
        job_cls.create_job()
        job_cls.run_render()
