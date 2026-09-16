""" Publish a houdini model page """
import ftrack_api
from ccgeneral.wizard.pages.base_page import BasePublishPage
import ccmaya.utils.maya_utils as maya_utils
import cccore.utils.file_utils as file_utils


WARNING = "color: rgb(255, 107, 2);"
GOOD = "color: rgb(85, 255, 0);"


class ModelingPage(BasePublishPage):
    title = "Create Thumbnail Page"
    subtitle = "Create a thumbnail for the asset"

    def __init__(self, parent=None):
        super(ModelingPage, self).__init__(parent)
        self.ftasset = None
        self.connect_signals()

    def set_no_update(self, task_type):
        # type: (str) -> None
        """
        Set the checkbox of the update if it is not possible to

        Args:
            task_type: Name of the task type to update
        """
        message = f"No {task_type} has been published to update"
        self.txt_information.setText(message)
        self.chk_update_lookdev.setChecked(False)
        self.chk_update_lookdev.setEnabled(False)

    def initializePage(self):
        """
        Analyse the previous model for mesh consistency
        """
        ftasset = self.wizard().ftasset
        data = self.wizard().data
        ftasset.asset_build_name_type = data.get("asset_build_name_type")
        ftasset.asset_build_name = data.get("asset_build_name")

        # get latest model version. If there isn't one then skip
        ftasset.task_name = "Modeling"
        latest_model_version = ftasset.latest_asset_version
        if not latest_model_version:
            self.set_no_update("model")
            return

        # check if there is a published lookdev version to update
        ftasset.task_name = "Lookdev"
        if not ftasset.latest_asset_version:
            self.set_no_update("lookdev")
            return

        # check the last model vertex information
        # and check the mesh names are the same
        mesh_data = maya_utils.get_mesh_data()
        latest_mesh_data = self.get_latest_mesh_data(latest_model_version)
        geo_same = list(mesh_data.keys()) == list(latest_mesh_data.keys())
        if not geo_same:
            self.txt_information.setText("The geometry of the new model"
                                         " is not the same as the last publish")
            self.txt_information.setStyleSheet(WARNING)
            return

        # compare the mesh counts of the meshes
        message = str()
        for mesh, vertex_num in mesh_data.items():
            if latest_mesh_data[mesh] != vertex_num:
                message = f"{mesh} has a different vertex count\n"

        # if there is a mismatch then set the message
        if message:
            self.txt_information.setText(message)
            self.txt_information.setStyleSheet(WARNING)
            return

        self.txt_information.setText("Ready for update")
        self.txt_information.setStyleSheet(GOOD)

    def get_latest_mesh_data(self, latest_model_version):
        # type: (ftrack_api.entity.asset_version) -> dict
        """
        Get the latest published models mesh data dictionary

        Args:
            latest_model_version: Latest model asset

        Returns:
            Mesh name to the vertex count
        """
        ftver = self.wizard().ftver
        ftver.asset_version_id = latest_model_version["id"]
        asset_data_path = ftver.get_component_path("AssetData")
        asset_data = file_utils.read_json(asset_data_path)
        return asset_data["mesh"]

    def connect_signals(self):
        """
        Connect the signal to the widget
        """
        self.chk_update_lookdev.toggled.connect(self.enable_publish)

    def enable_publish(self, checked):
        # type: (bool) -> None
        """
        Enable publish new checkbox

        Args:
            checked: Whether to set checked
        """
        self.chk_publish_new.setEnabled(checked)

    def validatePage(self):
        """
        Store the update lookdev option
        """
        update_lookdev = self.chk_update_lookdev.isChecked()
        publish_new = self.chk_publish_new.isChecked()
        self.wizard().data["update_lookdev"] = update_lookdev
        self.wizard().data["publish_new"] = publish_new
        return True

    def isComplete(self):
        # type: () -> bool
        """
        Always page is complete
        """
        return True

    def nextId(self):
        """
        Will go to the next page
        """
        return self.wizard().FINAL_PAGE
