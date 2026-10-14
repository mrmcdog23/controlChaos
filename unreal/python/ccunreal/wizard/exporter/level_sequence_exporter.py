""" Export level sequence actors as fbx files """
import os
import re
import unreal as ue
import cccore.utils.file_utils as file_utils
import ccunreal.utils.api_wrap as api_wrap
import ccunreal.utils.sequencer_utils as sequencer_utils
import ccunreal.utils.unreal_context as unreal_context
import ccunreal.render.movie_render_queue as movie_render_queue
from ccgeneral.wizard.exporter.base_exporter import BaseExporter


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
        self.map = ue.load_asset(self.data["map_path"])
        self.ls = ue.load_asset(self.data["ls_path"])

        # load each the level sequence and export
        self.set_export_context()
        self.export_sequence_level()
        self.write_metadata()
        self.publish_shot()
        self.render_movie_queue()
        self.finish_exporter_process()

    def set_export_context(self):
        # type: () -> unreal_context.UnrealContext
        """
        Fron the level sequence path get an instance of
        the context class to export the fbx paths

        Returns:
            ue_ctx: The level sequence context instance
        """
        self.output_name = self.ls.get_name()

        # create overrides to get the unreal context
        overrides = self.data.copy()
        overrides["aov"] = "main"
        overrides["ext"] = "fbx"
        overrides["version"] = "1"

        # set the next version for the exports
        self.ctx = unreal_context.UnrealContext(overrides=overrides)
        self.next_version = self.ftquery.next_version_from_ctx(self.ctx)
        self.ctx.use_version = self.next_version

    @BaseExporter.add_to_percentage(10)
    def export_sequence_level(self):
        """
        Get the characters to export and create a fbx export
        """
        self.log(f"Level name: {self.ls.get_name()}")
        bindings = self.ls.get_bindings()
        for binding in bindings:
            sequence_actor = self.get_level_sequence_actor(binding)
            if not sequence_actor:
                ue.log_warning(f"No binding found for binding {binding.get_display_name()}")
                continue

            # skip the camera component as it's not needed
            if isinstance(sequence_actor, ue.CineCameraComponent):
                ue.log_warning("Skipping ue.CineCameraComponent")
                continue

            # get the fbx export path
            binding_name = binding.get_name()
            match = re.match(r"(.*)_v\d+$", binding_name)
            suffix = match.group(1) if match else binding_name
            self.ctx.use_suffix = suffix

            fbx_path = self.ctx.fbx_file_path
            self.log(f"FBX Path: {fbx_path}")

            # export the fbx file to disk
            file_utils.create_directories(os.path.dirname(fbx_path))
            sequencer_utils.export_fbx_file(fbx_path, self.map, self.ls, [binding])
            asset_export_data = {"fbx_path": fbx_path, "is_camera": False}

            # save the camera data as a camera only
            if isinstance(sequence_actor, ue.CineCameraActor):
                asset_export_data["asset_type_name"] = "camera"
                asset_export_data["is_camera"] = True

            elif isinstance(sequence_actor, ue.SkeletalMeshActor):
                comp = sequence_actor.get_component_by_class(ue.SkeletalMeshComponent)
                metadata = api_wrap.get_metadata_tag_values(comp.skeletal_mesh_asset)
                asset_export_data.update(metadata)

            self.exported_files_to_data[fbx_path] = asset_export_data

            # remove log component name to a short one
            version_match = re.match(r".*_(.+?)_v\d+$", binding_name)
            if version_match:
                binding_name = version_match.group(1)

            self.additional_components[binding_name] = fbx_path
        self.data["additional_components"] = self.additional_components

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
        if bound_actors:
            return bound_actors[0]

    @BaseExporter.add_to_percentage(20)
    def render_movie_queue(self):
        """
        Render the level via the movie render
        """
        if not self.data["create_movie"]:
            ue.log_warning(f"Skipping create movie")
            return

        thumbnail_path = self.data["thumbnail_path"]
        add_to_queue = False
        self.ctx.use_ext = "exr"
        render_sequence_path = self.ctx.render_sequence_path
        ls_path = self.ls.get_path_name()
        map_path = self.map.get_path_name()

        job_cls = movie_render_queue.CreateMovieRenderQueueJob(
            add_to_queue,
            render_sequence_path,
            ls_path,
            map_path,
            self.ftshot.resolution,
            asset_version_id=self.ftver.asset_version_id,
            thumbnail_path=thumbnail_path
        )
        job_cls.create_job()
        job_cls.run_render()
