""" Material creator interface """
import hou
import cccore.base_ui as base_ui
from CCPySide import QtWidgets, QtCore
from cchoudini.texture.materials_tree import MaterialsTreeWidget
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.texture.create_material as create_material


class MaterialCreator(base_ui.WidgetBase):
    title = "Material Creator"
    window_icon = "material_network"
    SUPPORTED_EXT = ["cpio", "abc", "exr", "fbx"]

    def __init__(self, parent=None):
        """
        Set the scene range or set it on ftrack
        """
        super().__init__(parent)
        self.main_layout = None
        self.tw_materials = None
        self.txt_material_name = None
        self.btn_create_material = None

        self.stay_on_top()
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        """
        Create the layout of the ui
        """
        # create the materials tree
        self.tw_materials = MaterialsTreeWidget(["Select Material Path"])
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.tw_materials)

        # create material name input
        lbl_material_name = QtWidgets.QLabel("Material Name")
        self.txt_material_name = QtWidgets.QLineEdit()
        lyt_material_name = QtWidgets.QHBoxLayout()
        lyt_material_name.addWidget(lbl_material_name)
        lyt_material_name.addWidget(self.txt_material_name)
        self.main_layout.addLayout(lyt_material_name)

        # create material button
        self.btn_create_material = QtWidgets.QPushButton("Create Material")
        self.main_layout.addWidget(self.btn_create_material)

        # set the layout
        self.setLayout(self.main_layout)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.btn_create_material.clicked.connect(self.create_material)

    def create_material(self):
        """
        Create the material
        """
        # check there is a name entered and error if there isn't one
        material_name_txt = self.txt_material_name.text()
        if not material_name_txt:
            hou_utils.hou_messagebox(
                "No Material Name", "No material name entered", "critical")
            return

        # create the material name
        material_name = f"SHD_{material_name_txt}"

        # get the selected network node and
        # error if there isn't one selected
        items = self.tw_materials.selectedItems()
        if not items:
            hou_utils.hou_messagebox(
                "No Material Network", "No material network selected", "critical")
            return

        material_path = items[0].data(0, QtCore.Qt.UserRole)
        material_network = hou.node(material_path)
        create_material.CreateArnoldShader(material_network, material_name)


def launch():
    """
    Launch the material creator ui
    """
    hou_utils.launch_hou_win(MaterialCreator)
