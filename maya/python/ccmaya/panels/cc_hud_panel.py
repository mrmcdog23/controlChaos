""" Add the context panel to maya """
import maya.cmds as cmds
import ccmaya.utils.create_dockable_widget as create_dockable_widget
import cccore.base_ui as base_ui
import ccmaya.utils.maya_utils as maya_utils


FONT_LIST = ['Ariel', 'Times New Roman', 'Courier', "Serif"]
# dictionary of text weights
FONT_WEIGHT = ['Normal', 'DemiBold', 'Bold']


class ControlChaosHUDPanel(base_ui.WidgetBase):
    icon_to_widget = {
        "hud_header": "lbl_header"
    }
    title = "Hud"
    def __init__(self, parent):
        super().__init__(parent)
        self.populate_data()
        self.connect_signals()

    def populate_data(self):
        font_size = cmds.getAttr(f"{self.speed_node}.font_size")
        self.sp_font_size.setValue(font_size)
        # set fonts
        font_type_index = cmds.getAttr(f"{self.speed_node}.text_font")
        self.cmb_font_type.addItems(FONT_LIST)
        self.cmb_font_type.setCurrentIndex(font_type_index)

        # set
        font_type_index = cmds.getAttr(f"{self.speed_node}.text_font")
        self.cmb_font_type.addItems(FONT_LIST)
        self.cmb_font_type.setCurrentIndex(font_type_index)

        font_weight_index = cmds.getAttr(f"{self.speed_node}.font_weight")
        self.cmb_font_weight.addItems(FONT_WEIGHT)
        self.cmb_font_weight.setCurrentIndex(font_weight_index)

    def connect_signals(self):
        self.sp_font_size.valueChanged.connect(self.set_font_size)
        self.cmb_font_type.currentIndexChanged.connect(self.set_font_type)
        self.cmb_font_weight.currentIndexChanged.connect(self.set_font_weight)

    @property
    def speed_node(self):
        cc_speed_node = cmds.ls(type="objectSpeedHUD")
        if cc_speed_node:
            return cc_speed_node[0]

        if not cmds.pluginInfo("objectSpeedHUD.py", query=True, loaded=True):
            cmds.loadPlugin("objectSpeedHUD.py")

        return cmds.createNode("objectSpeedHUD")

    def set_font_size(self):
        font_size = self.sp_font_size.value()
        cmds.setAttr(f"{self.speed_node}.font_size", font_size)

    def set_font_type(self):
        font_type_index = self.cmb_font_type.currentIndex()
        cmds.setAttr(f"{self.speed_node}.text_font", font_type_index)

    def set_font_weight(self):
        font_weight_index = self.cmb_font_weight.currentIndex()
        cmds.setAttr(f"{self.speed_node}.font_weight", font_weight_index)


def create_cc_panel():
    """
    Create the dockable panel in Maya
    """
    create_dockable_widget.CreateDockableWidget(
        ControlChaosHUDPanel, "Control Chaos Hud", "Control Chaos Hud", 500
    )


def main():
    """
    Launch the maya multi playblast
    """
    maya_utils.launch_maya_win(ControlChaosHUDPanel)