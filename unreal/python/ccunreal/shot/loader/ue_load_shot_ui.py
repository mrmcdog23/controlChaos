""" Import shot to Unreal """
import os
import cccore.utils.file_utils as file_utils
import cccore.file_env.context as context
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.shot.loader.ue_load_shot as ue_load_shot
import ccunreal.shot.loader.wdg_import_shot as wdg_import_shot
from CCPySide import QtWidgets, QtCore
import ccgeneral.shot.load_shot_ui as load_shot_ui


class UELoadShotUI(load_shot_ui.LoadShotUI):
    title = "Import Unreal Shot"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.wdg_ue_import_shot = wdg_import_shot.UEWidgetImportShot(self)
        self.ue_wdg_layout.addWidget(self.wdg_ue_import_shot)

    def load_settings(self):
        """
        Load the settings to create the context
        """
        overrides = dict()
        for key in ["sequence_name", "shot_name", "task_name"]:
            overrides[key] = self.ui_settings.value(key)
        self.ctx = context.Context(overrides=overrides)

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
        if not version_num:
            return

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
        #for key, value in self.cmb_shot.get_data().items():
        #    self.ui_settings.setValue(key, value)

    def import_files(self):
        """
        Import cameras into unreal
        """
        level_path = self.wdg_ue_import_shot.level_path
        shot_path = self.wdg_ue_import_shot.shot_path
        ue_load_shot.UELoadShot(
            self.import_files_list, self.data, level_path, shot_path)


def main():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(UELoadShotUI)
