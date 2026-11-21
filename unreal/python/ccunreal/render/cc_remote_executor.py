import unreal as ue
import ccunreal.utils.api_wrap as api_wrap


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

    def on_job(self, job, success):

        for job in queue.get_jobs():
            print("Job:", job.job_name, "|", job.sequence)
            for shot in job.shot_info:
                print("  Shot:", shot.outer_name, "/", shot.inner_name,
                      "| enabled:", shot.enabled)



        ue.log_warning(f"[PostProcess] finished: job={job} success={success}")
        if not success:
            return
        # The delegate passes None, so use the snapshot. With several jobs this
        # fires once per job, so pop them in queue order.
        if job is None:
            job = self._jobs.pop(0) if self._jobs else None
        if job is None:
            return
        out = job.get_configuration().find_setting_by_class(ue.MoviePipelineOutputSetting)
        ue.log_warning(f"[PostProcess] {job.job_name} -> {out.output_directory.path}")

        soft_path = job.sequence  # unreal.SoftObjectPath
        seq_path = soft_path.export_text()
        ue.log_warning(f"[PostProcess] sequence: {seq_path}")

        ls = ue.load_asset(seq_path)
        metadata_dict = api_wrap.get_metadata_tag_values(ls)
        ue.log_warning(f"[PostProcess] metadata_dict: {metadata_dict}")
