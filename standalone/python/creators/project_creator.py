""" Create a project on FTrack """
from typing import Optional
import ccftrack.shot as shot
import cccore.base_ui as base_ui
import cccore.utils.cc_logging as cc_logging
import cccore.utils.ui_utils as ui_utils
from CCPySide import QtWidgets, QtCore, QtGui


class ProjectCreator(base_ui.StandaloneWindowBase):
    title = "Project Creator"
    window_icon = "project_creator"
    icon_to_widget = {
        "lbl_project_icon": "project",
        "lbl_houdini_icon": "houdini",
        "lbl_maya_icon": "maya",
        "lbl_nuke_icon": "nuke",
        "lbl_blender_icon": "blender",
        "lbl_flame_icon": "flame"
    }
    default_fps = "24"
    default_schema = "Control Chaos Feature"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ftshot = shot.FtShot()
        self.logger = cc_logging.cc_logger()
        self.app_name_cmb_dict = dict()

        # run setup functions
        self.populate_data()
        self.populate_app_versions()
        self.connect_signals()

    def populate_data(self):
        """
        Populate the dta of the ui
        """
        self.cmb_schema.addItems(self.ftshot.all_schemas)
        self.set_combobox_index(self.cmb_schema, self.default_schema)
        self.cmb_frames_per_second.addItems(self.ftshot.all_fps)
        self.set_combobox_index(self.cmb_frames_per_second, self.default_fps)

    def connect_signals(self):
        """
        Connect the widgets to the signals
        """
        self.le_name.textChanged.connect(self.update_code)
        self.btn_create_project.clicked.connect(self.create_project)

    def update_code(self):
        """
        Work out the project code from the name
        """
        selected_project_name = self.le_name.text()
        project_code = selected_project_name[0:3].upper()
        self.le_code.setText(project_code)

    def populate_app_versions(self):
        """
        Populate the application versions
        """
        for app_name, versions in self.ftshot.application_versions.items():
            combo_name = f"cmb_{app_name}"
            app_combobox = self.findChild(QtWidgets.QComboBox, combo_name)
            if app_combobox is None:
                continue
            app_combobox.addItems(versions)
            default_value = self.ftshot.attribute_default_value(app_name)
            self.set_combobox_index(app_combobox, default_value)
            self.app_name_cmb_dict[app_name] = app_combobox

    def validate_info(self):
        # type: () -> Optional[str]
        """
        Validate the info of the project
        """
        # Check the name is valid
        project_name = self.le_name.text()
        if " " in project_name:
            return "No spaces in project name only underescores"
        if len(project_name) < 5:
            return "Project name is too short"
        if project_name in self.ftshot.projects_names:
            return f"Project name {project_name} exists"

        # Check the code is valid
        project_code = self.le_code.text()
        if len(project_code) != 3:
            return "Project code is too short"
        if not project_code.isupper():
            return "Project code needs to be uppercase"
        if project_code in self.ftshot.projects_code:
            return f"Project code {project_code} exists"

    def create_project(self):
        """
        Creating project on ftrack
        """
        is_valid_message = self.validate_info()
        if is_valid_message:
            ui_utils.messagebox(
                "Info Invalid",
                is_valid_message,
                "critical",
                parent=self
            )
            return

        project_name = self.le_name.text()
        create = ui_utils.messagebox(
            "Create",
            f"Create Project {project_name}?",
            "question",
            buttons=["Create", "Cancel"],
            parent=self
        )
        if create == "Cancel":
            return

        self.logger.info(f"Creating on FTrack... {project_name}")
        schema_name = self.cmb_schema.currentText()
        project_code = self.le_code.text()
        fps = self.cmb_frames_per_second.currentText()

        # get information of the applications
        apps_dict = dict()
        for app_name, app_combobox in self.app_name_cmb_dict.items():
            apps_dict[app_name] = app_combobox.currentText()

        # create the ftrack project
        self.ftshot.create_ftrack_project(
            project_name, project_code, apps_dict, fps, schema_name
        )
        ui_utils.messagebox(
            "Complete", f"Project {project_name} created", "info", parent=self)


if __name__ == "__main__":
    base_ui.open_ui(ProjectCreator)
