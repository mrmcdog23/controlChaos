""" Ui to load sequences and files into houdini """
import hou
import ccgeneral.shot.browser.shot_browser as shot_browser
import cchoudini.utils.hou_utils as hou_utils
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
from CCPySide import QtCore


class ShotBrowser(shot_browser.BaseShotBrowser):

    @property
    def supported_ext(self):
        # type: () -> list[str]
        """ The file types that are supported """
        return [".vdb", ".abc", "bgeo.sc"]

    def import_files(self):
        """
        Import all the files in the list
        """
        nodes = list()
        ypos = xpos = 0
        for index in range(self.lw_load_paths.count()):
            node = None
            item = self.lw_load_paths.item(index)
            file_path = item.data(QtCore.Qt.UserRole)
            file_name = file_utils.get_file_name(file_path)
            if file_path.endswith(".abc"):
                node = hou.node("/obj").createNode("alembicarchive", f"{file_name}_abc")
                node.parm("fileName").set(file_path)

            elif file_path.endswith((".vdb", ".bgeo.sc")):
                seq_data = sequence_utils.get_sequence_data(file_path)
                node = hou.node("/obj").createNode("geo", f"{file_name}_geo")
                file_node = node.createNode("file", f"{file_name}_cache")
                file_node.parm("file").set(seq_data.houdini_path_unpadded)

            if node:
                node.setPosition((xpos, ypos))
                nodes.append(node)
                xpos += 2
        hou_utils.create_network_box(nodes, "Imported Shot")


def launch():
    """
    Launch the houdini window
    """
    hou_utils.launch_hou_win(ShotBrowser)
