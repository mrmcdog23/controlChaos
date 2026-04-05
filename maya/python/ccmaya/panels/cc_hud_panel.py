""" Add the context panel to maya """
import maya.cmds as cmds
import ccmaya.utils.create_dockable_widget as create_dockable_widget
import cccore.base_ui as base_ui
import ccmaya.utils.maya_utils as maya_utils
from PySide6 import QtWidgets


FONT_LIST = ['Ariel', 'Times New Roman', 'Courier', "Serif"]
FONT_WEIGHT = ['Normal', 'DemiBold', 'Bold']
SPEED_UNITS = [
    "Meters Per Second",
    "Kilometers Per Hour",
    "Miles Per Hour",
    "Feet Per Second",
    "Knots Per Hour"
]


class ControlChaosHUDPanel(base_ui.WidgetBase):
    icon_to_widget = {
        "hud_header": "lbl_header"
    }
    title = "Hud"
    def __init__(self, parent):
        super().__init__(parent)
        self.populate_data()
        self.populate_speed_objects()
        self.update_controls()
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

        speed_unit_index = cmds.getAttr(f"{self.speed_node}.speed_unit")
        self.cmb_speed_unit.addItems(SPEED_UNITS)
        self.cmb_speed_unit.setCurrentIndex(speed_unit_index)

    def connect_signals(self):
        self.sp_font_size.valueChanged.connect(self.set_font_size)
        self.cmb_font_type.currentIndexChanged.connect(self.set_font_type)
        self.cmb_font_weight.currentIndexChanged.connect(self.set_font_weight)
        self.cmb_speed_unit.currentIndexChanged.connect(self.set_speed_unit)
        self.btn_add_selected.clicked.connect(self.add_selected_object)
        self.cmb_speed_objects.currentIndexChanged.connect(self.update_controls)
        self.sld_x_offset.valueChanged.connect(self.set_x_sb)
        self.sld_y_offset.valueChanged.connect(self.set_y_sb)
        self.chk_visible.toggled.connect(self.set_visible)
        self.btn_text_colour.clicked.connect(self.set_colour)

    def set_visible(self):
        visible = self.chk_visible.isChecked()
        index = self.get_object_index()
        cmds.setAttr(f"{self.speed_node}.show_object_speed{index}", visible)

    def get_object_index(self):
        speed_object_list = self.get_speed_object_list()
        selected_object = self.cmb_speed_objects.currentText()
        if not selected_object:
            return 0
        index = speed_object_list.index(selected_object) + 1
        return index

    def set_x_sb(self):
        x_offset = self.sld_x_offset.value()
        self.sb_x_offset.setValue(x_offset)
        index = self.get_object_index()
        cmds.setAttr(f"{self.speed_node}.text_x_offset{index}", x_offset)

    def set_y_sb(self):
        y_offset = self.sld_y_offset.value()
        self.sb_y_offset.setValue(y_offset)
        index = self.get_object_index()
        cmds.setAttr(f"{self.speed_node}.text_y_offset{index}", y_offset)

    @property
    def speed_node(self):
        cc_speed_node = cmds.ls(type="objectSpeedHUD")
        if cc_speed_node:
            return cc_speed_node[0]
        if not cmds.pluginInfo("objectSpeedHUD.py", query=True, loaded=True):
            cmds.loadPlugin("objectSpeedHUD.py")
        return cmds.createNode("objectSpeedHUD")

    def get_speed_object_list(self):
        speed_object_list = list()
        for num in range(1, 6):
            attribute_name = f"{self.speed_node}.object_name{num}"
            object_name = cmds.getAttr(attribute_name)
            if not object_name:
                return speed_object_list
            speed_object_list.append(object_name)
        return speed_object_list

    def add_selected_object(self):
        selected_object = cmds.ls(sl=True)[0]
        speed_object_list = self.get_speed_object_list()
        if selected_object in speed_object_list:
            QtWidgets.QMessageBox.critical(
                self,
                "Already Added",
                f"{selected_object} added already",
                QtWidgets.QMessageBox.Ok
            )
            return
        index = len(speed_object_list)

        attribute_name = f"{self.speed_node}.object_name{index + 1}"
        cmds.setAttr(attribute_name, selected_object, type="string")
        self.cmb_speed_objects.addItem(selected_object)
        self.cmb_speed_objects.setCurrentIndex(index)

    def populate_speed_objects(self):
        self.cmb_speed_objects.clear()
        for num in range(1, 6):
            attribute_name = f"{self.speed_node}.object_name{num}"
            object_name = cmds.getAttr(attribute_name)
            if not object_name:
                break
            self.cmb_speed_objects.addItem(object_name)

    def set_font_size(self):
        font_size = self.sp_font_size.value()
        cmds.setAttr(f"{self.speed_node}.font_size", font_size)

    def set_font_type(self):
        font_type_index = self.cmb_font_type.currentIndex()
        cmds.setAttr(f"{self.speed_node}.text_font", font_type_index)

    def set_font_weight(self):
        font_weight_index = self.cmb_font_weight.currentIndex()
        cmds.setAttr(f"{self.speed_node}.font_weight", font_weight_index)

    def set_speed_unit(self):
        speed_unit_index = self.cmb_speed_unit.currentIndex()
        cmds.setAttr(f"{self.speed_node}.speed_unit", speed_unit_index)

    def get_stylesheet_from_attribute(self, attribute_name):
        colour = cmds.getAttr(attribute_name)[0]
        r = max(0.0, min(1.0, colour[0])) * 255
        g = max(0.0, min(1.0, colour[1])) * 255
        b = max(0.0, min(1.0, colour[2])) * 255
        return f"background-color: rgb({r}, {g}, {b});"

    def set_colour(self):
        colour = QtWidgets.QColorDialog.getColor()
        r, g, b, _ = colour.getRgb()
        print (colour.getRgb())
        stylesheet = f"background-color: rgb({r}, {g}, {b});"
        self.btn_text_colour.setStyleSheet(stylesheet)

        index = self.get_object_index()
        attribute_name = f"{self.speed_node}.speed_text_colour{index}"
        print ((r/255), (g/255), (b/255))
        cmds.setAttr(attribute_name, (r/255), (g/255), (b/255), type="double3")




    def update_controls(self):
        index = self.get_object_index()
        if index == 0:
            return
        # update the sliders
        x_offset = cmds.getAttr(f"{self.speed_node}.text_x_offset{index}")
        self.sld_x_offset.setValue(x_offset)
        y_offset = cmds.getAttr(f"{self.speed_node}.text_y_offset{index}")
        self.sld_y_offset.setValue(y_offset)

        visible = cmds.getAttr(f"{self.speed_node}.show_object_speed{index}")
        self.chk_visible.setChecked(visible)

        # set the colour
        attribute_name = f"{self.speed_node}.speed_text_colour{index}"
        stylesheet = self.get_stylesheet_from_attribute(attribute_name)
        self.btn_text_colour.setStyleSheet(stylesheet)

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