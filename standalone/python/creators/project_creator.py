""" The Control Chaos project creator tool """
import os
import cccore.utils.cc_logging as cc_logging
import cccore.base_ui as base_ui
import cccore.core_constants as core_constants
import cccore.utils.data_utils as data_utils
import cccore.utils.file_utils as file_utils
from ccgeneral.widgets.line_browser import LineBrowser
from PySide6 import QtWidgets, QtCore, QtGui


class ProjectCreator(base_ui.StandaloneWindowBase):
    title = "Project Creator"
    window_icon = "project_creator"
    icon_to_widget = {
        "maya": "lbl_maya_icon",
        "houdini": "lbl_houdini_icon",
        "nuke": "lbl_nuke_icon",
        "unreal": "lbl_unreal_icon",
        "expand": "btn_expand",
        "collapse": "btn_collapse",
    }

    def __init__(self):
        super().__init__()
        self.wdg_browse_root = None
        self.project_root = str()

        self.logger = cc_logging.cc_logger()
        self.ui_settings = QtCore.QSettings('controlChaos', 'project_creator')

        self.populate_files()
        self.create_layout()
        self.populate_structure()
        self.populate_app_versions()
        self.load_settings()
        self.connect_signals()

    def load_settings(self):
        """
        Load the previous settings to the widgets
        """
        project_dir = self.ui_settings.value("project_dir", str())
        self.wdg_browse_root.set_file_path(project_dir)
        project_name = self.ui_settings.value("project_name", str())
        self.le_project_name.setText(project_name)

    def create_layout(self):
        """
        Build the layout of the tool
        """
        project_dir = self.ui_settings.value("project_dir", str())
        self.wdg_browse_root = LineBrowser(
            self, "dir", "Select Project Directory", project_dir, "Project Directory")
        self.lyt_project_root.addWidget(self.wdg_browse_root)

        # hide the headers of the tree widget
        self.tw_project_structure.setHeaderHidden(True)

    def populate_files(self):
        """
        Populate the list of potential project structures
        """
        project_structures_dir = data_utils.get_relative_path("core/config/project_structures")
        project_structures_files = file_utils.get_files_recursively(project_structures_dir)

        # add the files to the combo box
        for project_structure_file in project_structures_files:
            file_name = file_utils.get_file_name(project_structure_file)
            self.cmb_project_structure.addItem(file_name, project_structure_file)

    def insert_nodes(self, parent_item, data):
        # type: (QtWidgets.QTreeWidgetItem, dict) -> None
        """
        Recursively populate a QTreeWidgetItem from nested dict data.

        Args:
            parent_item: The parent tree widget item to add to
            data: The dictionary to add to the item
        """
        if not isinstance(data, dict):
            return

        for key, value in data.items():
            child = QtWidgets.QTreeWidgetItem([key])
            parent_item.addChild(child)
            if isinstance(value, dict) and value:
                self.insert_nodes(child, value)

    def populate_app_versions(self):
        """
        Populate the application versions and frames per second
        """
        self.cmb_fps.addItems(core_constants.FRAME_RATES)
        self.set_combobox_index(self.cmb_fps, core_constants.DEFAULT_FPS)

        # populate application versions
        self.cmb_unreal.addItems(core_constants.APPS.UNREAL.value)
        self.cmb_nuke.addItems(core_constants.APPS.NUKE.value)
        self.cmb_maya.addItems(core_constants.APPS.MAYA.value)
        self.cmb_houdini.addItems(core_constants.APPS.HOUDINI.value)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.btn_expand.clicked.connect(self.expand_all)
        self.btn_collapse.clicked.connect(self.collapse_all)
        self.le_project_name.textChanged.connect(self.enable_button)
        self.wdg_browse_root.line_edit.textChanged.connect(self.enable_button)
        self.btn_create_project.clicked.connect(self.create_new_project)
        self.cmb_project_structure.currentIndexChanged.connect(self.populate_structure)
        self.tw_project_structure.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tw_project_structure.customContextMenuRequested.connect(self.action_menu)

    def action_menu(self, event):
        """
        Create action menu for removing items
        """
        if not self.tw_project_structure.selectedItems():
            return
        action_save = QtGui.QAction(self)
        action_save.setText("Add Folder")
        action_save.triggered.connect(self.add_folder)

        # show the menu
        menu = QtWidgets.QMenu(self)
        menu.addSeparator()
        menu.addAction(action_save)
        menu.popup(QtGui.QCursor.pos())

    def add_folder(self):
        """
        Add folder to the tree widget item
        """
        text, ok = QtWidgets.QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if not ok:
            return
        item = self.tw_project_structure.selectedItems()[0]
        new_item = QtWidgets.QTreeWidgetItem([text])
        item.addChild(new_item)
        item.setExpanded(True)

    def enable_button(self):
        """
        If the text is filled out enable the button
        """
        project_name = self.le_project_name.text()
        project_dir = self.wdg_browse_root.file_path

        enabled = bool(project_name and project_dir)
        self.btn_create_project.setEnabled(enabled)

        self.ui_settings.setValue("project_dir", project_dir)
        self.ui_settings.setValue("project_name", project_name)

    def populate_structure(self):
        """
        Populate the structure of the project from the yaml file
        """
        # load the project structure from the yaml file
        project_structure_file = self.cmb_project_structure.currentData()
        project_structure = file_utils.read_file(project_structure_file)

        # add the root node to add to
        top_item = QtWidgets.QTreeWidgetItem(["PROJECT_ROOT"])
        self.tw_project_structure.clear()
        self.tw_project_structure.addTopLevelItem(top_item)

        # build the tree recursively and expand on completion
        self.insert_nodes(top_item, project_structure)
        top_item.setExpanded(True)

    def expand_all(self):
        """
        Expand all the items to show all
        """
        self.tw_project_structure.expandAll()

    def collapse_all(self):
        """
        Collapse the items to only the roots are showing
        """
        self.tw_project_structure.collapseAll()
        root = self.tw_project_structure.topLevelItem(0)
        if root is not None:
            root.setExpanded(True)

    def item_to_dict(self, item):
        # type: (QtWidgets.QTreeWidgetItem) -> dict
        """
        Build a dictionary from the item and its children

        Args:
            item: The item to get the dictionary for

        Returns:
            result: The dictionary of the project
        """
        result = dict()
        for index in range(item.childCount()):
            child = item.child(index)
            result[child.text(0)] = self.item_to_dict(child) if child.childCount() > 0 else None
        return result

    def create_new_project(self):
        """
        Create new control chaos project
        """
        self.build_project_on_disk()
        self.save_settings()
        QtWidgets.QMessageBox.information(self, "Created", "Created project", QtWidgets.QMessageBox.Ok)

    def build_project_on_disk(self):
        root = self.tw_project_structure.topLevelItem(0)
        if root is None:
            return dict()

        project_structure = self.item_to_dict(root)
        project_dir = self.wdg_browse_root.file_path
        project_name = self.le_project_name.text()

        self.project_root = file_utils.join_file_names(project_dir, project_name)
        self.create_folder_structure(self.project_root, project_structure)

    def create_folder_structure(self, project_root, structure):
        # type: (str, dict) -> None
        """
        Build the default folder structure

        Args:
            project_root: The project root folder
            structure: Folder structure to build
        """
        for p, v in self.iteritems_recursive(structure):
            sub_path = "/".join(list(p))
            folder_path = os.path.join(project_root, sub_path)
            file_utils.create_directories(folder_path)
            
    def iteritems_recursive(self, d):
        # type: (dict) -> (set, str)
        """
        Recursively build folder path

        Args:
            d: Dictionary of folder structure

        Returns:
            Folder set
            Folder name
        """
        for k, v in d.items():
            if isinstance(v, dict):
                for k1, v1 in self.iteritems_recursive(v):
                    yield (k,) + k1, v1
            else:
                yield (k,), v

    def save_settings(self):
        """
        Save the project settings to a json file
        """
        project_name = self.le_project_name.text()
        general_settings = {
            "project_name": project_name,
            "project_code": self.le_project_code.text()
        }

        application_versions = {
            "fps": self.cmb_fps.currentText(),
            "unreal": self.cmb_unreal.currentText(),
            "maya": self.cmb_maya.currentText(),
            "houdini": self.cmb_houdini.currentText(),
            "nuke": self.cmb_nuke.currentText()
        }

        project_settings = {
            "general_settings": general_settings,
            "application_versions": application_versions,
            "project_root": self.project_root
        }

        user_profile = os.environ["USERPROFILE"]
        write_path = f"{user_profile}/Documents/{project_name}.json"
        file_utils.write_file(write_path, project_settings)


if __name__ == "__main__":
    base_ui.open_standalone_ui(ProjectCreator)
