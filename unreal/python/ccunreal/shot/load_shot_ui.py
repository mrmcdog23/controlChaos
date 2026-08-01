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

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui_settings = QtCore.QSettings('controlChaos', 'ue_load_shot')
        self.create_layout()
        self.populate_levels()
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
        self.le_shot_name.textChanged.connect(self.enable_btn)
        self.le_new.textChanged.connect(self.enable_btn)
        self.rbn_existing.toggled.connect(self.enable_existing_level)
        self.btn_import_files.clicked.connect(self.import_files)

    def enable_existing_level(self, enable):
        self.lbl_existing.setEnabled(enable)
        self.cmb_existing.setEnabled(enable)
        self.lbl_new.setEnabled(not enable)
        self.le_new.setEnabled(not enable)

    @property
    def level_path(self):
        if self.rbn_existing.isChecked():
            level_path = self.cmb_existing.currentText()
        else:
            map_name = self.le_new.text()
            level_path = f"/Game/Level/{map_name}"
        return level_path

    def enable_btn(self):
        if not self.le_shot_name.text():
            self.btn_import_files.setEnabled(False)
            return

        if self.rbn_new.isChecked():
            new_name = self.le_new.text()
            self.btn_import_files.setEnabled(bool(new_name))
        else:
            self.btn_import_files.setEnabled(True)

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
        shot_name = self.le_shot_name.text()
        start_frame = self.sb_start_frame.value()
        end_frame = self.sb_end_frame.value()
        ue_load_shot.UELoadShot(
            self.import_files_list, shot_name, self.level_path, start_frame, end_frame
        )


def launch():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(LoadShotUI)
