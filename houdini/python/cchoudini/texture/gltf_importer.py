""" GLTF material importer """
import os
import hou
import cccore.utils.file_utils as file_utils
import cchoudini.utils.node_utils as node_utils
import cccore.base_ui as base_ui
import cchoudini.utils.hou_utils as hou_utils
from CCPySide import QtWidgets
from ccgeneral.widgets.tree_widget import No8TreeWidget
from ccgeneral.widgets.line_browser import LineBrowser


start_dir = "/mnt/jobs/013961_BadWolf_RedEye/vfx/RE_0201/026/0045/unreal/cache/Models/Grass/Foliage_Exports"
COLOUR_TO_PARM = {
    "basecolor": "base_color",
    "rough": "coat_roughness",
    "metallic": "specular_roughness",
    "baseNormal": "normal"
}


class GLTFImporter(base_ui.WidgetBase):
    title = "GLTF Creator"
    window_icon = "material_network"

    def __init__(self, parent=None):
        """
        Set the scene range or set it on ftrack
        """
        super().__init__(parent)
        self.main_layout = None
        self.tw_gltf_files = None
        self.txt_material_name = None
        self.btn_create_material = None
        self.gltf_node_list = list()

        self.stay_on_top()
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        """
        Create the layout of the ui
        """
        # create the materials tree
        self.tw_gltf_files = No8TreeWidget(["GLTF File Names"])
        self.gltf_path_wdg = LineBrowser(
            self, "path_dir", "Find images path", start_dir, "Selected Folder"
        )
        self.btn_create_material = QtWidgets.QPushButton("Import GLTF Materials")

        # build the layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.gltf_path_wdg)
        self.main_layout.addWidget(self.tw_gltf_files)
        self.main_layout.addWidget(self.btn_create_material)

        # set the layout
        self.setLayout(self.main_layout)

    def connect_signals(self):
        """
        Connect the widget to a signal
        """
        self.gltf_path_wdg.line_edit.textChanged.connect(self.populate_files)
        self.btn_create_material.clicked.connect(self.import_gltf_files)

    def populate_files(self):
        """
        Populate all gltf files in the tree widget
        found under the selected directory
        """
        gltf_directory = self.gltf_path_wdg.text
        gltf_file_list = list()
        for gltf_file in os.listdir(gltf_directory):
            if gltf_file.endswith(".gltf"):
                gltf_file_list.append(gltf_file)
        self.tw_gltf_files.populate_items(gltf_file_list, )

    def import_gltf_files(self):
        """
        Import all the check gltf file nodes
        """
        gltf_files = self.tw_gltf_files.items_text(checked_only=True)
        for gltf_file in gltf_files:
            self.create_gltf_node(gltf_file)
        node_utils.set_position_nodes(self.gltf_node_list)
        hou_utils.create_network_box(self.gltf_node_list, "GLTF Nodes")

    @staticmethod
    def create_arnold_network(gltf_node):
        # type: (hou.Node) -> None
        """
        Create an arnold next work from a gltf node

        Args:
            gltf_node: The main gltf node
        """
        material_node = hou_utils.find_subnode_of_type(gltf_node, "matnet")
        shader_node = hou_utils.find_subnode_of_type(material_node, "principledshader::2.0")

        # create shader and output
        arnold_shader_node = material_node.createNode("arnold::standard_surface")
        arnold_out_node = material_node.createNode("arnold_material")
        arnold_out_node.setInput(0, arnold_shader_node)

        texture_nodes = list()
        for parm in shader_node.allParms():

            # if the parameter name is use texture and its check then use the path
            parameter_name = parm.name()
            if not parameter_name.endswith("_useTexture"):
                continue
            if not parm.eval():
                continue

            parm_base_name = parameter_name.split("_useTexture")[0]
            texture_path = shader_node.parm(f"{parm_base_name}_texture").eval()
            texture_node = material_node.createNode("arnold::image", parm_base_name)

            input_name = COLOUR_TO_PARM.get(parm_base_name)
            if input_name:
                arnold_shader_node.setNamedInput(input_name, texture_node, 'rgba')

            # set the texture path
            texture_node.parm("filename").set(texture_path)
            texture_nodes.append(texture_node)

        # reposition the nodes to a column
        node_utils.set_position_nodes(texture_nodes, ygap=2)

        # create shader and output
        ypos = (3 * len(texture_nodes)) * -1
        arnold_shader_node.setPosition((3, ypos))
        arnold_out_node.setPosition((5, ypos))

    def create_gltf_node(self, gltf_file):
        # type: (str) -> hou.Node
        """
        Create the gltf node from the file path

        Args:
            gltf_file: Path of the gltf file

        Returns:
            gltf_node: The new gltf houdini node
        """
        gltf_path = os.path.join(self.gltf_path_wdg.text, gltf_file)
        gltf_name = file_utils.get_file_name(gltf_file)
        gltf_node = hou.node("/obj").createNode("gltf_hierarchy", gltf_name)
        gltf_node.parm("filename").set(gltf_path)
        gltf_node.parm("buildscene").pressButton()
        self.create_arnold_network(gltf_node)
        self.gltf_node_list.append(gltf_node)
        return gltf_node


def launch():
    """
    Launch the material creator ui
    """
    hou_utils.launch_hou_win(GLTFImporter)
