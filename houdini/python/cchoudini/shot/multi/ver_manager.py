""" Manage houdini versions of nodes """
import cchoudini.utils.hou_utils as hou_utils
from ccgeneral.shot.version_manager.ver_manager import BaseVersionManager


class HouVersionManager(BaseVersionManager):
    title = "Version Manager"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def populate_scene_assets(self):
        """
        Populate the published and unpublished assets
        """
        shot_assets_dict = hou_utils.get_shot_assets()
        for component_name, node_asset in shot_assets_dict.items():
            if "/" not in node_asset.current_path:
                continue
            self.create_shot_asset_item(node_asset)


def launch():
    """
    Launch the reference manager
    """
    hou_utils.launch_hou_win(HouVersionManager)
