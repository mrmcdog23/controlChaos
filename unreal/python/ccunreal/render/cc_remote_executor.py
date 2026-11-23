import os
import unreal as ue
import ccunreal.utils.api_wrap as api_wrap
import cccore.file_env.context as context
import cccore.utils.sequence_utils as sequence_utils
import ccftrack.publish as publish
import ccunreal.utils.cc_wrap as cc_wrap
from cccore.utils import file_utils


@ue.uclass()
class ControlChaosPIEExecutor(ue.MoviePipelinePIEExecutor):

    _bound = ue.uproperty(bool)

    @ue.ufunction(override=True)
    def on_begin_frame(self):
        super(ControlChaosPIEExecutor, self).on_begin_frame()
        queue = ue.get_editor_subsystem(ue.MoviePipelineQueueSubsystem).get_queue()
        self._jobs = [j for j in queue.get_jobs() if j.is_enabled()]

        if not self._bound:
            self.on_individual_job_finished_delegate.add_callable(self.on_job)
            self._bound = True

    @staticmethod
    def child_sequences(master):
        """Return {shot_name: sequence_path} for every shot under the master's Shot Track."""
        result = {}
        tracks = master.find_tracks_by_exact_type(ue.MovieSceneCinematicShotTrack)
        for track in tracks:
            for section in track.get_sections():
                seq = section.get_sequence()
                if seq:
                    result[section.get_shot_display_name()] = seq
        return result

    def on_job(self, job, success):
        ue.log_warning(f"[PostProcess] finished: job={job} success={success}")
        if not success:
            return
        # The delegate passes None, so use the snapshot. With several jobs this
        # fires once per job, so pop them in queue order.
        if job is None:
            job = self._jobs.pop(0) if self._jobs else None
        if job is None:
            return

        master = ue.load_asset(job.sequence.export_text())
        children = self.child_sequences(master)

        # Only the shots ticked in the queue
        rendered = {s.outer_name for s in job.shot_info if s.enabled}

        for shot_name, seq in children.items():
            if shot_name not in rendered:
                continue

            data = api_wrap.get_metadata_tag_values(seq)
            ue.log_warning(f"[PostProcess] level sequence path: {seq.get_path_name()}")
            ue.log_warning(f"[PostProcess] metadata_dict: {data}")

            ctx = context.Context(overrides=data)
            ue.log_warning(f"[PostProcess] render_dir: {ctx.render_dir}")

            versions_dir = os.listdir(ctx.render_dir)
            versions_dir.sort()
            render_version_dir = file_utils.join_file_names(ctx.render_dir, versions_dir[-1])
            ue.log_warning(f"[PostProcess] Latest version: {render_version_dir}")

            seq_data = sequence_utils.get_first_sequence_from_dir(render_version_dir)
            data["file_sequences"] = [seq_data.padded_path]
            data["status_name"] = "WIP"
            data["comment"] = job.comment

            ue.log_warning(f"[PostProcess] data: {data}")

            publish_inst = publish.FtrackPublish(data)
            asset_version_id = publish_inst.asset_version["id"]
            ue.log_warning(f"[PostProcess] asset_version_id: {asset_version_id}")
            cc_wrap.notification(f"Movie successfully published {shot_name}", "shot_built", duration=3)
