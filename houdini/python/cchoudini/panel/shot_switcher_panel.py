""" Switch houdini shot assets """
import os
import hou
import ftrack_api
from typing import Any
from CCPySide import QtWidgets, QtGui, QtCore
import cchoudini.panel.create_cc_panel as create_cc_panel
import cchoudini.wizard.build_shots_wizard as build_shots_wizard
import ccgeneral.widgets.shot_cmb as shot_cmb
import ccftrack.shot as shot
import ccftrack.query as query
import cccore.base_ui as base_ui
import cccore.utils.file_utils as file_utils
import cccore.core_constants as core_constants
import cccore.file_env.context_utils as context_utils
import cccore.utils.cc_logging as cc_logging
import cccore.file_env.context as context
import cccore.data.server_data as server_data
from ccgeneral.widgets.tree_widget import No8TreeWidget
from ccgeneral.widgets.dragdrop_listwidget import DragDropListWidget
from ccgeneral.widgets.line_browser import LineBrowser
from ccgeneral.widgets.progress_widget import ProgressWidget
from cchoudini.shot.switch_to_shot import SwitchToShot


# constants
SUPPORTED_EXT = ["cpio", "abc", "exr", "fbx", "jpeg"]
HEADER_LABELS = ["Path", "Task", "Component", "Version"]
TASK_NAMES = ["animation", "fx", "layout", "lighting", "rendering"]
DEFAULT_TASK = "animation"
PATH_INDEX = 0
TASK_INDEX = 1
COMPONENT_INDEX = 2
VERSION_INDEX = 3


class ComponentItem(QtWidgets.QTreeWidgetItem):
    """
    Component item that is the parent
    """
    def __init__(self, shot_asset, icon_path):
        # type: (Any, str) -> None
        """
        Args:
            shot_asset: The shot asset instance
            icon_path: Path of the icon to set
        """
        super().__init__()
        self.shot_asset = shot_asset
        self.setText(PATH_INDEX, shot_asset.current_name)
        self.setIcon(PATH_INDEX, QtGui.QIcon(icon_path))
        self.setText(TASK_INDEX, shot_asset.ftver.task_name)
        self.setText(COMPONENT_INDEX, shot_asset.component_name)
        self.setText(VERSION_INDEX, str(shot_asset.current_version_num))


class AssetVersionItem(QtWidgets.QTreeWidgetItem):
    """
    Create an asset version widgets
    """
    def __init__(self, component, icon_path):
        # type: (ftrack_api.entity.component, str) -> None
        """
        Args:
            component: Component to find data for
            icon_path: Path of the icon to set
        """
        super().__init__()
        self.file_path = file_utils.path_from_component(component)
        ctx = context_utils.get_context_from_path(self.file_path)
        self.setIcon(PATH_INDEX, QtGui.QIcon(icon_path))
        self.setText(TASK_INDEX, ctx.task)
        self.setText(COMPONENT_INDEX, component["name"])
        self.setText(VERSION_INDEX, str(ctx.version))
        self.component = component
        self.asset_version_id = component["version"]["id"]


class ShotSwitcherPanel(base_ui.WidgetBase):
    """
    Interface to switch between shot assets
    """
    title = "Shot Switch"
    window_icon = "shot_switch"
    icon_to_widget = {"shot_switch": "btn_switch_shot",
                      "build_shot": "btn_build_shot",
                      "refresh": "btn_refresh"
                      }
    tab_to_icons = {"tab_widget": ["shot_switch", "build_shot"]}
    SUPPORTED_EXT = ["cpio", "abc", "exr", "fbx"]

    def __init__(self, parent=None):
        """
        Set the scene range or set it on ftrack
        """
        super().__init__(parent)
        self.browser = None
        self.cmb_shot = None
        self.key_to_widget = dict()
        self.tw_scene_components = None
        self.tw_selected_shot_components = None
        self.lw_shots_list = None
        self.lw_shots_to_publish = None
        self.btn_list_shot_components = None
        self.progress_wdg = None
        self.output_path = str()
        self.existing_components = list()
        self.shot_assets_dict = dict()

        self.ftquery = query.FtQuery()
        self.ftshot = shot.FtShot(session=self.ftquery.session)
        self.project_data = server_data.ProjectData()
        self.logger = cc_logging.cc_logger()
        self.ui_settings = QtCore.QSettings('cc', 'switch_shot')

        self.create_layout()
        self.populate_episode_names()
        self.populate_shots_to_build()
        self.load_settings()
        self.connect_signals()

    def load_settings(self):
        """
        Load the previous setting
        """
        self.key_to_widget = {
            "rbn_lighting_template": self.rbn_lighting_template,
            "rbn_current_scene": self.rbn_current_scene,
            "rbn_browse": self.rbn_browse
        }
        for key, wdg in self.key_to_widget.items():
            if self.ui_settings.value(key):
                wdg.setChecked(True)
                self.show_browse_template(key == "rbn_browse")
                break

    def create_layout(self):
        """
        Build the layout widgets
        """
        self.create_switch_shots_layout()
        self.create_build_shots_layout()
        self.created_files_wdg.setHidden(True)

        self.set_widget_font_size(self.btn_switch_shot, 14)
        self.set_widget_font_size(self.btn_build_shot, 14)

    def create_switch_shots_layout(self):
        """
        Build the layout to switch shots
        """
        # create the combo boxes to select the shot
        self.cmb_shot = shot_cmb.ShotCmbHorizontal(ftshot=self.ftshot, hide_tasks=True)
        self.vertical_lyt.addWidget(self.cmb_shot)

        # create the destination shot components
        self.tw_selected_shot_components = No8TreeWidget(HEADER_LABELS)
        self.tw_selected_shot_components.set_column_widths([50, 90, 230, 30])
        self.vertical_lyt.addWidget(self.tw_selected_shot_components)

    def create_build_shots_layout(self):
        """
        Add the list widgets to the page of the assets to publish
        """
        # create the build tab widgets
        default_text = hou.hipFile.path()
        browse_path = self.ui_settings.value("browse_path")
        if browse_path:
            default_text = browse_path

        self.browser = LineBrowser(
            self,
            "file",
            "Select template file",
            os.path.dirname(default_text),
            "Template File:",
            file_filter="*.hip",
            default_text=default_text
        )
        self.source_file_lyt.addWidget(self.browser)
        self.browser.setHidden(True)

        # add drag drop list widgets
        self.lw_shots_list = DragDropListWidget()
        self.lw_shots_to_publish = DragDropListWidget()
        self.drag_drop_lyt.addWidget(self.lw_shots_list)
        self.drag_drop_lyt.addWidget(self.lw_shots_to_publish)

        # add progress widget
        self.progress_wdg = ProgressWidget(self)
        self.progress_wdg.set_font_size(10)
        self.progress_wdg.setHidden(True)
        self.progress_lyt.addWidget(self.progress_wdg)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.cmb_episode_names.currentIndexChanged.connect(self.populate_shots_to_build)
        self.cmb_shot.cmb_shot.currentIndexChanged.connect(self.populate_destination_shot)
        self.btn_switch_shot.clicked.connect(self.run_switch_shot)
        self.btn_build_shot.clicked.connect(self.run_build_shots)
        self.lw_shots_to_publish.model().rowsInserted.connect(self.enable_build_button)
        self.lw_shots_to_publish.model().rowsRemoved.connect(self.enable_build_button)
        self.btn_refresh.clicked.connect(self.refresh)
        self.rbn_browse.toggled.connect(self.show_browse_template)
        self.browser.line_edit.textChanged.connect(self.save_ui_settings)
        for _, wdg in self.key_to_widget.items():
            wdg.toggled.connect(self.save_ui_settings)

    def show_browse_template(self, checked):
        # type: (bool) -> None
        """
        Hide or show the browse template

        Args:
            checked: Is browse is checked
        """
        self.browser.setHidden(not checked)

    def refresh(self):
        """
        Refresh the shot information
        """
        self.tw_selected_shot_components.clear()

    def enable_build_button(self):
        """
        Enable the build button
        """
        self.btn_build_shot.setEnabled(self.lw_shots_to_publish.items_added)

    def update_switch_btn(self):
        """
        Clear the and turn off the switch button
        """
        self.tw_selected_shot_components.clear()
        self.btn_switch_shot.setEnabled(False)

    def populate_episode_names(self):
        """
        Populate the episode names
        """
        self.cmb_episode_names.addItems(self.ftshot.episode_names)

    def populate_shots_to_build(self):
        """
        Populate every shot on the project
        """
        self.lw_shots_to_publish.clear()
        self.lw_shots_list.clear()
        episode_name = self.cmb_episode_names.currentText()
        self.ftshot.episode_name = episode_name
        sequence_names = self.ftshot.sequence_names
        for sequence_name in sequence_names:
            shot_names = self.ftshot.get_shot_names(sequence_name)
            for shot_name in shot_names:
                item = QtWidgets.QListWidgetItem(f"{sequence_name}_{shot_name}")
                self.lw_shots_list.addItem(item)

    @staticmethod
    def get_component_version_from_path(component):
        # type: (ftrack_api.entity.component) -> str
        """
        Get the component path version

        Args:
            component: FTrack component to get path for

        Returns:
            Version of the path
        """
        path = file_utils.get_component_path(component)
        ctx = context_utils.get_context_from_path(path)
        return ctx.version

    def get_component_name_to_versions(self, components):
        # type: (list[ftrack_api.entity.component]) -> dict
        """
        Dictionary of component name to their versions

        Args:
            components: List of ftrack components

        Returns:
            component_name_to_versions: Component name to version numbers
        """
        component_name_to_versions = dict()
        for component in components:
            component_name = component["name"]
            versions = component_name_to_versions.get(component_name, list())
            version = self.get_component_version_from_path(component)
            versions.append(version)
            component_name_to_versions[component_name] = versions
        return component_name_to_versions

    def populate_destination_shot(self):
        """
        Populate the destination shot components
        """
        self.btn_switch_shot.setEnabled(True)

        self.tw_selected_shot_components.clear()
        sequence_name = self.cmb_shot.sequence_name
        shot_name = self.cmb_shot.shot_name

        shot_id = self.ftshot.get_shot_id(sequence_name, shot_name)
        latest_component_version = self.ftquery.get_latest_component_version(shot_id)

        for component in latest_component_version:
            extension = component["file_type"].strip(".")
            if extension not in SUPPORTED_EXT:
                continue

            # find the icon and create a tree widget item
            icon_name = core_constants.EXT_TO_IMAGE.get(extension, extension)
            icon_path = self.get_path(icon_name)
            asset_item = AssetVersionItem(component, icon_path)
            self.tw_selected_shot_components.addTopLevelItem(asset_item)

    def set_context_panel(self):
        """
        Set the context panel buttons and environment
        """
        ctx_panel = create_cc_panel.get_ctx_panel()
        overrides = self.cmb_shot.get_data()
        overrides["task_name"] = DEFAULT_TASK
        ctx = context.Context(overrides=overrides)
        ctx_panel.set_buttons_from_ctx(ctx)

    def run_switch_shot(self):
        """
        Switch to the new shot
        """
        self.logger.info("Switching shot...")
        self.set_context_panel()
        SwitchToShot(
            self.cmb_shot.episode_name,
            self.cmb_shot.sequence_name,
            self.cmb_shot.shot_name,
            "animation",
            ftshot=self.ftshot
        )

    @property
    def template_file(self):
        # type: () -> str
        """
        Get the selected template file path
        """
        if self.rbn_lighting_template.isChecked():
            # get version prefix
            major, minor, patch = hou.applicationVersion()
            version = f"{major}{minor}{patch}"
            file_template_name = f"lighting_template_{version}.hip"
            template_file = os.path.join(
                self.project_data.houdini_template_dir, version, file_template_name
            )
        elif self.rbn_current_scene.isChecked():
            template_file = hou.hipFile.path()
        else:
            template_file = self.browser.text
        return template_file

    def run_build_shots(self):
        """
        Run the build shots in the background function
        """
        publish_shots_list = self.lw_shots_to_publish.list_names
        args = {
            "master_episode_name": self.cmb_episode_names.currentText(),
            "publish_shots_list": publish_shots_list,
            "template_file": self.template_file
        }
        build_shots_wizard.main(args)

    def switch_widget_visibility(self, override=None):
        """
        Switch the widgets visibility state
        """
        widgets = [self.browser,
                   self.lw_shots_list,
                   self.lw_shots_to_publish,
                   self.progress_wdg,
                   self.task_name_wdg
                   ]
        for wdg in widgets:
            hidden = wdg.isHidden()
            hide = not hidden if override is None else override
            wdg.setHidden(hide)

    def save_ui_settings(self):
        self.ui_settings.setValue("browse_path", self.browser.text)
        for key, wdg in self.key_to_widget.items():
            self.ui_settings.setValue(key, int(wdg.isChecked()))
