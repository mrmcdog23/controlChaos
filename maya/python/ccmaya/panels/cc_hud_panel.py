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
    title = "Control Chaos HUD"
    def __init__(self, parent):
        super().__init__(parent)
        self.populate_data()
        self.populate_speed_objects()
        self.update_cam_controls()
        self.update_speed_controls()
        self.connect_signals()
        self.lbl_header.setHidden(True)
        self.resize(500, 600)

    def populate_data(self):
        top_text_font_index = cmds.getAttr(f"{self.cam_node}.top_text_font")
        self.cmb_cam_font_type.addItems(FONT_LIST)
        self.cmb_cam_font_type.setCurrentIndex(top_text_font_index)

        font_weight_index = cmds.getAttr(f"{self.cam_node}.top_text_font_weight")
        self.cmb_cam_font_weight.addItems(FONT_WEIGHT)
        self.cmb_cam_font_weight.setCurrentIndex(font_weight_index)

        cam_unit_index = cmds.getAttr(f"{self.cam_node}.camera_height_units")
        self.cmb_camera_height_units.addItems(["Meters", "Feet"])
        self.cmb_camera_height_units.setCurrentIndex(cam_unit_index)

        # populate speed data
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
        # connect the camera controls
        self.sld_cam_text_scale.valueChanged.connect(self.set_cam_text_scale)
        self.sld_cam_x_offset.valueChanged.connect(self.set_cam_x_offset)
        self.sld_cam_y_offset.valueChanged.connect(self.set_cam_y_offset)
        self.cmb_cam_font_type.currentIndexChanged.connect(self.set_cam_font_type)
        self.cmb_cam_font_weight.currentIndexChanged.connect(self.set_cam_font_weight)
        self.btn_cam_text_colour.clicked.connect(self.set_cam_colour)
        self.sld_cam_font_alpha.valueChanged.connect(self.set_cam_font_alpha)

        # display objects
        self.chk_focal_length.toggled.connect(self.show_focal_length)
        self.chk_rotations.toggled.connect(self.show_rotations)
        self.chk_height.toggled.connect(self.show_height)
        self.chk_frame_number.toggled.connect(self.show_frame_number)
        self.chk_speed.toggled.connect(self.show_speed)
        self.chk_object_distance.toggled.connect(self.show_object_distance)

        # set the text positions
        self.sb_focal_length.valueChanged.connect(self.set_focal_length_pos)
        self.sb_rotations.valueChanged.connect(self.set_rotations_pos)
        self.sb_height.valueChanged.connect(self.set_height_pos)
        self.sb_frame_number.valueChanged.connect(self.set_frame_number_pos)
        self.sb_speed.valueChanged.connect(self.set_speed_pos)
        self.sb_object_distance.valueChanged.connect(self.set_object_distance_pos)

        # options signals
        self.btn_add_ground_geo.clicked.connect(self.add_ground_geo)
        self.cmb_camera_height_units.currentIndexChanged.connect(self.set_camera_height_units)
        self.btn_distance_object.clicked.connect(self.set_distance_object)

        # connect the speed controls
        self.sp_font_size.valueChanged.connect(self.set_font_size)
        self.cmb_font_type.currentIndexChanged.connect(self.set_font_type)
        self.cmb_font_weight.currentIndexChanged.connect(self.set_font_weight)
        self.cmb_speed_unit.currentIndexChanged.connect(self.set_speed_unit)
        self.btn_add_selected.clicked.connect(self.add_selected_object)
        self.cmb_speed_objects.currentIndexChanged.connect(self.update_speed_controls)
        self.sld_x_offset.valueChanged.connect(self.set_x_sb)
        self.sld_y_offset.valueChanged.connect(self.set_y_sb)
        self.chk_visible.toggled.connect(self.set_visible)
        self.btn_text_colour.clicked.connect(self.set_speed_colour)

    @property
    def cam_node(self):
        cc_cam_node = cmds.ls(type="controlChaosHUD")
        if cc_cam_node:
            return cc_cam_node[0]
        if not cmds.pluginInfo("controlChaosHUD.py", query=True, loaded=True):
            cmds.loadPlugin("controlChaosHUD.py")
        return cmds.createNode("controlChaosHUD")

    @property
    def speed_node(self):
        cc_speed_node = cmds.ls(type="objectSpeedHUD")
        if cc_speed_node:
            return cc_speed_node[0]
        if not cmds.pluginInfo("objectSpeedHUD.py", query=True, loaded=True):
            cmds.loadPlugin("objectSpeedHUD.py")
        return cmds.createNode("objectSpeedHUD")

    def show_focal_length(self, show):
        cmds.setAttr(f"{self.cam_node}.show_focal_length", show)

    def show_rotations(self, show):
        cmds.setAttr(f"{self.cam_node}.show_camera_rotations", show)

    def show_height(self, show):
        cmds.setAttr(f"{self.cam_node}.show_camera_height", show)

    def show_frame_number(self, show):
        cmds.setAttr(f"{self.cam_node}.show_frame_number", show)

    def show_speed(self, show):
        cmds.setAttr(f"{self.cam_node}.show_camera_speed", show)

    def show_object_distance(self, show):
        cmds.setAttr(f"{self.cam_node}.show_distance_to_object", show)

    def set_focal_length_pos(self, value):
        cmds.setAttr(f"{self.cam_node}.focal_length_position", value)

    def set_rotations_pos(self, value):
        cmds.setAttr(f"{self.cam_node}.camera_rotations_position", value)

    def set_height_pos(self, value):
        cmds.setAttr(f"{self.cam_node}.camera_height_position", value)

    def set_frame_number_pos(self, value):
        cmds.setAttr(f"{self.cam_node}.frame_number_position", value)

    def set_speed_pos(self, value):
        cmds.setAttr(f"{self.cam_node}.camera_speed_position", value)

    def set_object_distance_pos(self, value):
        cmds.setAttr(f"{self.cam_node}.distance_to_actor_position", value)

    def set_cam_text_scale(self):
        cam_text_scale = self.sld_cam_text_scale.value() / 100
        self.sb_cam_text_scale.setValue(cam_text_scale)
        cmds.setAttr(f"{self.cam_node}.overall_text_scale", cam_text_scale)

    def set_cam_x_offset(self):
        cam_x_offset = self.sld_cam_x_offset.value()
        self.sb_cam_x_offset.setValue(cam_x_offset)
        cmds.setAttr(f"{self.cam_node}.top_text_padding", cam_x_offset)
        cmds.setAttr(f"{self.cam_node}.bottom_text_padding", cam_x_offset)

    def set_cam_y_offset(self):
        cam_y_offset = self.sld_cam_y_offset.value()
        self.sb_cam_y_offset.setValue(cam_y_offset)
        cmds.setAttr(f"{self.cam_node}.text_y_offset", cam_y_offset)

    def set_cam_font_type(self):
        cam_font_type_index = self.cmb_cam_font_type.currentIndex()
        cmds.setAttr(f"{self.cam_node}.top_text_font", cam_font_type_index)
        cmds.setAttr(f"{self.cam_node}.bottom_text_font", cam_font_type_index)

    def set_cam_font_weight(self):
        cam_font_weight_index = self.cmb_cam_font_weight.currentIndex()
        cmds.setAttr(f"{self.cam_node}.top_text_font_weight", cam_font_weight_index)
        cmds.setAttr(f"{self.cam_node}.bottom_text_font_weight", cam_font_weight_index)

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

    def get_speed_object_list(self):
        speed_object_list = list()
        for num in range(1, 6):
            attribute_name = f"{self.speed_node}.object_name{num}"
            object_name = cmds.getAttr(attribute_name)
            if not object_name:
                return speed_object_list
            speed_object_list.append(object_name)
        return speed_object_list

    def add_ground_geo(self):
        selected_object = cmds.ls(sl=True)[0]
        self.le_ground_geo.setText(selected_object)
        cmds.setAttr(f"{self.cam_node}.ground_geo", selected_object, type="string")

    def set_distance_object(self):
        selected_object = cmds.ls(sl=True)[0]
        self.le_distance_object.setText(selected_object)
        cmds.setAttr(f"{self.cam_node}.object_name", selected_object, type="string")

    def set_camera_height_units(self):
        camera_height_units_index = self.cmb_camera_height_units.currentIndex()
        cmds.setAttr(f"{self.cam_node}.camera_height_units", camera_height_units_index)

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

    def set_speed_colour(self):
        colour = QtWidgets.QColorDialog.getColor()
        r, g, b, _ = colour.getRgb()
        stylesheet = f"background-color: rgb({r}, {g}, {b});"
        self.btn_text_colour.setStyleSheet(stylesheet)

        index = self.get_object_index()
        attribute_name = f"{self.speed_node}.speed_text_colour{index}"
        cmds.setAttr(attribute_name, (r/255), (g/255), (b/255), type="double3")

    def set_cam_colour(self):
        colour = QtWidgets.QColorDialog.getColor()
        r, g, b, _ = colour.getRgb()
        stylesheet = f"background-color: rgb({r}, {g}, {b});"
        self.btn_cam_text_colour.setStyleSheet(stylesheet)
        for attr in ["top_text_color", "bottom_text_color"]:
            attribute_name = f"{self.cam_node}.{attr}"
            cmds.setAttr(attribute_name, (r/255), (g/255), (b/255), type="double3")

    def set_cam_font_alpha(self):
        cam_font_alpha = self.sld_cam_font_alpha.value() / 100
        self.sb_cam_font_alpha.setValue(cam_font_alpha)
        cmds.setAttr(f"{self.cam_node}.top_text_alpha", cam_font_alpha)
        cmds.setAttr(f"{self.cam_node}.bottom_text_alpha", cam_font_alpha)

    def update_cam_controls(self):
        # set the colour
        attribute_name = f"{self.cam_node}.top_text_color"
        stylesheet = self.get_stylesheet_from_attribute(attribute_name)
        self.btn_cam_text_colour.setStyleSheet(stylesheet)

        cam_text_scale = cmds.getAttr(f"{self.cam_node}.overall_text_scale")
        self.sld_cam_text_scale.setValue(cam_text_scale * 100)
        self.sb_cam_text_scale.setValue(cam_text_scale)

        cam_x_offset = cmds.getAttr(f"{self.cam_node}.top_text_padding")
        self.sld_cam_x_offset.setValue(cam_x_offset)
        self.sb_cam_x_offset.setValue(cam_x_offset)

        cam_y_offset = cmds.getAttr(f"{self.cam_node}.text_y_offset")
        self.sld_cam_y_offset.setValue(cam_y_offset)
        self.sb_cam_y_offset.setValue(cam_y_offset)

        cam_font_alpha = cmds.getAttr(f"{self.cam_node}.top_text_alpha")
        self.sld_cam_font_alpha.setValue(cam_font_alpha * 100)
        self.sb_cam_font_alpha.setValue(cam_font_alpha)

        # camera positions
        show_focal_length = cmds.getAttr(f"{self.cam_node}.show_focal_length")
        self.chk_focal_length.setChecked(show_focal_length)
        focal_length_position = cmds.getAttr(f"{self.cam_node}.focal_length_position")
        self.sb_focal_length.setValue(focal_length_position)

        show_rotations = cmds.getAttr(f"{self.cam_node}.show_camera_rotations")
        self.chk_rotations.setChecked(show_rotations)
        camera_rotations_position = cmds.getAttr(f"{self.cam_node}.camera_rotations_position")
        self.sb_rotations.setValue(camera_rotations_position)

        show_height = cmds.getAttr(f"{self.cam_node}.show_camera_height")
        self.chk_height.setChecked(show_height)
        camera_height_position = cmds.getAttr(f"{self.cam_node}.camera_height_position")
        self.sb_height.setValue(camera_height_position)

        show_frame_number = cmds.getAttr(f"{self.cam_node}.show_frame_number")
        self.chk_frame_number.setChecked(show_frame_number)
        frame_number_position = cmds.getAttr(f"{self.cam_node}.frame_number_position")
        self.sb_frame_number.setValue(frame_number_position)

        show_camera_speed = cmds.getAttr(f"{self.cam_node}.show_camera_speed")
        self.chk_speed.setChecked(show_camera_speed)
        camera_speed_position = cmds.getAttr(f"{self.cam_node}.camera_speed_position")
        self.sb_speed.setValue(camera_speed_position)

        show_distance_to_object = cmds.getAttr(f"{self.cam_node}.show_distance_to_object")
        self.chk_object_distance.setChecked(show_distance_to_object)
        distance_to_actor_position = cmds.getAttr(f"{self.cam_node}.distance_to_actor_position")
        self.sb_object_distance.setValue(distance_to_actor_position)

        ground_geo = cmds.getAttr(f"{self.cam_node}.ground_geo")
        self.le_ground_geo.setText(ground_geo)

        object_name = cmds.getAttr(f"{self.cam_node}.object_name")
        self.le_distance_object.setText(object_name)

    def update_speed_controls(self):
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


'''
def create_cc_panel():
    """
    Create the dockable panel in Maya
    """
    create_dockable_widget.CreateDockableWidget(
        ControlChaosHUDPanel, "Control Chaos Hud", "Control Chaos Hud", 500
    )
'''


def main():
    """
    Launch the maya multi playblast
    """
    maya_utils.launch_maya_win(ControlChaosHUDPanel)