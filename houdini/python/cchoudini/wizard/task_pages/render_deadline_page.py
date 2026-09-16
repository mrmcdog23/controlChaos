""" Render on Deadline options page """
from ccgeneral.wizard.pages.base_page import BasePublishPage
import ccgeneral.widgets.deadline_widget as deadline_widget
import cccore.utils.file_utils as file_utils
import cccore.data.server_data as server_data
import cchoudini.wizard.widgets.tile_rendering as tile_rendering


class RenderDeadlinePage(BasePublishPage):
    title = "Render Deadline Page"
    subtitle = "Select the render deadline options"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ass_dw = None
        self.render_dw = None
        self.tile_wdg = None
        self.create_layout()

    def create_layout(self):
        """
        Create the layout of two different
        deadline widgets one for the ass files
        and one for the kick
        """
        # create the ass deadline widget
        ass_settings = {"use_pool": "h_batch"}
        self.ass_dw = deadline_widget.DeadlineWidget(settings=ass_settings)
        self.ass_dw.grp_deadline.setTitle("Ass Options")
        self.main_layout.addWidget(self.ass_dw)

        # set the chuk size to one for the kick
        project_data = server_data.ProjectData()
        houdini_render_pool = project_data.get("houdini_render_pool")
        kick_settings = {"use_pool": houdini_render_pool,
                         "one_frame_per_task": True,
                         }
        self.render_dw = deadline_widget.DeadlineWidget(settings=kick_settings)
        self.render_dw.grp_deadline.setTitle("Render Options")
        self.main_layout.addWidget(self.render_dw)

        # add check box for tile rendering
        self.tile_wdg = tile_rendering.TileRenderingWidget()
        self.main_layout.addWidget(self.tile_wdg)

    def initializePage(self):
        """
        If it's not an arnold render hide the options
        """
        if "arnold" not in self.data["renderers"]:
            self.ass_dw.setHidden(True)

    @property
    def ass_chunk_size(self):
        # type: () -> int
        """ Get the size of the chunks """
        start = self.data["start"]
        end = self.data["end"]
        chunk_size = file_utils.get_number_of_chunks(
            start, end, self.ass_dw.num_of_chunks)
        return chunk_size

    def validatePage(self):
        # type: () -> int
        """
        Store the selected options in the wizard data
        """
        self.data["deadline_mode"] = True
        self.data["ass_chunk_size"] = self.ass_chunk_size
        self.data["ass_pool"] = self.ass_dw.pool
        self.data["ass_priority"] = self.ass_dw.priority
        self.data["render_chunk_size"] = self.render_dw.num_of_chunks
        self.data["render_pool"] = self.render_dw.pool
        self.data["render_priority"] = self.render_dw.priority
        self.data["tile_rendering"] = self.tile_wdg.do_tile_rendering
        self.data["tile_x"] = self.tile_wdg.tile_x
        self.data["tile_y"] = self.tile_wdg.tile_y
        return True


