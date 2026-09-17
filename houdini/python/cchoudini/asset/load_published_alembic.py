""" Import the materialx file and rebuild the shader network """
import hou
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
import cchoudini.utils.hou_utils as hou_utils
from typing import Optional


class LoadPublishedAlembic(object):
    """ Import materials into houdini """
    def __init__(self, alembic_path, materialx_path=None, metadata_path=None, asset_name=None):
        # type: (str, Optional[str], Optional[str], Optional[str]) -> None
        """
        Args:
            alembic_path: The alembic file to import
            materialx_path: The materialx file to import
            metadata_path: Asset version metadata file path
            asset_name: Name of the build asset
        """
        self.abc_path = alembic_path
        self.materialx_path = materialx_path
        self.metadata_path = metadata_path
        self.asset_name = asset_name
        self.logger = cc_logging.cc_logger()

        self.abc_node = None
        self.geo_node = None
        self.fetch_node = None
        self.material_node = None
        self.subnet_node = None

        self.import_alembic()
        self.load_materialx_file()
        self.create_subnet()
        self.load_assignments()
        self.set_material_parameter()

    def import_alembic(self):
        """
        Import the alembic node by creating it under a geo node
        """
        self.logger.info(f"Importing alembic file...")
        self.geo_node = hou.node("/obj").createNode("geo", self.asset_name)
        self.geo_node.moveToGoodPosition()

        self.abc_node = self.geo_node.createNode("alembic")
        self.abc_node.parm("fileName").set(self.abc_path)

    def load_materialx_file(self):
        """
        Load the materialx shaders into a materials network
        """
        if not self.materialx_path:
            return
        self.material_node = hou.node("/out").createNode("matnet", f"{self.asset_name}_mat")
        self.material_node.moveToGoodPosition()

        # get the subnet node
        self.logger.info(f"Node: {self.material_node.path()}")
        self.logger.info(f"Path: {self.materialx_path}")
        material.materialImport(self.material_node, self.materialx_path)

    def set_material_parameter(self):
        """
        Set the material parameters by creation expression nodes
        """
        parm_nodes = hou_utils.find_all_subnodes_of_types(self.subnet_node, ["arnold::set_parameter"])
        prev_collection_node = None

        for parm_node in parm_nodes:
            collection_node = self.create_collection_node(parm_node, prev_collection_node)
            prev_collection_node = collection_node

        self.create_merge_and_null_node()

    def find_last_node(self, node_type):
        # type: (str) -> Optional[hou.Node]
        """
        In the subnode find the node with no outputs

        Args:
            node_type: The node type to find

        Returns:
            node: Node with no outputs
        """
        nodes = hou_utils.find_all_subnodes_of_types(self.subnet_node, [node_type])
        for node in nodes:
            if not node.outputConnections():
                return node

    def create_merge_and_null_node(self):
        """
        Finish the collection creation with a merge and null node
        """
        # create merge node
        last_parameter_node = self.find_last_node("arnold::set_parameter")
        last_collection_node = self.find_last_node("arnold::collection")
        merge_node = self.subnet_node.createNode("merge")

        # find the connection node with no outputs
        # and set the merge node and the output
        merge_node.setInput(0, last_collection_node)
        merge_node.setInput(1, last_parameter_node)

        # set the position and connect
        if not last_parameter_node:
            return
        xpos, ypos = last_parameter_node.position()
        merge_node.setPosition((xpos - 5, ypos - 3))

        # create a null node
        null_node = self.subnet_node.createNode("null", "OUT_LDEV")
        null_node.setInput(0, merge_node)
        null_node.setPosition((xpos - 5, ypos - 6))

        self.fetch_node.parm("source").set(null_node.path())

    def create_collection_node(self, parm_node, prev_collection_node):
        # type: (hou.Node, hou.Node) -> hou.Node
        """
        Create collection node and keep in line with the parameter node.
        Connect to eh previous collection node if there is one

        Args:
            parm_node: The original parameter node
            prev_collection_node: The previous collection if there is one

        Returns:
            collection_node: New collection node
        """
        parm_name = parm_node.name()
        collection_name = f"cc_{parm_name}"
        collection_node = self.subnet_node.createNode("arnold::collection", collection_name)
        xpos, ypos = parm_node.position()
        collection_node.setPosition((xpos - 10, ypos))
        collection_node.parm("collection").set("$OS")

        # connect to the previous collection node
        if prev_collection_node:
            prev_collection_node.setInput(0, collection_node)

        # set the new expression on the node
        collection_exp = self.get_collection_expression(parm_node)
        collection_node.parm("selection").set(collection_exp)
        parm_node.parm("selection").set("#cc_$OS")
        return collection_node

    @staticmethod
    def get_collection_expression(parm_node):
        # type: (hou.Node) -> str
        """
        Get the expression from the parameter node
        and work out the new expression to set

        Args:
            parm_node: The original parameter node

        Returns:
            collection_exp: New expression to set on the node
        """
        selection = parm_node.parm("selection").eval()
        remove_stars = selection.replace("*", "")
        object_list = remove_stars.split(" ")

        new_name_list = list()
        for expression in object_list:
            basename = expression.split("|")[-1]
            new_name = f"*.*{basename}*"
            new_name_list.append(new_name)
        collection_exp = " or ".join(new_name_list)
        return collection_exp

    def create_subnet(self):
        """
        Create the material overrides with the subnet
        """
        if not self.material_node:
            return
        subnet_name = f"{self.asset_name}_ldev"
        self.subnet_node = hou.node("/out").createNode("subnet", subnet_name)
        self.subnet_node.moveToGoodPosition()

        fetch_name = f"{subnet_name}_OUT_LDEV"
        self.fetch_node = hou.node("/out").createNode("fetch", fetch_name)
        self.fetch_node.setInput(0, self.subnet_node)

        # set the position and connect
        xpos, ypos = self.subnet_node.position()
        self.fetch_node.setPosition((xpos, ypos - 1))

        arnold_material_nodes = hou_utils.find_all_subnodes_of_types(
            self.material_node, ["arnold_materialbuilder"]
        )

        previous_parameter_node = None
        for index, arnold_material in enumerate(arnold_material_nodes):

            # create and set the parameter node to the correct position
            set_parameter_node = self.subnet_node.createNode(
                "arnold::set_parameter", arnold_material.name()
            )
            set_parameter_node.setPosition((0, index))
            set_parameter_node.parm("assignment").set(1)

            # set the expression to the material shader path
            arnold_material_path = arnold_material.path()
            expression = f"shader = '`opfullpath(\"{arnold_material_path}\")`'"
            set_parameter_node.parm("assignment_1").set(expression)

#           # set the input of the set parameter node
            if previous_parameter_node:
                previous_parameter_node.setInput(0, set_parameter_node)
            previous_parameter_node = set_parameter_node

    def load_assignments(self):
        """
        Load the material assignments
        """
        asset_metadata = file_utils.read_json(self.metadata_path)
        mesh_to_materials = asset_metadata["mesh_to_materials"]
        subnet_path = self.subnet_node.path()

        # build the meshes to materials list
        material_to_geo_path = dict()
        for mesh, material in mesh_to_materials.items():
            set_parameter_path = f"{subnet_path}/{self.asset_name}_{material}_material_shader"

            # add the mesh to the material geo list
            geo_list = material_to_geo_path.get(set_parameter_path, list())
            geo_list.append(mesh)
            material_to_geo_path[set_parameter_path] = geo_list

        # find the parameter path and the geo list and
        # create the expression to assign the geometry
        for set_parameter_path, geo_list in material_to_geo_path.items():
            geo_list_expression = "* *".join(geo_list)
            parameter_node = hou.node(set_parameter_path)
            if parameter_node:
                parameter_node.parm("selection").set(geo_list_expression)

