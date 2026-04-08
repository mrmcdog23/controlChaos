# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cc_hud_panel_source.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from CCPySide.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from CCPySide.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from CCPySide.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_context_panel(object):
    def setupUi(self, context_panel):
        if not context_panel.objectName():
            context_panel.setObjectName(u"context_panel")
        context_panel.resize(446, 947)
        context_panel.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_3 = QVBoxLayout(context_panel)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lbl_header = QLabel(context_panel)
        self.lbl_header.setObjectName(u"lbl_header")
        self.lbl_header.setMinimumSize(QSize(400, 0))
        self.lbl_header.setMaximumSize(QSize(400, 0))
        self.lbl_header.setScaledContents(True)

        self.verticalLayout_3.addWidget(self.lbl_header)

        self.tabWidget = QTabWidget(context_panel)
        self.tabWidget.setObjectName(u"tabWidget")
        self.camera_tab = QWidget()
        self.camera_tab.setObjectName(u"camera_tab")
        self.verticalLayout_2 = QVBoxLayout(self.camera_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lbl_cam_x_offset = QLabel(self.camera_tab)
        self.lbl_cam_x_offset.setObjectName(u"lbl_cam_x_offset")

        self.gridLayout_2.addWidget(self.lbl_cam_x_offset, 1, 0, 1, 1)

        self.sld_cam_x_offset = QSlider(self.camera_tab)
        self.sld_cam_x_offset.setObjectName(u"sld_cam_x_offset")
        self.sld_cam_x_offset.setMinimum(0)
        self.sld_cam_x_offset.setMaximum(50)
        self.sld_cam_x_offset.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sld_cam_x_offset, 1, 2, 1, 1)

        self.cmb_cam_font_type = QComboBox(self.camera_tab)
        self.cmb_cam_font_type.setObjectName(u"cmb_cam_font_type")
        self.cmb_cam_font_type.setMaximumSize(QSize(100, 16777215))

        self.gridLayout_2.addWidget(self.cmb_cam_font_type, 5, 1, 1, 1)

        self.lbl_cam_y_offset = QLabel(self.camera_tab)
        self.lbl_cam_y_offset.setObjectName(u"lbl_cam_y_offset")

        self.gridLayout_2.addWidget(self.lbl_cam_y_offset, 2, 0, 1, 1)

        self.lbl_cam_font_type = QLabel(self.camera_tab)
        self.lbl_cam_font_type.setObjectName(u"lbl_cam_font_type")

        self.gridLayout_2.addWidget(self.lbl_cam_font_type, 5, 0, 1, 1)

        self.sb_cam_text_scale = QDoubleSpinBox(self.camera_tab)
        self.sb_cam_text_scale.setObjectName(u"sb_cam_text_scale")
        self.sb_cam_text_scale.setMinimumSize(QSize(100, 0))
        self.sb_cam_text_scale.setMaximumSize(QSize(100, 16777215))
        self.sb_cam_text_scale.setReadOnly(True)
        self.sb_cam_text_scale.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.sb_cam_text_scale.setMinimum(0.500000000000000)
        self.sb_cam_text_scale.setMaximum(2.000000000000000)
        self.sb_cam_text_scale.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.sb_cam_text_scale, 0, 1, 1, 1)

        self.lbl_cam_text_scale = QLabel(self.camera_tab)
        self.lbl_cam_text_scale.setObjectName(u"lbl_cam_text_scale")

        self.gridLayout_2.addWidget(self.lbl_cam_text_scale, 0, 0, 1, 1)

        self.lbl_cam_text_colour = QLabel(self.camera_tab)
        self.lbl_cam_text_colour.setObjectName(u"lbl_cam_text_colour")

        self.gridLayout_2.addWidget(self.lbl_cam_text_colour, 7, 0, 1, 1)

        self.sb_cam_x_offset = QSpinBox(self.camera_tab)
        self.sb_cam_x_offset.setObjectName(u"sb_cam_x_offset")
        self.sb_cam_x_offset.setMinimumSize(QSize(100, 0))
        self.sb_cam_x_offset.setMaximumSize(QSize(100, 16777215))
        self.sb_cam_x_offset.setReadOnly(True)
        self.sb_cam_x_offset.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.sb_cam_x_offset.setMinimum(0)
        self.sb_cam_x_offset.setMaximum(50)

        self.gridLayout_2.addWidget(self.sb_cam_x_offset, 1, 1, 1, 1)

        self.lbl_cam_font_weight = QLabel(self.camera_tab)
        self.lbl_cam_font_weight.setObjectName(u"lbl_cam_font_weight")

        self.gridLayout_2.addWidget(self.lbl_cam_font_weight, 6, 0, 1, 1)

        self.btn_cam_text_colour = QPushButton(self.camera_tab)
        self.btn_cam_text_colour.setObjectName(u"btn_cam_text_colour")
        self.btn_cam_text_colour.setMinimumSize(QSize(100, 0))
        self.btn_cam_text_colour.setMaximumSize(QSize(100, 16777215))
        self.btn_cam_text_colour.setStyleSheet(u"background-color: rgb(255, 258, 0.6);")

        self.gridLayout_2.addWidget(self.btn_cam_text_colour, 7, 1, 1, 1)

        self.sb_cam_y_offset = QSpinBox(self.camera_tab)
        self.sb_cam_y_offset.setObjectName(u"sb_cam_y_offset")
        self.sb_cam_y_offset.setMinimumSize(QSize(100, 0))
        self.sb_cam_y_offset.setMaximumSize(QSize(100, 16777215))
        self.sb_cam_y_offset.setReadOnly(True)
        self.sb_cam_y_offset.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.sb_cam_y_offset.setMinimum(-50)
        self.sb_cam_y_offset.setMaximum(50)

        self.gridLayout_2.addWidget(self.sb_cam_y_offset, 2, 1, 1, 1)

        self.sld_cam_text_scale = QSlider(self.camera_tab)
        self.sld_cam_text_scale.setObjectName(u"sld_cam_text_scale")
        self.sld_cam_text_scale.setMinimum(50)
        self.sld_cam_text_scale.setMaximum(200)
        self.sld_cam_text_scale.setSingleStep(1)
        self.sld_cam_text_scale.setValue(50)
        self.sld_cam_text_scale.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sld_cam_text_scale, 0, 2, 1, 1)

        self.line = QFrame(self.camera_tab)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line, 4, 0, 1, 3)

        self.cmb_cam_font_weight = QComboBox(self.camera_tab)
        self.cmb_cam_font_weight.setObjectName(u"cmb_cam_font_weight")
        self.cmb_cam_font_weight.setMaximumSize(QSize(100, 16777215))

        self.gridLayout_2.addWidget(self.cmb_cam_font_weight, 6, 1, 1, 1)

        self.sld_cam_y_offset = QSlider(self.camera_tab)
        self.sld_cam_y_offset.setObjectName(u"sld_cam_y_offset")
        self.sld_cam_y_offset.setMinimum(-50)
        self.sld_cam_y_offset.setMaximum(50)
        self.sld_cam_y_offset.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sld_cam_y_offset, 2, 2, 1, 1)

        self.lbl_cam_text_alpha = QLabel(self.camera_tab)
        self.lbl_cam_text_alpha.setObjectName(u"lbl_cam_text_alpha")

        self.gridLayout_2.addWidget(self.lbl_cam_text_alpha, 3, 0, 1, 1)

        self.sld_cam_font_alpha = QSlider(self.camera_tab)
        self.sld_cam_font_alpha.setObjectName(u"sld_cam_font_alpha")
        self.sld_cam_font_alpha.setMinimum(0)
        self.sld_cam_font_alpha.setMaximum(100)
        self.sld_cam_font_alpha.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sld_cam_font_alpha, 3, 2, 1, 1)

        self.sb_cam_font_alpha = QDoubleSpinBox(self.camera_tab)
        self.sb_cam_font_alpha.setObjectName(u"sb_cam_font_alpha")
        self.sb_cam_font_alpha.setMinimumSize(QSize(100, 0))
        self.sb_cam_font_alpha.setMaximumSize(QSize(100, 16777215))
        self.sb_cam_font_alpha.setReadOnly(True)
        self.sb_cam_font_alpha.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.sb_cam_font_alpha.setMaximum(100.000000000000000)
        self.sb_cam_font_alpha.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.sb_cam_font_alpha, 3, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_2)

        self.line_2 = QFrame(self.camera_tab)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_2)

        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.lbl_cam_x_offset_4 = QLabel(self.camera_tab)
        self.lbl_cam_x_offset_4.setObjectName(u"lbl_cam_x_offset_4")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_4, 3, 3, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_2, 6, 2, 1, 1)

        self.lbl_cam_x_offset_5 = QLabel(self.camera_tab)
        self.lbl_cam_x_offset_5.setObjectName(u"lbl_cam_x_offset_5")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_5, 4, 3, 1, 1)

        self.chk_focal_length = QCheckBox(self.camera_tab)
        self.chk_focal_length.setObjectName(u"chk_focal_length")

        self.gridLayout_7.addWidget(self.chk_focal_length, 1, 0, 1, 1)

        self.chk_object_distance = QCheckBox(self.camera_tab)
        self.chk_object_distance.setObjectName(u"chk_object_distance")

        self.gridLayout_7.addWidget(self.chk_object_distance, 6, 0, 1, 2)

        self.chk_speed = QCheckBox(self.camera_tab)
        self.chk_speed.setObjectName(u"chk_speed")

        self.gridLayout_7.addWidget(self.chk_speed, 5, 0, 1, 1)

        self.lbl_cam_x_offset_2 = QLabel(self.camera_tab)
        self.lbl_cam_x_offset_2.setObjectName(u"lbl_cam_x_offset_2")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_2, 1, 3, 1, 1)

        self.sb_rotations = QSpinBox(self.camera_tab)
        self.sb_rotations.setObjectName(u"sb_rotations")
        self.sb_rotations.setMinimumSize(QSize(60, 0))
        self.sb_rotations.setMinimum(0)
        self.sb_rotations.setMaximum(6)
        self.sb_rotations.setValue(0)

        self.gridLayout_7.addWidget(self.sb_rotations, 2, 4, 1, 1)

        self.sb_object_distance = QSpinBox(self.camera_tab)
        self.sb_object_distance.setObjectName(u"sb_object_distance")
        self.sb_object_distance.setMinimumSize(QSize(60, 0))
        self.sb_object_distance.setMinimum(0)
        self.sb_object_distance.setMaximum(6)
        self.sb_object_distance.setValue(0)

        self.gridLayout_7.addWidget(self.sb_object_distance, 6, 4, 1, 1)

        self.sb_frame_number = QSpinBox(self.camera_tab)
        self.sb_frame_number.setObjectName(u"sb_frame_number")
        self.sb_frame_number.setMinimumSize(QSize(60, 0))
        self.sb_frame_number.setMinimum(0)
        self.sb_frame_number.setMaximum(6)
        self.sb_frame_number.setValue(0)

        self.gridLayout_7.addWidget(self.sb_frame_number, 4, 4, 1, 1)

        self.chk_rotations = QCheckBox(self.camera_tab)
        self.chk_rotations.setObjectName(u"chk_rotations")

        self.gridLayout_7.addWidget(self.chk_rotations, 2, 0, 1, 1)

        self.sb_focal_length = QSpinBox(self.camera_tab)
        self.sb_focal_length.setObjectName(u"sb_focal_length")
        self.sb_focal_length.setMinimumSize(QSize(60, 0))
        self.sb_focal_length.setMinimum(0)
        self.sb_focal_length.setMaximum(6)
        self.sb_focal_length.setValue(0)

        self.gridLayout_7.addWidget(self.sb_focal_length, 1, 4, 1, 1)

        self.chk_frame_number = QCheckBox(self.camera_tab)
        self.chk_frame_number.setObjectName(u"chk_frame_number")

        self.gridLayout_7.addWidget(self.chk_frame_number, 4, 0, 1, 1)

        self.sb_speed = QSpinBox(self.camera_tab)
        self.sb_speed.setObjectName(u"sb_speed")
        self.sb_speed.setMinimumSize(QSize(60, 0))
        self.sb_speed.setMinimum(0)
        self.sb_speed.setMaximum(6)
        self.sb_speed.setValue(0)

        self.gridLayout_7.addWidget(self.sb_speed, 5, 4, 1, 1)

        self.lbl_cam_x_offset_7 = QLabel(self.camera_tab)
        self.lbl_cam_x_offset_7.setObjectName(u"lbl_cam_x_offset_7")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_7, 6, 3, 1, 1)

        self.chk_height = QCheckBox(self.camera_tab)
        self.chk_height.setObjectName(u"chk_height")

        self.gridLayout_7.addWidget(self.chk_height, 3, 0, 1, 1)

        self.lbl_cam_x_offset_3 = QLabel(self.camera_tab)
        self.lbl_cam_x_offset_3.setObjectName(u"lbl_cam_x_offset_3")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_3, 2, 3, 1, 1)

        self.sb_height = QSpinBox(self.camera_tab)
        self.sb_height.setObjectName(u"sb_height")
        self.sb_height.setMinimumSize(QSize(60, 0))
        self.sb_height.setMinimum(0)
        self.sb_height.setMaximum(6)
        self.sb_height.setValue(0)

        self.gridLayout_7.addWidget(self.sb_height, 3, 4, 1, 1)

        self.lbl_cam_x_offset_6 = QLabel(self.camera_tab)
        self.lbl_cam_x_offset_6.setObjectName(u"lbl_cam_x_offset_6")

        self.gridLayout_7.addWidget(self.lbl_cam_x_offset_6, 5, 3, 1, 1)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_9, 6, 5, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_7)

        self.line_3 = QFrame(self.camera_tab)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.lbl_camera_height_units = QLabel(self.camera_tab)
        self.lbl_camera_height_units.setObjectName(u"lbl_camera_height_units")
        self.lbl_camera_height_units.setMaximumSize(QSize(16777215, 16777215))
        self.lbl_camera_height_units.setLayoutDirection(Qt.RightToLeft)
        self.lbl_camera_height_units.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_8.addWidget(self.lbl_camera_height_units, 0, 0, 1, 1)

        self.cmb_camera_height_units = QComboBox(self.camera_tab)
        self.cmb_camera_height_units.setObjectName(u"cmb_camera_height_units")

        self.gridLayout_8.addWidget(self.cmb_camera_height_units, 0, 1, 1, 2)

        self.btn_add_ground_geo = QPushButton(self.camera_tab)
        self.btn_add_ground_geo.setObjectName(u"btn_add_ground_geo")

        self.gridLayout_8.addWidget(self.btn_add_ground_geo, 1, 0, 1, 1)

        self.le_ground_geo = QLineEdit(self.camera_tab)
        self.le_ground_geo.setObjectName(u"le_ground_geo")

        self.gridLayout_8.addWidget(self.le_ground_geo, 1, 1, 1, 2)

        self.btn_distance_object = QPushButton(self.camera_tab)
        self.btn_distance_object.setObjectName(u"btn_distance_object")

        self.gridLayout_8.addWidget(self.btn_distance_object, 2, 0, 1, 1)

        self.le_distance_object = QLineEdit(self.camera_tab)
        self.le_distance_object.setObjectName(u"le_distance_object")

        self.gridLayout_8.addWidget(self.le_distance_object, 2, 1, 1, 2)


        self.verticalLayout_2.addLayout(self.gridLayout_8)

        self.verticalSpacer_2 = QSpacerItem(20, 84, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.camera_tab, "")
        self.speed_tab = QWidget()
        self.speed_tab.setObjectName(u"speed_tab")
        self.verticalLayout = QVBoxLayout(self.speed_tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(self.speed_tab)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_4, 0, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_3, 0, 0, 1, 1)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.cmb_font_type = QComboBox(self.groupBox)
        self.cmb_font_type.setObjectName(u"cmb_font_type")

        self.gridLayout_3.addWidget(self.cmb_font_type, 1, 1, 1, 1)

        self.cmb_font_weight = QComboBox(self.groupBox)
        self.cmb_font_weight.setObjectName(u"cmb_font_weight")

        self.gridLayout_3.addWidget(self.cmb_font_weight, 2, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)

        self.sp_font_size = QSpinBox(self.groupBox)
        self.sp_font_size.setObjectName(u"sp_font_size")

        self.gridLayout_3.addWidget(self.sp_font_size, 0, 1, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btn_add_selected = QPushButton(self.speed_tab)
        self.btn_add_selected.setObjectName(u"btn_add_selected")

        self.horizontalLayout_2.addWidget(self.btn_add_selected)

        self.cmb_speed_objects = QComboBox(self.speed_tab)
        self.cmb_speed_objects.setObjectName(u"cmb_speed_objects")

        self.horizontalLayout_2.addWidget(self.cmb_speed_objects)

        self.lbl_speed_unit = QLabel(self.speed_tab)
        self.lbl_speed_unit.setObjectName(u"lbl_speed_unit")
        self.lbl_speed_unit.setMaximumSize(QSize(40, 16777215))
        self.lbl_speed_unit.setLayoutDirection(Qt.RightToLeft)
        self.lbl_speed_unit.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.lbl_speed_unit)

        self.cmb_speed_unit = QComboBox(self.speed_tab)
        self.cmb_speed_unit.setObjectName(u"cmb_speed_unit")

        self.horizontalLayout_2.addWidget(self.cmb_speed_unit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.groupBox_2 = QGroupBox(self.speed_tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_6 = QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.chk_visible = QCheckBox(self.groupBox_2)
        self.chk_visible.setObjectName(u"chk_visible")

        self.horizontalLayout_4.addWidget(self.chk_visible)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_7)

        self.lbl_text_colour = QLabel(self.groupBox_2)
        self.lbl_text_colour.setObjectName(u"lbl_text_colour")

        self.horizontalLayout_4.addWidget(self.lbl_text_colour)

        self.btn_text_colour = QPushButton(self.groupBox_2)
        self.btn_text_colour.setObjectName(u"btn_text_colour")
        self.btn_text_colour.setMinimumSize(QSize(100, 0))
        self.btn_text_colour.setStyleSheet(u"background-color: rgb(255, 258, 0.6);")

        self.horizontalLayout_4.addWidget(self.btn_text_colour)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)


        self.gridLayout_6.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.lbl_y_offset = QLabel(self.groupBox_2)
        self.lbl_y_offset.setObjectName(u"lbl_y_offset")

        self.gridLayout_5.addWidget(self.lbl_y_offset, 1, 0, 1, 1)

        self.sld_x_offset = QSlider(self.groupBox_2)
        self.sld_x_offset.setObjectName(u"sld_x_offset")
        self.sld_x_offset.setMinimum(-50)
        self.sld_x_offset.setMaximum(50)
        self.sld_x_offset.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.sld_x_offset, 0, 3, 1, 1)

        self.sld_y_offset = QSlider(self.groupBox_2)
        self.sld_y_offset.setObjectName(u"sld_y_offset")
        self.sld_y_offset.setMinimum(-50)
        self.sld_y_offset.setMaximum(50)
        self.sld_y_offset.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.sld_y_offset, 1, 3, 1, 1)

        self.lbl_x_offset = QLabel(self.groupBox_2)
        self.lbl_x_offset.setObjectName(u"lbl_x_offset")

        self.gridLayout_5.addWidget(self.lbl_x_offset, 0, 0, 1, 2)

        self.sb_x_offset = QSpinBox(self.groupBox_2)
        self.sb_x_offset.setObjectName(u"sb_x_offset")
        self.sb_x_offset.setMinimumSize(QSize(100, 0))
        self.sb_x_offset.setMaximumSize(QSize(100, 16777215))
        self.sb_x_offset.setReadOnly(True)
        self.sb_x_offset.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.sb_x_offset.setMinimum(-50)
        self.sb_x_offset.setMaximum(50)

        self.gridLayout_5.addWidget(self.sb_x_offset, 0, 2, 1, 1)

        self.sb_y_offset = QSpinBox(self.groupBox_2)
        self.sb_y_offset.setObjectName(u"sb_y_offset")
        self.sb_y_offset.setMinimumSize(QSize(100, 0))
        self.sb_y_offset.setMaximumSize(QSize(100, 16777215))
        self.sb_y_offset.setReadOnly(True)
        self.sb_y_offset.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.sb_y_offset.setMinimum(-50)
        self.sb_y_offset.setMaximum(50)

        self.gridLayout_5.addWidget(self.sb_y_offset, 1, 2, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_5, 1, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.verticalSpacer = QSpacerItem(20, 76, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.speed_tab, "")

        self.verticalLayout_3.addWidget(self.tabWidget)


        self.retranslateUi(context_panel)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(context_panel)
    # setupUi

    def retranslateUi(self, context_panel):
        context_panel.setWindowTitle(QCoreApplication.translate("context_panel", u"Form", None))
        self.lbl_header.setText("")
        self.lbl_cam_x_offset.setText(QCoreApplication.translate("context_panel", u"Text X Offset", None))
        self.lbl_cam_y_offset.setText(QCoreApplication.translate("context_panel", u"Text Y Offset", None))
        self.lbl_cam_font_type.setText(QCoreApplication.translate("context_panel", u"Font Type", None))
        self.lbl_cam_text_scale.setText(QCoreApplication.translate("context_panel", u"Text Scale", None))
        self.lbl_cam_text_colour.setText(QCoreApplication.translate("context_panel", u"Text Colour", None))
        self.lbl_cam_font_weight.setText(QCoreApplication.translate("context_panel", u"Font Weight", None))
        self.btn_cam_text_colour.setText("")
        self.lbl_cam_text_alpha.setText(QCoreApplication.translate("context_panel", u"Text Alpha", None))
        self.lbl_cam_x_offset_4.setText(QCoreApplication.translate("context_panel", u"Position", None))
        self.lbl_cam_x_offset_5.setText(QCoreApplication.translate("context_panel", u"Position", None))
        self.chk_focal_length.setText(QCoreApplication.translate("context_panel", u"Focal Length", None))
        self.chk_object_distance.setText(QCoreApplication.translate("context_panel", u"Object Distance", None))
        self.chk_speed.setText(QCoreApplication.translate("context_panel", u"Speed", None))
        self.lbl_cam_x_offset_2.setText(QCoreApplication.translate("context_panel", u"Position", None))
        self.chk_rotations.setText(QCoreApplication.translate("context_panel", u"Rotations", None))
        self.chk_frame_number.setText(QCoreApplication.translate("context_panel", u"Frame Number", None))
        self.lbl_cam_x_offset_7.setText(QCoreApplication.translate("context_panel", u"Position", None))
        self.chk_height.setText(QCoreApplication.translate("context_panel", u"Height", None))
        self.lbl_cam_x_offset_3.setText(QCoreApplication.translate("context_panel", u"Position", None))
        self.lbl_cam_x_offset_6.setText(QCoreApplication.translate("context_panel", u"Position", None))
        self.lbl_camera_height_units.setText(QCoreApplication.translate("context_panel", u"Camera Height Unit ", None))
        self.btn_add_ground_geo.setText(QCoreApplication.translate("context_panel", u"Add Selected Ground Geo", None))
        self.btn_distance_object.setText(QCoreApplication.translate("context_panel", u"Distance To Selected Object", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.camera_tab), QCoreApplication.translate("context_panel", u"Camera", None))
        self.groupBox.setTitle(QCoreApplication.translate("context_panel", u"Font Settings", None))
        self.label_2.setText(QCoreApplication.translate("context_panel", u"Font Weight", None))
        self.label_4.setText(QCoreApplication.translate("context_panel", u"Font Size", None))
        self.label.setText(QCoreApplication.translate("context_panel", u"Font Type", None))
        self.btn_add_selected.setText(QCoreApplication.translate("context_panel", u"Add Selected", None))
        self.lbl_speed_unit.setText(QCoreApplication.translate("context_panel", u"Unit", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("context_panel", u"Text Controls", None))
        self.chk_visible.setText(QCoreApplication.translate("context_panel", u"Visible", None))
        self.lbl_text_colour.setText(QCoreApplication.translate("context_panel", u"Text Color", None))
        self.btn_text_colour.setText("")
        self.lbl_y_offset.setText(QCoreApplication.translate("context_panel", u"X Offset", None))
        self.lbl_x_offset.setText(QCoreApplication.translate("context_panel", u"X Offset", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.speed_tab), QCoreApplication.translate("context_panel", u"Speed", None))
    # retranslateUi

