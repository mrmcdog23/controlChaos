""" Control Chaos executor for post process publishing """
import os
import unreal as ue
import ccunreal.utils.api_wrap as api_wrap
import ccunreal.utils.cc_wrap as cc_wrap
import cccore.file_env.context as context
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
import ccftrack.publish as publish
import ccftrack.shot as shot
from typing import Any


@ue.uclass()
class ControlChaosPIEExecutor(ue.MoviePipelinePIEExecutor):
    _bound = ue.uproperty(bool)

    @ue.ufunction(override=True)
    def on_begin_frame(self):
        """
        When the frame starts rendering build a list of jobs
        """
        super(ControlChaosPIEExecutor, self).on_begin_frame()
        queue = ue.get_editor_subsystem(ue.MoviePipelineQueueSubsystem).get_queue()
        self._jobs = [j for j in queue.get_jobs() if j.is_enabled()]

        if not self._bound:
            self.on_individual_job_finished_delegate.add_callable(self.on_job_finish)
            self._bound = True

    @staticmethod
    def child_sequences(master):
        # type: (ue.LevelSequence) -> dict
        """
        Build a dictionary of shot names to their level sequence from the master layer

        Returns:
            result: Dictionary of every shot under the master's Shot Track.
        """
        result = dict()
        tracks = master.find_tracks_by_exact_type(ue.MovieSceneCinematicShotTrack)
        for track in tracks:
            for section in track.get_sections():
                seq = section.get_sequence()
                if seq:
                    result[section.get_shot_display_name()] = seq
        return result

    def get_shot_and_sequence(self, ftshot, seq):
        ls_name = seq.get_name()
        use_sequence_name = None
        for sequence_name in ftshot.sequence_names:
            if ls_name.startswith(sequence_name):
                use_sequence_name = sequence_name
                break

        if not use_sequence_name:
            raise Exception("Can't find sequence name")

        use_shot_name = None
        ftshot.sequence_name = use_sequence_name
        for shot_name in ftshot.shot_names:
            if shot_name in ls_name:
                use_shot_name = shot_name
                break
        if not use_shot_name:
            raise Exception("Can't find shot name")

        data = {"sequence_name": use_sequence_name, "shot_name": use_shot_name}
        ue.log_warning(f"Level sequence data: {data}")
        return data

    def on_job_finish(self, job, success):
        # type: (Any, bool) -> None
        """
        When the job finishes find the current one and on completion upload to ftrack

        Args:
            job: The completed job on the render queue
            success: Whether it run successfully or not
        """
        ue.log_warning(f"[PostProcess] finished: job={job} success={success}")
        if not success:
            return
        # The delegate passes None, so use the snapshot. With several jobs this
        # fires once per job, so pop them in queue order.
        if job is None:
            job = self._jobs.pop(0) if self._jobs else None
        if job is None:
            return

        # get the settings
        config = job.get_configuration()
        setting = config.find_setting_by_class(ue.CCMoviePipelineSettings)

        output_setting = config.find_setting_by_class(ue.MoviePipelineOutputSetting)
        output_dir_raw = output_setting.output_directory.path
        output_dir = output_dir_raw.replace("{project_dir}", ue.Paths.project_dir())
        ue.log_warning(f"Render directory {output_setting.file_name_format}")

        ue.log_warning(f"Format {output_dir}")
        # if publish is not checked then skip
        publish_to_ftrack = setting.get_editor_property("bPublishToFTrack")
        if not publish_to_ftrack:
            ue.log_warning("Skipping the publish to FTrack")
            return

        task_name = setting.get_editor_property("Task").name.lower()
        ue.log_warning(f"Publishing to tasks name {task_name}")

        master = ue.load_asset(job.sequence.export_text())
        children = self.child_sequences(master)

        # Filter to only the shots ticked in the queue
        rendered = {s.outer_name for s in job.shot_info if s.enabled}

        ftshot = shot.FtShot()
        for shot_name, seq in children.items():
            if shot_name not in rendered:
                continue

            # get the level sequence metadata
            data = self.get_shot_and_sequence(ftshot, seq)
            data["task_name"] = task_name
            ue.log_warning(f"Rendering level sequence: {seq.get_path_name()}")

            # get the latest directory just rendered
            found_file_name = None
            for file_name in os.listdir(output_dir):
                if data["shot_name"] in file_name:
                    ue.log_warning(f"Found: {file_name}")
                    found_file_name = file_name
                    break

            full_path = file_utils.join_file_names(output_dir, found_file_name)
            if not file_name.endswith(".mov"):
                seq_data = sequence_utils.get_sequence_data(full_path)
                full_path = seq_data.padded_path
            else:
                data["movie_component_path"] = full_path

            # add additional data to the dictionary to publish
            data["file_sequences"] = [full_path]
            data["status_name"] = "WIP"
            data["category"] = "Image Sequence"
            data["comment"] = job.comment
            ue.log_warning(f"Data: {data}")

            # publish the sequence to ftrack
            publish_inst = publish.FtrackPublish(data)
            asset_version_id = publish_inst.asset_version["id"]
            ue.log_warning(f"[PostProcess] asset_version_id: {asset_version_id}")
            cc_wrap.notification(f"Movie successfully published {shot_name}", "shot_built", duration=3)
