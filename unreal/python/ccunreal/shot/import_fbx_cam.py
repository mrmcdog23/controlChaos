""" Export FBX cameras to Unreal """
import os
import unreal as ue
import cccore.base_ui as base_ui
import cccore.utils.file_utils as file_utils
import ccunreal.utils.api_wrap as api_wrap
import ccunreal.utils.unreal_utils as unreal_utils
from ccgeneral.widgets.line_browser import LineBrowser
from CCPySide import QtWidgets, QtCore


class ImportFBXCam(base_ui.WindowBase):
    title = "Import Unreal Cameras"
    window_icon = "camera"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.create_layout()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.browse_fbx_wdg.line_edit.textChanged.connect(self.populate_fbx)
        self.btn_import_cameras.clicked.connect(self.import_cameras)
        self.chk_all.toggled.connect(self.check_all)
        #self.browse_fbx_wdg.set_file_path("//192.168.1.10/storage/jobs/011231_TestProject/vfx/appdata")

    def check_all(self, checked):
        # type: (bool) -> None
        """
        Check all the camera items

        Args:
            checked: State to check the items
        """
        state = QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked
        for index in range(self.lw_cameras.count()):
            item = self.lw_cameras.item(index)
            item.setCheckState(state)

    def populate_fbx(self):
        """
        Populate the list widget with the fbx files
        """
        self.lw_cameras.clear()
        import_dir = self.browse_fbx_wdg.file_path
        fbx_files = file_utils.get_files_recursively(import_dir, ["fbx"])
        fbx_files.sort()
        for fbx_path in fbx_files:
            item = QtWidgets.QListWidgetItem(os.path.basename(fbx_path))
            item.setCheckState(QtCore.Qt.Checked)
            self.lw_cameras.addItem(item)

    def create_layout(self):
        """
        Create the layout for the ui
        """
        self.browse_fbx_wdg = LineBrowser(
            self, "dir", "Select FBX Directory", "", "FBX Directory")
        self.lyt_browse.addWidget(self.browse_fbx_wdg)
        self.btn_import_cameras.setMinimumHeight(25)

    @property
    def checked_cameras(self):
        # type: () -> list[str]
        """ Get a list of checked cameras """
        checked_cameras = list()
        for index in range(self.lw_cameras.count()):
            item = self.lw_cameras.item(index)
            if item.checkState() != QtCore.Qt.CheckState.Checked:
                continue
            checked_cameras.append(item.text())
        return checked_cameras

    def import_cameras(self):
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
    unreal_utils.launch_unreal_win(ImportFBXCam)
