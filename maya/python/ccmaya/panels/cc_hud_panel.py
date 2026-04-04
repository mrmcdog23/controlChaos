""" Add the context panel to maya """
import maya.cmds as cmds
import ccmaya.utils.create_dockable_widget as create_dockable_widget
import cccore.base_ui as base_ui


class ControlChaosHUDPanel(base_ui.WidgetBase):
    def __init__(self, node):
        super().__init__(node)

    def initialize_panel(self):
        """
        Rebuild the widgets of the panel first
        """
        self.rebuild_widgets()
        super().initialize_panel()
        self.btn_entity.setHidden(True)

    def set_from_settings(self):
        pass

    @property
    def extension(self):
        """ File type to filter """
        return "ma"

    def open_wip(self):
        """ Open the selected nuke file """
        cmds.file(self.selected_wip_file,  open=True, force=True)

    @property
    def current_file_path(self):
        # type: () -> str
        """ Current file path """
        return cmds.file(q=True, sn=True)

    @staticmethod
    def save_file_path(file_path):
        # type: (str) -> None
        """ save the file with the given name """
        cmds.file(rename=file_path)
        cmds.file(save=True, type='mayaAscii')


def create_cc_panel():
    """
    Create the dockable panel in Maya
    """
    create_dockable_widget.CreateDockableWidget(
        ControlChaosHUDPanel, "Control Chaos Hud", "control_chaos_hud", 500
    )
