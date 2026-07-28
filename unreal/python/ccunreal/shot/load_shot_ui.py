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

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.create_layout()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.wdg_import_dir.line_edit.textChanged.connect(self.populate_files)
        self.btn_import_files.clicked.connect(self.import_files)

    def populate_files(self):
        """
        Populate the list widget with the fbx files
        """
        self.lw_import_files.clear()
        import_json = self.wdg_import_dir.file_path
        file_list = file_utils.read_file(import_json)
        for file_path in file_list:
            print (file_path)
            item = QtWidgets.QListWidgetItem(os.path.basename(file_path))
            item.setCheckState(QtCore.Qt.Checked)
            self.lw_import_files.addItem(item)

    def create_layout(self):
        """
        Create the layout for the ui
        """
        self.main_layout = QtWidgets.QVBoxLayout()
        self.wdg_import_dir = LineBrowser(
            self, "file", "Select Import file", "", "Import File", file_filter="*.json")
        self.main_layout.addWidget(self.wdg_import_dir)

        self.lw_import_files = QtWidgets.QListWidget()
        self.main_layout.addWidget(self.lw_import_files)

        self.btn_import_files = QtWidgets.QPushButton("Import Files")
        self.main_layout.addWidget(self.btn_import_files)

        self.setLayout(self.main_layout)

    @property
    def import_files_list(self):
        # type: () -> list[str]
        """ Get a list of checked cameras """
        import_files = list()
        import_dir = self.wdg_import_dir.file_path
        for index in range(self.lw_import_files.count()):
            item = self.lw_cameras.item(index)
            if item.checkState() != QtCore.Qt.CheckState.Checked:
                continue
            file_path = file_utils.join_file_names(import_dir, item.text())
            import_files.append(file_path)
        return import_files

    def import_files(self):
        """
        Import cameras into unreal
        """
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


def launch():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(LoadShotUI)
