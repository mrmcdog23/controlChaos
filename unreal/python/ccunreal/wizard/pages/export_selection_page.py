""" Select which assets in the maya scene to publish """
import unreal as ue
import ccunreal.utils.api_wrap as api_wrap
import ccunreal.unreal_constants as unreal_constants
import cccore.file_env.context as context
import cccore.utils.file_utils as file_utils
from ccgeneral.widgets.dragdrop_listwidget import DragDropListWidget
from ccgeneral.wizard.pages.base_page import BasePublishPage
from CCPySide import QtWidgets, QtCore, QtGui


class ExportSelectionPage(BasePublishPage):
    title = "Unreal Selection Page"
    subtitle = "Select scene assets to publish"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lw_scene_assets = None
        self.lw_publish_assets = None
        self.wdg_save_dir = None

    def initializePage(self):
        # type: () -> bool
        """
        Set up the page when entered

        Return:
              False if the next page
        """
        #super().initializePage()
        self.create_layout()
        self.load_data_assets()
        self.connect_signals()
        return True

    def create_layout(self):
        """
        Add the list widgets to the page of the assets to publish
        """
        if self.built_layout:
            return

        self.lw_level_assets = DragDropListWidget()
        self.lw_layout.addWidget(self.lw_level_assets, 1, 1)
        self.lw_publish_assets = DragDropListWidget()
        self.lw_layout.addWidget(self.lw_publish_assets, 1, 2)

    def load_data_assets(self):
        seq_name_path = dict()
        ls = api_wrap.get_current_level_sequence()
        for track in ls.get_tracks():
            if isinstance(track, ue.MovieSceneCinematicShotTrack):
                for section in track.get_sections():
                    shot_sequence = section.get_sequence()
                    seq_name_path[shot_sequence.get_name()] = shot_sequence.get_path_name()

        if not seq_name_path:
            seq_name_path[ls.get_name()] = ls.get_path_name()

        ls_icon_path = self.get_icon_path("level_sequence")
        for ls_name, ls_path in seq_name_path.items():
            # create the list widget item
            item = QtWidgets.QListWidgetItem(ls_name)
            item.setData(QtCore.Qt.UserRole, ls_path)
            item.setIcon(QtGui.QIcon(ls_icon_path))
            self.lw_level_sequence.addItem(item)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.lw_level_sequence.itemSelectionChanged.connect(self.populate_assets)
        self.lw_publish_assets.model().rowsInserted.connect(self.check_complete)
        self.lw_publish_assets.model().rowsRemoved.connect(self.check_complete)

    def populate_assets(self):
        """
        Populate the map assets then the spawnable assets
        """
        item = self.lw_level_sequence.currentItem()
        ls_path = item.data(QtCore.Qt.UserRole)
        self.lw_level_assets.clear()

        # get the level actors
        level_actors = api_wrap.get_all_level_actors()
        for sequence_actor in level_actors:

            sequence_actor_cls = sequence_actor.__class__
            if sequence_actor_cls not in unreal_constants.SUPPORTED_EXPORT_CLASSES:
                ue.log_warning(f"Unsupported actor type: {sequence_actor_cls}")
                continue

            actor_name = sequence_actor.get_actor_label()
            icon_name = sequence_actor_cls.__name__
            item = QtWidgets.QListWidgetItem(actor_name)
            icon_path = self.get_icon_path(icon_name)
            item.setIcon(QtGui.QIcon(icon_path))
            self.lw_level_assets.addItem(item)

        # get the spawnable actors
        ls = ue.load_asset(ls_path)
        for spawnable_actor in ls.get_spawnables():          # MovieSceneBindingProxy
            spawnable_name = spawnable_actor.get_name()
            item = QtWidgets.QListWidgetItem(spawnable_name)
            self.lw_level_assets.addItem(item)

    def load_scene_assets(self):
        """
        Load the scene assets that are published rigs
        """
        self.lw_scene_assets.addItems(maya_utils.get_shot_namespaces())

    def check_complete(self):
        """
        When item is added or removed check for change
        """
        self.completeChanged.emit()

    def isComplete(self):
        # type: () -> bool
        """
        Check there is any asset to publish

        Returns:
            Whether there is assets to publish
        """
        if not self.lw_publish_assets:
            return
        has_assets = bool(self.lw_publish_assets.count())
        return has_assets

    def validatePage(self):
        # type: () -> bool
        """
        Store the selected options in the wizard data

        Returns:
            Whether the page is valid
        """
        item = self.lw_level_sequence.currentItem()
        ls_path = item.data(QtCore.Qt.UserRole)
        ls = ue.load_asset(ls_path)

        metadata_dict = api_wrap.get_metadata_tag_values(ls)
        if not metadata_dict:
            # if the metadata wasn't found use the level sequence name
            sequence, shot, task = item.text().split("_")
            metadata_dict = {
                "sequence_name": sequence,
                "shot_name": shot,
                "task_name": task
            }

        self.ctx = context.Context(overrides=metadata_dict)
        self.wizard().ctx = self.ctx

        thumbnail_path = file_utils.get_temp_file_path(f"{self.ctx.shot}_thumbnail.png")
        self.data["ls_path"] = ls_path
        self.data["thumbnail_path"] = thumbnail_path
        self.data["publish_assets"] = self.lw_publish_assets.items_text
        return True

