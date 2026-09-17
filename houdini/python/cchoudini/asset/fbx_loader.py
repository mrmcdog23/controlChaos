""" Import the fbx file and rebuild the shader network """
import hou
import cccore.utils.cc_logging as cc_logging
from typing import Optional


class FBXLoader(object):
    """ Import materials into houdini """
    def __init__(self, fbx_path, asset_name=None):
        # type: (str, Optional[str]) -> None
        """
        Args:
            fbx_path: The fbx file to import
            asset_name: Name of the build asset
        """
        self.fbx_path = fbx_path
        self.asset_name = asset_name
        self.logger = cc_logging.cc_logger()
        self.abc_node = None
        self.geo_node = None
        self.import_alembic()
        self.create_subnet()

    def import_alembic(self):
        """
        Import the fbx node by creating it under a geo node
        """
        node = hou.hipFile.importFBX(
            self.fbx_path,
            import_cameras=True,
            import_lights=True,
            import_geometry=True,
            import_materials=True,
            import_animation=True,
            import_joints_and_skin=True,
            resample_animation=False
        )

        self.logger.info(f"Importing fbx file...")
        self.geo_node = hou.node("/obj").createNode("geo", self.asset_name)
        self.geo_node.moveToGoodPosition()

        self.abc_node = self.geo_node.createNode("alembic")
        self.abc_node.parm("fileName").set(self.fbx_path)
