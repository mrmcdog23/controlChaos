""" Import shot to Unreal """
import os
import unreal as ue
import cccore.base_ui as base_ui
import cccore.utils.file_utils as file_utils
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.shot.ue_load_shot as ue_load_shot
import cccore.file_env.context as context
import ccftrack.shot as shot
import ccftrack.asset_version as ft_version
from CCPySide import QtWidgets, QtCore
from ccgeneral.widgets.shot_combobox import ShotComboBox


class LoadShotUI(base_ui.WidgetBase):
    title = "Import Unreal Shot"
    window_icon = "shot"
    control_chaos_ss = "../../css/ue_stylesheet.css"
    sequence_root = "/Game/ControlChaos/Sequence"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui_settings = QtCore.QSettings('controlChaos', 'ue_load_shot')
        self.ftshot = shot.FtShot()
        self.ftver = ft_version.FtAssetVersion(session=self.ftshot.session)
        self.ctx = None
        self.data = dict()

        self.load_settings()
        self.create_layout()
        self.populate_levels()
        self.populate_sequences()
        self.populate_sequence_shots()
        self.populate_files()
        self.connect_signals()

    def load_settings(self):
        """
        Load the settings to create the context
        """
        overrides = dict()
        for key in ["sequence_name", "shot_name", "task_name"]:
            overrides[key] = self.ui_settings.value(key)
        self.ctx = context.Context(overrides=overrides)

    def create_layout(self):
        """
        Create the layout for the ui
        """
        self.cmb_shot = ShotComboBox(self.ftshot, ctx=self.ctx)
        self.lyt_shot_combo.addWidget(self.cmb_shot)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.le_new_shot.textChanged.connect(self.enable_btn)
        self.rbn_existing.toggled.connect(self.enable_existing_level)
        self.rbn_existing_shot.toggled.connect(self.enable_existing_shots)
        self.btn_import_files.clicked.connect(self.import_files)
        self.cmb_sequence.currentIndexChanged.connect(self.populate_sequence_shots)
        self.cmb_shot.cmb_version.currentIndexChanged.connect(self.populate_files)

    def enable_existing_level(self, enable):
        # type: (bool) -> None
        """
        Enable the existing level widgets

        Args:
            enable: Whether to enable the widgets
        """
        self.lbl_existing.setEnabled(enable)
        self.cmb_existing.setEnabled(enable)
        self.lbl_new.setEnabled(not enable)
        self.le_new.setEnabled(not enable)

    def enable_existing_shots(self, enable):
        # type: (bool) -> None
        """
        Enable the existing shots widgets

        Args:
            enable: Whether to enable the widgets
        """
        self.cmb_existing_shots.setEnabled(enable)
        self.lbl_existing_shots.setEnabled(enable)
        self.lbl_new_shot.setEnabled(not enable)
        self.le_new_shot.setEnabled(not enable)

    @property
    def level_path(self):
        # type: () -> str
        """
        Work out the level to create path
        """
        if self.rbn_existing.isChecked():
            level_path = self.cmb_existing.currentText()
        else:
            map_name = self.le_new.text()
            level_path = f"/Game/Level/{map_name}"
        return level_path

    @property
    def shot_path(self):
        # type: () -> str
        """ The selected shot path """
        if self.rbn_existing_shot.isChecked():
            shot_name = self.cmb_existing_shots.currentText()
        else:
            shot_name = self.le_new_shot.text()
        sequence_name = self.cmb_sequence.currentText()
        shot_folders = [self.sequence_root, sequence_name, "Shots", shot_name]
        shot_path = ue.Paths.combine(shot_folders)
        return shot_path

    def enable_btn(self):
        """
        Enable the new shot button
        """
        if self.rbn_new_shot.isChecked():
            new_name = self.le_new_shot.text()
            self.btn_import_files.setEnabled(bool(new_name))
        else:
            self.btn_import_files.setEnabled(True)

    def populate_files(self):
        """
        Update the version list based on the asset selection
        """
        self.lw_import_files.clear()
        self.cmb_shot.set_ftshot()

        # get the versions from the combo boxes
        version_num = self.cmb_shot.cmb_version.currentText()
        asset_version = self.ftshot.get_asset_version_from_number(version_num)

        self.ftver.asset_version_id = asset_version["id"]
        for component_name, component_path in self.ftver.component_to_path.items():
            if component_name == "metadata":
                self.data = file_utils.read_file(component_path)

            if not component_path.endswith(".fbx"):
                continue

            item = QtWidgets.QListWidgetItem(os.path.basename(component_path))
            item.setCheckState(QtCore.Qt.Checked)
            item.setData(QtCore.Qt.UserRole, component_path)
            self.lw_import_files.addItem(item)

        # set the frame range from the data
        self.sb_start_frame.setValue(self.data["start_frame"])
        self.sb_end_frame.setValue(self.data["end_frame"])

        # set the ftrack widgets
        self.txt_created_by.setText(self.ftver.created_by)
        self.txt_comments_by.setText(self.ftver.comment)

    def populate_sequence_shots(self):
        """
        Populate the existing shot names combo box
        """
        selected_sequence = self.cmb_sequence.currentText()
        shots_path = f"{self.sequence_root}/{selected_sequence}/Shots"
        shot_names = unreal_utils.list_subfolders(shots_path, recursive=False)
        self.cmb_existing_shots.clear()
        self.cmb_existing_shots.addItems(shot_names)

    def populate_levels(self):
        """
        Populate the level sequences combobox
        """
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
        """
        Populate the sequences combo box
        """
        folder_names = unreal_utils.list_subfolders(self.sequence_root, recursive=False)
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

    def closeEvent(self, event):
        """
        Save the values on ui close
        """
        event.accept()
        for key, value in self.cmb_shot.get_data().items():
            self.ui_settings.setValue(key, value)

    def import_files(self):
        """
        Import cameras into unreal
        """
        ue_load_shot.UELoadShot(
            self.import_files_list, self.data, self.level_path, self.shot_path)


def launch():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(LoadShotUI)
