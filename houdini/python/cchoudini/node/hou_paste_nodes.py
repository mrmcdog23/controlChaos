""" Paste node in houdini from another user """
import hou
from typing import Any
import cchoudini.utils.hou_utils as hou_utils
from ccgeneral.shot.copy_paste_nodes.paste_nodes import PasteNodes


class HouPasteNodes(PasteNodes):
    MSG_FUNCTION = hou_utils.hou_messagebox

    def __init__(self, parent=None):
        """
        Set the scene range or set it on ftrack
        """
        super(HouPasteNodes, self).__init__(parent)

    @property
    def selected_nodes(self):
        """
        The current selected nodes

        Returns:
            list[hou.Node]: Selected Houdini nodes
        """
        return hou.selectedItems()

    @property
    def msg_function(self):
        # type: () -> Any
        """ The message box display function """
        return hou_utils.hou_messagebox

    @staticmethod
    def paste_nodes_from_file(file_path):
        """
        Paste nodes from file
        """
        tab = hou_utils.get_current_tab()
        parent = tab.pwd()
        parent.loadItemsFromFile(file_path)


def main():
    """
    Launch the houdini window
    """
    hou_utils.launch_hou_win(HouPasteNodes)

