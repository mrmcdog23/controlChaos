""" Drag and drop cameras to publish in the scene """
import hou
from ccgeneral.wizard.pages.scene_assets_page import SceneAssetsPage
from CCPySide import QtWidgets


class HoudiniCameraAssetsPage(SceneAssetsPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lb_scene_assets.setText("Camera Nodes")
        self.lb_publish_assets.setText("Publish Camera Nodes")
        self.chk_playblast_scene.setHidden(True)

    def load_scene_assets(self):
        """
        List all cameras in the scene
        """
        for node in hou.node("/obj/").allSubChildren():
            if node.type().name() != "cam":
                continue
            item = QtWidgets.QListWidgetItem(node.name())
            self.lw_scene_assets.addItem(item)
