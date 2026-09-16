""" Ui to load textures into houdini """
import hou
from CCPySide import QtWidgets, QtCore
import cchoudini.utils.hou_utils as hou_utils
import ccgeneral.asset.asset_loader as asset_loader
import cchoudini.texture.create_material as create_material
from cchoudini.texture.materials_tree import MaterialsTreeWidget


class HouTextureLoader(asset_loader.AssetLoaderBase):
    """
    Texture loader for houdini
    """
    title = "Load Texture Asset Version"
    window_icon = "texture"
    icon_to_widget = {"cc_logo_text": "lbl_cc_icon",
                      "texture": "lbl_load_icon"
                      }

    def __init__(self, parent=None):
        self.tw_materials = None
        self.le_name_input = None
        super().__init__(parent=parent)
        self.stay_on_top()

    def set_label_text_and_size(self):
        """
        Set the loader labels and text size to match the texture loading
        """
        self.set_widget_font_size(self.title_asset, 25)
        self.set_widget_font_size(self.title_loader, 25)
        self.title_asset.setText("TEXTURE")
        self.btn_load_asset.setText("LOAD TEXTURES")

    def add_load_options(self):
        """
        Build the load tree and create the input material line edit
        """
        self.create_materials_tree()
        self.create_name_input_line()
        self.set_label_text_and_size()

    def create_name_input_line(self):
        """
        Create a line edit widget for the shader name
        """
        lbl_name_input = QtWidgets.QLabel("Shader Name:")
        self.le_name_input = QtWidgets.QLineEdit()
        self.lyt_options.addItem(self.create_spacer())
        self.lyt_options.addWidget(lbl_name_input)
        self.lyt_options.addWidget(self.le_name_input)
        self.lyt_options.addItem(self.create_spacer())

    def create_materials_tree(self):
        """
        Create the material tree widget to select where the material will go
        """
        self.tw_materials = MaterialsTreeWidget(["Select Material Path"])
        self.tw_materials.itemSelectionChanged.connect(self.update_selected_version)
        self.lyt_additional.addWidget(self.tw_materials)

    def update_selected_version(self):
        """
        Only enable the button when a material path is selected
        """
        super().update_selected_version()
        selected_items = self.tw_materials.selectedItems()
        self.btn_load_asset.setEnabled(bool(selected_items))

    def load_selected_version(self):
        """
        Load the alembic asset
        """
        material_name_txt = self.le_name_input.text()
        if not material_name_txt:
            hou_utils.hou_messagebox(
                "No Texture Name", "No texture name entered", "critical")
            return

        # create the material name
        material_name = f"SHD_{material_name_txt}"

        # create the material network node
        item = self.tw_materials.selectedItems()[0]
        material_path = item.data(0, QtCore.Qt.UserRole)
        material_network = hou.node(material_path)

        if material_network.type().name() != "matnet":
            hou_utils.hou_messagebox(
                "Not a material network", "Not a material network selected", "critical")
            return

        mat_inst = create_material.CreateArnoldShader(material_network, material_name)

        # link the textures to the material
        asset_version = self.selected_version()
        self.ftver.asset_version_id = asset_version['id']
        sequence_path_dict = self.ftver.get_sequence_path_dict()
        prioritize_tx_dict = mat_inst.link_textures(sequence_path_dict)

        # show created message box
        created_textures = list(prioritize_tx_dict.keys())
        created_textures_str = "\n".join(created_textures)
        hou_utils.hou_messagebox(
            "Created Textures",
            f"Created the following textures:\n{created_textures_str}",
            "info"
        )


def main():
    """
    Launch the loader
    """
    hou_utils.launch_hou_win(HouTextureLoader)
