""" Import shot to Unreal """
import os
import unreal as ue
import cccore.base_ui as base_ui
import cccore.utils.file_utils as file_utils
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.shot.ue_load_shot as ue_load_shot
from ccgeneral.widgets.line_browser import LineBrowser
from CCPySide import QtWidgets, QtCore


class LoadShotUI(base_ui.WidgetBase):
    title = "Import Unreal Shot"
    window_icon = "shot"
    control_chaos_ss = "../../css/ue_stylesheet.css"
    sequence_root = "/Game/ControlChaos/Sequence"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui_settings = QtCore.QSettings('controlChaos', 'ue_load_shot')
        self.create_layout()
        self.populate_levels()
        self.populate_sequences()
        self.populate_sequence_shots()
        self.connect_signals()

    def create_layout(self):
        """
        Create the layout for the ui
        """
        default_text = self.ui_settings.value("import_json")
        self.wdg_import_dir = LineBrowser(
            self, "file", "Select Import file", "",
            "Import File", file_filter="*.json", default_text=default_text
        )
        self.lyt_import_dir.addWidget(self.wdg_import_dir)
        if default_text:
            self.populate_values()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.wdg_import_dir.line_edit.textChanged.connect(self.populate_values)
        self.le_new_shot.textChanged.connect(self.enable_btn)
        self.rbn_existing.toggled.connect(self.enable_existing_level)
        self.rbn_existing_shot.toggled.connect(self.enable_existing_shots)
        self.btn_import_files.clicked.connect(self.import_files)
        self.cmb_sequence.currentIndexChanged.connect(self.populate_sequence_shots)

    def enable_existing_level(self, enable):
        self.lbl_existing.setEnabled(enable)
        self.cmb_existing.setEnabled(enable)
        self.lbl_new.setEnabled(not enable)
        self.le_new.setEnabled(not enable)

    def enable_existing_shots(self, enable):
        self.cmb_existing_shots.setEnabled(enable)
        self.lbl_existing_shots.setEnabled(enable)
        self.lbl_new_shot.setEnabled(not enable)
        self.le_new_shot.setEnabled(not enable)

    @property
    def level_path(self):
        if self.rbn_existing.isChecked():
            level_path = self.cmb_existing.currentText()
        else:
            map_name = self.le_new.text()
            level_path = f"/Game/Level/{map_name}"
        return level_path

    def enable_btn(self):
        if self.rbn_new_shot.isChecked():
            new_name = self.le_new_shot.text()
            self.btn_import_files.setEnabled(bool(new_name))
        else:
            self.btn_import_files.setEnabled(True)

    def list_subfolders(self, folder_path, recursive=False):
        asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
        if not ue.EditorAssetLibrary.does_directory_exist(folder_path):
            ue.log_warning(f"Folder not found: {folder_path}")
            return list()

        subfolders = asset_registry.get_sub_paths(folder_path, recursive)
        folder_names = list()
        for folder_path in subfolders:
            base_name = ue.Paths.get_base_filename(folder_path)
            folder_names.append(base_name)  # "SubFolder"
        return folder_names

    def populate_values(self):
        """
        Populate the list widget with the fbx files
        """
        self.lw_import_files.clear()
        import_json = self.wdg_import_dir.file_path
        if not os.path.exists(import_json):
            return
        data = file_utils.read_file(import_json)

        exported_files = data["exported_files"]
        for file_path in exported_files:
            if not file_path.endswith(".fbx"):
                continue
            item = QtWidgets.QListWidgetItem(os.path.basename(file_path))
            item.setCheckState(QtCore.Qt.Checked)
            item.setData(QtCore.Qt.UserRole, file_path)
            self.lw_import_files.addItem(item)

        self.sb_start_frame.setValue(data["start_frame"])
        self.sb_end_frame.setValue(data["end_frame"])
        self.ui_settings.setValue("import_json", import_json)

    def populate_sequence_shots(self):
        selected_sequence = self.cmb_sequence.currentText()
        shots_path = f"{self.sequence_root}/{selected_sequence}/Shots"
        shot_names = self.list_subfolders(shots_path, recursive=False)
        self.cmb_existing_shots.clear()
        self.cmb_existing_shots.addItems(shot_names)

    def populate_levels(self):
        asset_registry = ue.AssetRegistryHelpers.get_asset_registry()

        # Filter for World assets (levels/maps)
        filter = ue.ARFilter(
            class_names=["World"],
            package_paths=["/Game"],
            recursive_paths=True,
            recursive_classes=True
        )
        assets = asset_registry.get_assets(filter)

        level_paths = []
        for asset in assets:
            path = str(asset.package_name)
            level_paths.append(path)
        level_paths.sort()
        self.cmb_existing.addItems(level_paths)

    def populate_sequences(self):
        folder_names = self.list_subfolders(self.sequence_root, recursive=False)
        self.cmb_sequence.addItems(folder_names)

    @property
    def import_files_list(self):
        # type: () -> list[str]
        """ Get a list of checked cameras """
        import_files = list()
        for index in range(self.lw_import_files.count()):
            item = self.lw_import_files.item(index)
            if item.checkState() != QtCore.Qt.CheckState.Checked:
                continue
            file_path = item.data(QtCore.Qt.UserRole)
            import_files.append(file_path)
        return import_files

    def import_files(self):
        """
        Import cameras into unreal
        """
        ue.log_warning("Building shot...")
        start_frame = self.sb_start_frame.value()
        end_frame = self.sb_end_frame.value()

        if self.rbn_existing_shot.isChecked():
            shot_name = self.cmb_existing_shots.currentText()
        else:
            shot_name = self.le_new_shot.text()

        sequence_name = self.cmb_sequence.currentText()
        shot_path = f"{self.sequence_root}/{sequence_name}/Shots/{shot_name}"
        number_of_versions = self.list_subfolders(shot_path, recursive=False)
        next_version_number = len(number_of_versions) + 1
        version_dir = f"{shot_path}/v{next_version_number}"
        ue.log_warning(f"version_dir: {version_dir}")
        ue_load_shot.UELoadShot(
            self.import_files_list, shot_name, version_dir, self.level_path, start_frame, end_frame
        )


def launch():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(LoadShotUI)
