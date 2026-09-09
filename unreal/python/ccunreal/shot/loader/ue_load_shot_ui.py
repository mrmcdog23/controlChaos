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
        level_path = self.wdg_ue_import_shot.level_path
        shot_path = self.wdg_ue_import_shot.shot_path
        ue_load_shot.UELoadShot(
            self.import_files_list,
            self.data, level_path,
            shot_path,
            self.start_frame,
            self.end_frame
        )


def main():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(UELoadShotUI)
