""" Control Chaos executor for post process publishing """
import os
import unreal as ue
import ccunreal.utils.api_wrap as api_wrap
import ccunreal.utils.cc_wrap as cc_wrap
import cccore.file_env.context as context
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
import ccftrack.publish as publish
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

        for shot_name, seq in children.items():
            if shot_name not in rendered:
                continue

            # get the level sequence metadata
            data = api_wrap.get_metadata_tag_values(seq)
            ue.log_warning(f"Rendering level sequence: {seq.get_path_name()}")

            ctx = context.Context(overrides=data)
            ue.log_warning(f"Root render directory {ctx.render_dir}")

            # get the latest directory just rendered
            versions_dir = os.listdir(ctx.render_dir)
            versions_dir.sort()
            render_version_dir = file_utils.join_file_names(ctx.render_dir, versions_dir[-1])
            ue.log_warning(f"Latest version directory {render_version_dir}")

            # add additional data to the dictionary to publish
            seq_data = sequence_utils.get_first_sequence_from_dir(render_version_dir)
            data["file_sequences"] = [seq_data.padded_path]
            data["task_name"] = task_name
            data["status_name"] = "WIP"
            data["category"] = "Image Sequence"
            data["comment"] = job.comment

            # publish the sequence to ftrack
            publish_inst = publish.FtrackPublish(data)
            asset_version_id = publish_inst.asset_version["id"]
            ue.log_warning(f"[PostProcess] asset_version_id: {asset_version_id}")
            cc_wrap.notification(f"Movie successfully published {shot_name}", "shot_built", duration=3)
