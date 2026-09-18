""" Get the shot asset from a node """
import os
import hou
from typing import Optional
import ccgeneral.asset.shot_asset as shot_asset
import cchoudini.node.ftrack_hou_node as ftrack_hou_node
import cchoudini.utils.hou_utils as hou_utils


class ShotAsset(shot_asset.BaseShotAsset):
    """
    From a namespace of ftrack attribute get
    all the data related to the asset
    """
    def __init__(self, node, session=None):
        super().__init__(node, session=session)

    @property
    def node_type(self):
        # type: () -> str
        """ Node type name """
        return self.node.type().name()

    @property
    def node_path(self):
        # type: () -> str
        """ Path of the node """
        return self.node.path()

    @property
    def is_visible(self):
        # type: () -> bool
        """ Is the node visible """
        return self.node.isDisplayFlagSet()

    @property
    def is_non_deletable(self):
        # type: () -> bool
        """ Is the node deletable """
        parm = self.node.parm("non_deletable")
        if not parm:
            return False
        return parm.eval()

    @property
    def current_path(self):
        # type: () -> Optional[str]
        """ Path of the current file """
        if not self._current_path:
            potential_parm_name = ["source_path", "fileName", "shot_cache_path", "asset_cache_path"]
            for parm_name in potential_parm_name:
                parm = self.node.parm(parm_name)
                if parm:
                    self._current_path = parm.evalAsString()
                    break
        return self._current_path

    @property
    def current_name(self):
        # type: () -> str
        """ Current path base name """
        return os.path.basename(self._current_path)

    @property
    def component_name(self):
        # type: () -> str
        """ Name of the component of the node """
        if self.node.parm("component_name"):
            return self.node.parm("component_name").evalAsString()
        return super().component_name

    def toggle(self):
        """ Toggle the node visibility """
        set_visible = not self.node.isDisplayFlagSet()
        self.node.setDisplayFlag(set_visible)

    def set_visible(self):
        """ Set the houdini node visible """
        self.node.setDisplayFlag(True)

    def set_invisible(self):
        """ Set the houdini node invisible """
        self.node.setDisplayFlag(False)

    def select(self):
        """ Select the node """
        self.node.setSelected(True, clear_all_selected=True)

    def update_to_version(self, current_version):
        # type: (int) -> None
        """
        Update the asset version to the new version

        Args:
            current_version: New version to set to
        """
        version_padded = str(current_version).zfill(3)
        node_path = self.node.path()
        ftrack_node_name = node_path.split("/")[2]
        ftrack_node = hou.node(f"/obj/{ftrack_node_name}")
        ftnode = ftrack_hou_node.FTrackHouNode(ftrack_node)
        ftnode.set_padded_version_number(version_padded)

    def switch_version(self, task_id, shot_asset_version_id, shot_alembic_path, version_padded):
        # type: (str, str, str, str) -> None
        """
        Switch the ftrack node to a new shot

        Args:
            task_id: The task id
            shot_asset_version_id: The shot asset version id
            shot_alembic_path: Path of the shot alembic
            version_padded: The version in padded form
        """
        ftnode = ftrack_hou_node.FTrackHouNode(self.node)

        # build shot data dictionary
        shot_data = {
            "shot_task_ftrack_id": task_id,
            "shot_version_ftrack_id": shot_asset_version_id,
            "shot_cache_path": shot_alembic_path,
            "shot_cache_name": os.path.basename(shot_alembic_path),
            "shot_version": version_padded
        }
        ftnode.set_shot_data(shot_data)
        self.set_visible()
        self.reload()

    def reload(self):
        """
        Reload the houdini node from its path
        """
        reload_parm = None
        if self.node_type == "geo":
            loading_node = hou_utils.find_all_subnodes_of_types(self.node, ["alembic"])[0]
            reload_parm = loading_node.parm("reload")

        elif self.node_type == "alembicarchive":
            reload_parm = self.node.parm("buildHierarchy")

        if reload_parm:
            reload_parm.pressButton()
