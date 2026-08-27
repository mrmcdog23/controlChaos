""" Shot combo boxes to select the context """
from typing import Optional, Any
from CCPySide import QtWidgets
import cccore.base_ui as base_ui
import cccore.file_env.context as context
import ccftrack.shot as shot


class ShotComboBox(base_ui.WidgetBase):
    """
    The Ftrack combo boxes for loading shots and versions
    """
    def __init__(self,
                 ftshot=None,  # type: Optional[shot.FtShot]
                 ctx=None,  # type: Optional[context.Context]
                 hide_versions=True,  # type: Optional[bool]
                 sel_tasks=False,  # type: Optional[bool]
                 hide_tasks=False  # type: Optional[bool]
                 ):
        """
        Args:
            ftshot: Ftrack shot object
            ctx: Current shot context
            ver: Whether to load the version combobox
            sel_tasks: Add an option to select the task
            hide_tasks: Hide the task combobox
        """
        super(ShotComboBox, self).__init__(
            ftshot=ftshot, ctx=ctx, hide_versions=hide_versions,
            sel_tasks=sel_tasks, hide_tasks=hide_tasks)
        self.ftshot = ftshot
        self.ctx = ctx
        self.hide_versions = hide_versions
        self.sel_tasks = sel_tasks
        self.hide_tasks = hide_tasks
        self.is_commercial = True

        # run the setup functions
        self.populate_episodes()
        self.populate_sequences()
        self.populate_shots()
        self.populate_shot_tasks()
        self.connect_signals()
        self.set_versions()

    def set_versions(self):
        """
        Set the version combobox hidden if not specified.
        If not connect the task combobox to the signal
        """
        if not self.hide_versions:
            self.lbl_version.setHidden(True)
            self.cmb_version.setHidden(True)
        else:
            self.cmb_task.currentIndexChanged.connect(self.populate_versions)
            self.populate_versions()

    @staticmethod
    def clear_combo_boxes(combo_boxes):
        # type: (list[QtWidgets.QComboBox]) -> None
        """
        Clear all combo boxes and block the signals inbetween

        Args:
            combo_boxes: List of combo boxes
        """
        for combo_box in combo_boxes:
            combo_box.blockSignals(True)
            combo_box.clear()
            combo_box.blockSignals(False)

    def populate_episodes(self):
        """
        Populate or hide the episodes
        """
        if self.is_commercial:
            self.lbl_episode.setHidden(True)
            self.cmb_episode.setHidden(True)
            return
        episode_names = self.ftshot.episode_names
        self.cmb_episode.addItems(episode_names)
        if self.ctx:
            self.set_combobox_index(self.cmb_episode, self.ctx.episode)

    def populate_sequences(self):
        """
        Populate sequences based on the selected episode
        """
        self.ftshot.episode_name = self.episode_name
        sequence_names = self.ftshot.sequence_names
        self.clear_combo_boxes([self.cmb_sequence, self.cmb_shot, self.cmb_task])
        self.cmb_sequence.addItems(sequence_names)
        if self.ctx:
            self.set_combobox_index(self.cmb_sequence, self.ctx.sequence)

    def populate_shots(self):
        """
        Populate all shots from the sequence selected
        """
        shot_names = self.ftshot.get_shot_names(self.sequence_name)
        self.clear_combo_boxes([self.cmb_shot, self.cmb_task])
        self.cmb_shot.addItems(shot_names)
        if self.ctx:
            self.set_combobox_index(self.cmb_shot, self.ctx.shot)

    @property
    def episode_name(self):
        # type: () -> str
        """ Selected episode name """
        if self.is_commercial:
            return str()
        return self.cmb_episode.currentText()

    @property
    def sequence_name(self):
        # type: () -> str
        """ Selected sequence name """
        return self.cmb_sequence.currentText()

    @property
    def shot_name(self):
        # type: () -> str
        """ Selected shot name """
        return self.cmb_shot.currentText()

    @property
    def task_name(self):
        # type: () -> str
        """ Selected task name """
        return self.cmb_task.currentText()

    @property
    def version_num(self):
        # type: () -> str
        """ Selected version number """
        return self.cmb_version.currentText()

    def populate_shot_tasks(self):
        """
        Populate the tasks from the selected shot
        """
        if self.hide_tasks:
            self.cmb_task.blockSignals(True)
            self.cmb_task.setHidden(True)
            self.lbl_task.setHidden(True)
            return

        task_names = self.ftshot.get_shot_task_names(
            self.sequence_name, self.shot_name
        )
        # if select tasks add a select option
        if self.sel_tasks:
            task_names.insert(0, "<select task>")

        self.clear_combo_boxes([self.cmb_task])
        self.cmb_task.addItems(task_names)

        # if context and not select task set the current index
        if self.ctx and not self.sel_tasks:
            self.set_combobox_index(self.cmb_task, self.ctx.task)

    def connect_signals(self):
        """
        Connect the widgets to the signals
        """
        self.cmb_episode.currentIndexChanged.connect(self.populate_sequences)
        self.cmb_sequence.currentIndexChanged.connect(self.populate_shots)
        self.cmb_shot.currentIndexChanged.connect(self.populate_shot_tasks)

    def set_ftshot(self):
        """
        Set the ftrack asset class values based
        on the combobox selections
        """
        self.ftshot.sequence_name = self.sequence_name
        self.ftshot.shot_name = self.shot_name
        self.ftshot.task_name = self.task_name
        self.ftshot.category = "Scene"

    def populate_versions(self):
        """
        Populate the combobox versions
        """
        self.set_ftshot()
        self.cmb_version.clear()
        for version in self.ftshot.asset_versions:
            self.cmb_version.addItem(str(version['version']))

    @property
    def sel_asset_version(self):
        # type: () -> Any
        """
        Get the selected asset version based on
        the combo boxes and version number

        Returns:
            Selected asset version
        """
        padded = str(self.version_num).zfill(3)
        asset_version = self.ftshot.get_shot_asset_version(
            self.sequence_name, self.shot_name, self.task_name, padded
        )
        return asset_version

    def get_data(self):
        # type: () -> dict
        """ The selection as a dictionary """
        context_dict = {
            "entity": "shot",
            "episode_name": self.episode_name,
            "sequence_name": self.sequence_name,
            "shot_name": self.shot_name,
            "task_name": self.task_name

        }
        return context_dict


class ShotComboBoxHorizontal(ShotComboBox):
    """
    Shot combo boxes horizontal
    """
    ui_name = "shot_combobox_horz"

    def __init__(self, ftshot=None, ctx=None, ver=False, hide_tasks=False):
        super().__init__(ftshot=ftshot, ctx=ctx, ver=ver, hide_tasks=hide_tasks)
