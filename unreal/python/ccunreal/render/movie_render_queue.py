""" Create a local movie render queue job """
import os
import unreal as ue
from typing import Optional
import cccore.core_constants as core_constants
import cccore.data.server_data as server_data
import cccore.utils.file_utils as file_utils
import cccore.utils.ffmpeg_utils as ffmpeg_utils
import cccore.utils.sequence_utils as sequence_utils
import ccunreal.utils.api_wrap as api_wrap
import ccftrack.asset_version as asset_version


class CreateMovieRenderQueueJob(object):
    """
    Create a movie render queue job and render  option also
    """
    def __init__(self, add_to_queue, sequence_path, ls_path, map_path, resolution, asset_version_id=None):
        # type: (bool, str, str, str, list[int], Optional[str]) -> None
        """
        Args:
            add_to_queue: If true add to queue else render
            sequence_path: Path to the destination sequence
            ls_path: Level sequence to render path
            map_path: Map path to render
            resolution: The output size. e.g. [1280, 720]
            asset_version_id: The asset version to upload to
        """
        self.sequence_path = sequence_path
        self.ls_path = ls_path
        self.map_path = map_path
        self.resolution = resolution
        self.asset_version_id = asset_version_id

        self.output_name = file_utils.get_file_name(sequence_path)
        self.output_dir = os.path.dirname(sequence_path)
        self.project_data = server_data.ProjectData()

        self.image_sequence = str()
        self.job = None
        self.comments = str()
        self._config = None

        global RENDER_QUEUE
        global QUEUE_EXECUTOR

        if add_to_queue:
            RENDER_QUEUE = api_wrap.get_queue()
        else:
            RENDER_QUEUE = ue.MoviePipelineQueue()

    def create_job(self):
        """
        Create a MoviePipelineExecutorJob and set its configurations

        Returns:
            ue.MoviePipelineExecutorJob
        """
        global RENDER_QUEUE

        self.job = RENDER_QUEUE.allocate_new_job(ue.MoviePipelineExecutorJob)
        self.job.set_editor_property('sequence', ue.SoftObjectPath(self.ls_path))
        self.job.set_editor_property('map', ue.SoftObjectPath(self.map_path))
        self.job.job_name = self.output_name
        self.job.author = core_constants.USERNAME

        self.set_output_setting()
        self.job.set_configuration(self.config)

    @property
    def config(self):
        # type: () -> ue.MoviePipelineMasterConfig
        """
        Create the default configuration of the movie render queue job

        Returns:
            config: Configured job config
        """
        if self._config:
            return self._config
        self._config = ue.MoviePipelinePrimaryConfig()
        self._config.initialize_transient_settings()
        anti_aliasing_setting = self._config.find_or_add_setting_by_class(
            ue.MoviePipelineAntiAliasingSetting.static_class())

        anti_aliasing_setting.temporal_sample_count = 1
        anti_aliasing_setting.engine_warm_up_count = 30
        anti_aliasing_setting.render_warm_up_frames = 30

        self._config.find_or_add_setting_by_class(ue.MoviePipelineDeferredPassBase.static_class())
        self._config.find_or_add_setting_by_class(ue.MoviePipelineImageSequenceOutput_EXR.static_class())
        return self._config

    def set_output_setting(self):
        """
        Set the output render settings to go to the correct place and format
        """
        file_name_format = self.output_name + ".{frame_number}"

        # set the output directory and name
        output_setting = self.config.find_or_add_setting_by_class(ue.MoviePipelineOutputSetting)
        output_setting.output_directory = ue.DirectoryPath(self.output_dir)
        output_setting.file_name_format = file_name_format
        output_setting.set_editor_property("override_existing_output", True)

        # set the output resolution
        width, height = self.resolution
        output_setting.output_resolution = ue.IntPoint(width, height)

        # set the image sequence name
        self.image_sequence = f"{self.output_dir}/{self.output_name}.####.exr"

    def run_render(self):
        """
        Run the movie render queue
        """
        global RENDER_QUEUE
        global QUEUE_EXECUTOR
        QUEUE_EXECUTOR = ue.MoviePipelinePIEExecutor()
        if self.asset_version_id:
            QUEUE_EXECUTOR.on_individual_job_finished_delegate.add_callable(self.upload_render)
        QUEUE_EXECUTOR.execute(RENDER_QUEUE)

    def upload_render(self, job, success):
        """
        Export locally by adding the wizard variables to the
        exporter variables class and exporting. If it fails
        then set red in the message
        """
        ftver = asset_version.FtAssetVersion()
        ftver.asset_version_id = self.asset_version_id
        ue.log_warning(f"Uploading: {self.sequence_path} to {self.asset_version_id}")
        ftver.add_component("MovieRender", self.sequence_path)

        mov_path = file_utils.temp_file_path(self.output_name, "mov")
        seq_data = sequence_utils.get_sequence_data(self.sequence_path)
        created = ffmpeg_utils.convert_sequence_to_movie(seq_data.start, seq_data.nuke_path, mov_path)
        if not created:
            ue.log_warning("Failed to create movie file")
            return

        ue.log(f"Uploading movie file: {mov_path}")
        ftver.add_playable_component(mov_path)
