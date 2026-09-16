""" Set the absolute path on the nodes """
import hou


class AbsolutePath(object):
    """ Set the absolute path on nodes """
    COLOUR_TO_SET = (0.8, 0.3, 1.1)  # pink

    def __init__(self):
        # Get the selected nodes
        selected_nodes = hou.selectedNodes()
        
        for parent_node in selected_nodes:
            if parent_node.type().category() == hou.objNodeTypeCategory():
                self.make_paths_absolute_in_geo(parent_node)
        
        for node in selected_nodes:
            self.make_paths_absolute_for_node(node)

        for node in selected_nodes:
            node.setColor(hou.Color(self.COLOUR_TO_SET))
    
        hou.ui.displayMessage("Selected nodes changed their"
                              " relative paths to absolute paths.")

    @staticmethod
    def make_paths_absolute_for_node(node):
        # type: (hou.Node) -> None
        """
        Make the paths absolute for the node

        Args:
            node: The houdini node to set to absolute
       """
        for parm in node.parms():
            if parm.parmTemplate().type() != hou.parmTemplateType.String:
                continue
            value = parm.eval()
            if value:
                expanded_path = hou.expandString(value)
                parm.set(expanded_path)
    
    def make_paths_absolute_in_geo(self, parent_node):
        # type: (hou.Node) -> None
        """
        Make the paths absolute for the geometry

        Args:
            parent_node: The houdini geo to set to absolute
       """
        for child_node in parent_node.allSubChildren():
            self.make_paths_absolute_for_node(child_node)

