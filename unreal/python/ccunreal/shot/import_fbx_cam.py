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

        self.map = api_wrap.get_editor_world()
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
        # check for existing camera first
        camera_name = file_utils.get_file_name(fbx_path)

        # spawn a no8 camera to the map
        camera_actor = ue.EditorLevelLibrary.spawn_actor_from_class(
            ue.CineCameraActor, ue.Vector(0, 0, 0))

        # add to the level sequence
        api_wrap.add_actors_to_current_sequence([camera_actor])
        binding = unreal_utils.find_binding_by_actor_class(ue.CineCameraActor, self.ls)

        binding.set_name(camera_name)
        # set tag and label
        camera_actor.set_actor_label(camera_name)

        # ── 6. Import! ─────────────────────────────────────────────────────────────
        ue.SequencerTools.import_level_sequence_fbx(
            self.map,
            self.ls,
            [binding],
            unreal_utils.camera_ue_options(),
            fbx_path,
        )



def launch():
    """
    Launch the unreal shot loader
    """
    unreal_utils.launch_unreal_win(ImportFBXCam)
