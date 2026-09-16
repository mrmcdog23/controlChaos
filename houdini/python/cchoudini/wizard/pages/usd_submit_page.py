""" Submitting the USD render to the farm """
import os
import hou
import cccore.deadline.submit as submit
import cchoudini.node.usdrender_rop_node as usdrender_rop_node
from cchoudini.wizard.pages.hou_progress_page import HouProgressPage


class USDRenderProgressPage(HouProgressPage):
    title = "Houdini Progress Page"
    subtitle = "Submitting USD Render Node"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prefix = str()
        self.data_file_path = str()

    def deadline_export(self):
        """
        Export locally by adding the wizard variables to the
        exporter variables class and exporting. If it fails then
        set red in the message
        """
        hou.hipFile.save()

        # set progress
        self.add_message("Submitting to Deadline...")

        # set the playable component
        rop_node = hou.node(self.data["node_path"])
        usd_inst = usdrender_rop_node.USDRenderRopNode(rop_node)
        self.data["playable_component"] = usd_inst.output_path

        # set the start and end frame for the publish
        start, end = self.get_frame_range()
        self.data["start"] = start
        self.data["end"] = end

        # save backup file and data
        self.data_file_path = self.save_data_to_json()
        self.prefix, _ = os.path.splitext(hou.hipFile.basename())

        self.submit_usd_renders()
        self.process_finished()

    def get_frame_range(self):
        # type: () -> (int, int)
        """
        Find the frame range from the selected node
        """
        usd_render_node = hou.node(self.data["node_path"])
        start = usd_render_node.parm("f1").eval()
        end = usd_render_node.parm("f2").eval()
        return int(start), int(end)

    @property
    def frame_range(self):
        # type: () -> str
        """
        The render frame range as text
        """
        start, end = self.get_frame_range()
        return f"{int(start)}-{int(end)}"

    def submit_usd_renders(self):
        """
        Submit to deadline
        """
        custom_dict = {"prefix": self.prefix}
        job_info_dict = self.get_render_job_dict()
        job_info_dict["Name"] = f"{self.prefix} (USD Render)"
        job_info_dict["Frames"] = self.frame_range
        plugin_info_dict = {"Arguments": self.data_file_path}

        # submit the usd render to deadline
        usd_render_job = submit.USDRenderDeadlineSubmit(
            job_info_dict, plugin_info_dict, custom_dict)
        usd_render_job_id = usd_render_job.submit_job()
        self.add_submit_data(usd_render_job_id, self.USD_RENDER)
        self.logger.info(f"Submitted: {usd_render_job_id}")

        # delete the python home as it breaks the publish
        python_home = os.environ['PYTHONHOME']
        del os.environ['PYTHONHOME']

        # submit the published job
        publish_job_info_dict = {"Name": self.prefix + " (Publish)"}
        plugin_info_dict = {"DataFilePath": self.data_file_path,
                            "AddSlackNotification": True
                            }
        publish_job = submit.FTrackPublishDeadlineSubmit(publish_job_info_dict,
                                                         plugin_info_dict,
                                                         custom_dict
                                                         )
        publish_job.add_dependencies(usd_render_job_id, usd_render_job.batch_name)
        publish_id = publish_job.submit_job()

        # reinstate the python home
        os.environ['PYTHONHOME'] = python_home

        self.add_submit_data(publish_id, self.FTRACK_PUBLISH)
        self.add_message("Submitted!")
        self.process_finished()
