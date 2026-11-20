""" Import shot to Unreal """
import os
import unreal as ue
import cccore.base_ui as base_ui
import ccunreal.unreal_constants as unreal_constants
from CCPySide import QtWidgets, QtCore


class UEWidgetImportShot(base_ui.WidgetBase):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.pw = parent
        self.populate_levels()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.rbn_existing.group().buttonClicked.connect(self.enable_existing_level)

    @property
    def level_path(self):
        # type: () -> str
        """
        Work out the level to create path
        """
        level_root = unreal_constants.CC_LEVEL_DIR
        sequence_name = self.pw.cmb_shot.sequence_name
        if self.rbn_sequence.isChecked():
            level_path = f"{level_root}/{sequence_name}/{sequence_name}"
        elif self.rbn_existing.isChecked():
            level_path = self.cmb_existing.currentText()
        else:
            map_name = self.le_new.text()
            level_path = f"{level_root}/Custom/{map_name}"
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

    def enable_existing_level(self, radio):
        # type: (bool) -> None
        """
        Enable the existing level widgets

        Args:
            enable: Whether to enable the widgets
        """
        if radio.objectName() == "rbn_sequence":
            enable_existing = False
            enable_new = False
        elif radio.objectName() == "rbn_existing":
            enable_existing = True
            enable_new = False
        else:
            enable_existing = False
            enable_new = True

        self.lbl_existing.setEnabled(enable_existing)
        self.cmb_existing.setEnabled(enable_existing)
        self.lbl_new.setEnabled(enable_new)
        self.le_new.setEnabled(enable_new)

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
