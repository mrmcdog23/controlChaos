""" Export level sequence actors as fbx files """
import os
import re
import unreal as ue
import cccore.utils.file_utils as file_utils
import cccore.file_env.context_utils as context_utils
import ccunreal.unreal_constants as unreal_constants
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
        self.publish_assets = self.data["publish_assets"]
        ue.LevelSequenceEditorBlueprintLibrary.open_level_sequence(self.ls)

        # load each the level sequence and export
        self.set_export_context()
        self.export_animated_actors()
        self.export_static_actors()
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

    def get_actor_name(self, sequence_actor):
        # type: (ue.Actor) -> Optiona[str]
        """
        From the actor get the label to use to export.

        Args:
            sequence_actor: The unreal actor to get the name for

        Returns:
            actor_name_clean: The clean name to export
        """
        # get the fbx export path
        actor_name = sequence_actor.get_actor_label()
        if actor_name not in self.publish_assets:
            self.log(f"Skipping actor {actor_name} not set to export")
            return

        match = re.match(r"(.*)_v\d+$", actor_name)
        actor_name_clean = match.group(1) if match else actor_name

        if actor_name_clean in self.additional_components:
            self.log(f"Actor {actor_name_clean} has already been exported")
            return

        return actor_name_clean

    @BaseExporter.add_to_percentage(10)
    def export_animated_actors(self):
        """
        Export the actors bind to the level sequence
        """
        bindings = self.ls.get_bindings()
        for binding in bindings:
            sequence_actor = sequencer_utils.get_level_sequence_actor(self.ls, binding)
            if not sequence_actor:
                ue.log_warning(f"No binding found for binding {binding.get_display_name()}")
                continue
            self.export_actor_fbx(sequence_actor, binding=binding)
        self.data["additional_components"] = self.additional_components

    @BaseExporter.add_to_percentage(10)
    def export_static_actors(self):
        """
        Export the static mesh level actors
        """
        level_actors = api_wrap.get_all_level_actors()
        for sequence_actor in level_actors:
            self.export_actor_fbx(sequence_actor)

    def export_actor_fbx(self, sequence_actor, binding=None):
        # type: (ue.Actor, Optional[ue.MovieSceneBindingProxy]) -> None
        """
        Export the actor as a fbx be it an actor that has a
        binding to the level sequence or static on the level

        Args:
            sequence_actor: The sequence actor to export as a fbx
            binding: The binding to the level sequence
        """
        supported_cls_tuple = tuple(unreal_constants.SUPPORTED_EXPORT_CLASSES)
        if not isinstance(sequence_actor, supported_cls_tuple):
            ue.log_warning(f"Skipping {sequence_actor}")
            return

        # skip the camera component as it's not needed
        actor_name = self.get_actor_name(sequence_actor)
        if not actor_name:
            return

        # set the fbx export file path
        self.ctx.use_suffix = actor_name
        fbx_path = self.ctx.fbx_file_path
        self.log(f"FBX Path: {fbx_path}")

        # export the fbx file to disk
        if binding:
            sequencer_utils.export_sequencer_fbx_file(
                fbx_path, self.map, self.ls, [binding])
        else:
            sequencer_utils.export_static_actor_fbx_file(
                fbx_path, sequence_actor)

        # build a dictionary of the asset export data
        asset_export_data = {
            "fbx_path": fbx_path,
            "is_camera": False,
            "namespace": actor_name
        }

        # save the camera data as a camera only
        if isinstance(sequence_actor, ue.CineCameraActor):
            asset_export_data["asset_type_name"] = "camera"
            asset_export_data["is_camera"] = True

        elif isinstance(sequence_actor, ue.SkeletalMeshActor):
            comp = sequence_actor.get_component_by_class(ue.SkeletalMeshComponent)
            metadata = api_wrap.get_metadata_tag_values(comp.skeletal_mesh_asset)
            asset_export_data.update(metadata)

        elif isinstance(sequence_actor, ue.StaticMeshActor):
            comp = sequence_actor.get_component_by_class(ue.StaticMeshComponent)
            metadata = api_wrap.get_metadata_tag_values(comp.static_mesh)
            asset_export_data.update(metadata)

        # add the data to the export data
        self.exported_files_to_data[fbx_path] = asset_export_data

        # add the actor to the additional components to publish
        self.additional_components[actor_name] = fbx_path

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


class USDLevelSequenceExporter(LevelSequenceExporter):
    def __init__(self):
        super().__init__()

    def export(self):
        """
        Export the level as all usd file
        """
        self.export_usd_file()
        self.publish_shot()
        self.render_movie_queue()
        self.finish_exporter_process()

    def export_usd_file(self):
        """
        Export the usd file as a stage all file
        """
        ue.log("Exporting usd file...")

        usd_stage_path = self.data["usd_stage_path"]
        self.ctx = context_utils.get_context_from_path(usd_stage_path)
        self.ctx.use_suffix = "all"
        self.ctx.set_next_save_version()

        # create the usd file directory
        usd_path = self.ctx.usd_file_path
        file_utils.create_directories(usd_path)

        # load the map to export
        map = ue.load_asset(self.data["map_path"])

        # create the usd file directory
        options = ue.LevelExporterUSDOptions()
        options.stage_options.meters_per_unit = 0.01       # Unreal units are cm
        options.stage_options.up_axis = ue.UsdUpAxis.Z_AXIS

        # run the asset export task
        task = ue.AssetExportTask()
        task.object = map
        task.filename = usd_path                            # .usda / .usdc / .usd
        task.automated = True                               # suppress dialogs
        task.prompt = False
        task.replace_identical = True
        task.options = options
        ue.Exporter.run_asset_export_task(task)

        # create the usd file directory
        ue.log(f"USD level export succeeded: {usd_path}")
        self.additional_components["usd_all"] = usd_path
