""" Submit caches to publish the farm progress page """
import os
import hou
import cccore.deadline.submit as submit
import cccore.utils.file_utils as file_utils
import cccore.core_constants as core_constants
from cchoudini.wizard.pages.hou_progress_page import HouProgressPage


BUILD_SHOTS_EXPORTER = "houdini/python/cchoudini/exporter/build_shots_exporter.py"


class BuildShotProgressPage(HouProgressPage):
    title = "Build Shot Progress Page"
    subtitle = "Submitting Build SHots on Deadline"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prefix = str()
        self.metadata_path = str()
        self.custom_dict = dict()
        self.publish_id = str()
        self.maya_job_id = str()
        self.batch_name = str()

    def deadline_export(self):
        """
        Submit the cache to deadline
        """
        self.add_message("Submitting to Deadline...")
        build_exporter_path = self.project_data.get_relative_path(BUILD_SHOTS_EXPORTER)
        prefix = file_utils.get_file_name(self.data["template_file"])

        self.set_output_paths()
        self.save_data_to_json()
        self.add_message(f"Written {self.metadata_file_path}")

        number_of_shots = len(self.data["publish_shots_list"])
        job_info_dict = {
            "Name": f"Creating {number_of_shots} shots (Build)",
            "Pool": "h_batch",
            "FailureDetectionJobErrors": 1,
            "OverrideJobFailureDetection": True,
            "AddSlackNotification": True
        }

        plugin_info_dict = {
            "Arguments": self.metadata_file_path,
            "PythonFile": build_exporter_path
        }
        custom_dict = {
            "prefix": prefix
        }
        build_job = submit.HoudiniPyDeadlineSubmit(
            job_info_dict,
            plugin_info_dict,
            custom_dict
        )
        build_job_id = build_job.submit_job()
        self.batch_name = build_job.batch_name
        self.add_submit_data(build_job_id, core_constants.HOUDINI_BUILD)
        self.add_message("Submitted!")
        self.process_finished()
