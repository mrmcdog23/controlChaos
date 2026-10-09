""" Create a movie render """
from ccgeneral.wizard.pages.progress_page import ProgressPage
import no8unreal.render.movie_render_queue as mrq
import no8core.utils.file_utils as file_utils


class MovieProgressPage(ProgressPage):
    """
    Progress page specific to animation to
    deal with lighting submitting
    """
    title = "Creating movie render queue render"
    subtitle = "Creating local render"

    def __init__(self, parent=None):
        super(MovieProgressPage, self).__init__(parent)

    def export(self):
        """
        Render the lighting scene and publish to ftrack
        """
        self.add_message("Generating movie render...")

        ftquery = self.wizard().ftquery
        ctx = self.wizard().ctx
        ls_path = self.wizard().ls_path
        mp_path = self.wizard().mp_path
        resolution = ftquery.resolution

        # get the render directory
        ctx.use_aov = "main"
        ctx.use_ext = "exr"
        ctx.use_next_sequence_version()
        use_version = ftquery.get_correct_version(ctx.sequence_path)
        ctx.use_version = use_version

        sequence_path_linux = ctx.sequence_path
        sequence_path = file_utils.convert_path_to_win(sequence_path_linux)
        self.data["version_num"] = use_version
        self.data["file_sequences"] = [sequence_path]
        self.data["playable_component"] = sequence_path

        self.add_message(f"Creating movie render queue job...")
        job_cls = mrq.CreateMovieRenderQueueJob(
            False, sequence_path, ls_path, mp_path, resolution, data=self.data, mpp=self
        )
        job_cls.create_job()
        job_cls.run_render()

