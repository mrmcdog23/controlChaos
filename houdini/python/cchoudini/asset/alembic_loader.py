""" Import the materialx file and rebuild the shader network """
import hou
import cccore.utils.cc_logging as cc_logging
from typing import Optional


class AlembicLoader(object):
    """ Import materials into houdini """
    def __init__(self, alembic_path, asset_name=None):
        # type: (str, Optional[str]) -> None
        """
        Args:
            alembic_path: The alembic file to import
            asset_name: Name of the build asset
        """
        self.abc_path = alembic_path
        self.asset_name = asset_name
        self.logger = cc_logging.cc_logger()
        self.abc_node = None
        self.geo_node = None
        self.import_alembic()

    def import_alembic(self):
        """
        Import the alembic node by creating it under a geo node
        """
        self.logger.info(f"Importing alembic file...")
        self.geo_node = hou.node("/obj").createNode("geo", self.asset_name)
        self.geo_node.moveToGoodPosition()

        self.abc_node = self.geo_node.createNode("alembic")
        self.abc_node.parm("fileName").set(self.abc_path)
