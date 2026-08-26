""" Base context panel class """
import os
import re
from functools import partial
import cccore.base_ui as base_ui
import cccore.data.server_data as server_data
import cccore.file_env.context as context
import cccore.file_env.context_utils as context_utils
import cccore.utils.ui_utils as ui_utils
import ccftrack.shot as shot
import ccftrack.asset as asset
import ccftrack.asset_version as asset_version
import cccore.utils.file_utils as file_utils
from CCPySide import QtWidgets, QtGui, QtCore, QAction
from ccgeneral.widgets.tree_widget import CCTreeWidget
import cccore.file_env.ctx_constants as ctx_constants


WIP_PATH_INDEX = 0
WIP_PATH_WIDTH = 270
DATE_INDEX = 1
DATE_WIDTH = 120
VERSION_INDEX = 2
VERSION_WIDTH = 80
WIP_MINIMUM_HEIGHT = 100
BUTTON_SIZE = 45
IGNORE_FILE_EXT = (".autosave", "~")
PROJECT_DATA = server_data.ProjectData()

# import constants
BUILD = ctx_constants.BUILD
SHOT = ctx_constants.SHOT
ENTITY = ctx_constants.ENTITY
ASSET_BUILD_TYPE_NAME = ctx_constants.ASSET_BUILD_TYPE_NAME
ASSET_BUILD_NAME = ctx_constants.ASSET_BUILD_NAME
TASK_NAME = ctx_constants.TASK_NAME
SEQUENCE_NAME = ctx_constants.SEQUENCE_NAME
SHOT_NAME = ctx_constants.SHOT_NAME
ENTITIES = ctx_constants.ENTITIES
ASSET_ORDER = ctx_constants.ASSET_ORDER
SHOT_ORDER = ctx_constants.SHOT_ORDER
ENTITY_DICT = ctx_constants.ENTITY_DICT


class ContextButton(QtWidgets.QPushButton):
    """
    A publish button for context variables
    """
    def __init__(self, parent, envvar):
        super(ContextButton, self).__init__(parent)
        self.pw = parent
        self.envvar = envvar
        self.label = context_utils.get_btn_label(envvar)
        self.menu = QtWidgets.QMenu(self)
        self.selected_text = str()
        #button_width_size = PROJECT_DATA.get("context_panel.button_width")
        #self.use_display_text = PROJECT_DATA.get("context_panel.use_display_text")

        self.setObjectName(envvar)
        self.setText(self.label)
        self.setFixedSize(45, 45)
        self.connect_signals()
        self.setStyleSheet("padding: 3px;")

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.pressed.connect(self.show_context_items)

    def show_context_items(self):
        """
        Show menu of context items
        """
        self.menu.popup(QtGui.QCursor.pos())

    def build_menu_items(self, populate_list):
        # type: (str) -> None
        """
        Remove all menu items and add new ones

        Args:
            populate_list: List of items to add
        """
        # Remove entries from own menu
        for action in self.menu.actions():
            self.menu.removeAction(action)

        if not populate_list:
            populate_list = ["No Items"]
        for option in populate_list:
            self.menu.addAction(option, partial(self.set_variable, option))

    def set_variable(self, selected_text):
        # type: (str) -> None
        """
        When the item is selected set the environment variable
        set the button text run the next button function

        Args:
            selected_text: Select items text
        """
        self.setDown(False)
        self.selected_text = selected_text

        os.environ[self.envvar] = selected_text
        if self.use_display_text:
            display_text = context_utils.get_display_text(self.envvar, selected_text)
        else:
            display_text = selected_text
        self.setText(display_text)
        self.pw.set_next_button(self.envvar, selected_text)

    def set_button_released(self):
        """
        When the button is released set up
        """
        self.setDown(False)

    def reset_label(self):
        """
        Reset the button to the original label
        """
        self.setText(self.label)
        if self.envvar in os.environ:
            del os.environ[self.envvar]


class ContextPanel(base_ui.WidgetBase):
    """
    The context panel for setting a file context
    """
    title = "Project"
    use_cc_ss = False

    def __init__(self, node=None):
        super(ContextPanel, self).__init__()

        # initialize class variables
        self.btn_dict = dict()
        self.use_list = list()
        self.btn_entity = None
        self.selected_path = str()
        self.ftshot = shot.FtShot()

        # set up function
        self.ftasset = asset.FtAsset(session=self.ftshot.session)
        self.ftver = asset_version.FtAssetVersion(session=self.ftshot.session)
        self.project_data = server_data.ProjectData()
        self.ui_settings = QtCore.QSettings('ccpanel', os.environ["APP_NAME"])
        self.tw_wip_files.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.initialize_panel()

    def initialize_panel(self):
        """
        Run the setup function
        """
        self.set_project_icons()
        self.enable_buttons()
        self.create_layout()
        self.set_from_settings()
        self.populate_wip_versions()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        try:
            self.btn_opened_selected.clicked.disconnect(self.open_wip)
            self.btn_version_up.clicked.disconnect(self.version_up)
            self.btn_save_without_suffix.clicked.disconnect(self.save_without_suffix)
            self.btn_save_with_suffix.clicked.disconnect(self.save_with_suffix)
            self.tw_wip_files.itemSelectionChanged.disconnect(self.enable_buttons)
            self.tw_wip_files.customContextMenuRequested.disconnect(self.action_menu)
        except RuntimeError:
            pass
        self.btn_opened_selected.clicked.connect(self.open_wip)
        self.btn_version_up.clicked.connect(self.version_up)
        self.btn_save_without_suffix.clicked.connect(self.save_without_suffix)
        self.btn_save_with_suffix.clicked.connect(self.save_with_suffix)
        self.tw_wip_files.itemSelectionChanged.connect(self.enable_buttons)
        self.tw_wip_files.customContextMenuRequested.connect(self.action_menu)

    def open_wip(self):
        """ Open the work in progress file """
        raise NotImplemented

    @property
    def extension(self):
        # type: () -> str
        """ File type to filter """
        raise NotImplemented

    @staticmethod
    def save_file_path(file_path):
        # type: (str) -> None
        """ save the file with the given name """
        raise NotImplemented

    @property
    def current_file_path(self):
        # type: () -> str
        """ File type to filter """
        raise NotImplemented

    def version_up(self):
        """ Version up the current file """
        if not self.current_file_path:
            ui_utils.messagebox(
                "Not Saved", "Save File To Version Up", "critical")
            return

        ctx = context_utils.context_from_path(self.current_file_path)
        if not ctx:
            ui_utils.messagebox(
                "Invalid Path", "Path not valid to version up", "critical")
            return

        self.save_file_path(ctx.next_save_path)
        self.populate_wip_versions()

    def save_with_suffix(self):
        """ Daydreamer save with suffix """
        next_save_file_path = ui_utils.cc_save_with_suffix(self.extension)
        if not next_save_file_path:
            return
        self.save_file_path(next_save_file_path)
        self.populate_wip_versions()

    def save_without_suffix(self):
        """
        Save the file path next file

        Returns:
            save_path: Path of the file to save
        """
        response = ui_utils.messagebox(
            "WIP file save",
            "Save Control Chaos file?",
            "question",
            buttons=["Save File", "Cancel"]
        )
        if response != "Save File":
            return

        # use the script path first to work out the context
        ctx = context.Context(overrides={"ext": self.extension})
        self.save_file_path(ctx.next_save_path)
        self.populate_wip_versions()

    @property
    def selected_wip_file(self):
        # type: () -> str
        """
        Get the selected work in progress file in the list

        Returns:
            wip_file_path: Path to wip file
        """
        item = self.tw_wip_files.selectedItems()[0]
        wip_file_path = item.data(WIP_PATH_INDEX, QtCore.Qt.UserRole)
        return wip_file_path

    @property
    def selected_pub_file(self):
        # type: () -> str
        """
        Get the selected published file in the list

        Returns:
            pub_file_path: Path to published file
        """
        item = self.tv_pub_files.selectedItems()[0]
        pub_file_path = item.data(WIP_PATH_INDEX, QtCore.Qt.UserRole)
        return pub_file_path

    def enable_buttons(self):
        """
        Enable the open selected button
        """
        enable = bool(self.tw_wip_files.selectedItems())
        self.btn_opened_selected.setEnabled(enable)

    @property
    def selected_publish_file(self):
        # type: () -> str
        """
        The selected file path that is published

        Returns:
            Path of the published file selected
        """
        item = self.tv_pub_files.selectedItems()[0]
        data = item.data(0, QtCore.Qt.UserRole)
        return data["master_path"]

    def makeUI(self):
        """
        Needed by Nuke to add the widget
        """
        return self

    def updateValue(self):
        """
        Needed by Nuke to add the widget
        """
        pass

    def action_menu(self, event):
        """
        Create action menu for removing items
        """
        action_menu = QAction(self)
        action_menu.setText("Copy selected path")
        action_menu.triggered.connect(self.copy_selected_path)

        # show the menu
        menu = QtWidgets.QMenu(self)
        menu.addSeparator()
        menu.addAction(action_menu)
        menu.popup(QtGui.QCursor.pos())

    def copy_selected_path(self):
        """
        Copy the selected items path
        """
        for index in range(self.tw_wip_files.topLevelItemCount()):
            item = self.tw_wip_files.topLevelItem(index)
            selected_path = item.data(WIP_PATH_INDEX, QtCore.Qt.UserRole)
            QtWidgets.QApplication.clipboard().setText(selected_path)
            return

    def create_btn(self, btn_name):
        # type: (str) -> None
        """
        Create a context button and add it to the layout

        Args:
            btn_name: Name of the button  to create
        """
        button = ContextButton(self, btn_name)
        button.setHidden(True)
        self.btn_dict[btn_name] = button
        self.horzlayout.addWidget(button)

    def create_layout(self):
        """
        Create the layout of all possible buttons. The
        entity first then the rest. As there are two task
        buttons add it at the end
        """
        # create the entity button
        self.tw_wip_files.setColumnWidth(WIP_PATH_INDEX, WIP_PATH_WIDTH)
        self.tw_wip_files.setColumnWidth(DATE_INDEX, DATE_WIDTH)
        self.tw_wip_files.setColumnWidth(VERSION_INDEX, VERSION_WIDTH)
        self.tw_wip_files.sortByColumn(VERSION_INDEX, QtCore.Qt.DescendingOrder)
        self.btn_entity = ContextButton(self, ENTITY)
        self.btn_entity.build_menu_items(ENTITIES)
        self.horzlayout.addWidget(self.btn_entity)

        # go through both lists and create the buttons
        for btn_name in SHOT_ORDER + ASSET_ORDER:
            if btn_name in [ENTITY, TASK_NAME]:
                continue
            if self.findChild(QtWidgets.QPushButton, btn_name):
                continue
            self.create_btn(btn_name)

        # create the task name button at the end
        self.create_btn(TASK_NAME)

        # add a spacer to make the buttons bunched
        spacer = QtWidgets.QSpacerItem(20, 40,
                                       QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Minimum
                                       )
        self.horzlayout.addItem(spacer)

    @property
    def panel_ctx(self):
        # type: () -> context.Context
        """ Get a context class from the buttons """
        overrides = {"ext": self.extension}
        for btn_name, btn in self.btn_dict.items():
            if btn.isHidden():
                continue
            overrides[btn_name] = btn.selected_text
        return context.Context(overrides=overrides)

    def set_context_button_from_path(self, path):
        # type: (str) -> None
        """
        Set the context buttons and variables from a file path

        Args:
            path: Path of the file to set to
        """
        ctx = context_utils.get_context_from_path(path)
        if not ctx:
            return
        self.set_buttons_from_ctx(ctx)

    def set_from_settings(self):
        """
        On load set the buttons from the previous context
        """
        context_dict = self.ui_settings.value("ctx_key")
        if not context_dict:
            return
        if os.environ["PROJECT_NAME"] != context_dict.get("project_name"):
            return

        # get the context dictionary
        try:
            ctx = context.Context(overrides=context_dict)
            if ctx.is_shot and not os.path.exists(ctx.shot_dir):
                return

            # set the context buttons
            self.set_buttons_from_ctx(ctx)
            self.set_project()
        except TypeError:
            return

    def rebuild_widgets(self):
        """
        It breaks when reopening files so delete
        the widgets and rebuild
        """
        delete_widgets = [self.tw_wip_files,
                          self.btn_opened_selected,
                          self.btn_version_up,
                          self.btn_save_without_suffix,
                          self.btn_save_with_suffix
                          ]
        for delete_widget in delete_widgets:
            self.rebuild_layout.removeWidget(delete_widget)
            delete_widget.deleteLater()

        # rebuild wip tree widget
        self.tw_wip_files = CCTreeWidget(["File Name", "Date", "Version"])
        self.tw_wip_files.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tw_wip_files.setColumnWidth(WIP_PATH_INDEX, WIP_PATH_WIDTH)
        self.tw_wip_files.setColumnWidth(DATE_INDEX, DATE_WIDTH)
        self.tw_wip_files.setColumnWidth(VERSION_INDEX, VERSION_WIDTH)
        self.tw_wip_files.setMinimumHeight(WIP_MINIMUM_HEIGHT)
        self.tw_wip_files.setSortingEnabled(True)
        self.tw_wip_files.sortByColumn(VERSION_INDEX, QtCore.Qt.DescendingOrder)
        self.rebuild_layout.addWidget(self.tw_wip_files)

        # rebuild the open button
        self.btn_opened_selected = QtWidgets.QPushButton("Open Selected WIP File")
        icon_path = self.get_icon_path("folder")
        self.btn_opened_selected.setIcon(QtGui.QIcon(icon_path))
        self.rebuild_layout.addWidget(self.btn_opened_selected)

        save_btn_layout = QtWidgets.QHBoxLayout()
        # rebuild save button
        self.btn_version_up = QtWidgets.QPushButton("Version Up")
        icon_path = self.get_icon_path("up")
        self.btn_version_up.setIcon(QtGui.QIcon(icon_path))
        save_btn_layout.addWidget(self.btn_version_up)

        # rebuild save button
        self.btn_save_without_suffix = QtWidgets.QPushButton("Save Without Suffix")
        icon_path = self.get_icon_path("save")
        self.btn_save_without_suffix.setIcon(QtGui.QIcon(icon_path))
        save_btn_layout.addWidget(self.btn_save_without_suffix)

        # rebuild save button
        self.btn_save_with_suffix = QtWidgets.QPushButton("Save With Suffix")
        icon_path = self.get_icon_path("suffix")
        self.btn_save_with_suffix.setIcon(QtGui.QIcon(icon_path))
        save_btn_layout.addWidget(self.btn_save_with_suffix)
        self.rebuild_layout.addLayout(save_btn_layout)

    def set_buttons_from_ctx(self, ctx):
        # type: (context.Context) -> None
        """
        From a context class set the context buttons

        Args:
            ctx: The class to set to
        """
        self.rebuild_widgets()

        # set entity button
        self.set_entity(ctx.entity)
        self.btn_entity.set_variable(ctx.entity)

        # set the context based on the shot or asset
        if ctx.entity == context_utils.SHOT:
            self.btn_dict[SEQUENCE_NAME].set_variable(ctx.sequence)
            self.btn_dict[SHOT_NAME].set_variable(ctx.shot)
        else:
            self.btn_dict[ASSET_BUILD_NAME].set_variable(ctx.asset_build)
        self.btn_dict[TASK_NAME].set_variable(ctx.task)

    def set_sequence_shot_task(self, sequence_name, shot_name, task_name):
        # type: (str, str, str) -> None
        """
        Set the context to a different shot and task

        Args:
            sequence_name: New sequence name to switch to
            shot_name: New shot name to switch to
            task_name: New task name to switch to
        """
        self.rebuild_widgets()

        # set entity button
        self.set_entity("shot")
        self.btn_entity.set_variable("shot")
        self.btn_dict[SEQUENCE_NAME].set_variable(sequence_name)
        self.btn_dict[SHOT_NAME].set_variable(shot_name)
        self.btn_dict[TASK_NAME].set_variable(task_name)

    def set_entity(self, envvar):
        # type: (str) -> None
        """
        Set the entity option if it has been changed. This will
        define the list of variables to use

        Args:
            envvar: Name of the environment variable
        """
        if envvar != ENTITY:
            return
        entity_name = os.environ[ENTITY]
        self.use_list = ENTITY_DICT[entity_name]
        for text, btn in self.btn_dict.items():
            if text != context_utils.ENTITY:
                btn.setHidden(True)

    def set_project_icons(self):
        """
        Set the project and pipeline icons and text
        """
        self.lbl_show_text.setText(self.project_data.project_name)
        self.lbl_pipeline_text.setText(self.project_data.display_name)
        icon_dict = {
            "lbl_pipeline_icon": "development",
            "lbl_show_icon": "project",
        }
        self.set_widget_icons(icon_dict=icon_dict)

        # set the logo to the header label
        logo_path = os.path.join(os.path.dirname(__file__), "context_header.png")
        pixmap = QtGui.QPixmap(logo_path)
        self.lbl_cc_project.setPixmap(pixmap)

        # reposition the ui
        self.lbl_cc_project.setMinimumHeight(110)
        self.lbl_cc_project.setMaximumHeight(110)

    def set_next_button(self, envvar, selected_text):
        # type: (str, str) -> None
        """
        Set the next button text and make visible and
        reset the labels of all following ones

        Args:
            envvar: Environment variable name
            selected_text: Selected items value
        """
        self.set_entity(envvar)
        self.tw_wip_files.clear()
        self.btn_version_up.setEnabled(False)
        self.btn_save_without_suffix.setEnabled(False)
        self.btn_save_with_suffix.setEnabled(False)

        # if it's the task then it's the last button
        # and no need to set the next one
        if envvar == TASK_NAME:
            self.save_ctx_ui_settings()
            self.create_task_folder()
            self.set_project()
            self.populate_wip_versions()
            self.btn_version_up.setEnabled(True)
            self.btn_save_without_suffix.setEnabled(True)
            self.btn_save_with_suffix.setEnabled(True)
            return

        # find the next button and show it
        index = self.use_list.index(envvar) + 1

        # find and show the next button
        next_button_name = self.use_list[index]
        next_button = self.btn_dict[next_button_name]
        next_button.setHidden(False)

        # get the list of options to populate the menu with
        populate_list = list()
        if next_button_name == ASSET_BUILD_NAME:
            populate_list = self.ftasset.get_asset_build_names()

        elif next_button_name == TASK_NAME:
            if os.environ[ENTITY] == BUILD:
                task_list = self.ftasset.get_asset_build_task_names(selected_text)
            else:
                sequence_name = os.environ[SEQUENCE_NAME]
                task_list = self.ftshot.get_shot_task_names(sequence_name, selected_text)

            # filter the task list by checking if the folder is on disk
            populate_list = context_utils.filter_tasks_on_disk(task_list)

        if next_button_name == SEQUENCE_NAME:
            populate_list = self.ftshot.sequence_names

        elif next_button_name == SHOT_NAME:
            populate_list = self.ftshot.get_shot_names(selected_text)

        # build the menu items
        next_button.build_menu_items(populate_list)

        # reset all the following buttons labels
        for btn_name in self.use_list[index:]:
            btn = self.btn_dict[btn_name]
            btn.reset_label()

    def save_ctx_ui_settings(self):
        """
        Save the context as a dictionary
        """
        ctx = context.Context()
        self.ui_settings.setValue("ctx_key", ctx.as_dict())

    @staticmethod
    def create_task_folder():
        """
        Check that the folder structure exists
        """
        ctx = context.Context()
        task_dir = ctx.wip_dir
        if os.path.exists(task_dir):
            file_utils.create_directory(task_dir)

    def set_project(self):
        """
        Set the project path
        """
        pass

    @staticmethod
    def date_value(value):
        # type: (int) -> str
        """
        Convert a value to a padded number

        Args:
            value: Integer before padding

        Returns:
            Value padded
        """
        return str(value).zfill(2)

    def populate_wip_versions(self):
        """
        Populate the work in progress file versions
        """
        self.tw_wip_files.clear()
        ctx = context.Context()
        if not ctx.task:
            return

        user_dir = ctx.user_dir
        if not os.path.exists(user_dir):
            return
        # get an initial list of wip file paths
        file_paths = list()
        for file_name in os.listdir(user_dir):
            file_path = os.path.join(user_dir, file_name)
            if os.path.isdir(file_path):
                continue
            file_paths.append(file_path)
        file_paths.sort()
        file_paths.reverse()

        # populate the tree widget items
        for file_path in file_paths:
            if not file_path.endswith(self.extension):
                continue

            file_name = os.path.basename(file_path)
            if file_name.endswith(IGNORE_FILE_EXT):
                continue

            # Get the creation and modification datetime of the file
            date_text = file_utils.get_file_date_text(file_path)
            frame_num = re.findall(r'\d+', file_path)[-1]
            item = QtWidgets.QTreeWidgetItem([file_name, date_text, frame_num])
            item.setData(WIP_PATH_INDEX, QtCore.Qt.UserRole, file_path)
            self.tw_wip_files.addTopLevelItem(item)

    def update_pub_info(self, selected_row):
        """
        Update the published information from the selected item
        """
        index = selected_row.indexes()[0]
        ftrack_id = self.model.data(index, QtCore.Qt.ItemDataRole)
        self.ftver.asset_version_id = ftrack_id
        self.selected_path = self.ftver.master_component_path
        self.lbl_comments.setText(self.ftver.comment)

        gif_path = self.ftver.gif_component_path
        if gif_path:
            # set the gif to the label
            movie = QtGui.QMovie(gif_path, QtCore.QByteArray())
            movie.setCacheMode(QtGui.QMovie.CacheAll)
            movie.setSpeed(100)
            movie.start()
            self.thumbnail.setMovie(movie)
        else:
            self.set_thumbnail_image(image_path=self.ftver.thumbnail_url)
