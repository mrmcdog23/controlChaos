"""Get material node network """
import hou


class MaterialNetwork(object):
    """
    From one material node get every node in the network
    """
    def __init__(self, material_node):
        self.material_node = material_node
        self.all_node_list = list()

    @staticmethod
    def get_output_nodes(node):
        # type: (hou.Node) -> list[hou.Node]
        """
        Get all output nodes of the network

        Args:
            node: The material node

        Returns:
            output_nodes: List of output nodes
        """
        output_nodes = list()
        for connection in node.outputConnectors():
            for conn in connection:
                output_nodes.append(conn.outputNode())
        return output_nodes

    @staticmethod
    def get_input_nodes(node):
        # type: (hou.Node) -> list[hou.Node]
        """
        Get all input nodes of the network

        Args:
            node: The material node

        Returns:
            input_nodes: List of input nodes
        """
        input_nodes = list()
        for connection in node.inputConnectors():
            for conn in connection:
                input_nodes.append(conn.inputNode())
        return input_nodes

    def get_all_nodes(self):
        # type: () -> list[hou.Node]
        """
        Get all nodes in the material network

        Returns:
            all_nodes: List of every node in the network
        """
        input_nodes = [self.material_node]
        for index in range(5):
            for input_node in input_nodes:
                input_nodes = self.get_input_nodes(input_node)
                self.all_node_list.extend(input_nodes)

        output_nodes = [self.material_node]
        for index in range(5):
            for output_node in output_nodes:
                output_nodes = self.get_output_nodes(output_node)
                self.all_node_list.extend(output_nodes)

        for index in range(3):
            for input_node in self.all_node_list:
                input_nodes = self.get_input_nodes(input_node)
                self.all_node_list.extend(input_nodes)

        for index in range(3):
            for output_node in self.all_node_list:
                output_nodes = self.get_output_nodes(output_node)
                self.all_node_list.extend(output_nodes)

        nodes_set = set(self.all_node_list)
        all_nodes = list(nodes_set)
        if self.material_node in all_nodes:
            all_nodes.remove(self.material_node)
        return all_nodes


def get_material_network(shader_node):
    # type: (hou.Node) -> list[hou.Node]
    """
    Get the entire material network

    Args:
        shader_node: Main shader node

    Returns:
        all_nodes: List of every node in the network
    """
    material_network_inst = MaterialNetwork(shader_node)
    all_nodes = material_network_inst.get_all_nodes()
    return all_nodes

