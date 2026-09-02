""" Publish an image sequence to FTrack """
import os
import ccftrack.publish as publish
from ccgeneral.wizard.pages.progress_page import ProgressPage
import cccore.file_env.context as context
import cccore.utils.file_utils as file_utils
import cccore.utils.sequence_utils as sequence_utils


class UploadProgressPage(ProgressPage):
    title = "Sequence Publishing Progress Page"
    subtitle = "Sequence Publishing the version"

    def __init__(self, parent=None):
        super(UploadProgressPage, self).__init__(parent)
        self.publish_sequences_list = list()
        self.project_name = os.environ["PROJECT_NAME"]

    def local_export(self):
        """
        Export locally by adding the wizard variables to the
        exporter variables class and exporting. If it fails then
        set red in the message
        """
        # publishing to ftrack
        self.add_message("Submitting to FTrack")
        self.local_progress(20)

        # publish the data
        pub_inst = publish.FtrackPublish(self.data)
        asset_version = pub_inst.asset_version
        asset_version_id = asset_version["id"]
        self.data["version"] = asset_version["version"]

        self.add_message(f"Asset Version: {asset_version_id}")
        self.local_progress(20)
        self.add_message("Submitted!")

        # once the process is finished go to the next page
        self.process_finished()
