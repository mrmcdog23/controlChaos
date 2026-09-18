""" Add the Control Chaos panel to houdini """
import hou
import cccore.file_env.context as context
import cchoudini.utils.hou_utils as hou_utils
import ccgeneral.panel.base_context_panel as base_ctx_panel
from typing import Optional
from CCPySide import QtWidgets


class HouContextPanel(base_ctx_panel.ContextPanel):
    def __init__(self):
        super(HouContextPanel, self).__init__()

    def rebuild_widgets(self):
        super().rebuild_widgets()
        self.connect_signals()

    @property
    def extension(self):
        """ File type to filter """
        return "hip"

    @staticmethod
    def save_file_path(file_path):
        # type: (str) -> None
        """ save the file with the given name """
        hou.hipFile.save(file_path)

    @property
    def current_file_path(self):
        # type: () -> Optional[str]
        """ Current file path """
        path = hou.hipFile.path()
        if path.endswith("untitled.hip"):
            return str()
        return hou.hipFile.path()

    def set_project(self):
        """
        Set the $JOB variable
        """
        ctx = context.Context()
        hou_utils.set_houdini_vars_from_ctx(ctx)

    def open_wip(self):
        """
        Open the selected houdini file
        """
        hou.hipFile.load(self.selected_wip_file)


class HouContextWidget(QtWidgets.QWidget):
    """
    Add the context widget to houdini
    """
    def __init__(self):
        super(HouContextWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(HouContextPanel())
