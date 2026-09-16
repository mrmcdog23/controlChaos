""" The materials tree for houdini material networks """
import os
import hou
from ccgeneral.widgets.tree_widget import No8TreeWidget
from CCPySide import QtWidgets, QtCore, QtGui
import cchoudini.utils.hou_utils as hou_utils


MATERIAL_BUILDER = "arnold_materialbuilder"
MATERIAL_NET = "matnet"


class MaterialsTreeWidget(No8TreeWidget):
    """
    Materials tree to show path of materials networks
    """
    def __init__(self, labels):
        # type: (list[str]) -> None
        """
        Args:
            labels: List of header labels
        """
        super().__init__(labels=labels)
        self.setMinimumWidth(200)
        self.populate_materials_tree()

    @property
    def material_network_icon(self):
        # type: () -> str
        """
        Get material network icon path
        """
        material_network_icon = os.path.join(
            os.environ["PIPELINE_ROOT"], "core", "icons", "material_network")
        return material_network_icon

    @property
    def shader_icon(self):
        # type: () -> str
        """
        Get material network icon path
        """
        material_network_icon = os.path.join(
            os.environ["PIPELINE_ROOT"], "core", "icons", "shader_icon")
        return material_network_icon

    def populate_materials_tree(self):
        """
        Build the material tree from a list of material networks
        The tree must reflect the structure in houdini
        """
        # build a list of all material networks
        root = hou.node("/")
        material_nodes = hou_utils.find_all_subnodes_of_types(root, ["matnet", MATERIAL_BUILDER])
        material_nodes.append(hou.node("/mat/"))  # add the default network

        # initialize a dictionary of a material path to its item
        path_to_item = dict()
        for material_node in material_nodes:

            # convert paths to values to make the item names
            path = material_node.path()
            path_values = path.split("/")
            path_values.remove("")

            # loop through the path values and create an item
            item_path = str()
            current_path_list = list()  # create list to build the path
            for index, value in enumerate(path_values):
                current = item_path[:]

                # add the current path to the list
                current_path_list.append(value)

                item_path += f"_{value}"
                if item_path in path_to_item:
                    continue

                # if the item has not been created then make and if it
                # is the last value in the path set the material icon
                new_item = QtWidgets.QTreeWidgetItem([value])
                current_path = "/" + "/".join(current_path_list)  # the full node path
                new_item.setData(0, QtCore.Qt.UserRole, current_path)

                current_node = hou.node(current_path)
                node_type = current_node.type().name()
                if node_type == MATERIAL_BUILDER:
                    new_item.setIcon(0, QtGui.QIcon(self.shader_icon))
                elif node_type == MATERIAL_NET:
                    new_item.setIcon(0, QtGui.QIcon(self.material_network_icon))

                # add the new item to the dictionary with its path as the key
                path_to_item[item_path] = new_item

                # if it is the first item add it as the top level item
                if index == 0:
                    self.addTopLevelItem(new_item)
                else:
                    # if not the root then find the parent item and add
                    # it to that. set as expanded also so its easy to view
                    parent_item = path_to_item[current]
                    parent_item.addChild(new_item)
                    parent_item.setExpanded(True)
