""" Import shot to Unreal """
import os
import unreal as ue
import cccore.base_ui as base_ui
import ccunreal.utils.unreal_utils as unreal_utils
from CCPySide import QtWidgets, QtCore


class UEWidgetImportShot(base_ui.WidgetBase):
    sequence_root = "/Game/ControlChaos/Sequence"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.populate_levels()
        self.populate_sequences()
        self.populate_sequence_shots()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.rbn_existing.toggled.connect(self.enable_existing_level)
        self.rbn_existing_shot.toggled.connect(self.enable_existing_shots)
        self.cmb_sequence.currentIndexChanged.connect(self.populate_sequence_shots)

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
