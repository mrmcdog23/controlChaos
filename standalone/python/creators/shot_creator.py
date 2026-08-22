""" Shot creator for ftrack and on disk """
from typing import Optional
from CCPySide import QtWidgets, QtCore, QtGui
import cccore.data.server_data as server_data
import cccore.base_ui as base_ui
import cccore.utils.ui_utils as ui_utils
import cccore.utils.cc_logging as cc_logging
import ccftrack.shot as shot
from ccgeneral.widgets.dragdrop_listwidget import DragDropListWidget


class ContextItem(QtWidgets.QListWidgetItem):
    def __init__(self, text, new_entity):
        super().__init__()
        # set variables
        self.new_entity = new_entity
        self.setText(text)

        # if new set the colour to green
        if new_entity:
            self.setForeground(QtCore.Qt.green)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)


class ShotCreator(base_ui.StandaloneWindowBase):
    title = "Shot Creator"
    window_icon = "shot_creator"
    widget_to_icon = {
        "lbl_project_icon": "project",
        "lbl_icon_sequence": "sequence",
        "lbl_icon_shot": "shot",
        "btn_add_sequence": "add",
        "btn_add_specific_shot_number": "add",
        "btn_add_shot_range": "add",
        "btn_reset": "refresh"
    }

    def __init__(self):
        super().__init__()
        self.project_data = server_data.ProjectData()
        self.ftshot = shot.FtShot()
        self.logger = cc_logging.cc_logger()
        self.folder_structure = dict()
        self.lbl_project_name.setText(self.project_data.project_name)
        self.create_layout()
        self.set_option_hidden()
        self.populate_sequences()
        self.connect_signals()

    def create_layout(self):
        self.lw_sequence = DragDropListWidget()
        self.lyt_sequence.addWidget(self.lw_sequence)
        self.lw_shot = DragDropListWidget()
        self.lyt_shot.addWidget(self.lw_shot)

    def set_option_hidden(self):
        """ Set the option hidden on startup """
        self.hide_shot_option(False)
        self.grp_shot.setEnabled(False)

    def enable_add_button(self):
        """
        Enable the create button if the text entered is valid
        """
        sequence_name = self.le_new_sequence_name.text()
        size_of_sequence = len(sequence_name)
        set_btn_on = size_of_sequence == 3 and sequence_name.isupper()
        self.btn_add_sequence.setEnabled(set_btn_on)

    def connect_signals(self):
        """
        Connect the signals over the widgets
        """
        self.le_new_sequence_name.textChanged.connect(self.enable_add_button)
        self.lw_sequence.itemSelectionChanged.connect(self.populate_shots)
        self.btn_create_context.clicked.connect(self.create_context)
        self.btn_add_sequence.clicked.connect(self.add_sequence_to_create)
        self.rbn_specific_shot_number.toggled.connect(self.hide_shot_option)
        self.btn_add_specific_shot_number.clicked.connect(self.add_specific_shot)
        self.btn_add_shot_range.clicked.connect(self.add_shot_range)
        self.btn_reset.clicked.connect(self.populate_sequences)
        self.lw_shot.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lw_shot.customContextMenuRequested.connect(self.action_menu)

    def action_menu(self, event):
        """
        Create action menu for creating all folders
        """
        selected_items = self.lw_shot.selectedItems()
        if not selected_items:
            return

        if selected_items[0].new_entity:
            return

        action_save = QtWidgets.QAction(self)
        action_save.setText("Create All Folder")
        action_save.triggered.connect(self.create_all_folders)

        # show the menu
        menu = QtWidgets.QMenu(self)
        menu.addSeparator()
        menu.addAction(action_save)
        menu.popup(QtGui.QCursor.pos())

    def create_all_folders(self):
        """
        Create folders for all applications
        """
        item = self.lw_shot.selectedItems()[0]
        shot_name = item.text()
        create_dict = {self.sequence_name: [shot_name]}

        # add new episodes to dictionary
        create_folders = folder_creator.CreateFolders(
            session=self.ftshot.session, create_dict=create_dict)
        create_folders.create_shots_and_sequences()
        ui_utils.messagebox("Complete", "Created Folders", "info", parent=self)

    def get_shot_name(self, shot_number):
        # type: (int) -> str
        """
        Get a shot name from the selected sequence and number

        Args:
            shot_number: The shot number to use

        Returns:
            Name of the padded shot with the sequence
        """
        shot_number_padded = str(shot_number).zfill(4)
        return f"{self.sequence_name}_sh{shot_number_padded}"

    def add_shot_range(self):
        """
        Add shot in frame range
        """
        start_range = self.sb_start_range.value()
        end_range = self.sb_end_range.value() + 10

        new_shot_list = list()
        for shot_number in range(start_range, end_range, 10):
            new_shot_name = self.get_shot_name(shot_number)
            if self.does_existing_shot_in_list(new_shot_name):
                return
            new_shot_list.append(new_shot_name)

        # check and warn the shot already exists
        for new_shot_name in new_shot_list:
            item = ContextItem(new_shot_name, True)
            self.lw_shot.addItem(item)
        self.enabled_create_button()

    @property
    def sequence_name(self):
        # type: () -> str
        """ Get the selected sequence name """
        return self.lw_sequence.selectedItems()[0].text()

    def does_existing_shot_in_list(self, shot_name):
        # type: (str) -> bool
        """
        Does the shot already exist in the shots list widget

        Args:
            shot_name: Name of the shot to check exists

        Returns:
            True if the shot exists
        """
        if shot_name in self.lw_shot.items_text:
            ui_utils.messagebox(
                "Shot exists",
                f"Shot {shot_name} already exists",
                "critical",
                parent=self
            )
            return True
        return False

    def add_specific_shot(self):
        """
        Add a specific shot number to the list
        """
        shot_number = self.sb_specific_shot_number.value()
        specific_shot_name = self.get_shot_name(shot_number)

        # check and warn the shot already exists
        if not self.does_existing_shot_in_list(specific_shot_name):
            item = ContextItem(specific_shot_name, True)
            self.lw_shot.addItem(item)
        self.enabled_create_button()

    def hide_shot_option(self, set_hidden):
        # type: (bool) -> None
        """
        Hide the shot options when the radio button is checked

        Args:
            set_hidden: Set the widget hidden
        """
        self.wdg_shot_number.setHidden(not set_hidden)
        self.wdg_shots_in_range.setHidden(set_hidden)

    def add_sequence_to_create(self):
        """
        Add the given sequence to the sequence list
        """
        create_sequence_name = self.le_new_sequence_name.text()
        item = ContextItem(create_sequence_name, True)
        self.lw_sequence.addItem(item)
        self.enabled_create_button()

    def get_text_to_item_dict(self, list_widget):
        # type: (QtWidgets.QListWidget, bool) -> dict
        """
        From a list widget build a dictionary
        of the text to the item

        Args:
            list_widget: The list to get the items from
            new_shot_or_seq: Only add new items

        Returns:
            item_dict: Item text to the QListWidgetItem
        """
        new_items_dict = dict()
        for item in list_widget.list_items:
            if item.new_entity:
                new_items_dict[item.text()] = item
        return new_items_dict

    def populate_sequences(self):
        """
        Populate sequences on the project
        """
        self.lw_sequence.clear()
        self.lw_shot.clear()

        sequence_names = self.ftshot.sequence_names
        for seq_name in sequence_names:
            item = ContextItem(seq_name, False)
            self.lw_sequence.addItem(item)

    def get_new_shot_names(self):
        # type: () -> Optional[list[str]]
        """
        Work out the new shot names. Account for the existing
        shots and the number of new shots requested

        Returns:
            new_shot_list: List of the shot names to create
        """
        shot_count = self.sb_shot_count.value()
        seq_item = self.lw_sequence.currentItem()
        if not seq_item:
            return

        sequence_name = seq_item.txt
        current_shot_names = seq_item.child_names
        current_shot_count = len(current_shot_names)
        seq_item.current_shot_count = current_shot_count
        new_shot_list = self.get_new_shot_names_list(
            current_shot_count, shot_count, sequence_name)
        return new_shot_list

    @staticmethod
    def get_new_shot_names_list(current_shot_count, shot_count, sequence_name):
        # type: (int, int, str) -> list[str]
        """
        From the given range workout the shots to create

        Args:
            current_shot_count: The amount of shots that already exist
            shot_count: Number of shots to create
            sequence_name: Name of the sequence to make the shots for

        Returns:
            new_shot_list: List of new shot names
        """
        current_count = current_shot_count + 1
        total = shot_count + current_count

        new_shot_list = list()
        for index in range(current_count, total):
            num = str(index * 10).zfill(4)
            new_shot_name = f"{sequence_name}_sh{num}"
            new_shot_list.append(new_shot_name)
        return new_shot_list

    def populate_shots(self):
        """
        Populate the list of shots from ftrack
        based on the episode selection
        """
        self.lw_shot.clear()
        items = self.lw_sequence.selectedItems()
        if not items:
            self.grp_shot.setEnabled(False)
            return

        self.grp_shot.setEnabled(True)
        seq_item = items[0]
        if not seq_item.new_entity:
            sequence_name = seq_item.text()

            shot_names = self.ftshot.get_shot_names(sequence_name)
            for shot_name in shot_names:
                item = ContextItem(shot_name, False)
                self.lw_shot.addItem(item)
            seq_item.child_names = shot_names

    def enabled_create_button(self):
        """
        Enabled the create button if there are new sequences or shots to create
        """
        seq_item_dict = self.get_text_to_item_dict(self.lw_sequence)
        shot_item_dict = self.get_text_to_item_dict(self.lw_shot)
        enable_btn = bool(seq_item_dict or shot_item_dict)
        self.btn_create_context.setEnabled(enable_btn)

    @staticmethod
    def get_current_item_text(list_widget):
        # type: (QtWidgets.QListWidget) -> str
        """
        From a list widget get the current items text

        Args:
            list_widget: The widget to get the item for

        Returns:
            text: The current item text
        """
        item = list_widget.currentItem()
        text = item.txt if item else None
        return text

    def get_entity_list_to_create(self, list_widget):
        # type: (QtWidgets.QListWidget) -> list[str]
        """
        From a list widget get the new items to create

        Args:
            list_widget: The widget to get the new item from

        Returns:
            List of new sequences or shots to create
        """
        new_items_dict = self.get_text_to_item_dict(list_widget)
        return list(new_items_dict.keys())

    def create_context(self):
        """
        Create all episodes, sequences and shots
        """
        # build a dictionary of what to create
        shots_to_create = self.get_entity_list_to_create(self.lw_shot)

        # add new episodes to dictionary
        self.ftshot.create_sequence(self.sequence_name)
        for shot_name in shots_to_create:
            self.ftshot.create_shot(shot_name, self.sequence_name)

        self.logger.info("Shot creation complete")
        ui_utils.messagebox("Complete", "Created Shots", "info", parent=self)


if __name__ == "__main__":
    base_ui.open_ui(ShotCreator)
