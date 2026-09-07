""" Exporter for an asset from Maya in fbx format """
import os
import pymel.core as pm
import maya.cmds as cmds
import ccmaya.utils.maya_utils as maya_utils
import cccore.utils.cc_logging as cc_logging
import cccore.utils.file_utils as file_utils
import ccmaya.maya_constants as maya_constants


class FbxAssetExport(object):
    """
    Export fbx asset to the given path
    """
    def __init__(self, fbx_asset_path):
        # type: (str) -> None
        """
        Args:
            fbx_asset_path: Path to save asset to
        """
        self.fbx_asset_path = fbx_asset_path
        self.logger = cc_logging.cc_logger()
        self.export_asset()

    def export_asset(self):
        """
        Set the fbx properties and export
        """
        select_objects = [maya_constants.GEO_GRP]

        root_joint = maya_utils.get_root_joint()
        if root_joint:
            select_objects.append(root_joint)
        cmds.select(select_objects)
        self.logger.info(f"Selected: {select_objects}")
        cmds.select(hierarchy=True)

        # run the fbx export commands
        pm.mel.FBXResetExport()
        pm.mel.FBXExportFileVersion(v="FBX201900")
        pm.mel.FBXExportUpAxis("y")
        pm.mel.FBXExportScaleFactor(1)
        pm.mel.FBXExportEmbeddedTextures(v=True)

        # geometry
        pm.mel.FBXExportSmoothingGroups(v=True)
        pm.mel.FBXExportAnimationOnly(v=False)
        pm.mel.FBXExportHardEdges(v=False)
        pm.mel.FBXExportTangents(v=False)
        pm.mel.FBXExportSmoothMesh(v=True)
        pm.mel.eval('FBXProperty "Export|IncludeGrp|Geometry|SelectionSet" -v 0;')
        pm.mel.FBXExportInstances(v=False)
        pm.mel.FBXExportReferencedAssetsContent(v=True)
        pm.mel.FBXExportTriangulate(v=False)

        # connections
        pm.mel.FBXExportInputConnections(v=True)
        pm.mel.FBXExportIncludeChildren(v=True)

        # camera
        pm.mel.FBXExportCameras(v=True)

        # lights
        pm.mel.FBXExportLights(v=True)

        # constraints
        pm.mel.FBXExportConstraints(v=False)
        pm.mel.FBXExportSkeletonDefinitions(v=False)

        # deformed models
        pm.mel.FBXExportShapes(v=True)
        pm.mel.FBXExportSkins(v=True)

        # export the fbx path
        self.logger.info(f"Export FBX path: {self.fbx_asset_path}")
        file_utils.create_directories(os.path.dirname(self.fbx_asset_path))
        pm.mel.FBXExport(f=self.fbx_asset_path, s=True)
