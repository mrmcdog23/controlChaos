""" Import shot to Unreal """
import os
import unreal as ue
import cccore.base_ui as base_ui
import ccftrack.shot as shot
import ccunreal.utils.unreal_utils as unreal_utils
from CCPySide import QtWidgets, QtCore, QtGui
from ccgeneral.widgets.shot_combobox import ShotComboBox


class ConvertLevelSequence(base_ui.WidgetBase):
    title = "Convert"
    control_chaos_ss = "../../css/ue_stylesheet.css"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ftshot = shot.FtShot()
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        """
        Create the level sequence ui layout
        """
        self.cmb_shot = ShotComboBox(self.ftshot)
        self.btn_convert = QtWidgets.QPushButton("Convert Sequence")

        # create the layout and add widgets
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.cmb_shot)
        main_layout.addWidget(self.btn_convert)
        self.setLayout(main_layout)

    def connect_signals(self):
        """
        Connect signals to the widgets
        """
        self.btn_convert.clicked.connect(self.convert)

    def get_new_ls_path(self):
        # type: () -> str
        """
        Get the level sequence path
        """
        ls_name = f"{self.cmb_shot.sequence_name}_{self.cmb_shot.shot_name}_{self.cmb_shot.task_name}"
        new_ls_path = ue.Paths.combine([
            "/Game/ControlChaos/Sequence",
            self.cmb_shot.sequence_name,
            self.cmb_shot.shot_name,
            ls_name
        ])
        return new_ls_path

    def convert(self):
        """
        Convert the level sequence to a ftrack one
        """
        selected = ue.EditorUtilityLibrary.get_selected_assets()
        level_sequences = [ls for ls in selected if isinstance(ls, ue.LevelSequence)]

        # if there is no level sequence selected
        # do not allow the publish
        if not level_sequences:
            unreal_utils.unreal_messagebox(
                "No selection",
                "No level sequences sequence selected",
                "critical",
                parent=self
            )
            return

        # question whether to continue with the publish
        convert_shot = unreal_utils.unreal_messagebox(
            "Convert Shot",
            f"Convert level sequence to a FTrack shot?",
            "question",
            ["Convert", "Cancel"],
            parent=self
        )
        if convert_shot != "Convert":
            return

        # if the level sequence already exists do not allow copy
        new_ls_path = self.get_new_ls_path()
        if ue.EditorAssetLibrary.does_asset_exist(new_ls_path):
            unreal_utils.unreal_messagebox(
                "Level Exists",
                "A level sequence for this shot already exists",
                "critical",
                parent=self
            )
            return

        # move the asset to the new location
        ls_path = level_sequences[0].get_path_name()
        ue.EditorAssetLibrary.rename_asset(ls_path, new_ls_path)

        # add metadata to the level sequence
        new_ls = ue.load_asset(new_ls_path)
        unreal_utils.apply_metadata(self.cmb_shot.get_data(), new_ls)
        ue.EditorAssetLibrary.sync_browser_to_objects([new_ls_path])


def main():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(ConvertLevelSequence)
