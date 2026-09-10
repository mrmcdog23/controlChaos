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
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.rbn_existing.toggled.connect(self.enable_existing_level)

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
