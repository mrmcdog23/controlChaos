# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cc_hud_panel_source.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
from CCPySide import QtWidgets, QtGui, QtCore


class Ui_context_panel(object):
    def setupUi(self, context_panel):
        if not context_panel.objectName():
            context_panel.setObjectName(u"context_panel")
        context_panel.resize(446, 947)
        context_panel.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(context_panel)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lbl_header = QtWidgets.QLabel(context_panel)
        self.lbl_header.setObjectName(u"lbl_header")
        self.lbl_header.setMinimumSize(QtCore.QSize(400, 0))
        self.lbl_header.setMaximumSize(QtCore.QSize(400, 0))
        self.lbl_header.setScaledContents(True)

        self.verticalLayout_3.addWidget(self.lbl_header)

        self.tabWidget = QtWidgets.QTabWidget(context_panel)
        self.tabWidget.setObjectName(u"tabWidget")
        self.camera_tab = QtWidgets.QWidget()
        self.camera_tab.setObjectName(u"camera_tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.camera_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lbl_cam_x_offset = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_x_offset.setObjectName(u"lbl_cam_x_offset")

        self.gridLayout_2.addWidget(self.lbl_cam_x_offset, 1, 0, 1, 1)

        self.sld_cam_x_offset = QtWidgets.QSlider(self.camera_tab)
        self.sld_cam_x_offset.setObjectName(u"sld_cam_x_offset")
        self.sld_cam_x_offset.setMinimum(0)
        self.sld_cam_x_offset.setMaximum(50)
        self.sld_cam_x_offset.setOrientation(QtCore.Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sld_cam_x_offset, 1, 2, 1, 1)

        self.cmb_cam_font_type = QtWidgets.QComboBox(self.camera_tab)
        self.cmb_cam_font_type.setObjectName(u"cmb_cam_font_type")
        self.cmb_cam_font_type.setMaximumSize(QtCore.QSize(100, 16777215))

        self.gridLayout_2.addWidget(self.cmb_cam_font_type, 5, 1, 1, 1)

        self.lbl_cam_y_offset = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_y_offset.setObjectName(u"lbl_cam_y_offset")

        self.gridLayout_2.addWidget(self.lbl_cam_y_offset, 2, 0, 1, 1)

        self.lbl_cam_font_type = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_font_type.setObjectName(u"lbl_cam_font_type")

        self.gridLayout_2.addWidget(self.lbl_cam_font_type, 5, 0, 1, 1)

        self.sb_cam_text_scale = QtWidgets.QDoubleSpinBox(self.camera_tab)
        self.sb_cam_text_scale.setObjectName(u"sb_cam_text_scale")
        self.sb_cam_text_scale.setMinimumSize(QtCore.QSize(100, 0))
        self.sb_cam_text_scale.setMaximumSize(QtCore.QSize(100, 16777215))
        self.sb_cam_text_scale.setReadOnly(True)
        self.sb_cam_text_scale.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.sb_cam_text_scale.setMinimum(0.500000000000000)
        self.sb_cam_text_scale.setMaximum(2.000000000000000)
        self.sb_cam_text_scale.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.sb_cam_text_scale, 0, 1, 1, 1)

        self.lbl_cam_text_scale = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_text_scale.setObjectName(u"lbl_cam_text_scale")

        self.gridLayout_2.addWidget(self.lbl_cam_text_scale, 0, 0, 1, 1)

        self.lbl_cam_text_colour = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_text_colour.setObjectName(u"lbl_cam_text_colour")

        self.gridLayout_2.addWidget(self.lbl_cam_text_colour, 7, 0, 1, 1)

        self.sb_cam_x_offset = QtWidgets.QSpinBox(self.camera_tab)
        self.sb_cam_x_offset.setObjectName(u"sb_cam_x_offset")
        self.sb_cam_x_offset.setMinimumSize(QtCore.QSize(100, 0))
        self.sb_cam_x_offset.setMaximumSize(QtCore.QSize(100, 16777215))
        self.sb_cam_x_offset.setReadOnly(True)
        self.sb_cam_x_offset.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.sb_cam_x_offset.setMinimum(0)
        self.sb_cam_x_offset.setMaximum(50)

        self.gridLayout_2.addWidget(self.sb_cam_x_offset, 1, 1, 1, 1)

        self.lbl_cam_font_weight = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_font_weight.setObjectName(u"lbl_cam_font_weight")

        self.gridLayout_2.addWidget(self.lbl_cam_font_weight, 6, 0, 1, 1)

        self.btn_cam_text_colour = QtWidgets.QPushButton(self.camera_tab)
        self.btn_cam_text_colour.setObjectName(u"btn_cam_text_colour")
        self.btn_cam_text_colour.setMinimumSize(QtCore.QSize(100, 0))
        self.btn_cam_text_colour.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btn_cam_text_colour.setStyleSheet(u"background-color: rgb(255, 258, 0.6);")

        self.gridLayout_2.addWidget(self.btn_cam_text_colour, 7, 1, 1, 1)

        self.sb_cam_y_offset = QtWidgets.QSpinBox(self.camera_tab)
        self.sb_cam_y_offset.setObjectName(u"sb_cam_y_offset")
        self.sb_cam_y_offset.setMinimumSize(QtCore.QSize(100, 0))
        self.sb_cam_y_offset.setMaximumSize(QtCore.QSize(100, 16777215))
        self.sb_cam_y_offset.setReadOnly(True)
        self.sb_cam_y_offset.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.sb_cam_y_offset.setMinimum(-50)
        self.sb_cam_y_offset.setMaximum(50)

        self.gridLayout_2.addWidget(self.sb_cam_y_offset, 2, 1, 1, 1)

        self.sld_cam_text_scale = QtWidgets.QSlider(self.camera_tab)
        self.sld_cam_text_scale.setObjectName(u"sld_cam_text_scale")
        self.sld_cam_text_scale.setMinimum(50)
        self.sld_cam_text_scale.setMaximum(200)
        self.sld_cam_text_scale.setSingleStep(1)
        self.sld_cam_text_scale.setValue(50)
        self.sld_cam_text_scale.setOrientation(QtCore.Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sld_cam_text_scale, 0, 2, 1, 1)

        self.line = QtWidgets.QFrame(self.camera_tab)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line, 4, 0, 1, 3)

        self.cmb_cam_font_weight = QtWidgets.QComboBox(self.camera_tab)
        self.cmb_cam_font_weight.setObjectName(u"cmb_cam_font_weight")
        self.cmb_cam_font_weight.setMaximumSize(QtCore.QSize(100, 16777215))

        self.gridLayout_2.addWidget(self.cmb_cam_font_weight, 6, 1, 1, 1)

        self.sld_cam_y_offset = QtWidgets.QSlider(self.camera_tab)
        self.sld_cam_y_offset.setObjectName(u"sld_cam_y_offset")
        self.sld_cam_y_offset.setMinimum(-50)
        self.sld_cam_y_offset.setMaximum(50)
        self.sld_cam_y_offset.setOrientation(QtCore.Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sld_cam_y_offset, 2, 2, 1, 1)

        self.lbl_cam_text_alpha = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_text_alpha.setObjectName(u"lbl_cam_text_alpha")

        self.gridLayout_2.addWidget(self.lbl_cam_text_alpha, 3, 0, 1, 1)

        self.sld_cam_font_alpha = QtWidgets.QSlider(self.camera_tab)
        self.sld_cam_font_alpha.setObjectName(u"sld_cam_font_alpha")
        self.sld_cam_font_alpha.setMinimum(0)
        self.sld_cam_font_alpha.setMaximum(100)
        self.sld_cam_font_alpha.setOrientation(QtCore.Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sld_cam_font_alpha, 3, 2, 1, 1)

        self.sb_cam_font_alpha = QtWidgets.QDoubleSpinBox(self.camera_tab)
        self.sb_cam_font_alpha.setObjectName(u"sb_cam_font_alpha")
        self.sb_cam_font_alpha.setMinimumSize(QtCore.QSize(100, 0))
        self.sb_cam_font_alpha.setMaximumSize(QtCore.QSize(100, 16777215))
        self.sb_cam_font_alpha.setReadOnly(True)
        self.sb_cam_font_alpha.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.sb_cam_font_alpha.setMaximum(100.000000000000000)
        self.sb_cam_font_alpha.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.sb_cam_font_alpha, 3, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_2)

        self.line_2 = QtWidgets.QFrame(self.camera_tab)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_2)

        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.lbl_cam_x_offset_4 = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_x_offset_4.setObjectName(u"lbl_cam_x_offset_4")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_4, 3, 3, 1, 1)

        self.horizontalSpacer_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_2, 6, 2, 1, 1)

        self.lbl_cam_x_offset_5 = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_x_offset_5.setObjectName(u"lbl_cam_x_offset_5")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_5, 4, 3, 1, 1)

        self.chk_focal_length = QtWidgets.QCheckBox(self.camera_tab)
        self.chk_focal_length.setObjectName(u"chk_focal_length")

        self.gridLayout_7.addWidget(self.chk_focal_length, 1, 0, 1, 1)

        self.chk_object_distance = QtWidgets.QCheckBox(self.camera_tab)
        self.chk_object_distance.setObjectName(u"chk_object_distance")

        self.gridLayout_7.addWidget(self.chk_object_distance, 6, 0, 1, 2)

        self.chk_speed = QtWidgets.QCheckBox(self.camera_tab)
        self.chk_speed.setObjectName(u"chk_speed")

        self.gridLayout_7.addWidget(self.chk_speed, 5, 0, 1, 1)

        self.lbl_cam_x_offset_2 = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_x_offset_2.setObjectName(u"lbl_cam_x_offset_2")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_2, 1, 3, 1, 1)

        self.sb_rotations = QtWidgets.QSpinBox(self.camera_tab)
        self.sb_rotations.setObjectName(u"sb_rotations")
        self.sb_rotations.setMinimumSize(QtCore.QSize(60, 0))
        self.sb_rotations.setMinimum(0)
        self.sb_rotations.setMaximum(6)
        self.sb_rotations.setValue(0)

        self.gridLayout_7.addWidget(self.sb_rotations, 2, 4, 1, 1)

        self.sb_object_distance = QtWidgets.QSpinBox(self.camera_tab)
        self.sb_object_distance.setObjectName(u"sb_object_distance")
        self.sb_object_distance.setMinimumSize(QtCore.QSize(60, 0))
        self.sb_object_distance.setMinimum(0)
        self.sb_object_distance.setMaximum(6)
        self.sb_object_distance.setValue(0)

        self.gridLayout_7.addWidget(self.sb_object_distance, 6, 4, 1, 1)

        self.sb_frame_number = QtWidgets.QSpinBox(self.camera_tab)
        self.sb_frame_number.setObjectName(u"sb_frame_number")
        self.sb_frame_number.setMinimumSize(QtCore.QSize(60, 0))
        self.sb_frame_number.setMinimum(0)
        self.sb_frame_number.setMaximum(6)
        self.sb_frame_number.setValue(0)

        self.gridLayout_7.addWidget(self.sb_frame_number, 4, 4, 1, 1)

        self.chk_rotations = QtWidgets.QCheckBox(self.camera_tab)
        self.chk_rotations.setObjectName(u"chk_rotations")

        self.gridLayout_7.addWidget(self.chk_rotations, 2, 0, 1, 1)

        self.sb_focal_length = QtWidgets.QSpinBox(self.camera_tab)
        self.sb_focal_length.setObjectName(u"sb_focal_length")
        self.sb_focal_length.setMinimumSize(QtCore.QSize(60, 0))
        self.sb_focal_length.setMinimum(0)
        self.sb_focal_length.setMaximum(6)
        self.sb_focal_length.setValue(0)

        self.gridLayout_7.addWidget(self.sb_focal_length, 1, 4, 1, 1)

        self.chk_frame_number = QtWidgets.QCheckBox(self.camera_tab)
        self.chk_frame_number.setObjectName(u"chk_frame_number")

        self.gridLayout_7.addWidget(self.chk_frame_number, 4, 0, 1, 1)

        self.sb_speed = QtWidgets.QSpinBox(self.camera_tab)
        self.sb_speed.setObjectName(u"sb_speed")
        self.sb_speed.setMinimumSize(QtCore.QSize(60, 0))
        self.sb_speed.setMinimum(0)
        self.sb_speed.setMaximum(6)
        self.sb_speed.setValue(0)

        self.gridLayout_7.addWidget(self.sb_speed, 5, 4, 1, 1)

        self.lbl_cam_x_offset_7 = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_x_offset_7.setObjectName(u"lbl_cam_x_offset_7")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_7, 6, 3, 1, 1)

        self.chk_height = QtWidgets.QCheckBox(self.camera_tab)
        self.chk_height.setObjectName(u"chk_height")

        self.gridLayout_7.addWidget(self.chk_height, 3, 0, 1, 1)

        self.lbl_cam_x_offset_3 = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_x_offset_3.setObjectName(u"lbl_cam_x_offset_3")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_3, 2, 3, 1, 1)

        self.sb_height = QtWidgets.QSpinBox(self.camera_tab)
        self.sb_height.setObjectName(u"sb_height")
        self.sb_height.setMinimumSize(QtCore.QSize(60, 0))
        self.sb_height.setMinimum(0)
        self.sb_height.setMaximum(6)
        self.sb_height.setValue(0)

        self.gridLayout_7.addWidget(self.sb_height, 3, 4, 1, 1)

        self.lbl_cam_x_offset_6 = QtWidgets.QLabel(self.camera_tab)
        self.lbl_cam_x_offset_6.setObjectName(u"lbl_cam_x_offset_6")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_6, 5, 3, 1, 1)

        self.horizontalSpacer_9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_9, 6, 5, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_7)

        self.line_3 = QtWidgets.QFrame(self.camera_tab)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.lbl_camera_height_units = QtWidgets.QLabel(self.camera_tab)
        self.lbl_camera_height_units.setObjectName(u"lbl_camera_height_units")
        self.lbl_camera_height_units.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lbl_camera_height_units.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lbl_camera_height_units.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.lbl_camera_height_units, 0, 0, 1, 1)

        self.cmb_camera_height_units = QtWidgets.QComboBox(self.camera_tab)
        self.cmb_camera_height_units.setObjectName(u"cmb_camera_height_units")

        self.gridLayout_8.addWidget(self.cmb_camera_height_units, 0, 1, 1, 2)

        self.btn_add_ground_geo = QtWidgets.QPushButton(self.camera_tab)
        self.btn_add_ground_geo.setObjectName(u"btn_add_ground_geo")

        self.gridLayout_8.addWidget(self.btn_add_ground_geo, 1, 0, 1, 1)

        self.le_ground_geo = QtWidgets.QLineEdit(self.camera_tab)
        self.le_ground_geo.setObjectName(u"le_ground_geo")

        self.gridLayout_8.addWidget(self.le_ground_geo, 1, 1, 1, 2)

        self.btn_distance_object = QtWidgets.QPushButton(self.camera_tab)
        self.btn_distance_object.setObjectName(u"btn_distance_object")

        self.gridLayout_8.addWidget(self.btn_distance_object, 2, 0, 1, 1)

        self.le_distance_object = QtWidgets.QLineEdit(self.camera_tab)
        self.le_distance_object.setObjectName(u"le_distance_object")

        self.gridLayout_8.addWidget(self.le_distance_object, 2, 1, 1, 2)


        self.verticalLayout_2.addLayout(self.gridLayout_8)

        self.verticalSpacer_2 = QtWidgets.QSpacerItem(20, 84, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.camera_tab, "")
        self.speed_tab = QtWidgets.QWidget()
        self.speed_tab.setObjectName(u"speed_tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.speed_tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.speed_tab)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalSpacer_4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_4, 0, 2, 1, 1)

        self.horizontalSpacer_3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_3, 0, 0, 1, 1)

        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.cmb_font_type = QtWidgets.QComboBox(self.groupBox)
        self.cmb_font_type.setObjectName(u"cmb_font_type")

        self.gridLayout_3.addWidget(self.cmb_font_type, 1, 1, 1, 1)

        self.cmb_font_weight = QtWidgets.QComboBox(self.groupBox)
        self.cmb_font_weight.setObjectName(u"cmb_font_weight")

        self.gridLayout_3.addWidget(self.cmb_font_weight, 2, 1, 1, 1)

        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)

        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)

        self.sp_font_size = QtWidgets.QSpinBox(self.groupBox)
        self.sp_font_size.setObjectName(u"sp_font_size")

        self.gridLayout_3.addWidget(self.sp_font_size, 0, 1, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btn_add_selected = QtWidgets.QPushButton(self.speed_tab)
        self.btn_add_selected.setObjectName(u"btn_add_selected")

        self.horizontalLayout_2.addWidget(self.btn_add_selected)

        self.cmb_speed_objects = QtWidgets.QComboBox(self.speed_tab)
        self.cmb_speed_objects.setObjectName(u"cmb_speed_objects")

        self.horizontalLayout_2.addWidget(self.cmb_speed_objects)

        self.lbl_speed_unit = QtWidgets.QLabel(self.speed_tab)
        self.lbl_speed_unit.setObjectName(u"lbl_speed_unit")
        self.lbl_speed_unit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.lbl_speed_unit.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lbl_speed_unit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.lbl_speed_unit)

        self.cmb_speed_unit = QtWidgets.QComboBox(self.speed_tab)
        self.cmb_speed_unit.setObjectName(u"cmb_speed_unit")

        self.horizontalLayout_2.addWidget(self.cmb_speed_unit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.groupBox_2 = QtWidgets.QGroupBox(self.speed_tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.chk_visible = QtWidgets.QCheckBox(self.groupBox_2)
        self.chk_visible.setObjectName(u"chk_visible")

        self.horizontalLayout_4.addWidget(self.chk_visible)

        self.horizontalSpacer_7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_7)

        self.lbl_text_colour = QtWidgets.QLabel(self.groupBox_2)
        self.lbl_text_colour.setObjectName(u"lbl_text_colour")

        self.horizontalLayout_4.addWidget(self.lbl_text_colour)

        self.btn_text_colour = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_text_colour.setObjectName(u"btn_text_colour")
        self.btn_text_colour.setMinimumSize(QtCore.QSize(100, 0))
        self.btn_text_colour.setStyleSheet(u"background-color: rgb(255, 258, 0.6);")

        self.horizontalLayout_4.addWidget(self.btn_text_colour)

        self.horizontalSpacer_8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)


        self.gridLayout_6.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.lbl_y_offset = QtWidgets.QLabel(self.groupBox_2)
        self.lbl_y_offset.setObjectName(u"lbl_y_offset")

        self.gridLayout_5.addWidget(self.lbl_y_offset, 1, 0, 1, 1)

        self.sld_x_offset = QtWidgets.QSlider(self.groupBox_2)
        self.sld_x_offset.setObjectName(u"sld_x_offset")
        self.sld_x_offset.setMinimum(-50)
        self.sld_x_offset.setMaximum(50)
        self.sld_x_offset.setOrientation(QtCore.Qt.Horizontal)

        self.gridLayout_5.addWidget(self.sld_x_offset, 0, 3, 1, 1)

        self.sld_y_offset = QtWidgets.QSlider(self.groupBox_2)
        self.sld_y_offset.setObjectName(u"sld_y_offset")
        self.sld_y_offset.setMinimum(-50)
        self.sld_y_offset.setMaximum(50)
        self.sld_y_offset.setOrientation(QtCore.Qt.Horizontal)

        self.gridLayout_5.addWidget(self.sld_y_offset, 1, 3, 1, 1)

        self.lbl_x_offset = QtWidgets.QLabel(self.groupBox_2)
        self.lbl_x_offset.setObjectName(u"lbl_x_offset")

        self.gridLayout_5.addWidget(self.lbl_x_offset, 0, 0, 1, 2)

        self.sb_x_offset = QtWidgets.QSpinBox(self.groupBox_2)
        self.sb_x_offset.setObjectName(u"sb_x_offset")
        self.sb_x_offset.setMinimumSize(QtCore.QSize(100, 0))
        self.sb_x_offset.setMaximumSize(QtCore.QSize(100, 16777215))
        self.sb_x_offset.setReadOnly(True)
        self.sb_x_offset.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.sb_x_offset.setMinimum(-50)
        self.sb_x_offset.setMaximum(50)

        self.gridLayout_5.addWidget(self.sb_x_offset, 0, 2, 1, 1)

        self.sb_y_offset = QtWidgets.QSpinBox(self.groupBox_2)
        self.sb_y_offset.setObjectName(u"sb_y_offset")
        self.sb_y_offset.setMinimumSize(QtCore.QSize(100, 0))
        self.sb_y_offset.setMaximumSize(QtCore.QSize(100, 16777215))
        self.sb_y_offset.setReadOnly(True)
        self.sb_y_offset.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.sb_y_offset.setMinimum(-50)
        self.sb_y_offset.setMaximum(50)

        self.gridLayout_5.addWidget(self.sb_y_offset, 1, 2, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_5, 1, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 76, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.speed_tab, "")

        self.verticalLayout_3.addWidget(self.tabWidget)


        self.retranslateUi(context_panel)

        self.tabWidget.setCurrentIndex(0)


        QtCore.QMetaObject.connectSlotsByName(context_panel)
    # setupUi

    def retranslateUi(self, context_panel):
        context_panel.setWindowTitle(QtCore.QCoreApplication.translate("context_panel", u"Form", None))
        self.lbl_header.setText("")
        self.lbl_cam_x_offset.setText(QtCore.QCoreApplication.translate("context_panel", u"Text X Offset", None))
        self.lbl_cam_y_offset.setText(QtCore.QCoreApplication.translate("context_panel", u"Text Y Offset", None))
        self.lbl_cam_font_type.setText(QtCore.QCoreApplication.translate("context_panel", u"Font Type", None))
        self.lbl_cam_text_scale.setText(QtCore.QCoreApplication.translate("context_panel", u"Text Scale", None))
        self.lbl_cam_text_colour.setText(QtCore.QCoreApplication.translate("context_panel", u"Text Colour", None))
        self.lbl_cam_font_weight.setText(QtCore.QCoreApplication.translate("context_panel", u"Font Weight", None))
        self.btn_cam_text_colour.setText("")
        self.lbl_cam_text_alpha.setText(QtCore.QCoreApplication.translate("context_panel", u"Text Alpha", None))
        self.lbl_cam_x_offset_4.setText(QtCore.QCoreApplication.translate("context_panel", u"Position", None))
        self.lbl_cam_x_offset_5.setText(QtCore.QCoreApplication.translate("context_panel", u"Position", None))
        self.chk_focal_length.setText(QtCore.QCoreApplication.translate("context_panel", u"Focal Length", None))
        self.chk_object_distance.setText(QtCore.QCoreApplication.translate("context_panel", u"Object Distance", None))
        self.chk_speed.setText(QtCore.QCoreApplication.translate("context_panel", u"Speed", None))
        self.lbl_cam_x_offset_2.setText(QtCore.QCoreApplication.translate("context_panel", u"Position", None))
        self.chk_rotations.setText(QtCore.QCoreApplication.translate("context_panel", u"Rotations", None))
        self.chk_frame_number.setText(QtCore.QCoreApplication.translate("context_panel", u"Frame Number", None))
        self.lbl_cam_x_offset_7.setText(QtCore.QCoreApplication.translate("context_panel", u"Position", None))
        self.chk_height.setText(QtCore.QCoreApplication.translate("context_panel", u"Height", None))
        self.lbl_cam_x_offset_3.setText(QtCore.QCoreApplication.translate("context_panel", u"Position", None))
        self.lbl_cam_x_offset_6.setText(QtCore.QCoreApplication.translate("context_panel", u"Position", None))
        self.lbl_camera_height_units.setText(QtCore.QCoreApplication.translate("context_panel", u"Camera Height Unit ", None))
        self.btn_add_ground_geo.setText(QtCore.QCoreApplication.translate("context_panel", u"Add Selected Ground Geo", None))
        self.btn_distance_object.setText(QtCore.QCoreApplication.translate("context_panel", u"Distance To Selected Object", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.camera_tab), QtCore.QCoreApplication.translate("context_panel", u"Camera", None))
        self.groupBox.setTitle(QtCore.QCoreApplication.translate("context_panel", u"Font Settings", None))
        self.label_2.setText(QtCore.QCoreApplication.translate("context_panel", u"Font Weight", None))
        self.label_4.setText(QtCore.QCoreApplication.translate("context_panel", u"Font Size", None))
        self.label.setText(QtCore.QCoreApplication.translate("context_panel", u"Font Type", None))
        self.btn_add_selected.setText(QtCore.QCoreApplication.translate("context_panel", u"Add Selected", None))
        self.lbl_speed_unit.setText(QtCore.QCoreApplication.translate("context_panel", u"Unit", None))
        self.groupBox_2.setTitle(QtCore.QCoreApplication.translate("context_panel", u"Text Controls", None))
        self.chk_visible.setText(QtCore.QCoreApplication.translate("context_panel", u"Visible", None))
        self.lbl_text_colour.setText(QtCore.QCoreApplication.translate("context_panel", u"Text Color", None))
        self.btn_text_colour.setText("")
        self.lbl_y_offset.setText(QtCore.QCoreApplication.translate("context_panel", u"X Offset", None))
        self.lbl_x_offset.setText(QtCore.QCoreApplication.translate("context_panel", u"X Offset", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.speed_tab), QtCore.QCoreApplication.translate("context_panel", u"Speed", None))
    # retranslateUi


