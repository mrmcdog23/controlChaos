""" Launcher of daydreamer tools and applications """
import os
import subprocess
import logging
import cccore.base_ui as base_ui
import cccore.app_starter as app_starter
import cccore.core_constants as core_constants
import cccore.utils.cc_logging as cc_logging
from CCPySide import QtWidgets, QtCore, QtGui


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
        self.apply_icon_to_widget(self.lbl_app_icon, self.appclass.icon)

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
        "btn_dev_folder": "folder",
        "btn_refresh": "refresh"
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

        # initialize data
        self.ui_settings = QtCore.QSettings('control_chaos', 'launcher')
        self.logger = cc_logging.cc_logger()

        self.populate_apps_and_tools()
        self.load_from_settings()
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

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.rbn_apps.clicked.connect(self.filter_app_or_tool_list)
        self.rbn_tools.clicked.connect(self.filter_app_or_tool_list)
        self.btn_launch.clicked.connect(self.launch_selected)

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

        # update the launch button
        self.update_btn_text()

        app_versions = selected_app.app_versions
        if not app_versions:
            return

        self.cmb_application_version.clear()
        self.cmb_application_version.addItems(app_versions)

    def update_btn_text(self):
        """
        Update the button text when the selection changes
        """
        selected_app = self.get_selected_app()
        if selected_app.is_app:
            app_version = self.cmb_application_version.currentText()
            launch_text = f"{selected_app.display_text} {app_version}"
        else:
            launch_text = f"{selected_app.display_text}"
        button_text = f"L A U N C H: {launch_text}"
        self.btn_launch.setText(button_text)
        self.btn_launch.setEnabled(True)

    def does_exe_path_exist_on_disk(self):
        # type: () -> bool
        """
        Check and error if the exe path exists

        Returns:
            False if it is not installed
        """
        selected_app = self.get_selected_app()
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

    def launch_selected(self):
        """
        Launch the selected application or tool
        under the selected pipeline version
        """
        if not self.is_slate_ffmpeg_installed:
            return

        # store the launch version
        app_version = self.cmb_application_version.currentText()
        os.environ["APP_VERSION"] = app_version

        # if there is not exe path error
        exe_path_exists = self.does_exe_path_exist_on_disk()
        if not exe_path_exists:
            return

        selected_app = self.get_selected_app()
        directory = os.path.dirname(__file__)
        launch_wrapper = WRAPPER_PATH.format(directory)

        # create arg list
        cmd_list = [
            core_constants.PYTHON_EXE,
            launch_wrapper,
            selected_app.class_name,
            selected_app.display_text
        ]
        self.logger.info(f"Executing: {cmd_list}")

        # launch subprocess
        subprocess.run(cmd_list, check=True)


if __name__ == "__main__":
    base_ui.open_ui(ControlChaosLauncher)

