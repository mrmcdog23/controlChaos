""" Create a houdini material network """
import hou
import cccore.utils.cc_logging as cc_logging


class CreateArnoldShader(object):
    """
    Create an arnold shading network
    """
    def __init__(self, material_network, material_name):
        # type: (hou.Node, str) -> None
        """
        Args:
            material_network: Network to create material under
            material_name: Name of the material
        """
        self.material_network = material_network
        self.material_name = material_name
        self.material_arnold = None
        self.image_node_prefix = dict()
        self.logger = cc_logging.cc_logger()
        self.create_arnold_material()

    def create_image_node(self, prefix):
        # type: (str) -> hou.Node
        """
        Create an arnold image node and with a prefix in its name

        Args:
            prefix: Node name at the start of the node

        Returns:
            image_node: Create image node
        """
        self.logger.info(f"Creating image node: {prefix}")

        # create the image node
        image_node = self.material_arnold.createNode("arnold::image")
        image_node.setName(f"{prefix}_image", unique_name=True)
        image_node.parm("ignore_missing_textures").set(True)
        image_node.parm("autotx").set(0)
        self.image_node_prefix[prefix] = image_node
        return image_node
    
    def create_inbetween_node(self, input_node, node_type):
        # type: (hou.Node, str) -> hou.Node
        """
        Create a node that connects to the source image node

        Args:
            input_node: Source node to connect to
            node_type: The type of houdini node to create

        Returns:
            inbetween_node: Create node
        """
        inbetween_node = self.material_arnold.createNode(node_type)
        inbetween_node.setInput(0, input_node, 0)
        return inbetween_node
    
    def create_arnold_material(self):
        """
        Create the arnold material under
        the given material network
        """
        # Create the Material Builder
        self.material_arnold = self.material_network.createNode("arnold_materialbuilder")
        self.material_arnold.setName(self.material_name, unique_name=True)
    
        # Create Standard Surface
        standard_surface = self.material_arnold.createNode("arnold::standard_surface")
    
        # Get OUT
        node_out = hou.node(f"{self.material_arnold.path()}/OUT_material")
    
        # Create textures
        image_beauty = self.create_image_node("DIF")
        color_correct_beauty = self.create_inbetween_node(image_beauty, "arnold::color_correct")
    
        image_metalness = self.create_image_node("MTL")
        range_metalness = self.create_inbetween_node(image_metalness, "arnold::range")
    
        image_roughness = self.create_image_node("RGH")
        range_roughness = self.create_inbetween_node(image_roughness, "arnold::range")
    
        image_normal = self.create_image_node("NRM")
        normal_map = self.create_inbetween_node(image_normal, "arnold::normal_map")
    
        image_displacement = self.create_image_node("DSP")
        range_displacement = self.create_inbetween_node(image_displacement, "arnold::range")
    
        # AOVs
        aov_write = self.material_arnold.createNode("arnold::aov_write_rgba")
        aov_write.parm("aov_name").set("debug")
        aov_write.setInput(0, standard_surface, 0)
    
        # Connect
        standard_surface.setInput(1, color_correct_beauty, 0)
        standard_surface.setInput(3, range_metalness, 1)
        standard_surface.setInput(6, range_roughness, 1)
        standard_surface.setInput(39, normal_map, 0)
        node_out.setInput(1, range_displacement, 0)
        node_out.setInput(0, aov_write, 0)
    
        # Layout nicely
        self.material_arnold.layoutChildren()
        self.material_arnold.moveToGoodPosition()
    
        # switch to the tab in the panel
        panel = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        panel.setCurrentNode(range_roughness)

    def prioritize_tx_dict(self, sequence_path_dict):
        # type: (dict) -> dict
        """
        Create a dictionary that prioritizes tx files over
        other components of the same name

        Args:
            sequence_path_dict: Dictionary wit all texture components

        Returns:
            prioritize_tx_dict: The dictionary to load
        """
        # priorities the tx files over other formats
        prioritize_tx_dict = dict()
        for prefix, image_path in sequence_path_dict.items():
            prefix_stripped = prefix.split("_")[0]
            if prefix.endswith("tx"):
                self.logger.info(f"TX component found: {prefix_stripped}")
                prioritize_tx_dict[prefix_stripped] = image_path
            else:
                tx_prefix = f"{prefix_stripped}_tx"
                if tx_prefix not in sequence_path_dict:
                    self.logger.info(f"{prefix} has no tx component")
                    prioritize_tx_dict[prefix_stripped] = image_path
        return prioritize_tx_dict

    def link_textures(self, sequence_path_dict):
        # type: (dict) -> dict
        """
        Relink the textures to the material by using the prefix
        to see if one existed. If one doesn't create it.

        Args:
            sequence_path_dict: Component name to the sequence path

        Returns:
            prioritize_tx_dict: The dictionary to load
        """
        prioritize_tx_dict = self.prioritize_tx_dict(sequence_path_dict)
        for prefix, image_path in prioritize_tx_dict.items():
            image_node = self.image_node_prefix.get(prefix)
            self.logger.info(f"Found: {image_node}")
            if not image_node:
                image_node = self.create_image_node(prefix)
                self.logger.info(f"Created: {image_node}")
            image_node.parm("filename").set(image_path)
        self.material_arnold.layoutChildren()
        return prioritize_tx_dict
