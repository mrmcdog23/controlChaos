""" Share houdini nodes with another artist """
import hou
import cchoudini.utils.hou_utils as hou_utils
from ccgeneral.shot.copy_paste_nodes.share_nodes import ShareNodes


class HouShareNodes(ShareNodes):
    EXTENSION = "cpio"  # File extension to save

    def __init__(self, parent=None):
        """
        Set the scene range or set it on ftrack
        """
        super(HouShareNodes, self).__init__(parent)

    @property
    def msg_function(self):
        """
        Message function to show

        Returns:
            hou_messagebox: The message box display function
        """
        return hou_utils.hou_messagebox

    @property
    def selected_nodes(self):
        # type: () -> list[hou.Node]
        """
        The current selected nodes

        Returns:
            Selected Houdini nodes
        """
        return hou.selectedItems()

    def save_to_file(self, save_path):
        # type: (str) -> None
        """
        Export selected nodes to a file

        Args:
            save_path: Path to save to
        """
        self.logger.info(f"Saving file: {save_path}")
        context_node = self.selected_nodes[0].parent()
        context_node.saveChildrenToFile(self.selected_nodes, [], save_path)


def main():
    """
    Launch the houdini window
    """
    hou_utils.launch_hou_win(HouShareNodes)

