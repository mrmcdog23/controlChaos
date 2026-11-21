import unreal as ue


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