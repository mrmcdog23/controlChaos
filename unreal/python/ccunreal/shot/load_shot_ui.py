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
        self.btn_import_files.clicked.connect(self.import_files)

    def enable_btn(self, text):
        self.btn_import_files.setEnabled(bool(text))

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
            self.import_files_list, shot_name, start_frame, end_frame
        )
        '''
        # Get the current level sequence
        self.ls = ue.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        if not self.ls:
            QtWidgets.QMessageBox.critical(self, "No Level Sequence", "No level sequence open")
            return

        fbx_dir = self.browse_fbx_wdg.file_path
        for camera_file_name in self.checked_cameras:
            fbx_path = file_utils.join_file_names(fbx_dir, camera_file_name)
            self.import_camera_animation(fbx_path)

    def import_camera_animation(self, fbx_path):
        # type: (str) -> None
        """
        Import a camera into the level sequence by
        creating then importing the fbx afterward

        Args:
            fbx_path: Path of the camera fbx file
        """
        # Spawn a CineCameraActor as a Spawnable binding
        ls_system = ue.get_editor_subsystem(ue.LevelSequenceEditorSubsystem)
        camera_binding, camera_cut_track = ls_system.create_camera(spawnable=True)

        # Build the FBX import settings
        import_settings = ue.MovieSceneUserImportFBXSettings()
        import_settings.set_editor_property("create_cameras", False)   # camera already exists
        import_settings.set_editor_property("force_front_x_axis", False)
        import_settings.set_editor_property("match_by_name_only", False)
        import_settings.set_editor_property("reduce_keys", False)

        #  Import FBX onto the camera binding
        world = ue.EditorLevelLibrary.get_editor_world()
        ue.SequencerTools.import_level_sequence_fbx(
            world=world,
            sequence=self.ls,
            bindings=[camera_binding],
            import_fbx_settings=import_settings,
            import_filename=fbx_path
        )

        camera_name = file_utils.get_file_name(fbx_path)
        camera_binding.set_name(camera_name)
        camera_cut_track.set_actor_label(camera_name)
        camera_cut_track.set_folder_path("FBX_Cameras")
        '''


def launch():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(LoadShotUI)
