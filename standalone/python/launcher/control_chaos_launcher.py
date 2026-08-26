""" Launcher of daydreamer tools and applications """
import os
import subprocess
import cccore.base_ui as base_ui
import cccore.app_starter as app_starter
import cccore.core_constants as core_constants
import cccore.utils.cc_logging as cc_logging
import cccore.data.server_data as server_data
import cccore.folder_creator as folder_creator
import ccftrack.base as base
import ccftrack.shot as shot
from CCPySide import QtWidgets, QtCore, QtGui
from ccgeneral.widgets.line_browser import LineBrowser


SELECTED_COLOUR = "rgb(0, 0, 255)"
DESELECTED_COLOUR = "rgb(20, 20, 20)"
FRAME_STYLE = "background-color: {0};border: 1px solid rgb(255, 85, 0);"
DOUBLE_CLICK = "background-color: rgb(50, 50, 250);border: 1px solid rgb(255, 255, 255);"
WRAPPER_PATH = "{0}/wrapper.py"


class AppToolWidget(base_ui.WidgetBase):
    ui_name = "app_tool"

    def __init__(self, parent, appclass):
        super(AppToolWidget, self).__init__(parent, appclass)
        self.appclass = appclass()
        self.pw = parent
        self.is_selected = False
        self.class_name = type(self.appclass).__name__

        # take the data from the class and store in the widget
        self.name = self.appclass.name
        self.display_text = self.appclass.display_text
        self.app_versions = self.appclass.app_versions
        self.is_app = self.appclass.is_app

        # set the app label and icon
        self.lbl_display_name.setText(self.display_text)
        self.apply_widget_to_icon(self.lbl_app_icon, self.appclass.icon)

    def set_selected(self):
        """
        Set the widget selected and change the style sheet
        """
        style = FRAME_STYLE.format(SELECTED_COLOUR)
        self.frame.setStyleSheet(style)
        self.is_selected = True

    def set_deselected(self):
        """
        Deselect the widget and set the de-select stylesheet
        """
        style = FRAME_STYLE.format(DESELECTED_COLOUR)
        self.frame.setStyleSheet(style)
        self.is_selected = False

    def mousePressEvent(self, event):
        """
        When an item is clicked deleted all and set the new only selected
        """
        self.pw.deselect_all()
        self.set_selected()
        self.pw.update_selection()

    def mouseDoubleClickEvent(self, event):
        """
        Highlight the widget when double-clicked
        """
        self.frame.setStyleSheet(DOUBLE_CLICK)


class ControlChaosLauncher(base_ui.StandaloneWindowBase):
    title = "Launcher"
    window_icon = "launcher"
    widget_to_icon = {
        "lbl_project_icon": "project",
        "btn_refresh": "refresh",
        "btn_project_root": "roots"
    }
    add_cc_title_name = True

    def __init__(self):
        super().__init__()
        # define class variables
        self.project_data = None
        self.app_list = list()
        self.tool_list = list()
        self.app_widgets = list()
        self.app_versions = list()
        self.all_projects_data = dict()

        # initialize data
        self.server_data = server_data.ServerData()
        self.ui_settings = QtCore.QSettings('control_chaos', 'launcher')
        self.logger = cc_logging.cc_logger()
        self.ftbase = base.FtBase()
        self.ftshot = shot.FtShot(session=self.ftbase.session)

        self.create_layout()
        self.populate_apps_and_tools()
        self.populate_projects()
        self.load_from_settings()
        self.update_project_data()
        self.connect_signals()

    def load_from_settings(self):
        """
        Load the saved settings from the QSettings
        """
        # restore height and width
        height = self.ui_settings.value("height", 600)
        width = self.ui_settings.value("width", 300)
        self.resize(int(width), int(height))

        # radio buttons
        tools = self.ui_settings.value("tools", 0)
        self.rbn_tools.setChecked(int(tools))
        app = self.ui_settings.value("app", 0)
        self.rbn_apps.setChecked(int(app))

        # set the flame users name
        self.filter_app_or_tool_list()
        self.roots_dict = self.ui_settings.value("project_roots", dict())

        project_name = self.ui_settings.value("project_name")
        self.set_combobox_index(self.cmb_project, project_name)

    def closeEvent(self, event):
        """
        Save the settings on close
        """
        # store height and width
        self.ui_settings.setValue("height", self.size().height())
        self.ui_settings.setValue("width", self.size().width())

        # radio buttons check
        tools = int(self.rbn_tools.isChecked())
        self.ui_settings.setValue("tools", tools)
        app = int(self.rbn_apps.isChecked())
        self.ui_settings.setValue("app", app)

        project_name = self.cmb_project.currentText()
        self.ui_settings.setValue("project_name", project_name)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.rbn_apps.clicked.connect(self.filter_app_or_tool_list)
        self.rbn_tools.clicked.connect(self.filter_app_or_tool_list)
        self.btn_launch.clicked.connect(self.launch_selected)
        self.cmb_project.currentIndexChanged.connect(self.update_project_data)
        self.cmb_application_version.currentIndexChanged.connect(self.set_launch_button_text)
        self.btn_refresh.clicked.connect(self.populate_projects)
        self.btn_project_root.clicked.connect(self.show_project_root)

    def show_project_root(self, show):
        """
        Hide or show the project root widget
        """
        self.wgt_project_root.setHidden(not show)

    def create_layout(self):
        """
        Create the layout for the ui
        """
        self.wgt_project_root = LineBrowser(
            self, "dir", "Select Project Root", "", "Project Root")
        self.lyt_project_root.addWidget(self.wgt_project_root)
        self.wgt_project_root.setHidden(True)

    def update_project_data(self):
        """
        Update the project data based on the selected project
        """
        project_name = self.cmb_project.currentText()
        self.ftbase.project_name = project_name
        self.project_app_versions = self.ftbase.project_app_versions
        self.project_data = server_data.ProjectData(project_name=project_name)

        # set the project root
        roots_dict = self.ui_settings.value("project_roots", dict())
        project_name = self.cmb_project.currentText()
        project_root = roots_dict.get(project_name, str())
        self.wgt_project_root.set_file_path(project_root)

        self.update_selection()

    def populate_projects(self):
        """
        Populate the projects
        """
        self.cmb_project.clear()

        project_names_list = list()
        for project_code, project_name in self.ftbase.project_code_to_name.items():
            self.cmb_project.addItem(project_name, project_code)
            project_names_list.append(project_name)
        self.create_completer(self.cmb_project, items_list=project_names_list)

    def create_app_tool_list(self, app_tool_list):
        """
        From the apps file populate the tools and apps widgets list
        """
        # create the widget
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # initialize the index and row
        row_index = 0
        column_index = 0

        for appclass in app_tool_list:
            app_tool_widget = AppToolWidget(self, appclass)
            layout.addWidget(app_tool_widget, row_index, column_index)
            self.app_widgets.append(app_tool_widget)

            # once the column is to reset and go to next row
            column_index += 1
            if column_index == 1:
                column_index = 0
                row_index += 1
        return widget

    def populate_apps_and_tools(self):
        """
        From the apps file populate the tools and apps widgets list
        """
        self.app_list = self.create_app_tool_list(app_starter.APPLICATIONS)
        self.app_or_tool_layout.addWidget(self.app_list)
        self.tool_list = self.create_app_tool_list(app_starter.TOOLS)
        self.app_or_tool_layout.addWidget(self.tool_list)
        self.filter_app_or_tool_list()

    def filter_app_or_tool_list(self):
        """
        Hide or show the application based on selection in the radio buttons
        """
        self.deselect_all()
        show_apps = self.rbn_apps.isChecked()
        self.app_list.setHidden(not show_apps)
        self.tool_list.setHidden(show_apps)
        self.btn_launch.setEnabled(False)
        self.btn_launch.setText("L A U N C H")
        self.wdg_application_version.setHidden(not show_apps)

    def deselect_all(self):
        """
        Deselect app application widgets
        """
        for app_tool_widget in self.app_widgets:
            app_tool_widget.set_deselected()

    def get_selected_app(self):
        # type: () -> QtWidgets.QWidget
        """
        Get the selected application widget
        """
        for app_tool_widget in self.app_widgets:
            if app_tool_widget.is_selected:
                return app_tool_widget

    def update_selection(self):
        """
        Make the options none selectable until an app or tool is selected
        """
        selected_app = self.get_selected_app()
        if not selected_app:
            return

        # update app versions
        if self.rbn_apps.isChecked():
            application_versions = self.ftbase.application_versions[selected_app.name]
            project_version = self.project_app_versions[selected_app.name]
            self.cmb_application_version.clear()
            self.cmb_application_version.addItems(application_versions)
            self.set_combobox_index(self.cmb_application_version, project_version)

        # find the application name
        self.set_launch_button_text()

    def set_launch_button_text(self):
        """
        Update the launch button text
        """
        app_version = self.cmb_application_version.currentText()
        selected_app = self.get_selected_app()

        # get the button text. add the version
        launch_text = f"L A U N C H: {selected_app.display_text}"
        if selected_app.is_app:
            launch_text = f"{launch_text} {app_version}"

        self.btn_launch.setText(launch_text)
        self.btn_launch.setEnabled(True)

    def does_exe_path_exist_on_disk(self):
        # type: () -> bool
        """
        Check and error if the exe path exists

        Returns:
            False if it is not installed
        """
        selected_app = self.get_selected_app()
        use_version = self.cmb_application_version.currentText()

        # build the exe path
        selected_app.appclass.use_version = use_version
        exe_path = selected_app.appclass.exe_path

        if exe_path and not os.path.exists(exe_path):
            message = f"{exe_path} is not installed"
            QtWidgets.QMessageBox.critical(self, "No Exe", message)
            return False
        return True

    @property
    def is_slate_ffmpeg_installed(self):
        # type: () -> bool
        """
        Check if the slate creator is running and if the ffmpeg is installed
        """
        selected_app = self.get_selected_app()

        # if it is not the slate creator continue
        if selected_app.name != "slate_maker_tool":
            return True

        # if ffmpeg is installed continue
        if os.path.exists(core_constants.FFMPEG_EXE):
            return True

        # give message and return false if not installed
        message = f"{core_constants.FFMPEG_EXE} is not installed"
        QtWidgets.QMessageBox.critical(self, "No ffmpeg", message)
        return False

    def create_project_on_disk(self, project_root, project_name):
        """
        Create the project on disk
        """
        self.logger.info(f"Creating disk project: {project_root}")
        folder_creator_inst = folder_creator.CreateFolders()
        folder_creator_inst.create_project_structure(project_root)

        create_dict = dict()
        self.ftshot.project_name = project_name
        for sequence_name in self.ftshot.sequence_names:
            self.ftshot.sequence_name = sequence_name
            create_dict[sequence_name] = self.ftshot.shot_names

        folder_creator_inst.create_dict = create_dict
        folder_creator_inst.create_all_shot_folders()

    def get_and_save_project_root(self):
        """
        Set the project root
        """
        project_root = self.wgt_project_root.file_path
        if not self.wgt_project_root.file_path:
            QtWidgets.QMessageBox.critical(self, "No Root", "Set Project Root")
            return

        roots_dict = self.ui_settings.value("project_roots", dict())
        project_name = self.cmb_project.currentText()
        roots_dict[project_name] = project_root
        self.ui_settings.setValue("project_roots", roots_dict)
        return project_root

    def launch_selected(self):
        """
        Launch the selected application or tool
        under the selected pipeline version
        """
        if not self.is_slate_ffmpeg_installed:
            return

        # if there is not exe path error
        exe_path_exists = self.does_exe_path_exist_on_disk()
        if not exe_path_exists:
            return

        # create the project on disk
        project_root = self.get_and_save_project_root()
        if not project_root:
            return

        # store the launch version
        use_version = self.cmb_application_version.currentText()
        project_code = self.cmb_project.currentData()
        project_name = self.cmb_project.currentText()
        self.create_project_on_disk(project_root, project_name)

        selected_app = self.get_selected_app()
        directory = os.path.dirname(__file__)
        launch_wrapper = WRAPPER_PATH.format(directory)

        # create arg list
        cmd_list = [
            core_constants.PYTHON_EXE,
            launch_wrapper,
            selected_app.class_name,
            project_code,
            project_root,
            use_version
        ]
        self.logger.info(f"Executing: {cmd_list}")

        # launch subprocess
        subprocess.run(cmd_list, check=True)


if __name__ == "__main__":
    base_ui.open_ui(ControlChaosLauncher)
