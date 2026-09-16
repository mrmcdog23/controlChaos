""" Submit renders to the farm page """
import os
import hou
from ccgeneral.wizard.pages.progress_page import ProgressPage
import cccore.deadline.submit as submit
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.hou_constants as hou_constants
import cchoudini.render.create_render_jobs as create_render_jobs


# constants
COMP_EXPORTER = "houdini/python/cchoudini/exporter/comp_exporter.py"
RENDER_NODE_TYPES = hou_constants.RENDER_NODE_TYPES
ROP_TYPE_TO_PICTURE_PARM = hou_constants.ROP_TYPE_TO_PICTURE_PARM


class RenderProgressPage(ProgressPage):
    title = "Houdini Progress Page"
    subtitle = "Submitting Render Nodes"
    render_node_type = str()

    def __init__(self, parent=None):
        super(RenderProgressPage, self).__init__(parent)
        self.batch_name = str()
        self.prefix = str()
        self.sequences = list()
        self.custom_dict = dict()
        self.render_rops = list()
        self.deadline_node = None

    def deadline_export(self):
        """
        Export locally by adding the wizard variables to the
        exporter variables class and exporting. If it fails then
        set red in the message
        """
        hou.hipFile.save()

        # set progress
        self.add_message("Submitting to Deadline...")
        self.initialize_data()
        self.submit_renders()
        self.submit_comp_job()
        self.submit_publish_job()

        self.add_message("Submitted!")
        self.process_finished()

    def submit_renders(self):
        """
        Submit a tile render
        """
        raise NotImplemented

    def initialize_data(self):
        """
        Initialize the class data variables
        """
        # save backup file and data
        self.set_output_paths()
        self.save_data_to_json()
        self.prefix, _ = os.path.splitext(hou.hipFile.basename())

        # loop through all inputs
        self.deadline_node = hou.node(self.data["node_path"])
        self.render_rops = hou_utils.input_nodes_of_type(self.deadline_node, RENDER_NODE_TYPES)

    def submit_comp_job(self):
        """
        Submit the comp job if there is a comp input node
        """
        # loop through all inputs
        deadline_node = hou.node(self.data["node_path"])
        comp_rop = hou_utils.input_nodes_of_type(deadline_node, ["comp"])
        if comp_rop:
            self.create_comp_job()

    def submit_publish_job(self):
        """
        Submit the project to ftrack job if set
        """
        if not self.data["publish"]:
            return

        publish_job = create_render_jobs.create_publish_job(
            self.prefix,
            self.metadata_file_path,
            self.job_ids,
            self.batch_name
        )
        publish_job_id = publish_job.submit_job()
        self.add_submit_data(publish_job_id, self.FTRACK_PUBLISH)

    def submit_tile_assembler(self, render_id, tile_job_info_dict, tile_plugin_info_dict):
        # type: (str, dict, dict) -> None
        """
        Submit the tile assembler job to the farm

        Args:
            render_id: The render tile job id
            tile_job_info_dict: Assembler job dictionary to submit
            tile_plugin_info_dict: Assembler plugin dictionary to submit
        """
        # get the nuke project version
        assembly_job = submit.TileAssemblerDeadlineSubmit(tile_job_info_dict,
                                                          tile_plugin_info_dict,
                                                          self.custom_dict
                                                          )
        # add as a dependency to the main job
        assembly_job.add_dependencies(render_id, self.batch_name)
        assembly_id = assembly_job.submit_job()
        self.add_submit_data(assembly_id, self.TILE_ASSEMBLY)
        self.add_message(f"Job Id: {assembly_id}")

    def create_comp_job(self):
        """
        Create generate the ass file job
        """
        comp_exporter_path = self.project_data.get_relative_path(COMP_EXPORTER)
        job_name = f"{self.prefix} (Comp)"
        job_info_dict = {
            "Name": job_name,
            "Pool": "h_batch"
        }
        plugin_info_dict = {
            "Arguments": self.metadata_file_path,
            "PythonFile": comp_exporter_path
        }
        comp_job = submit.HoudiniPyDeadlineSubmit(
            job_info_dict,
            plugin_info_dict,
            self.custom_dict
        )
        comp_job.add_dependencies(self.job_ids, self.batch_name)
        ass_job_id = comp_job.submit_job()
        self.batch_name = comp_job.batch_name
        self.add_submit_data(ass_job_id, self.HOUDINI_COMP)
